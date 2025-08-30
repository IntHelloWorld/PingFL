import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from src.config import BugInfo
from src.core.llm_backend import AnthropicBackend, LLMBackend, OpenAIBackend
from src.core.memory import Memory
from src.core.prompt import (
    REACH_MAX_EDIT_COUNTS,
    REACH_MAX_RETRY_COUNTS,
    VERIFY_AGENT_DEBUGGING_PROMPT,
    VERIFY_AGENT_USER_PROMPT,
)
from src.core.prompt_ablation import (
    VERIFY_AGENT_DEBUGGING_PROMPT_ABLATION,
    VERIFY_AGENT_USER_PROMPT_NO_STACK_TRACE,
    VERIFY_AGENT_USER_PROMPT_NO_SUSPECTED_ISSUE,
    VERIFY_AGENT_USER_PROMPT_NO_TEST_CODE,
    VERIFY_AGENT_USER_PROMPT_NO_TEST_OUTPUT,
)
from src.core.utils import (
    ContextMatcher,
    extract_edit_block,
    extract_java_block,
    extract_print_blocks,
    extract_search_replace_block,
)
from src.exceptions import (
    EditCommandContentError,
    EditCommandFormatError,
    PrintDebugFileNotFoundError,
    PrintStmtNotFoundError,
)
from src.interfaces.d4j import check_out_playground, run_single_test_playground
from src.schema import VerifyInput


@dataclass
class ProcessState:
    verify_input: VerifyInput
    llm: LLMBackend
    memory: Memory
    edit_count: int = 0
    retry_count: int = 0

    @property
    def edit_trace(self):
        return f"{self.edit_count}/{self.retry_count}"


class VerifyAgent:

    def __init__(self, bug_info: BugInfo, org: str):
        self.bug_info = bug_info
        self.org = "openai"
        assert org in ["openai", "anthropic"]
        if org == "openai":
            self.llm_backend = OpenAIBackend
        else:
            self.llm_backend = AnthropicBackend
        self.max_edit_count = bug_info.config.hyper.max_edit_count
        self.max_retry_count = bug_info.config.hyper.max_retry_count
        if bug_info.config.hyper.use_ablation:
            self.prompt = VERIFY_AGENT_DEBUGGING_PROMPT_ABLATION
        else:
            self.prompt = VERIFY_AGENT_DEBUGGING_PROMPT

        self.user_prompt = VERIFY_AGENT_USER_PROMPT
        if bug_info.config.hyper.use_ablation:
            if bug_info.config.ablation.test_code:
                self.user_prompt = VERIFY_AGENT_USER_PROMPT_NO_TEST_CODE
            elif bug_info.config.ablation.suspected_issue:
                self.user_prompt = VERIFY_AGENT_USER_PROMPT_NO_SUSPECTED_ISSUE
            elif bug_info.config.ablation.test_output:
                self.user_prompt = VERIFY_AGENT_USER_PROMPT_NO_TEST_OUTPUT
            elif bug_info.config.ablation.stack_trace:
                self.user_prompt = VERIFY_AGENT_USER_PROMPT_NO_STACK_TRACE

    def run(self, input: VerifyInput) -> Memory:
        process: ProcessState = self.create_process(input)
        self.run_process(process)
        self.save_memory(process)
        print_debugging_report = process.memory.get_debug_report()
        return print_debugging_report

    def save_memory(self, process: ProcessState):
        verify_file = (
            process.verify_input.output_dir
            / process.verify_input.process_id
            / f"debug_{process.verify_input.method_id.replace('.', '_')}.json"
        )
        memory_cache = {
            "memory": process.memory.serialize(),
            "print_debugging_report": process.memory.get_debug_report(),
        }
        verify_file.write_text(json.dumps(memory_cache, indent=2))
        self.bug_info.logger.info(f"Save debug memory cache to {verify_file}")

    def create_process(self, input: VerifyInput) -> ProcessState:
        process = ProcessState(
            verify_input=input,
            llm=self.llm_backend(
                api_key=self.bug_info.config.verify_model.api_key,
                base_url=self.bug_info.config.verify_model.base_url,
            ),
            memory=Memory(
                self.prompt.format(max_edit_count=self.max_edit_count),
                model_name=self.bug_info.config.verify_model.model,
            ),
        )

        # initial message
        user_message = {
            "role": "user",
            "content": self.user_prompt.format(**asdict(input)),
        }
        process.memory.add_message(user_message)
        return process

    def run_process(self, process: ProcessState) -> None:

        method = process.verify_input.method
        process_verify_dir = (
            process.verify_input.output_dir / process.verify_input.process_id
        )
        if not process_verify_dir.exists():
            process_verify_dir.mkdir(parents=True, exist_ok=True)
        playgroud_dir = process_verify_dir / f"playground-{method.__hash__()}"

        # checkout the project
        check_out_playground(self.bug_info, playgroud_dir)

        # prepare some initial information
        java_file: Path = (
            playgroud_dir / self.bug_info.src_prefix / method.rel_fname
        )
        if not java_file.exists():
            raise PrintDebugFileNotFoundError()
        java_back_file = java_file.with_suffix(
            ".bak"
        )  # the initial version of the file
        if not java_back_file.exists():
            Path.replace(java_file, java_back_file)
        content = java_back_file.read_text()
        method_loc_interval = (method.line[0], method.line[1])

        # start print debugging
        while True:
            if process.edit_count >= self.max_edit_count:
                process.memory.add_message(
                    {"role": "user", "content": REACH_MAX_EDIT_COUNTS}
                )

            if process.retry_count >= self.max_retry_count:
                process.memory.add_message(
                    {"role": "user", "content": REACH_MAX_RETRY_COUNTS}
                )

            response = process.llm.call(
                messages=process.memory.get_messages(),
                model=self.bug_info.config.verify_model.model,
                **self.bug_info.config.verify_model.llm_args.asdict(),
            )
            message = self.llm_backend.get_msg(response)
            message_text = self.llm_backend.get_msg_text(message)
            input_tokens, output_tokens = self.llm_backend.get_tokens(response)
            edit_command = extract_edit_block(message_text)

            if edit_command:
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
                        {"role": "assistant", "content": message_text}
                    )
                    process.memory.add_message(
                        {"role": "user", "content": edit_result}
                    )
                    self.bug_info.logger.info(
                        f"[Print Debugging] Method: {process.verify_input.method.method_id}, Edit/Retry: {process.edit_trace}"
                    )
                    process.memory.add_cost(output_tokens, input_tokens)
                except Exception as e:
                    process.retry_count += 1
                    process.memory.add_message(
                        {"role": "assistant", "content": message_text},
                        "retry",
                    )
                    process.memory.add_message(
                        {"role": "user", "content": e.message}, "retry"
                    )
                    self.bug_info.logger.info(
                        f"[Print Debugging] Method: {process.verify_input.method.method_id}, Edit/Retry: {process.edit_trace}"
                    )
                    self.bug_info.logger.debug(str(e))
            else:
                # LLM return the debug report
                process.memory.add_message(
                    {"role": "assistant", "content": message_text},
                    type="debug_report",
                )
                self.bug_info.logger.info(
                    f"[Print Debugging] Method: {process.verify_input.method.method_id} OK!"
                )
                break

        # cleanup
        shutil.rmtree(playgroud_dir)


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

    # This not compatible with Java 1.4 compiler
    # write_stmt = (
    #     'try {{ java.nio.file.Path filePath = java.nio.file.Paths.get("{output_file}"); '
    #     'java.nio.file.Files.write(filePath, ({output_str} + "\\n").getBytes(), java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND); }} '
    #     "catch (Exception e) {{ e.printStackTrace(); }}"
    # )

    write_stmt = 'try {{ java.io.FileWriter fw = new java.io.FileWriter("{output_file}", true); fw.write({output_str} + "\\n"); fw.close(); }} catch (java.io.IOException e) {{ e.printStackTrace(); }}'
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
    # import_stmt = (
    #     "import java.nio.file.Files; "
    #     "import java.nio.file.Path; "
    #     "import java.nio.file.Paths; "
    #     "import java.nio.file.StandardOpenOption;"
    # )
    # content_lines = content.splitlines()
    # for i, line in enumerate(content_lines):
    #     if line.startswith("package "):
    #         content_lines.insert(i + 1, import_stmt)
    #         break
    # content = "\n".join(content_lines)
    return content
