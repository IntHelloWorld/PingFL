import json
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from openai.types.chat import ChatCompletionMessage
from rich.live import Live
from rich.table import Table

from src.config import BugInfo
from src.core.llm_backend import AnthropicBackend, LLMBackend
from src.core.memory import Memory
from src.core.prompt import (
    VERIFY_AGENT_SYSTEM_PROMPT,
    VERIFY_AGENT_TOOLS_CLAUDE,
    VERIFY_AGENT_TOOLS_OPENAI,
    VERIFY_AGENT_USER_PROMPT,
)
from src.core.utils import (
    ContextMatcher,
    add_line_numbers,
    extract_diff_block,
    extract_edit_block,
    extract_java_block,
    extract_json_blocks,
    extract_print_blocks,
    extract_replace_lines,
    extract_search_replace_blocks,
    get_original_lines,
    get_replace_lines,
    remove_whitespace,
)
from src.interfaces.d4j import check_out_playground, run_single_test_playground
from src.repograph.graph_searcher import Tag
from src.schema import VerifyInput, VerifyResult


@dataclass
class ProcessState:
    verify_input: VerifyInput
    llm: AnthropicBackend
    memory: Memory
    id: str
    edit_count: int = 0

    @property
    def edit_trace(self):
        return f"Edits: {self.edit_count}/3"


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
        table.add_column("Edit Progress")
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
    def __init__(
        self,
        bug_info: BugInfo,
        model_name: str,
        max_workers: int = 5,
        debug: bool = False,
        llm_args: Dict[str, Any] = {},
    ):
        self.bug_info = bug_info
        self.model_name = model_name
        self.debug = debug
        self.llm_args = llm_args
        self.processes: Dict[int, ProcessState] = {}
        self.process_counter = 0
        self.process_lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def create_process(self, input: VerifyInput) -> int:
        with self.process_lock:
            process_id = self.process_counter
            self.processes[process_id] = ProcessState(
                verify_input=input,
                llm=LLMBackend(),
                memory=Memory(
                    VERIFY_AGENT_SYSTEM_PROMPT, model_name=self.model_name
                ),
                id=str(process_id),
            )
            process = self.processes[process_id]

            # initial message
            input.method_code = add_line_numbers(
                input.method.code, input.method.line[0], input.method.line[1]
            )
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
            "Running",
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
        java_back_file = java_file.with_suffix(".bak")
        Path.replace(java_file, java_back_file)
        content = java_back_file.read_text()
        method_loc_interval = (method.line[0], method.line[1])

        while True:
            response = process.llm.call(
                messages=process.memory.get_messages(),
                model=self.model_name,
                tools=VERIFY_AGENT_TOOLS_OPENAI,
                parallel_tool_calls=False,
                # tool_choice={"type": "auto", "disable_parallel_tool_use": True},
                # tool_choice={"type": "tool", "name": "edit_and_run"},
                **self.llm_args,
            )
            message: ChatCompletionMessage = response.choices[0].message
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_args = json.loads(tool_call.function.arguments)
                start_line = function_args["start_line"]
                end_line = function_args["end_line"]
                edit_command = extract_java_block(
                    function_args["replace_code"]
                )
                method_loc_interval = (start_line, end_line)

                process.edit_count += 1
                monitor.update_status(
                    process.id,
                    process.verify_input.method.method_id,
                    "Running",
                    process.edit_trace,
                )

                edit_result = edit_and_run(
                    self.bug_info,
                    process,
                    edit_command,
                    playgroud_dir,
                    java_file,
                    content,
                    method_loc_interval,
                )
                process.memory.add_message(message)
                process.memory.add_message(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": edit_result,
                    }
                )
                continue
            else:
                # LLM return the final result
                try:
                    final_result = extract_json_blocks(message.content)
                except Exception:
                    raise Exception(
                        "Response format error. No json block found."
                    )
                monitor.update_status(
                    process.id,
                    process.verify_input.method.method_id,
                    "Completed",
                    process.edit_trace,
                )
                process.memory.add_message(
                    {"role": "assistant", "content": message.content}
                )
                break

        # cleanup
        shutil.rmtree(playgroud_dir)

    def run(self, inputs: List[VerifyInput]) -> List[Memory]:
        monitor = ThreadStatusMonitor()
        self.futures = []

        # Create processes
        for input in inputs:
            if (
                input.method.method_id
                != "com.google.javascript.jscomp.TypeCheck.visit#470-846"
            ):
                continue
            process_id = self.create_process(input)
            future = self.thread_pool.submit(
                self.run_process, process_id, monitor
            )
            future.process_id = process_id
            self.futures.append(future)

        if self.debug:
            with Live(monitor.get_table(), refresh_per_second=1) as live:
                while any([not future.done() for future in self.futures]):
                    live.update(monitor.get_table())
                    time.sleep(0.5)
        else:
            wait(self.futures)

        # check if there are exceptions in the futures
        for future in self.futures:
            if future.exception():
                raise future.exception()

        memories = [
            self.processes[future.process_id].memory for future in self.futures
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

    output_file = playgroud_dir / "output.txt"

    # create a window of the method for more precise replacement
    # start_line = max(method_loc_interval[0] - 6, 0)
    # end_line = method_loc_interval[1] + 4
    start_line = method_loc_interval[0]
    end_line = method_loc_interval[1]

    # apply the edits
    # try:
    #     new_content, extra_lines = apply_edit_command(edit_command, content, (start_line, end_line))
    # except Exception as e:
    #     return f"Error: {str(e)}"
    new_content, extra_lines = apply_edit_command(
        edit_command, content, (start_line, end_line)
    )

    # transform print statements
    new_loc_interval = (start_line, end_line + extra_lines)
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


# def apply_edit_command(command: str, content: str, loc_interval: tuple[int, int]):
#     content_lines = content.splitlines()
#     window_lines = content_lines[loc_interval[0]:loc_interval[1]]
#     replace_code = extract_edit_block(command)
#     if replace_code is None:
#         raise Exception("Edit command format error. No edit block found.")

#     replace_lines = replace_code.splitlines()
#     # find the line interval need to be replaced
#     matcher = ContextMatcher(window_lines, replace_lines)
#     interval = matcher.find_context()

#     start_line, end_line = interval
#     new_window_lines = window_lines[:start_line] + replace_lines + window_lines[end_line + 1:]
#     new_content = "\n".join(
#         content_lines[:loc_interval[0]]
#         + new_window_lines
#         + content_lines[loc_interval[1]:]
#     )

#     extra_lines = len(new_window_lines) - len(window_lines)
#     return new_content, extra_lines


def apply_edit_command(
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
        print("Warning: No print statements found in the edited method.")
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
