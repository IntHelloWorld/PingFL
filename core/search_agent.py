import copy
import json
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function
from rich.console import Console
from rich.live import Live
from rich.table import Table

from core.llm_backend import LLMBackend
from core.memory import Memory
from core.prompt import (
    SEARCH_AGENT_SYSTEM_PROMPT,
    SEARCH_AGENT_TOOLS,
    SEARCH_AGENT_USER_PROMPT,
)
from core.utils import extract_json_blocks
from repograph.graph_searcher import RepoSearcher, Tag


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
        }
        return "->".join([abbreviate_dict[fc] for fc in self.function_calls])



class ThreadStatusMonitor:
    def __init__(self):
        self.thread_statuses = {}
        self.lock = threading.Lock()
        
    def update_status(self, thread_name, status, call_trace):
        with self.lock:
            self.thread_statuses[thread_name] = {
                'status': status,
                'call_trace': call_trace,
                'last_update': time.time()
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
                    f"{time.strftime('%H:%M:%S', time.localtime(info['last_update']))}"
                )
        return table


@dataclass
class SearchInput:
    test_name: str
    test_code: str
    error_message: str
    output_dir: Path



@dataclass
class SearchResult:
    error_analysis: str
    suspicious_method: Tag



class SearchAgent:
    def __init__(
        self,
        model_name: str,
        searcher: RepoSearcher,
        max_workers: int = 5,
        debug: bool = False,
        llm_args: Dict[str, Any] = {}
    ):
        self.model_name = model_name
        self.debug = debug
        self.llm_args = llm_args
        self.processes: Dict[int, ProcessState] = {}
        self.process_counter = 0
        self.process_lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.visited_methods = set([])
        self.futures = []
        self.searcher = searcher
        
        self.functions = {
            "get_covered_classes": self.searcher.get_covered_classes,
            "get_covered_methods_of_class": self.searcher.get_covered_methods_of_class,
            "get_method_code": self.searcher.get_method_code,
        }

    def create_process(self, parent_id=None) -> int:
        with self.process_lock:
            process_id = self.process_counter
            if parent_id is not None:
                parent_process = self.processes[parent_id]
                self.processes[process_id] = ProcessState(
                    llm=LLMBackend(),
                    memory=copy.deepcopy(parent_process.memory),
                    id=f"{parent_process.id}-{process_id}",
                    function_calls=copy.deepcopy(parent_process.function_calls)
                )
            else:
                self.processes[process_id] = ProcessState(
                    llm=LLMBackend(),
                    memory=Memory(SEARCH_AGENT_SYSTEM_PROMPT, self.model_name),
                    id=str(process_id)
                )
            self.process_counter += 1
            return process_id

    def remove_process(self, process_id: int) -> None:
        self.processes.pop(process_id)
        for future in self.futures:
            if future.process_id == process_id:
                self.futures.remove(future)

    def process_function_calls(
        self,
        process_id: int,
        monitor: ThreadStatusMonitor,
        message: ChatCompletionMessage
    ) -> None:
        process = self.processes[process_id]
        for i, tool_call in enumerate(message.tool_calls):
            
            # # check if the method has already been visited
            # if tool_call.function.name == "get_method_code":
            #     arguments = json.loads(tool_call.function.arguments)
            #     arguments.pop("thought")
            #     arguments = str(arguments)
            #     with self.process_lock:
            #         if arguments in self.visited_methods:
            #             continue
            #         self.visited_methods.add(arguments)
            
            # create a new process for each tool call
            new_process_id = self.create_process(process_id)
            single_tool_call_message = copy.deepcopy(message)
            single_tool_call_message.tool_calls = [single_tool_call_message.tool_calls[i]]
            future = self.thread_pool.submit(
                self.run_process,
                new_process_id,
                monitor,
                single_tool_call_message,
                tool_call
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
        function_response = function_to_call(**function_args)
        return function_response

    def run_process(
        self, 
        process_id: int,
        monitor: ThreadStatusMonitor,
        message: ChatCompletionMessage = None,
        tool_call: ChatCompletionMessageToolCall = None
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
        
        monitor.update_status(process.id, "Running", process.function_call_trace)
        
        response = process.llm.call(
            messages=process.memory.get_messages(),
            tools=SEARCH_AGENT_TOOLS,
            model=self.model_name,
            parallel_tool_calls=True,
            **self.llm_args
        )
        
        message: ChatCompletionMessage = response.choices[0].message
        if message.tool_calls:
            self.process_function_calls(process_id, monitor, message)
        else:
            llm_message = {'role': 'assistant', 'content': message.content}
            self.processes[process_id].memory.add_message(llm_message)
            monitor.update_status(process.id, "Completed", process.function_call_trace)
    
    def read_results(self, search_input: SearchInput) -> Dict[str, Any]:
        res_file = search_input.output_dir / "search_results.json"
        if res_file.exists():
            res_dict = json.loads(res_file.read_text())
            search_results = []
            for method_id, error_analyses in res_dict.items():
                search_results.append(
                    SearchResult(
                        error_analysis="\n\n".join(error_analyses),
                        suspicious_method=self.searcher.method_id_map[method_id]
                    )
                )
            return search_results
        return None
    
    def parse_results(self, search_input: SearchInput) -> List[SearchResult]:
        res_dict = {}
        memories = [p.memory for p in self.processes.values()]
        llm_responses = [m.get_messages()[-1]['content'] for m in memories]
        for response in llm_responses:
            matches = extract_json_blocks(response)
            if matches:
                res = json.loads(matches[0])
                method_id = res['suspicious_method']
                error_analysis = res['error_analysis']
                if method_id not in res_dict:
                    res_dict[method_id] = [error_analysis]
                else:
                    res_dict[method_id].append(error_analysis)
            else:
                raise ValueError(f"Could not parse JSON response in LLM response: {response}")
        
        res_file = search_input.output_dir / "search_results.json"
        search_input.output_dir.mkdir(parents=True, exist_ok=True)
        res_file.write_text(json.dumps(res_dict, indent=4))

        search_results = []
        for method_id, error_analyses in res_dict.items():
            search_results.append(
                SearchResult(
                    error_analysis="\n\n".join(error_analyses),
                    suspicious_method=self.searcher.method_id_map[method_id]
                )
            )
        return search_results
    
    def init_memory(self, input: SearchInput, process_id: int) -> None:
        process = self.processes[process_id]
        user_message = {"role": "user", "content": SEARCH_AGENT_USER_PROMPT.format(**asdict(input))}
        process.memory.add_message(user_message)
        default_tool_call_message = ChatCompletionMessage(
            content='',
            role='assistant',
            tool_calls=[
                ChatCompletionMessageToolCall(
                    id='call_0',
                    type='function',
                    function=Function(
                        name='get_covered_classes',
                        arguments='{"type": "object","properties": {},"required": []}'
                    )
                )
            ]
        )
        process.memory.add_message(default_tool_call_message)
        process.memory.add_message({
            "role": "tool",
            "tool_call_id": 'call_0',
            "content": self.functions["get_covered_classes"]()
        })
        process.function_calls.append("get_covered_classes")

    def run(self, input: SearchInput) -> List[SearchResult]:
        results = self.read_results(input)
        if results:
            return results
        
        monitor = ThreadStatusMonitor()
        self.futures = []
        main_process_id = self.create_process()
        self.init_memory(input, main_process_id)
        
        main_future = self.thread_pool.submit(self.run_process, main_process_id, monitor)
        main_future.process_id = main_process_id
        self.futures.append(main_future)
        
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
        
        results = self.parse_results(input)
        return results


if __name__ == "__main__":
    agent = SearchAgent("gpt-4o-2024-08-06", 10)
    agent.run()