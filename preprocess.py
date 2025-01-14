import os
import pickle
import shutil
import subprocess
import sys
from argparse import Namespace
from pathlib import Path
from time import sleep

import pandas as pd

root = Path(__file__).resolve().parent
sys.path.append(str(root))

from src.config import BugInfo
from src.interfaces.d4j import (
    check_out,
    get_failed_tests,
    get_properties,
    get_test_case_dataset_path,
    get_test_case_output_path,
    run_all_tests,
)
from src.repograph.construct_graph_new import create_code_graph, split_graph


def run_all(dataset_file, config_file):
    df = pd.read_csv(dataset_file)
    bug_names = df.iloc[:, 0].tolist()
    for bug_name in bug_names:
        if bug_name != "Closure_4":
            continue
        proj, bug_id = bug_name.split("_")
        run_one(proj, bug_id, config_file)

def run_one(proj, bug_id, config_file):
    args = Namespace(project=proj, bugID=bug_id, config=config_file)
    bug_info = BugInfo(args)
    
    check_out(bug_info)
    
    # collect basic bug information
    get_properties(bug_info)
    test_failure_obj = get_failed_tests(bug_info)
    run_all_tests(bug_info, test_failure_obj)
    
    # create the raw repository graph
    # code_graph = create_code_graph(bug_info, 'java')
    # split_graph(bug_info, code_graph, test_failure_obj)

    from src.core.debug_agent import DebugAgent, DebugInput
    debug_inputs = []
    for test_class in test_failure_obj.test_classes:
        for test_case in test_class.test_cases:
            if test_case.name == "com.google.javascript.jscomp.TypeCheckTest::testImplementsLoop":
                dataset_path = get_test_case_dataset_path(bug_info, test_case)
                test_graph_file = dataset_path / "graph.pkl"
                with test_graph_file.open("rb") as f:
                    test_graph = pickle.load(f)
                
                stack_trace_file = dataset_path / "stack_trace.txt"
                test_output_file = dataset_path / "test_output.txt"
                test_name = test_case.name
                test_code = test_case.test_method.text
                error_message = stack_trace_file.read_text() + "\n\n" + test_output_file.read_text()
                output_path = get_test_case_output_path(bug_info, test_case)
                
                debug_inputs.append(DebugInput(
                    test_name=test_name,
                    test_code=test_code,
                    error_message=error_message,
                    test_graph=test_graph,
                    output_path=output_path
                ))
    
    debug_agent = DebugAgent(bug_info, "gpt-4o-2024-11-20", num_process=1, max_workers=3, debug_type="single")
    debug_agent.run(debug_inputs)
    bug_info.logger.info("Finish.")

if __name__ == "__main__":
    dataset_file = root / "dataset" / "complex_bugs_v2.csv"
    config_file = root / "config" / "preprocess.yml"
    run_all(dataset_file, config_file)