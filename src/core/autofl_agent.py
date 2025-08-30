import copy
import json
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from anthropic.types import ToolUseBlock
from openai.types.chat import ChatCompletionMessageToolCall

from src.config import BugInfo
from src.core.llm_backend import LLMBackend, OpenAIBackend
from src.core.memory import Memory
from src.core.prompt import (
    AUTOFL_DEBUGGING_PROMPT,
    FAULT_LOCALIZATION_PROMPT_AUTOFL,
    REACH_MAX_TOOL_CALLS,
    SEARCH_AGENT_USER_PROMPT,
    TOOLS_AUTOFL,
)
from src.repograph.graph_searcher import RepoSearcher
from src.schema import SearchInput, VerifyInput


@dataclass
class ProcessState:
    input: SearchInput
    llm: LLMBackend
    memory: Memory
    id: str
    function_calls: List[str] = field(default_factory=list)
    verify_rounds: int = 0

    @property
    def num_function_calls(self):
        return len(self.function_calls)


class AutoflAgent:

    def __init__(self, bug_info: BugInfo, searcher: RepoSearcher):
        self.bug_info = bug_info
        self.searcher = searcher

        self.max_tool_calls = bug_info.config.hyper.max_tool_calls
        self.debug_prompt = AUTOFL_DEBUGGING_PROMPT

        self.functions = {
            "get_covered_classes": self.searcher.get_covered_classes,
            "get_covered_method_ids_for_class": self.searcher.get_covered_method_ids_for_class,
            "get_method_code_for_id": self.searcher.get_method_code_for_id,
        }

        self.org = bug_info.config.search_model.org
        assert self.org == "openai"
        self.llm_backend = OpenAIBackend
        self.tool_set = TOOLS_AUTOFL

        self.processes: Dict[int, ProcessState] = {}
        self.futures: List[Future] = []
        self.process_counter = 0
        self.process_lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(
            max_workers=bug_info.config.hyper.search_workers,
        )
        self.futures = []

    def create_process(
        self, input: SearchInput, parent_id=None
    ) -> ProcessState:
        with self.process_lock:
            process_id = self.process_counter
            if parent_id is not None:
                parent_process = self.processes[parent_id]
                self.processes[process_id] = ProcessState(
                    input=input,
                    llm=self.llm_backend(
                        api_key=self.bug_info.config.search_model.api_key,
                        base_url=self.bug_info.config.search_model.base_url,
                    ),
                    memory=copy.deepcopy(parent_process.memory),
                    id=f"{parent_process.id}-{process_id}",
                    function_calls=copy.deepcopy(
                        parent_process.function_calls
                    ),
                )
            else:
                self.processes[process_id] = ProcessState(
                    input=input,
                    llm=self.llm_backend(
                        api_key=self.bug_info.config.search_model.api_key,
                        base_url=self.bug_info.config.search_model.base_url,
                    ),
                    memory=Memory(
                        self.debug_prompt,
                        self.bug_info.config.search_model.model,
                    ),
                    id=str(process_id),
                )
            self.process_counter += 1
            return process_id

    def save_memory(self):
        memory_cache = {}
        for process in self.processes.values():
            memory_cache[process.id] = {
                "memory": process.memory.serialize(),
                "debug_report": process.memory.get_debug_report(),
            }
        # save the memory cache to a file
        search_file = process.input.output_path / "search.json"
        search_file.write_text(json.dumps(memory_cache, indent=2))
        self.bug_info.logger.info(f"Save search memory cache to {search_file}")

    def init_memory(self, input: SearchInput, process_id: str) -> None:
        process = self.processes[process_id]
        default_messages = [
            {
                "role": "user",
                "content": SEARCH_AGENT_USER_PROMPT.format(**asdict(input)),
            },
            self.llm_backend.recover_msg(
                {
                    "content": None,
                    "refusal": None,
                    "role": "assistant",
                    "audio": None,
                    "function_call": None,
                    "tool_calls": [
                        {
                            "id": "call_default",
                            "function": {
                                "arguments": "{}",
                                "name": "get_covered_classes",
                            },
                            "type": "function",
                        }
                    ],
                }
            ),
            {
                "role": "tool",
                "tool_call_id": "call_default",
                "content": self.functions["get_covered_classes"](),
            },
        ]
        for message in default_messages:
            process.memory.add_message(message)

        process.function_calls.append("get_covered_classes")

    def run(self, input: SearchInput):
        entry_process_id = self.create_process(input)
        self.init_memory(input, entry_process_id)

        entry_future = self.thread_pool.submit(
            self.run_process, entry_process_id
        )
        entry_future.process_id = entry_process_id
        self.futures.append(entry_future)

        # wait for all futures to finish
        while not all(future.done() for future in self.futures):
            time.sleep(1)

        # check for exceptions in the futures
        has_exception = False
        for future in self.futures:
            try:
                result = future.result()
            except Exception as e:
                self.bug_info.logger.error(
                    f"<{self.processes[future.process_id].input.test_name}> - encountered an exception: {e}",
                    exc_info=True,
                )
                has_exception = True

        if has_exception:
            raise Exception(
                "Search agent encountered exceptions. Please check the logs for details."
            )
        self.save_memory()

    def execute_function(
        self,
        tool_call: ChatCompletionMessageToolCall | ToolUseBlock,
    ):
        function_args = self.llm_backend.get_tool_args(tool_call)
        function_name = self.llm_backend.get_tool_name(tool_call)
        function_to_call = self.functions[function_name]
        function_response = function_to_call(**function_args)
        return function_response

    def get_verify_input(
        self, process: ProcessState, suspected_issue: str, method_id: str
    ) -> VerifyInput:
        method = self.searcher.get_method(method_id)
        verify_input = VerifyInput(
            test_name=process.input.test_name,
            test_code=process.input.test_code,
            error_message=process.input.error_message,
            method_id=method_id,
            suspected_issue=suspected_issue,
            method_code=method.code,
            output_dir=process.input.output_path,
            method=method,
        )
        return verify_input

    def process_function_calls(
        self,
        process_id: int,
        message: ChatCompletionMessageToolCall | ToolUseBlock,
    ) -> None:
        tool_calls = self.llm_backend.get_tool_calls(message)
        for i in range(len(tool_calls[:1])):
            # create a new process for each tool call
            new_process_id = self.create_process(
                input=copy.deepcopy(self.processes[process_id].input),
                parent_id=process_id,
            )
            single_tool_call_message = (
                self.llm_backend.get_single_tool_call_msg(message, i)
            )
            future = self.thread_pool.submit(
                self.run_process,
                new_process_id,
                single_tool_call_message,
            )
            future.process_id = new_process_id
            self.futures.append(future)

        # remove the parent process and its futures
        with self.process_lock:
            self.processes.pop(process_id)
            for future in self.futures:
                if future.process_id == process_id:
                    self.futures.remove(future)

    def run_process(self, process_id: str, single_tool_call_msg=None) -> None:
        process = self.processes[process_id]

        if single_tool_call_msg:
            tool_call = self.llm_backend.get_tool_calls(single_tool_call_msg)[
                0
            ]
            tool_call_name = self.llm_backend.get_tool_name(tool_call)
            self.bug_info.logger.info(
                f"{self.bug_info.bug_name} - <{process.input.test_name}> - Process {process.id} - call function {tool_call_name}"
            )

            try:
                tool_call_result = self.execute_function(tool_call)
                process.function_calls.append(
                    self.llm_backend.get_tool_name(tool_call)
                )
            except Exception as e:
                self.bug_info.logger.error(
                    f"{self.bug_info.bug_name} - <{process.input.test_name}> - Process {process.id} - Error when executing function {tool_call}: {str(e)}"
                )
                tool_call_result = "Function cannot be called with the given arguments. Please try something else."
                process.function_calls.append("retry")
            process.memory.add_message(single_tool_call_msg)
            process.memory.add_message(
                self.llm_backend.get_tool_result_msg(
                    tool_call, tool_call_result
                )
            )

        # check if the process has reached the maximum number of tool calls
        if process.num_function_calls >= self.max_tool_calls:
            process.memory.add_message(
                {
                    "role": "assistant",
                    "content": REACH_MAX_TOOL_CALLS,
                }
            )
            response = process.llm.call(
                messages=process.memory.get_messages(),
                model=self.bug_info.config.search_model.model,
                **self.bug_info.config.search_model.llm_args.asdict(),
            )
        else:
            response = process.llm.call(
                messages=process.memory.get_messages(),
                tools=self.tool_set,
                model=self.bug_info.config.search_model.model,
                **self.bug_info.config.search_model.llm_args.asdict(),
            )

        message = self.llm_backend.get_msg(response)
        message_text = self.llm_backend.get_msg_text(message)
        tool_calls = self.llm_backend.get_tool_calls(message)
        input_tokens, output_tokens = self.llm_backend.get_tokens(response)
        process.memory.add_cost(output_tokens, input_tokens)

        if tool_calls:
            self.process_function_calls(process_id, message)
        else:
            self.bug_info.logger.info(
                f"{self.bug_info.bug_name} - <{process.input.test_name}> - Process {process.id} - start fault localization"
            )

            # get the bug explanation
            llm_message = {"role": "assistant", "content": message_text}
            process.memory.add_message(llm_message, "debug_report")

            # get the bug localization result
            fault_localization_message = {
                "role": "user",
                "content": FAULT_LOCALIZATION_PROMPT_AUTOFL,
            }
            process.memory.add_message(fault_localization_message)
            response = process.llm.call(
                messages=process.memory.get_messages(),
                model=self.bug_info.config.search_model.model,
                **self.bug_info.config.search_model.llm_args.asdict(),
            )
            message = self.llm_backend.get_msg(response)
            message_text = self.llm_backend.get_msg_text(message)
            input_tokens, output_tokens = self.llm_backend.get_tokens(response)
            process.memory.add_cost(output_tokens, input_tokens)
            process.memory.add_message(
                {
                    "role": "assistant",
                    "content": message_text,
                }
            )
