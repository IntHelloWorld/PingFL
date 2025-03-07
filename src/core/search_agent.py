import copy
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageToolCall,
)
from openai.types.chat.chat_completion_message_tool_call import Function
from rich.live import Live
from rich.table import Table

from src.config import BugInfo
from src.core.llm_backend import LLMBackend
from src.core.memory import Memory
from src.core.prompt import (
    SEARCH_AGENT_DEBUGGING_PROMPT_MULTIPLE,
    SEARCH_AGENT_DEBUGGING_PROMPT_SINGLE,
    SEARCH_AGENT_RESULT_PROMPT_SINGLE,
    SEARCH_AGENT_TOOLS,
    SEARCH_AGENT_USER_PROMPT,
    STOP_TAG,
)
from src.core.utils import extract_json_block
from src.repograph.graph_searcher import RepoSearcher
from src.schema import SearchInput


@dataclass
class ProcessState:
    llm: LLMBackend
    memory: Memory
    id: str
    function_calls: List[str] = field(default_factory=list)

    @property
    def function_call_trace(self):
        abbreviate_dict = {
            "get_covered_classes": "class",
            "get_covered_methods_of_class": "method",
            "get_method_code": "code",
            "search_methods_contain_string": "search",
            "get_callee_methods": "callee",
            "get_caller_methods": "caller",
        }
        return "->".join([abbreviate_dict[fc] for fc in self.function_calls])


class ThreadStatusMonitor:
    def __init__(self):
        self.thread_statuses = {}
        self.lock = threading.Lock()

    def update_status(self, thread_name, status, call_trace):
        with self.lock:
            self.thread_statuses[thread_name] = {
                "status": status,
                "call_trace": call_trace,
                "last_update": time.time(),
            }

    def remove_thread(self, thread_name):
        with self.lock:
            self.thread_statuses.pop(thread_name)

    def get_table(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Thread ID")
        table.add_column("Function Call Trace")
        table.add_column("Status")
        table.add_column("Last Update")

        with self.lock:
            for thread_name, info in self.thread_statuses.items():
                table.add_row(
                    thread_name,
                    f"[green]{info['status']}[/green]",
                    f"{info['call_trace']}",
                    f"{time.strftime('%H:%M:%S', time.localtime(info['last_update']))}",
                )
        return table


class SearchAgent:
    def __init__(
        self, bug_info: BugInfo, searcher: RepoSearcher, debug: bool = False
    ):
        self.bug_info = bug_info
        self.debug = debug
        self.processes: Dict[int, ProcessState] = {}
        self.process_counter = 0
        self.process_lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(
            max_workers=bug_info.config.hyper.search_workers
        )
        self.futures = []
        self.searcher = searcher

        self.parallel_search = bug_info.config.hyper.parallel_search
        if self.parallel_search:
            self.debug_prompt = SEARCH_AGENT_DEBUGGING_PROMPT_MULTIPLE
        else:
            self.debug_prompt = SEARCH_AGENT_DEBUGGING_PROMPT_SINGLE
        self.functions = {
            "get_covered_classes": self.searcher.get_covered_classes,
            "get_covered_methods_of_class": self.searcher.get_covered_methods_of_class,
            "get_method_code": self.searcher.get_method_code,
            "search_methods_contain_string": self.searcher.search_methods_contain_string,
            "get_callee_methods": self.searcher.get_callee_methods,
            "get_caller_methods": self.searcher.get_caller_methods,
        }

    def refresh(self):
        """refresh the agent state before starting a new round"""
        self.processes = {}
        self.process_counter = 0
        self.futures = []

    def create_process(self, parent_id=None) -> int:
        with self.process_lock:
            process_id = self.process_counter
            if parent_id is not None:
                parent_process = self.processes[parent_id]
                self.processes[process_id] = ProcessState(
                    llm=LLMBackend(
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
                    llm=LLMBackend(
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

    def process_function_calls(
        self,
        process_id: int,
        monitor: ThreadStatusMonitor,
        message: ChatCompletionMessage,
    ) -> None:
        process = self.processes[process_id]
        tool_calls = message.tool_calls
        if not self.parallel_search:
            tool_calls = [tool_calls[0]]
        for i, tool_call in enumerate(tool_calls):
            # create a new process for each tool call
            new_process_id = self.create_process(process_id)
            single_tool_call_message = copy.deepcopy(message)
            single_tool_call_message.tool_calls = [
                single_tool_call_message.tool_calls[i]
            ]
            future = self.thread_pool.submit(
                self.run_process,
                new_process_id,
                monitor,
                single_tool_call_message,
                tool_call,
            )
            future.process_id = new_process_id
            self.futures.append(future)

        # remove the parent process
        with self.process_lock:
            self.processes.pop(process_id)
            for future in self.futures:
                if future.process_id == process_id:
                    self.futures.remove(future)
        monitor.remove_thread(process.id)

    def execute_function(self, tool_call: ChatCompletionMessageToolCall):
        function_args = json.loads(tool_call.function.arguments)
        function_args.pop("thought")
        function_name = tool_call.function.name
        function_to_call = self.functions[function_name]
        self.bug_info.logger.info(f"Call function {function_name}")
        function_response = function_to_call(**function_args)
        return function_response

    def run_process(
        self,
        process_id: int,
        monitor: ThreadStatusMonitor,
        message: ChatCompletionMessage = None,
        tool_call: ChatCompletionMessageToolCall = None,
    ) -> None:

        process = self.processes[process_id]

        if tool_call:
            tool_call_result = self.execute_function(tool_call)
            process.memory.add_message(message)
            process.memory.add_message(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_call_result,
                }
            )
            process.function_calls.append(tool_call.function.name)

        monitor.update_status(
            process.id, "Searching", process.function_call_trace
        )

        response = process.llm.call(
            messages=process.memory.get_messages(),
            tools=SEARCH_AGENT_TOOLS,
            model=self.bug_info.config.search_model.model,
            parallel_tool_calls=self.parallel_search,
            **self.bug_info.config.search_model.llm_args.asdict(),
        )

        message: ChatCompletionMessage = response.choices[0].message
        if message.tool_calls:
            self.process_function_calls(process_id, monitor, message)
        else:
            # get the debug report
            llm_message = {"role": "assistant", "content": message.content}
            process.memory.add_message(llm_message)

            # check if the LLM wants to stop debugging
            if STOP_TAG in message.content:
                monitor.update_status(
                    process.id, "Early Stop", process.function_call_trace
                )
                return

            # get the final result
            monitor.update_status(
                process.id, "Summarizing", process.function_call_trace
            )
            summary_message = {
                "role": "user",
                "content": SEARCH_AGENT_RESULT_PROMPT_SINGLE,
            }
            process.memory.add_message(summary_message)
            while True:
                self.bug_info.logger.info(
                    f"Sumarizing debug report to get suspicious method"
                )
                response = process.llm.call(
                    messages=process.memory.get_messages(),
                    model=self.bug_info.config.search_model.model,
                    **self.bug_info.config.search_model.llm_args.asdict(),
                )
                response_message: ChatCompletionMessage = response.choices[
                    0
                ].message
                llm_message = {
                    "role": "assistant",
                    "content": response_message.content,
                }
                process.memory.add_message(llm_message)
                result = extract_json_block(response_message.content)

                # check result format
                if result is None:
                    error_message = f"Reponse format error, please return a JSON format verification result wrapped with ```json...``` block."
                    process.memory.add_message(
                        {"role": "user", "content": error_message}
                    )
                    continue

                # check if the method is a test method
                json_res = json.loads(result)
                method = self.searcher.get_method(json_res["method_id"])
                if method.is_test:
                    error_message = f"Reponse content error, the suspicious method should be a production method rather than a test method."
                    process.memory.add_message(
                        {"role": "user", "content": error_message}
                    )
                    continue

                self.bug_info.logger.info(
                    f"Get suspicious method {method.method_id}"
                )
                break

            monitor.update_status(
                process.id, "Finished", process.function_call_trace
            )

    def init_memory(self, input: SearchInput, process_id: int) -> None:
        process = self.processes[process_id]
        user_message = {
            "role": "user",
            "content": SEARCH_AGENT_USER_PROMPT.format(**asdict(input)),
        }
        process.memory.add_message(user_message)
        default_tool_call_message = ChatCompletionMessage(
            content="",
            role="assistant",
            tool_calls=[
                ChatCompletionMessageToolCall(
                    id="call_0",
                    type="function",
                    function=Function(
                        name="get_covered_classes",
                        arguments='{"type": "object","properties": {},"required": []}',
                    ),
                )
            ],
        )
        process.memory.add_message(default_tool_call_message)
        process.memory.add_message(
            {
                "role": "tool",
                "tool_call_id": "call_0",
                "content": self.functions["get_covered_classes"](),
            }
        )
        process.function_calls.append("get_covered_classes")

    def run(self, input: SearchInput) -> List[Memory]:
        self.refresh()
        monitor = ThreadStatusMonitor()
        main_process_id = self.create_process()
        self.init_memory(input, main_process_id)

        main_future = self.thread_pool.submit(
            self.run_process, main_process_id, monitor
        )
        main_future.process_id = main_process_id
        self.futures.append(main_future)

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


if __name__ == "__main__":
    agent = SearchAgent("gpt-4o-2024-08-06", 10)
    agent.run()
