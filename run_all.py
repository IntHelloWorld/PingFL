import argparse
import multiprocessing
import sys
from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent
sys.path.append(str(root))

import subprocess


def run_script(project, bugID, config):
    cmd = (
        f"python run.py --project {project} --bugID {bugID} --config {config}"
    )
    subprocess.run(cmd.split())


def main(dataset_file, config_file):
    df = pd.read_csv(dataset_file)
    bug_names = df.iloc[:, 0].tolist()

    pool = multiprocessing.Pool(processes=5)
    for bug_name in bug_names[:2]:
        proj, bug_id = bug_name.split("_")
        pool.apply_async(run_script, (proj, bug_id, config_file))
    pool.close()
    pool.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all bugs")
    parser.add_argument(
        "--dataset",
        type=str,
        help="dataset file",
        default="/home/qyh/projects/FixFL/dataset/complex_bugs_v2.csv",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="config file",
        default="/home/qyh/projects/FixFL/config/gpt4o_gpt4turbo.yml",
    )
    args = parser.parse_args()
    main(args.dataset, args.config)
