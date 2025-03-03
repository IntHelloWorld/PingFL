import shutil
import sys
from argparse import Namespace
from pathlib import Path

import pandas as pd

from src.core.debug_agent import DebugAgent

root = Path(__file__).resolve().parent
sys.path.append(str(root))

from src.config import BugInfo
from src.interfaces.d4j import get_failed_tests, get_properties


def run_all(dataset_file, config_file):
    df = pd.read_csv(dataset_file)
    bug_names = df.iloc[:, 0].tolist()
    for bug_name in bug_names:
        proj, bug_id = bug_name.split("_")
        run_one(proj, bug_id, config_file)

def run_one(proj, bug_id, config_file):
    args = Namespace(project=proj, bugID=bug_id, config=config_file)
    bug_info = BugInfo(args)
    
    # collect basic bug information from cache
    # for preprocessing please run `preprocess.py`
    get_properties(bug_info)
    test_failure_obj = get_failed_tests(bug_info)

    # run the debug agent
    debug_agent = DebugAgent(bug_info, num_process=5, max_workers=8)
    debug_agent.run(test_failure_obj)
    
    # clean up
    shutil.rmtree(bug_info.proj_tmp_path.parent)

if __name__ == "__main__":
    dataset_file = root / "dataset" / "complex_bugs_v2.csv"
    config_file = root / "config" / "gpt4o_gpt4turbo.yml"
    run_all(dataset_file, config_file)