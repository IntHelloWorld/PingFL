import logging
import multiprocessing as mp
import shutil
import sys
import traceback
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


def worker(bug_name):
    try:
        if bug_name != "Math_14":
            return bug_name, True
        proj, bug_id = bug_name.split("_")
        run_one(proj, bug_id, config_file)
        return bug_name, True
    except Exception as e:
        error_msg = (
            f"Error processing {bug_name}: {str(e)}\n{traceback.format_exc()}"
        )
        logging.error(error_msg)
        return bug_name, False


def run_all(dataset_file, config_file, num_processes=None):
    if num_processes is None:
        num_processes = int(mp.cpu_count() / 2)

    df = pd.read_csv(dataset_file)
    bug_names = df.iloc[:, 0].tolist()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="preprocess.log",
    )

    with mp.Pool(num_processes) as pool:
        results = pool.map(worker, bug_names)

    successful = [r[0] for r in results if r[1]]
    failed = [r[0] for r in results if not r[1]]

    logging.info(
        f"Processing completed. Success: {len(successful)}, Failed: {len(failed)}"
    )
    if failed:
        logging.info(f"Failed bugs: {failed}")


def run_one(proj, bug_id, config_file):
    args = Namespace(project=proj, bugID=bug_id, config=config_file)
    bug_info = BugInfo(args)

    check_out(bug_info)

    # collect basic bug information
    get_properties(bug_info)
    test_failure_obj = get_failed_tests(bug_info)
    run_all_tests(bug_info, test_failure_obj)

    # create the raw repository graph
    create_repo_graph(bug_info, test_failure_obj)

    # clean up
    shutil.rmtree(bug_info.proj_tmp_path.parent)


if __name__ == "__main__":
    dataset_file = root / "dataset" / "complex_bugs_v2.csv"
    config_file = root / "config" / "preprocess.yml"
    run_all(dataset_file, config_file)
