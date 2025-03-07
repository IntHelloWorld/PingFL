import json
import os
import pickle
import time
from dataclasses import dataclass, field
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
from openai.types.chat import ChatCompletionMessage
from rich.live import Live
from rich.table import Table

from src.config import BugInfo
from src.core.llm_backend import LLMBackend
from src.core.memory import Memory
from src.core.prompt import (
    EXPERIENCE_PROMPT,
    SINGLE_EXPERIENCE_PROMPT,
    SINGLE_RESULT_TEMPLATE,
    STOP_TAG,
    SUMMARIZE_SYSTEM_PROMPT,
    SUMMARIZE_USER_PROMPT,
)
from src.core.search_agent import SearchAgent
from src.core.utils import extract_json_block
from src.core.verify_agent import VerifyAgent
from src.interfaces.d4j import (
    get_test_case_dataset_path,
    get_test_case_output_path,
)
from src.repograph.graph_searcher import RepoSearcher
from src.schema import (
    DebugInput,
    RoundResult,
    SearchInput,
    SearchResult,
    TestFailure,
    VerifyInput,
    VerifyResult,
)
from src.utils import Timer


@dataclass
class DebugState:
    """Manage debug status and handle communication between agents"""

    bug_name: str
    input: DebugInput
    round_results: List[RoundResult] = field(default_factory=list)
    parallel_search: bool = False
    completed: bool = False
    found_bug: bool = False
    current_round: int = 1
    max_rounds: int = 3

    @property
    def current_round_result(self) -> Optional[RoundResult]:
        """Get the result for the current round"""
        try:
            return self.round_results[self.current_round - 1]
        except IndexError:
            return None

    @property
    def current_output_dir(self) -> Path:
        """Get the output directory for the current round"""
        return self.input.output_path / f"round-{self.current_round}"

    def update_round(self) -> None:
        """Update the current round"""
        self.current_round += 1
        if self.current_round > self.max_rounds:
            self.completed = True

        if self.parallel_search:
            # TODO: this may need to be implemented in the future
            pass
        else:
            # early stop if the latest verify round has a buggy method
            latest_verify_results = self.current_round_result.verify_results
            for latest_verify_result in latest_verify_results:
                if latest_verify_result.category == "buggy":
                    self.completed = True
                    self.found_bug = True

    def get_experience(self) -> Optional[str]:
        """Generate an experience report based on the previous round of VerifyResults"""
        if self.current_round == 1:
            return ""

        prev_verify_results = self.round_results[
            self.current_round - 2
        ].verify_results
        benign_methods = []
        uncertain_methods = []
        for result in prev_verify_results:
            if result.category == "benign":
                benign_methods.append(
                    SINGLE_EXPERIENCE_PROMPT.format(
                        method_id=result.method_id,
                        explanation=result.explanation,
                        suggestion=result.suggestion,
                    )
                )
            elif result.category == "uncertain":
                uncertain_methods.append(
                    SINGLE_EXPERIENCE_PROMPT.format(
                        method_id=result.method_id,
                        explanation=result.explanation,
                        suggestion=result.suggestion,
                    )
                )
            else:  # skip the methods that have been verified as 'buggy'
                pass
        return EXPERIENCE_PROMPT.format(
            benign_methods="\n\n".join(benign_methods),
            uncertain_methods="\n\n".join(uncertain_methods),
        )

    def build_search_results(
        self, results: List[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Build search results from the JSON results, we combine the explainations for the same method"""
        res_dict = {}
        for res in results:
            method_id = res["method_id"]
            if method_id not in res_dict:
                res_dict[method_id] = []
            res_dict[method_id].append(res["error_analysis"])

        search_results = []
        for method_id, error_analyses in res_dict.items():
            search_results.append(
                SearchResult(
                    error_analysis="\n\n".join(error_analyses),
                    method_id=method_id,
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
        llm_responses = [m.get_messages()[-1]["content"] for m in memories]
        for response in llm_responses:
            match = extract_json_block(response)
            if match:
                res = json.loads(match)
                results_info.extend(res)
            else:
                if STOP_TAG in response:
                    # the LLM may early stop, so we ignore the error
                    pass
                else:
                    print(
                        f"Could not parse JSON response in LLM response 111: {response}"
                    )

        memories_infos = [m.serialize() for m in memories]
        result_dict = {"results": results_info, "memories": memories_infos}
        res_file = self.current_output_dir / "search_results.json"
        self.current_output_dir.mkdir(parents=True, exist_ok=True)
        res_file.write_text(json.dumps(result_dict, indent=4))

        return self.build_search_results(results_info)

    def build_verify_results(
        self, results: List[Dict[str, Any]]
    ) -> List[VerifyResult]:
        """Build verify results from the JSON results"""
        verify_results = []
        for res in results:
            verify_results.append(
                VerifyResult(
                    method_id=res["method_id"],
                    category=res["category"],
                    explanation=res["explanation"],
                    suggestion=res["suggestion"],
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
        self, memories: List[Memory], verify_inputs: List[VerifyInput]
    ) -> List[VerifyResult]:
        llm_responses = [m.get_messages()[-1]["content"] for m in memories]

        results_info = []
        for i, verify_input in enumerate(verify_inputs):
            response = llm_responses[i]
            match = extract_json_block(response)
            if match:
                res = json.loads(match)
                res.update({"method_id": verify_input.method_id})
                results_info.append(res)
            else:
                raise Exception(
                    f"Could not parse JSON response in LLM response 222: {response}"
                )

        memories_infos = [m.serialize() for m in memories]
        result_dict = {"results": results_info, "memories": memories_infos}
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
            experience=experience,
        )

    def prepare_verify_inputs(
        self, searcher: RepoSearcher
    ) -> List[VerifyInput]:
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
                    output_dir=self.input.output_path
                    / f"round-{self.current_round}",
                    method=method,
                )
            )
        return verify_inputs

    def get_display_info(self) -> Tuple[str, str, str, str]:
        """Return the information for displaying the debug state"""
        status = "Completed" if self.completed else "Running"

        current_results = self.current_round_result
        if current_results:
            progress = f"Search: {len(current_results.search_results)} | Verify: {len(current_results.verify_results)}"
        else:
            progress = "Search: 0 | Verify: 0"

        return (
            self.input.test_name,
            str(self.current_round),
            status,
            progress,
        )


def debug_process(
    bug_info: BugInfo,
    debug_state: DebugState,
    max_workers: int,
    debug_type: str,
):
    """Debug process for a single test case"""
    thread_debug = True if debug_type == "single" else False
    searcher = RepoSearcher(
        debug_state.input.repo_graph, debug_state.input.loaded_classes
    )
    search_agent = SearchAgent(
        bug_info=bug_info,
        searcher=searcher,
        max_workers=max_workers,
        debug=thread_debug,
    )
    verify_agent = VerifyAgent(
        bug_info=bug_info, max_workers=max_workers, debug=thread_debug
    )

    while not debug_state.completed:
        # perform search
        search_input = debug_state.prepare_search_input()
        # with Timer(
        #     bug_info.logger,
        #     f"{search_input.test_name} - round {debug_state.current_round} search"
        # ):
        search_results = run_search(search_agent, search_input, debug_state)
        debug_state.add_search_results(search_results)

        # perform verification
        verify_inputs = debug_state.prepare_verify_inputs(searcher)
        # with Timer(
        #     bug_info.logger,
        #     f"{search_input.test_name} - round {debug_state.current_round} verify"
        # ):
        verify_results = run_verify(verify_agent, verify_inputs, debug_state)
        debug_state.add_verify_results(verify_results)

        debug_state.update_round()

    return debug_state


def run_search(
    search_agent: SearchAgent,
    search_input: SearchInput,
    debug_state: DebugState,
) -> List[SearchResult]:
    """Run the search agent"""
    search_results_file = (
        debug_state.current_output_dir / "search_results.json"
    )
    if search_results_file.exists():
        return debug_state.load_search_result(search_results_file)

    memories = search_agent.run(search_input)
    msgs = [m.serialize() for m in memories]
    with open(f"{os.getpid()}.json", "w") as f:
        json.dump(msgs, f)
    search_results = debug_state.get_search_results(memories)
    return search_results


def run_verify(
    verify_agent: VerifyAgent,
    verify_inputs: List[VerifyInput],
    debug_state: DebugState,
) -> List[VerifyResult]:
    """Run the verify agent"""
    verify_results_file = (
        debug_state.current_output_dir / "verify_results.json"
    )
    if verify_results_file.exists():
        return debug_state.load_verify_results(verify_results_file)

    memories = verify_agent.run(verify_inputs)
    verify_results = debug_state.get_verify_results(memories, verify_inputs)
    return verify_results


class DebugAgent:
    def __init__(
        self, bug_info: BugInfo, max_workers: int = 5, num_process: int = 3
    ):
        self.bug_info = bug_info
        self.max_workers = max_workers
        self.debug_states: Dict[int, DebugState] = {}
        self.num_process = num_process

        # "multiple" for multiple test cases, "single" for single test case
        self.debug_type = "single" if num_process == 1 else "multiple"

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
            table.add_row(
                str(state_id), test_name, round_num, status, progress
            )

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
                        self.max_workers,
                        self.debug_type,
                    ),
                )
                async_results.append(result)

            # Display the progress
            # if self.debug_type == "multiple":
            #     with Live(self.get_display_table(), refresh_per_second=3) as live:
            #         while not all(result.ready() for result in async_results):
            #             live.update(self.get_display_table())
            #             time.sleep(1)
            # else:
            while not all(result.ready() for result in async_results):
                time.sleep(1)

        # results = [result.get() for result in async_results]
        # Collect results
        results = []
        for result in async_results:
            try:
                results.append(result.get())  # Handle potential exceptions
            except Exception as e:
                print(f"Error in subprocess: {e}")
                results.append(None)  # Or handle the error as needed

        return results

    def run_singleprocess(self) -> List[DebugState]:
        results = []
        for _, debug_state in self.debug_states.items():
            result = debug_process(
                self.bug_info, debug_state, self.max_workers, self.debug_type
            )
            results.append(result)
        return results

    def prepare_debug_inputs(
        self, test_failure: TestFailure
    ) -> List[DebugInput]:
        debug_inputs = []
        test_cases = []
        for test_class in test_failure.test_classes:
            test_cases.append(test_class.test_cases)

        # Limit the number of test cases
        # We try to keep test cases from different test classes
        num_test_cases = sum(len(cs) for cs in test_cases)
        new_test_cases = []
        max_test_cases = self.bug_info.config.hyper.max_test_cases
        if num_test_cases > max_test_cases:
            while True:
                for cs in test_cases:
                    new_test_cases.append(cs.pop())
                    if len(new_test_cases) == max_test_cases:
                        break
        else:
            new_test_cases = [tc for cs in test_cases for tc in cs]

        for test_case in new_test_cases:
            dataset_path = get_test_case_dataset_path(self.bug_info, test_case)
            repo_graph_file = dataset_path / "repograph.pkl"
            with repo_graph_file.open("rb") as f:
                repo_graph = pickle.load(f)
            loaded_classes_file = dataset_path / "loaded_classes.txt"
            loaded_classes = loaded_classes_file.read_text().split("\n")

            stack_trace_file = dataset_path / "stack_trace.txt"
            test_output_file = dataset_path / "test_output.txt"
            test_name = test_case.name
            test_code = test_case.test_method.text
            error_message = (
                stack_trace_file.read_text()
                + "\n\n"
                + test_output_file.read_text()
            )
            output_path = get_test_case_output_path(self.bug_info, test_case)

            debug_inputs.append(
                DebugInput(
                    test_name=test_name,
                    test_code=test_code,
                    error_message=error_message,
                    repo_graph=repo_graph,
                    loaded_classes=loaded_classes,
                    output_path=output_path,
                )
            )
        return debug_inputs

    def get_result_report(self):
        debug_results = []
        for debug_state in self.debug_states.values():
            if debug_state.found_bug:
                verify_result = debug_state.round_results[-1].verify_results[0]
                method_id = verify_result.method_id
                explaination = verify_result.explanation
            else:
                method_id = (
                    "No suspicious method found for this failed test case"
                )
                explaination = "None"

            debug_results.append(
                SINGLE_RESULT_TEMPLATE.format(
                    test_name=debug_state.input.test_name,
                    test_code=debug_state.input.test_code,
                    error_message=debug_state.input.error_message,
                    method_id=method_id,
                    explaination=explaination,
                )
            )
        return SUMMARIZE_USER_PROMPT.format("\n".join(debug_results))

    def combine_test_case_results(self):
        """Combine the results for all test cases to generate a final suspicious methods rank list"""
        result_file: Path = self.bug_info.res_path / "debug_result.json"
        if result_file.exists():
            return

        llm = LLMBackend(
            api_key=self.bug_info.config.search_model.api_key,
            base_url=self.bug_info.config.search_model.base_url,
        )
        memory = Memory(
            system_prompt=SUMMARIZE_SYSTEM_PROMPT,
            model_name=self.bug_info.config.search_model.model,
        )
        memory.add_message(
            {"role": "user", "content": self.get_result_report()}
        )

        result = None
        while True:
            response = llm.call(
                messages=memory.get_messages(),
                model=self.bug_info.config.search_model.model,
                **self.bug_info.config.search_model.llm_args.asdict(),
            )
            message: ChatCompletionMessage = response.choices[0].message
            llm_message = {"role": "assistant", "content": message.content}
            memory.add_message(llm_message)
            result = extract_json_block(message.content)
            if result is None:
                error_message = f"Reponse format error, please return a JSON format verification result wrapped with ```json...``` block."
                memory.add_message(
                    {"role": "system", "content": error_message}
                )
                continue

            break

        result_dict = {"results": result, "memories": memory.serialize()}
        result_file.write_text(json.dumps(result_dict, indent=4))

    def run(self, test_failure: TestFailure) -> List[Dict[str, Any]]:
        # Prepare the debug inputs
        inputs = self.prepare_debug_inputs(test_failure)

        # Create debug states and run the debug process
        for i, debug_input in enumerate(inputs):
            debug_state = DebugState(
                bug_name=self.bug_info.bug_name,
                input=debug_input,
                max_rounds=self.bug_info.config.hyper.debug_rounds,
                parallel_search=self.bug_info.config.hyper.parallel_search,
            )
            self.debug_states[i] = debug_state

        if self.num_process > 1:
            self.run_multiprocess()
        else:
            self.run_singleprocess()

        # Get the final debugging result
        with Timer(self.bug_info.logger, "Combine test case results"):
            self.combine_test_case_results()
