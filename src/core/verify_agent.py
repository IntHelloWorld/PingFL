import json
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

from openai.types.chat import ChatCompletionMessage
from rich.live import Live
from rich.table import Table

from src.config import BugInfo
from src.core.llm_backend import LLMBackend
from src.core.memory import Memory
from src.core.prompt import (
    VERIFY_AGENT_DEBUGGING_PROMPT,
    VERIFY_AGENT_RESULT_PROMPT,
    VERIFY_AGENT_USER_PROMPT,
)
from src.core.utils import (
    ContextMatcher,
    extract_edit_block,
    extract_java_block,
    extract_json_block,
    extract_print_blocks,
    extract_search_replace_block,
)
from src.exceptions import (
    EditCommandContentError,
    EditCommandFormatError,
    PrintStmtNotFoundError,
)
from src.interfaces.d4j import check_out_playground, run_single_test_playground
from src.schema import VerifyInput


@dataclass
class ProcessState:
    verify_input: VerifyInput
    llm: LLMBackend
    memory: Memory
    id: str
    edit_count: int = 0
    retry_count: int = 0

    @property
    def edit_trace(self):
        return f"{self.edit_count}/{self.retry_count}"


class ThreadStatusMonitor:
    def __init__(self):
        self.thread_statuses = {}
        self.lock = threading.Lock()

    def update_status(self, thread_name, method_id, status, edit_trace):
        with self.lock:
            self.thread_statuses[thread_name] = {
                "method_id": method_id,
                "status": status,
                "edit_trace": edit_trace,
                "last_update": time.time(),
            }

    def get_table(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Thread ID")
        table.add_column("Method")
        table.add_column("Status")
        table.add_column("Edit/Retry")
        table.add_column("Last Update")

        with self.lock:
            for thread_name, info in self.thread_statuses.items():
                table.add_row(
                    thread_name,
                    info["method_id"],
                    f"[green]{info['status']}[/green]",
                    info["edit_trace"],
                    f"{time.strftime('%H:%M:%S', time.localtime(info['last_update']))}",
                )
        return table


class VerifyAgent:
    def __init__(self, bug_info: BugInfo, debug: bool = False):
        self.bug_info = bug_info
        self.debug = debug
        self.processes: Dict[int, ProcessState] = {}
        self.process_counter = 0
        self.process_lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(
            max_workers=bug_info.config.hyper.verify_workers
        )
        self.futures = []

    def refresh(self):
        self.processes = {}
        self.process_counter = 0
        self.futures = []

    def create_process(self, input: VerifyInput) -> int:
        with self.process_lock:
            process_id = self.process_counter
            self.processes[process_id] = ProcessState(
                verify_input=input,
                llm=LLMBackend(
                    api_key=self.bug_info.config.verify_model.api_key,
                    base_url=self.bug_info.config.verify_model.base_url,
                ),
                memory=Memory(
                    VERIFY_AGENT_DEBUGGING_PROMPT,
                    model_name=self.bug_info.config.verify_model.model,
                ),
                id=str(process_id),
            )
            process = self.processes[process_id]

            # initial message
            user_message = {
                "role": "user",
                "content": VERIFY_AGENT_USER_PROMPT.format(**asdict(input)),
            }
            process.memory.add_message(user_message)

            self.process_counter += 1
            return process_id

    def run_process(
        self,
        process_id: int,
        monitor: ThreadStatusMonitor,
    ) -> None:
        process = self.processes[process_id]
        monitor.update_status(
            process.id,
            process.verify_input.method.method_id,
            "Debugging",
            process.edit_trace,
        )

        method = process.verify_input.method
        playgroud_dir = (
            process.verify_input.output_dir / f"playground-{method.__hash__()}"
        )

        # checkout the project
        check_out_playground(self.bug_info, playgroud_dir)

        # prepare some initial information
        java_file: Path = (
            playgroud_dir / self.bug_info.src_prefix / method.rel_fname
        )
        assert java_file.exists(), f"Java file {java_file} does not exist"
        java_back_file = java_file.with_suffix(
            ".bak"
        )  # the initial version of the file
        if not java_back_file.exists():
            Path.replace(java_file, java_back_file)
        content = java_back_file.read_text()
        method_loc_interval = (method.line[0], method.line[1])

        # start print debugging
        retry_round = False
        while True:
            self.bug_info.logger.info(
                f"Print Debugging method {method.method_id}"
            )
            if retry_round:
                # label the last two messages as retry messages
                process.memory.retry_msg_idx.extend(
                    [
                        len(process.memory.messages) - 2,
                        len(process.memory.messages) - 1,
                    ]
                )

            response = process.llm.call(
                messages=process.memory.get_messages(),
                model=self.bug_info.config.verify_model.model,
                **self.bug_info.config.verify_model.llm_args.asdict(),
            )
            message: ChatCompletionMessage = response.choices[0].message
            process.memory.add_message(
                {"role": "assistant", "content": message.content}
            )
            edit_command = extract_java_block(message.content)

            if edit_command:
                monitor.update_status(
                    process.id,
                    process.verify_input.method.method_id,
                    "Debugging",
                    process.edit_trace,
                )

                try:
                    edit_result = edit_and_run(
                        self.bug_info,
                        process,
                        edit_command,
                        playgroud_dir,
                        java_file,
                        content,
                        method_loc_interval,
                    )
                    process.edit_count += 1
                    process.memory.add_message(
                        {"role": "user", "content": edit_result}
                    )
                    retry_round = False
                except Exception as e:
                    process.retry_count += 1
                    process.memory.add_message(
                        {"role": "user", "content": e.message}
                    )
                    retry_round = True
            else:
                # LLM return the debug report
                monitor.update_status(
                    process.id,
                    process.verify_input.method.method_id,
                    "Verifying",
                    process.edit_trace,
                )
                break

        # start verifying
        self.bug_info.logger.info(
            f"Get verify result of method {method.method_id}"
        )
        process.memory.add_message(
            {"role": "user", "content": VERIFY_AGENT_RESULT_PROMPT}
        )
        while True:
            response = process.llm.call(
                messages=process.memory.get_messages(),
                model=self.bug_info.config.search_model.model,
                **self.bug_info.config.search_model.llm_args.asdict(),
            )
            message: ChatCompletionMessage = response.choices[0].message
            process.memory.add_message(
                {"role": "assistant", "content": message.content}
            )
            result = extract_json_block(message.content)

            # check if the result is valid
            if result is None:
                process.retry_count += 1
                error_message = f"Reponse format error, please return a JSON format verification result wrapped with ```json...``` block."
                process.memory.add_message(
                    {"role": "user", "content": error_message}
                )
                continue
            else:
                result = json.loads(result)
                if result["category"] not in ["buggy", "benign", "uncertain"]:
                    process.retry_count += 1
                    error_message = f"Invalid verification result category: {result['category']}, should be one of ['buggy', 'benign', 'uncertain'], please try again."
                    process.memory.add_message(
                        {"role": "user", "content": error_message}
                    )
                    continue

            monitor.update_status(
                process.id,
                process.verify_input.method.method_id,
                "Finished",
                process.edit_trace,
            )
            break

        # cleanup
        shutil.rmtree(playgroud_dir)

    def run(self, inputs: List[VerifyInput]) -> List[Memory]:
        self.refresh()
        monitor = ThreadStatusMonitor()

        # Create processes
        for input in inputs:
            process_id = self.create_process(input)
            future = self.thread_pool.submit(
                self.run_process, process_id, monitor
            )
            future.process_id = process_id
            self.futures.append(future)

        if self.debug:
            with Live(monitor.get_table(), refresh_per_second=1) as live:
                while not all(future.done() for future in self.futures):
                    live.update(monitor.get_table())
                    time.sleep(1)
        else:
            while not all(future.done() for future in self.futures):
                time.sleep(1)

        # check if there are exceptions in the futures
        for future in self.futures:
            if future.exception():
                raise future.exception()

        memories = [
            self.processes[process_id].memory for process_id in self.processes
        ]
        return memories


def edit_and_run(
    bug_info: BugInfo,
    process: ProcessState,
    edit_command: str,
    playgroud_dir: Path,
    java_file: Path,
    content: str,
    method_loc_interval: tuple[int, int],
):

    # apply the edits
    new_content, extra_lines = apply_edit_commands_search_replace(
        edit_command, content, (method_loc_interval[0], method_loc_interval[1])
    )

    # transform print statements
    new_loc_interval = (
        method_loc_interval[0],
        method_loc_interval[1] + extra_lines,
    )
    output_file = playgroud_dir / "output.txt"
    final_content = transform_print_stmt(
        new_content, output_file, new_loc_interval
    )

    # create the new file
    java_file.write_text(final_content)

    # run the test
    output = run_single_test_playground(
        bug_info, playgroud_dir, process.verify_input.test_name
    )
    return output


def apply_edit_command_context_match(
    command: str, content: str, loc_interval: tuple[int, int]
):
    content_lines = content.splitlines()
    window_lines = content_lines[loc_interval[0] : loc_interval[1]]
    replace_code = extract_edit_block(command)
    if replace_code is None:
        raise Exception("Edit command format error. No edit block found.")

    replace_lines = replace_code.splitlines()
    # find the line interval need to be replaced
    matcher = ContextMatcher(window_lines, replace_lines)
    interval = matcher.find_context()

    start_line, end_line = interval
    new_window_lines = (
        window_lines[:start_line]
        + replace_lines
        + window_lines[end_line + 1 :]
    )
    new_content = "\n".join(
        content_lines[: loc_interval[0]]
        + new_window_lines
        + content_lines[loc_interval[1] :]
    )

    extra_lines = len(new_window_lines) - len(window_lines)
    return new_content, extra_lines


def apply_edit_commands_search_replace(
    edit_command: str, content: str, method_loc_interval: tuple[int, int]
):
    extra_lines = 0
    content_lines = content.splitlines()

    # create a window of the method for more precise replacement
    start_line = max(method_loc_interval[0] - 6, 0)
    end_line = method_loc_interval[1] + 6

    context_segment = "\n".join(content_lines[start_line:end_line])
    context_segment = "\n" + context_segment + "\n"

    # first check edit.
    match = extract_search_replace_block(edit_command)
    if match is None:
        raise EditCommandFormatError(edit_command)
    search_text, replace_text = match

    if search_text not in context_segment:
        raise EditCommandContentError(edit_command)

    # apply edits
    context_segment = context_segment.replace(search_text, replace_text)
    extra_lines += replace_text.count("\n") - search_text.count("\n")
    # reassembly
    content = (
        "\n".join(content_lines[:start_line])
        + context_segment
        + "\n".join(content_lines[end_line:])
    )

    return content, extra_lines


def apply_edit_command_all_method(
    command: str, content: str, loc_interval: tuple[int, int]
):
    content_lines = content.splitlines()
    replace_lines = command.splitlines()

    new_content = "\n".join(
        content_lines[: loc_interval[0] - 1]
        + replace_lines
        + content_lines[loc_interval[1] :]
    )

    extra_lines = len(replace_lines) - (loc_interval[1] - loc_interval[0] + 1)
    return new_content, extra_lines


def transform_print_stmt(
    content: str, output_file: Path, file_loc_interval: tuple[int, int]
) -> str:
    context_segment = "\n".join(
        content.splitlines()[file_loc_interval[0] : file_loc_interval[1]]
    )
    context_segment = "\n" + context_segment + "\n"

    # the junit framework intercepted the standard input and output
    # so we transform print statements to write to a file
    write_stmt = (
        'try {{ Path filePath = Paths.get("{output_file}"); '
        'Files.write(filePath, ({output_str} + "\\n").getBytes(), StandardOpenOption.CREATE, StandardOpenOption.APPEND); }} '
        "catch (Exception e) {{ e.printStackTrace(); }}"
    )
    matches = extract_print_blocks(context_segment)
    if not matches:
        raise PrintStmtNotFoundError(context_segment)
    for print_stmt, arguments in matches:
        context_segment = context_segment.replace(
            print_stmt,
            write_stmt.format(
                output_str=arguments.replace("\n", ""),
                output_file=output_file.resolve().as_posix(),
            ),
        )

    # reassembly
    content = (
        "\n".join(content.splitlines()[: file_loc_interval[0]])
        + context_segment
        + "\n".join(content.splitlines()[file_loc_interval[1] :])
    )

    # add import statements, should be after the package statement
    import_stmt = (
        "import java.nio.file.Files; "
        "import java.nio.file.Path; "
        "import java.nio.file.Paths; "
        "import java.nio.file.StandardOpenOption;"
    )
    content_lines = content.splitlines()
    for i, line in enumerate(content_lines):
        if line.startswith("package "):
            content_lines.insert(i + 1, import_stmt)
            break
    content = "\n".join(content_lines)
    return content


if __name__ == "__main__":
    agent = VerifyAgent("gpt-4")
    inputs = [
        {
            "test_name": "test1",
            "test_code": "...",
            "error_message": "...",
            "method_id": "...",
            "hypotheses": "...",
            "method_code": "...",
        }
    ]
    results = agent.run(inputs)
    print(results)
