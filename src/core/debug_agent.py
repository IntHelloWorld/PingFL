import json
import time
from dataclasses import asdict, dataclass, field
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
from rich.live import Live
from rich.table import Table

from src.config import BugInfo
from src.core.memory import Memory
from src.core.prompt import EXPERIENCE_PROMPT
from src.core.search_agent import SearchAgent
from src.core.utils import extract_json_blocks
from src.core.verify_agent import VerifyAgent
from src.repograph.graph_searcher import RepoSearcher
from src.schema import (
    DebugInput,
    RoundResult,
    SearchInput,
    SearchResult,
    VerifyInput,
    VerifyResult,
)


@dataclass
class DebugState:
    """Manage debug status and handle communication between agents"""
    bug_name: str
    input: DebugInput
    round_results: List[RoundResult] = field(default_factory=list)
    completed: bool = False
    current_round: int = 1
    max_rounds: int = 3
    
    @property
    def current_round_result(self) -> Optional[RoundResult]:
        """Get the result for the current round"""
        return self.round_results[self.current_round - 1]
    
    @property
    def current_output_dir(self) -> Path:
        """Get the output directory for the current round"""
        return self.input.output_path / f"round-{self.current_round}"
    
    def update_round(self) -> None:
        """Update the current round"""
        self.current_round += 1
        if self.current_round > self.max_rounds:
            self.completed = True
    
    def get_experience(self) -> Optional[str]:
        """Generate experience report based on the previous round of VerifyResults"""
        if self.current_round == 1:
            return ""
        
        prev_verify_results = self.round_results[self.current_round - 2].verify_results
        result_strings = []
        for result in prev_verify_results:
            if not result.is_buggy:
                result_strings.append(f"Method {result.method_id} is not buggy. {result.explanation}")
        return EXPERIENCE_PROMPT.format("\n\n".join(result_strings))
    
    def build_search_results(self, results: List[Dict[str, Any]]) -> List[SearchResult]:
        """Build search results from the JSON results"""
        res_dict = {}
        for res in results:
            method_id = res["suspicious_method"]
            if method_id not in res_dict:
                res_dict[method_id] = []
            res_dict[method_id].append(res["error_analysis"])
        
        search_results = []
        for method_id, error_analyses in res_dict.items():
            search_results.append(
                SearchResult(
                    error_analysis="\n\n".join(error_analyses),
                    method_id=method_id
                )
            )
        return search_results
    
    def load_search_result(self, results_file: Path) -> List[SearchResult]:
        if not results_file.exists():
            raise Exception(f"Search results file not found: {results_file}")
        
        results = json.loads(results_file.read_text())
        result_infos = results["results"]
        return self.build_search_results(result_infos)
    
    def get_search_results(self, memories: List[Memory]) -> List[SearchResult]:
        """Get the search results for the current round"""
        results_info = []
        llm_responses = [m.get_messages()[-1]['content'] for m in memories]
        for response in llm_responses:
            matches = extract_json_blocks(response)
            if matches:
                res = json.loads(matches[0])
                results_info.append(res)
            else:
                raise ValueError(f"Could not parse JSON response in LLM response: {response}")
        
        memories_infos = [m.serialize() for m in memories]
        result_dict = {
            "results": results_info,
            "memories": memories_infos
        }
        res_file = self.current_output_dir / "search_results.json"
        self.current_output_dir.mkdir(parents=True, exist_ok=True)
        res_file.write_text(json.dumps(result_dict, indent=4))

        return self.build_search_results(results_info)
    
    def build_verify_results(self, results: List[Dict[str, Any]]) -> List[VerifyResult]:
        """Build verify results from the JSON results"""
        verify_results = []
        for res in results:
            verify_results.append(
                VerifyResult(
                    method_id=res["method_id"],
                    is_buggy=res["is_buggy"],
                    explanation=res["explanation"]
                )
            )
        return verify_results
    
    def load_verify_results(self, results_file: Path) -> List[VerifyResult]:
        if not results_file.exists():
            raise Exception(f"Verify results file not found: {results_file}")
        
        results = json.loads(results_file.read_text())
        result_infos = results["results"]
        return self.build_verify_results(result_infos)
    
    def get_verify_results(
        self,
        memories: List[Memory],
        verify_inputs: List[VerifyInput]
    ) -> List[VerifyResult]:
        llm_responses = [m.get_messages()[-1]['content'] for m in memories]
        
        results_info = []
        for i, verify_input in enumerate(verify_inputs):
            response = llm_responses[i]
            matches = extract_json_blocks(response)
            if matches:
                res = json.loads(matches[0])
                res.update({'method_id': verify_input.method_id})
                results_info.append(res)
            else:
                raise Exception(f"Could not parse JSON response in LLM response: {response}")
        
        memories_infos = [m.serialize() for m in memories]
        result_dict = {
            "results": results_info,
            "memories": memories_infos
        }
        res_file = self.current_output_dir / "verify_results.json"
        self.current_output_dir.mkdir(parents=True, exist_ok=True)
        res_file.write_text(json.dumps(result_dict, indent=4))

        return self.build_verify_results(results_info)
    
    def add_search_results(self, results: List[SearchResult]) -> None:
        """Add the search results for the current round"""
        self.round_results.append(RoundResult(results, []))
    
    def add_verify_results(self, results: List[VerifyResult]) -> None:
        """Add the verify results for the current round"""
        self.current_round_result.verify_results = results

    def prepare_search_input(self) -> SearchInput:
        """Prepare the input for the search agent"""
        experience = self.get_experience()
        return SearchInput(
            test_name=self.input.test_name,
            test_code=self.input.test_code,
            error_message=self.input.error_message,
            experience=experience
        )
    
    def prepare_verify_inputs(self, searcher: RepoSearcher) -> List[VerifyInput]:
        """Prepare the input for the verify agent"""
        verify_inputs = []
        for search_result in self.current_round_result.search_results:
            method = searcher.get_method(search_result.method_id)
            verify_inputs.append(
                VerifyInput(
                    bug_name=self.bug_name,
                    test_name=self.input.test_name,
                    test_code=self.input.test_code,
                    error_message=self.input.error_message,
                    method_id=method.method_id,
                    hypotheses=search_result.error_analysis,
                    method_code=method.code,
                    output_dir=self.input.output_path / f"round-{self.current_round}",
                    method=method
                )
            )
        return verify_inputs

    def get_display_info(self) -> Tuple[str, str, str, str]:
        """Return the information for displaying the debug state"""
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
        # perform search
        search_input = debug_state.prepare_search_input()
        search_results = run_search(search_agent, search_input, debug_state)
        debug_state.add_search_results(search_results)
        
        # perform verification
        verify_inputs = debug_state.prepare_verify_inputs(searcher)
        verify_results = run_verify(verify_agent, verify_inputs, debug_state)
        debug_state.add_verify_results(verify_results)
        
        debug_state.update_round()
    
    return debug_state


def run_search(
        search_agent: SearchAgent,
        search_input: SearchInput,
        debug_state: DebugState
    ) -> List[SearchResult]:
    """Run the search agent"""
    search_results_file = debug_state.current_output_dir / "search_results.json"
    if search_results_file.exists():
        return debug_state.load_search_result(search_results_file)
    
    memories = search_agent.run(search_input)
    search_results = debug_state.get_search_results(memories)
    return search_results


def run_verify(
    verify_agent: VerifyAgent,
    verify_inputs: List[VerifyInput],
    debug_state: DebugState
) -> List[VerifyResult]:
    """Run the verify agent"""
    verify_results_file = debug_state.current_output_dir / "verify_results.json"
    if verify_results_file.exists():
        return debug_state.load_verify_results(verify_results_file)
    
    memories = verify_agent.run(verify_inputs)
    verify_results = debug_state.get_verify_results(memories, verify_inputs)
    return verify_results


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
