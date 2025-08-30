import copy
import json
import threading
import time
import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from anthropic.types import ToolUseBlock
from openai.types.chat import ChatCompletionMessageToolCall

from src.config import BugInfo
from src.core.llm_backend import AnthropicBackend, LLMBackend, OpenAIBackend
from src.core.memory import Memory
from src.core.prompt import (
    FAULT_LOCALIZATION_PROMPT_AUTOFL,
    PINGFL_DEBUGGING_PROMPT,
    PINGFL_DEBUGGING_PROMPT_NO_THOUGHT,
    PINGFL_DEBUGGING_PROMPT_PARALLEL,
    PINGFL_SUMMARIZATION_PROMPT,
    SEARCH_AGENT_TOOLS_ANTHROPIC,
    SEARCH_AGENT_USER_PROMPT,
    TOOLS_PINGFL_NO_ENHANCED,
)
from src.core.verify_agent import VerifyAgent
from src.repograph.graph_searcher import RepoSearcher
from src.schema import SearchInput, Tag, VerifyInput
from src.utils import Timer

DEFAULT_FUNCTION = {
    "content": "First, let's look at all the classes covered by the failing test to understand the debugging scope.",
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

DEFAULT_FUNCTION_NO_THOUGHT = {
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


class PingflAgent:

    def __init__(self, bug_info: BugInfo, searcher: RepoSearcher):
        self.bug_info = bug_info
        self.searcher = searcher

        self.max_parallel = self.bug_info.config.hyper.max_parallel_tool_calls
        self.max_paths = self.bug_info.config.hyper.max_search_paths
        self.cur_paths = 1

        self.max_tool_calls = bug_info.config.hyper.max_tool_calls
        self.max_verify_rounds = bug_info.config.hyper.max_verify_rounds
        if self.max_parallel > 1:
            self.debug_prompt = PINGFL_DEBUGGING_PROMPT_PARALLEL.format(
                max_tool_calls=self.max_tool_calls,
            )
        elif self.max_parallel == 1:
            self.debug_prompt = PINGFL_DEBUGGING_PROMPT.format(
                max_tool_calls=self.max_tool_calls,
            )
        else:
            raise ValueError(
                f"Invalid max_parallel_tool_calls:{self.max_parallel} setting in the config. It should be greater than 0."
            )
        self.default_function = DEFAULT_FUNCTION

        if not self.bug_info.config.hyper.thought:
            self.default_function = DEFAULT_FUNCTION_NO_THOUGHT
            self.debug_prompt = PINGFL_DEBUGGING_PROMPT_NO_THOUGHT.format(
                max_tool_calls=self.max_tool_calls,
            )

        self.functions = {
            "get_covered_classes": self.searcher.get_covered_classes,
            "get_covered_method_ids_for_class": self.searcher.get_covered_method_ids_for_class,
            "get_method_code_for_id": self.searcher.get_method_code_for_id,
            "search_covered_class_full_name": self.searcher.search_covered_class_full_name,
            "search_covered_method_id": self.searcher.search_covered_method_id,
        }

        self.org = bug_info.config.search_model.org
        assert self.org in ["openai", "anthropic"]
        if self.org == "openai":
            self.llm_backend = OpenAIBackend
            self.tool_set = TOOLS_PINGFL_NO_ENHANCED
        else:
            self.llm_backend = AnthropicBackend
            self.tool_set = SEARCH_AGENT_TOOLS_ANTHROPIC

        if hasattr(self.bug_info.config, "verify_model"):
            self.verify_agent = VerifyAgent(
                bug_info=self.bug_info,
                org=self.bug_info.config.verify_model.org,
            )

        self.processes: Dict[int, ProcessState] = {}
        self.futures: List[Future] = []
        self.process_counter = 0
        self.process_lock = threading.Lock()
        self.search_workers = bug_info.config.hyper.search_workers
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.search_workers,
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

    def load_memory(self, process: ProcessState):
        # load the memory cache from a file
        search_file = process.input.output_path / "search.json"
        memory_cache = json.loads(search_file.read_text())
        process_id = list(memory_cache.keys())[0]

        cached_messages = []
        function_calls = []
        for message in memory_cache[process_id]["memory"]["messages"]:
            if "tool_calls" in message:
                function_name = message["tool_calls"][0]["function"]["name"]
                if function_name == "nominate_suspicious_method":
                    break
                function_calls.append(function_name)
            cached_messages.append(message)

        process.id = process_id
        process.function_calls = function_calls
        for cached_message in cached_messages:
            process.memory.add_message(
                self.llm_backend.recover_msg(cached_message)
            )

        self.bug_info.logger.info(
            f"Load search memory cache from {search_file}"
        )

    def init_memory(self, input: SearchInput, process_id: str) -> None:
        process = self.processes[process_id]

        if self.bug_info.config.hyper.use_ablation:
            # load the memory cache from a file
            self.load_memory(process)
            return

        default_messages = [
            {
                "role": "user",
                "content": SEARCH_AGENT_USER_PROMPT.format(**asdict(input)),
            },
            self.llm_backend.recover_msg(self.default_function),
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
        process: ProcessState,
        message_text: str | None = None,
    ):
        function_args = self.llm_backend.get_tool_args(tool_call)
        function_name = self.llm_backend.get_tool_name(tool_call)
        if function_name == "nominate_suspicious_method":
            method_id = function_args["method_id"]
            method_tag = self.searcher.get_method(method_id)
            if method_tag is None:
                return self.searcher.get_method_code_for_id(method_id)
            suspected_issue = message_text
            verify_input = self.get_verify_input(
                process, suspected_issue, method_tag
            )
            with Timer(
                self.bug_info.logger,
                f"{self.bug_info.bug_name} - <{process.input.test_name}> - Process {process.id} - {method_id} nominated as suspicious",
            ):
                try:
                    function_response = self.verify_agent.run(verify_input)
                except Exception as e:
                    traceback.print_exc()
                    return e.message
            process.verify_rounds += 1
        else:
            function_to_call = self.functions[function_name]
            function_response = function_to_call(**function_args)
        return function_response

    def get_verify_input(
        self, process: ProcessState, suspected_issue: str, method_tag: Tag
    ) -> VerifyInput:
        verify_input = VerifyInput(
            test_name=process.input.test_name,
            test_code=process.input.test_code,
            error_message=process.input.error_message,
            method_id=method_tag.method_id,
            suspected_issue=suspected_issue,
            method_code=method_tag.code,
            output_dir=process.input.output_path,
            process_id=process.id,
            method=method_tag,
        )
        return verify_input

    def process_function_calls(
        self,
        process_id: int,
        message: ChatCompletionMessageToolCall | ToolUseBlock,
    ) -> None:
        tool_calls = self.llm_backend.get_tool_calls(message)

        # check if reached the maximum number of search paths
        with self.process_lock:
            max_parallel = self.max_parallel
            if self.cur_paths >= self.max_paths:
                # do not create new processes
                max_parallel = 1
            else:
                max_new_paths = min(len(tool_calls), self.max_parallel) - 1
                max_parallel = (
                    min(max_new_paths, self.max_paths - self.cur_paths) + 1
                )
            if max_parallel > 1:
                self.cur_paths += max_parallel - 1

        for i in range(len(tool_calls[:max_parallel])):
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

        with self.process_lock:
            # remove the parent process and its futures
            self.processes.pop(process_id)
            for future in self.futures:
                if future.process_id == process_id:
                    self.futures.remove(future)

    def run_process(self, process_id: str, single_tool_call_msg=None) -> None:
        process = self.processes[process_id]
        message_text = None

        if single_tool_call_msg:
            message_text = self.llm_backend.get_msg_text(single_tool_call_msg)
            tool_call = self.llm_backend.get_tool_calls(single_tool_call_msg)[
                0
            ]
            tool_call_name = self.llm_backend.get_tool_name(tool_call)
            self.bug_info.logger.info(
                f"{self.bug_info.bug_name} - <{process.input.test_name}> - Process {process.id} - call function {tool_call_name}"
            )

            try:
                tool_call_result = self.execute_function(
                    tool_call, process, message_text
                )
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
        if (process.num_function_calls >= self.max_tool_calls) or (
            process.verify_rounds >= self.max_verify_rounds
        ):
            message = self.llm_backend.recover_msg(
                {
                    "content": "I have reached the maximum number of tool calls or verify rounds. I will stop here.",
                    "refusal": None,
                    "role": "assistant",
                    "audio": None,
                    "function_call": None,
                    "tool_calls": [
                        {
                            "id": "call_exit",
                            "function": {
                                "arguments": "{}",
                                "name": "exit_debugging",
                            },
                            "type": "function",
                        }
                    ],
                }
            )
            message_text = self.llm_backend.get_msg_text(message)
            tool_calls = self.llm_backend.get_tool_calls(message)
            self.bug_info.logger.debug(
                f"{self.bug_info.bug_name} - <{process.input.test_name}> - Process {process.id} - reached max tool calls or verify rounds"
            )
        else:
            # get the next tool call
            messages = process.memory.get_messages()
            while True:
                response = process.llm.call(
                    messages=messages,
                    tools=self.tool_set,
                    model=self.bug_info.config.search_model.model,
                    **self.bug_info.config.search_model.llm_args.asdict(),
                )
                message = self.llm_backend.get_msg(response)
                message_text = self.llm_backend.get_msg_text(message)
                tool_calls = self.llm_backend.get_tool_calls(message)
                if tool_calls:
                    input_tokens, output_tokens = self.llm_backend.get_tokens(
                        response
                    )
                    process.memory.add_cost(output_tokens, input_tokens)
                    break
                else:
                    tmp_messages = [
                        {
                            "role": "assistant",
                            "content": message_text,
                        },
                        {
                            "role": "user",
                            "content": "Please call a function for the next step.",
                        },
                    ]
                    messages = process.memory.get_messages() + tmp_messages

        if self.llm_backend.get_tool_name(tool_calls[0]) != "exit_debugging":
            self.process_function_calls(process_id, message)
        else:
            self.bug_info.logger.info(
                f"{self.bug_info.bug_name} - <{process.input.test_name}> - Process {process.id} - start fault localization"
            )

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
