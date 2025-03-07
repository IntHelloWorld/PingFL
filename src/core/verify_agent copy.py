import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from openai.types.chat import ChatCompletionMessage
from rich.live import Live
from rich.table import Table

from src.config import BugInfo
from src.core.llm_backend import LLMBackend
from src.core.memory import Memory
from src.core.prompt import (
    EDIT_SUGGESTION,
    VERIFY_AGENT_EDITOR_SYSTEM_PROMPT,
    VERIFY_AGENT_EDITOR_USER_PROMPT,
    VERIFY_AGENT_TOOLS,
    VERIFY_AGENT_VERIFIER_SYSTEM_PROMPT,
    VERIFY_AGENT_VERIFIER_USER_PROMPT,
    MethodVerifyResult,
)
from src.core.utils import extract_print_blocks, remove_whitespace
from src.interfaces.d4j import check_out_playground, run_single_test_playground
from src.repograph.graph_searcher import Tag


@dataclass
class VerifyInput:
    bug_name: str
    test_name: str
    test_code: str
    error_message: str
    method_id: str
    hypotheses: str
    method_code: str
    output_dir: Path
    method: Tag


@dataclass
class VerifyResult:
    method_id: str
    category: str
    explanation: str


@dataclass
class ProcessState:
    verify_input: VerifyInput
    llm: LLMBackend
    memories: List[Memory]
    id: str
    edit_count: int = 0

    @property
    def edit_trace(self):
        return f"Edits: {self.edit_count}/3"

    @property
    def is_edit_turn(self):
        return len(self.memories) % 2 == 0


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
        max_edit_times: int = 3,
        max_workers: int = 5,
        debug: bool = False,
        llm_args: Dict[str, Any] = {},
    ):
        self.bug_info = bug_info
        self.model_name = model_name
        self.max_edit_times = max_edit_times
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
                memories=[],
                id=str(process_id),
            )
            self.process_counter += 1
            return process_id

    def create_verifier_memory(
        self, process: ProcessState, new_method_code: str, program_output: str
    ) -> Memory:
        verifier_memory = Memory(
            VERIFY_AGENT_VERIFIER_SYSTEM_PROMPT, model_name=self.model_name
        )
        input_dict = asdict(process.verify_input)
        input_dict.update(
            {"program_output": program_output, "method_code": new_method_code}
        )
        verifier_memory.add_message(
            {
                "role": "system",
                "content": VERIFY_AGENT_VERIFIER_USER_PROMPT.format(
                    **input_dict
                ),
            }
        )
        return verifier_memory

    def create_editor_memory(self, process: ProcessState) -> Memory:
        editor_memory = Memory(
            VERIFY_AGENT_EDITOR_SYSTEM_PROMPT, model_name=self.model_name
        )
        if len(process.memories) == 0:
            edit_suggestion = ""
        else:
            explaination = (
                process.memories[-1].get_messages()[-1].parsed["explanation"]
            )
            edit_suggestion = EDIT_SUGGESTION.format(explaination)

        input_dict = asdict(process.verify_input)
        input_dict.update({"edit_suggestion": edit_suggestion})
        editor_memory.add_message(
            {
                "role": "system",
                "content": VERIFY_AGENT_EDITOR_USER_PROMPT.format(
                    **input_dict
                ),
            }
        )
        return editor_memory

    def run_process(
        self,
        process_id: int,
        monitor: ThreadStatusMonitor,
    ) -> None:
        process = self.processes[process_id]

        # the LLM can try to edit and verify the method for N times
        while process.edit_count < self.max_edit_times:
            edit_result = None
            new_method_code = None

            # edit the method
            monitor.update_status(
                process.id,
                process.verify_input.method.method_id,
                "Editing",
                process.edit_trace,
            )
            process.memories.append(self.create_editor_memory(process))
            response = process.llm.call(
                messages=process.memories[-1].get_messages(),
                tools=VERIFY_AGENT_TOOLS,
                model=self.model_name,
                parallel_tool_calls=False,
                **self.llm_args,
            )
            message: ChatCompletionMessage = response.choices[0].message
            assert message.tool_calls is not None
            tool_call = message.tool_calls[0]
            process.edit_count += 1

            edit_commands = json.loads(tool_call.function.arguments)["edits"]
            edit_commands = [edit["edit"] for edit in edit_commands]
            new_method_code, edit_result = edit_and_run(
                self.bug_info, process, edit_commands
            )

            process.memories[-1].add_message(message)
            process.memories[-1].add_message(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": edit_result,
                }
            )

            # verify the method
            monitor.update_status(
                process.id,
                process.verify_input.method.method_id,
                "Verifying",
                process.edit_trace,
            )
            process.memories.append(
                self.create_verifier_memory(
                    process, new_method_code, edit_result
                )
            )
            response = process.llm.call_parse(
                messages=process.memories[-1].get_messages(),
                response_format=MethodVerifyResult,
                model=self.model_name,
                **self.llm_args,
            )
            llm_message = response.choices[0].message
            process.memories[-1].add_message(llm_message)
            json_res: MethodVerifyResult = llm_message.parsed
            if json_res.category != "UNCERTAIN":
                break

        monitor.update_status(
            process.id,
            process.verify_input.method.method_id,
            "Completed",
            process.edit_trace,
        )

    def read_results(
        self, verify_inputs: List[VerifyInput]
    ) -> List[VerifyResult]:
        res_file = verify_inputs[0].output_dir / "verify_results.json"
        if res_file.exists():
            res_dict = json.loads(res_file.read_text())
            verify_results = []
            for method_id, res in res_dict.items():
                verify_results.append(
                    VerifyResult(
                        method_id=method_id,
                        category=res["category"],
                        explanation=res["explanation"],
                    )
                )
            return verify_results
        return None

    def parse_results(
        self, verify_inputs: List[VerifyInput]
    ) -> List[VerifyResult]:
        memories = [p.memories[-1] for p in self.processes.values()]
        llm_responses = [m.get_messages()[-1] for m in memories]

        res_dict = {}
        for i, verify_input in enumerate(verify_inputs):
            res_dict[verify_input.method_id] = llm_responses[i].parsed

        res_dir = verify_inputs[0].output_dir
        res_file = res_dir / "verify_results.json"
        res_dir.mkdir(parents=True, exist_ok=True)
        res_file.write_text(json.dumps(res_dict, indent=4))

        verify_results = []
        for method_id, res in res_dict.items():
            verify_results.append(
                VerifyResult(
                    method_id=method_id,
                    category=res.category,
                    explanation=res.explanation,
                )
            )
        return verify_results

    def run(self, inputs: List[VerifyInput]) -> List[Dict[str, Any]]:
        results = self.read_results(inputs)
        if results:
            return results

        monitor = ThreadStatusMonitor()
        self.futures = []

        # Create processes
        for input in inputs[:1]:
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
                print(f"Exception in future: {future.exception()}")

        results = self.parse_results(inputs)
        return results


def edit_and_run(
    bug_info: BugInfo, process: ProcessState, edit_commands: List[str]
) -> Tuple[str, str]:
    method = process.verify_input.method
    playgroud_dir = (
        process.verify_input.output_dir / f"playground-{method.__hash__()}"
    )
    output_file = process.verify_input.output_dir / "output.txt"

    # checkout the project
    check_out_playground(bug_info, playgroud_dir)

    # prepare input for the method editor
    edits = [
        extract_search_replace_blocks(command)[0] for command in edit_commands
    ]
    java_file: Path = playgroud_dir / bug_info.src_prefix / method.rel_fname
    assert java_file.exists(), f"Java file {java_file} does not exist"
    java_back_file = java_file.with_suffix(".bak")
    Path.replace(java_file, java_back_file)
    content = java_back_file.read_text()
    start_line = max(method.line[0] - 6, 0)
    end_line = method.line[1] + 4

    # apply the edits
    new_content, extra_lines = apply_edit_commands(
        edits, content, (start_line, end_line)
    )
    new_loc_interval = (start_line, end_line + extra_lines)
    new_method_code = "\n".join(
        new_content.splitlines()[
            method.line[0] - 2 : method.line[1] + extra_lines
        ]
    )

    # transform print statements
    final_content = transform_print_stmt(
        new_content, output_file, new_loc_interval
    )

    # create the new file
    java_file.write_text(final_content)

    # run the test
    run_single_test_playground(
        bug_info, playgroud_dir, process.verify_input.test_name
    )

    # read the output
    if not output_file.exists():
        raise Exception(f"Output file {output_file} does not exist")
    output = output_file.read_text()
    return new_method_code, output


def apply_edit_commands(commands, content, file_loc_interval: tuple[int, int]):
    replaced = False
    extra_lines = 0
    content_lines = content.splitlines()
    context_segment = "\n".join(
        content_lines[file_loc_interval[0] : file_loc_interval[1]]
    )
    context_segment = remove_whitespace(context_segment)
    context_segment = "\n" + context_segment + "\n"

    # first check for all edits.
    can_apply = []
    for subcommand in commands:
        if not (
            subcommand.startswith("<<<<<<< SEARCH")
            and subcommand.endswith(">>>>>>> REPLACE")
        ):
            raise Exception(f"Wrong format for edit command: {subcommand}")

        subcommand = "\n".join(subcommand.splitlines()[1:-1])
        if len(subcommand.split("\n=======\n")) != 2:
            raise Exception(f"Wrong format for edit command: {subcommand}")

        original, replace = subcommand.split("\n=======\n")
        original = remove_whitespace(original)
        replace = remove_whitespace(replace)
        original = "\n" + original + "\n"
        replace = "\n" + replace + "\n"

        if original in context_segment:
            can_apply.append((original, replace))
        else:
            raise Exception(
                f"Code block not found in the context:\n{original}"
            )

    # apply edits backwards
    for original, replace in can_apply[::-1]:
        if (
            original in context_segment
        ):  # This may not be true after some previously applied edits
            context_segment = context_segment.replace(original, replace)
            replaced = True
            extra_lines += replace.count("\n") - original.count("\n")
    # reassembly
    new_content = (
        "\n".join(content_lines[: file_loc_interval[0]])
        + context_segment
        + "\n".join(content_lines[file_loc_interval[1] :])
    )

    if not replaced:
        raise Exception("No edit was applied. Please check the edit commands.")

    return new_content, extra_lines


def transform_print_stmt(
    content: str, output_file: Path, file_loc_interval: tuple[int, int]
) -> str:
    context_segment = "\n".join(
        content.splitlines()[file_loc_interval[0] : file_loc_interval[1]]
    )
    context_segment = "\n" + context_segment + "\n"

    # transform print statements to write to a file
    write_stmt = (
        'try {{ Path filePath = Paths.get("{output_file}"); '
        'Files.write(filePath, ({output_str} + "\\n").getBytes(), StandardOpenOption.CREATE, StandardOpenOption.APPEND); }} '
        "catch (Exception e) {{ e.printStackTrace(); }}"
    )
    matches = extract_print_blocks(context_segment)
    if not matches:
        raise Exception("No print statements found in the code.")
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
