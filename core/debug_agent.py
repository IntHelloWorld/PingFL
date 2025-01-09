import time
from dataclasses import asdict, dataclass, field
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
from rich.live import Live
from rich.table import Table

from core.config import BugInfo
from core.search_agent import SearchAgent, SearchInput, SearchResult
from core.verify_agent import VerifyAgent, VerifyInput, VerifyResult
from repograph.graph_searcher import RepoSearcher


@dataclass
class DebugInput:
    test_name: str
    test_code: str
    error_message: str
    test_graph: nx.Graph
    output_path: Path


@dataclass
class RoundResult:
    search_results: List[SearchResult]
    verify_results: List[VerifyResult]


@dataclass
class DebugState:
    bug_name: str
    input: DebugInput
    round_results: List[RoundResult] = field(default_factory=list)
    completed: bool = False
    current_round: int = 1
    max_rounds: int = 3

    @property
    def needs_new_search(self) -> bool:
        """Check if a new search is needed"""
        if self.completed:
            return False
        return len(self.round_results) < self.current_round
    
    @property
    def current_round_result(self) -> Optional[RoundResult]:
        """Get the result for the current round"""
        return self.round_results[self.current_round - 1]

    def add_search_results(self, results: List[SearchResult]) -> None:
        """Add the search results for the current round"""
        if self.needs_new_search:
            self.round_results.append(RoundResult(results, []))
    
    def add_verify_results(self, results: List[VerifyResult]) -> None:
        """Add the verify results for the current round"""
        self.current_round_result.verify_results = results
        self.process_verify_results()

    def process_verify_results(self) -> None:
        """处理验证结果，决定是否需要继续搜索"""
        verify_results = self.current_round_result.verify_results
        
        # 检查是否找到确定的bug
        found_bug = any(result.is_buggy for result in verify_results)
                
        if found_bug:
            self.completed = True
        elif self.current_round < self.max_rounds:
            self.current_round += 1
        else:
            self.completed = True

    def prepare_search_input(self) -> SearchInput:
        """Prepare the input for the search agent"""
        return SearchInput(
            test_name=self.input.test_name,
            test_code=self.input.test_code,
            error_message=self.input.error_message,
            output_dir=self.input.output_path / f"round-{self.current_round}"
        )
    
    def prepare_verify_inputs(self) -> List[VerifyInput]:
        """Prepare the input for the verify agent"""
        verify_inputs = []
        for search_result in self.current_round_result.search_results:
            verify_inputs.append(
                VerifyInput(
                    bug_name=self.bug_name,
                    test_name=self.input.test_name,
                    test_code=self.input.test_code,
                    error_message=self.input.error_message,
                    method_id=search_result.suspicious_method.method_id,
                    hypotheses=search_result.error_analysis,
                    method_code=search_result.suspicious_method.code,
                    output_dir=self.input.output_path / f"round-{self.current_round}",
                    method=search_result.suspicious_method
                )
            )
        return verify_inputs

    def get_display_info(self) -> Tuple[str, str, str, str]:
        """返回用于显示的信息：(测试名称, 当前轮次, 状态, 进度)"""
        status = "Completed" if self.completed else "Running"
        if self.needs_new_search:
            status = "Starting New Round"
        
        current_results = self.current_round_result
        if current_results:
            progress = f"Search: {len(current_results.search_results)} | Verify: {len(current_results.verify_results)}"
        else:
            progress = "Waiting"
        
        return (
            self.input.test_name,
            str(self.current_round),
            status,
            progress
        )


def debug_process(
    bug_info: BugInfo,
    debug_state: DebugState,
    model_name: str,
    max_workers: int,
    debug_type: str,
    llm_args: Dict[str, Any]
):
    """Debug process for a single test case"""
    thread_debug = True if debug_type == "single" else False
    searcher = RepoSearcher(debug_state.input.test_graph)
    search_agent = SearchAgent(
        model_name=model_name,
        searcher=searcher,
        max_workers=max_workers,
        debug=thread_debug,
        llm_args=llm_args
    )
    verify_agent = VerifyAgent(
        bug_info=bug_info,
        model_name=model_name,
        max_workers=max_workers,
        debug=thread_debug,
        llm_args=llm_args
    )
    
    while not debug_state.completed:
        if debug_state.needs_new_search:
            # perform search
            search_input = debug_state.prepare_search_input()
            search_results = search_agent.run(search_input)
            debug_state.add_search_results(search_results)
            
            # perform verification
            verify_inputs = debug_state.prepare_verify_inputs()
            verify_results = verify_agent.run(verify_inputs)
            debug_state.add_verify_results(verify_results)
    
    return debug_state



class DebugAgent:
    def __init__(
        self,
        bug_info: BugInfo,
        model_name: str,
        max_workers: int = 5,
        num_process: int = 3,
        debug_type: str = "multiple", # "multiple" for multiple test cases, "single" for single test case
        llm_args: Dict[str, Any] = {}
    ):
        self.bug_info = bug_info
        self.model_name = model_name
        self.max_workers = max_workers
        self.debug_type = debug_type
        self.llm_args = llm_args
        self.debug_states: Dict[int, DebugState] = {}
        self.num_process = num_process
        
        assert self.debug_type in ["multiple", "single"]
        assert not (self.debug_type == "single" and num_process > 1)

    def get_display_table(self) -> Table:
        """Get a table for displaying the debug states"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("State ID")
        table.add_column("Test Name")
        table.add_column("Round")
        table.add_column("Status")
        table.add_column("Progress")
        
        for state_id, state in self.debug_states.items():
            test_name, round_num, status, progress = state.get_display_info()
            table.add_row(str(state_id), test_name, round_num, status, progress)
            
        return table
    
    def run_multiprocess(self) -> List[DebugState]:
        # Create a pool of processes
        with Pool(processes=self.num_process) as pool:
            # Start the debug processes
            async_results = []
            for i, debug_state in self.debug_states.items():
                result = pool.apply_async(
                    debug_process,
                    args=(
                        self.bug_info,
                        debug_state,
                        self.model_name,
                        self.max_workers,
                        self.debug_type,
                        self.llm_args
                    )
                )
                async_results.append(result)
            
            # Display the progress
            if self.debug_type == "multiple":
                with Live(self.get_display_table(), refresh_per_second=1) as live:
                    while not all(result.ready() for result in async_results):
                        live.update(self.get_display_table())
                        time.sleep(0.5)
            else:
                while not all(result.ready() for result in async_results):
                    time.sleep(1)
        
        results = [result.get() for result in async_results]
        return results
    
    def run_singleprocess(self) -> List[DebugState]:
        results = []
        for _, debug_state in self.debug_states.items():
            result =debug_process(
                self.bug_info,
                debug_state,
                self.model_name,
                self.max_workers,
                self.debug_type,
                self.llm_args
            )
            results.append(result)
        return results

    def run(self, inputs: List[DebugInput]) -> List[Dict[str, Any]]:
        # Create debug states
        for i, debug_input in enumerate(inputs):
            debug_state = DebugState(bug_name=self.bug_info.bug_name, input=debug_input)
            self.debug_states[i] = debug_state
        
        if self.num_process > 1:
            self.run_multiprocess()
        else:
            self.run_singleprocess()


if __name__ == "__main__":
    agent = DebugAgent("gpt-4", None)  # 替换为实际的 RepoSearcher 实例
    inputs = [
        {
            "test_name": "test1",
            "test_code": "...",
            "error_message": "...",
        }
    ]
    results = agent.run(inputs)
    print(results)
