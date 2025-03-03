import sys
from argparse import Namespace
from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent
sys.path.append(str(root))

from src.config import BugInfo
from src.interfaces.d4j import (
    check_out,
    get_failed_tests,
    get_properties,
    run_all_tests,
)
from src.repograph.construct_graph import create_repo_graph


def run_all(dataset_file, config_file):
    df = pd.read_csv(dataset_file)
    bug_names = df.iloc[:, 0].tolist()
    for bug_name in bug_names:
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
    repo_graph = create_repo_graph(bug_info, test_failure_obj)

if __name__ == "__main__":
    dataset_file = root / "dataset" / "complex_bugs_v2.csv"
    config_file = root / "config" / "preprocess.yml"
    run_all(dataset_file, config_file)