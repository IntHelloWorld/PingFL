import argparse
import multiprocessing
import shutil
import sys
from argparse import Namespace
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import BugInfo
from src.interfaces.d4j import (
    check_out,
    get_failed_tests,
    get_properties,
    run_all_tests,
)

ALL_BUGS = {
    "d4j2.0.1": {
        "Chart": (list(range(1, 27)), [23]),
        "Closure": (list(range(1, 177)), [63, 93]),
        "Lang": (list(range(1, 66)), [2]),
        "Math": (list(range(1, 107)), []),
        "Mockito": (list(range(1, 39)), []),
        "Time": (list(range(1, 28)), [21]),
        "Cli": (list(range(1, 41)), [6]),
        "Codec": (list(range(1, 19)), []),
        "Collections": (list(range(1, 29)), list(range(1, 25))),
        "Compress": (list(range(1, 48)), []),
        "Csv": (list(range(1, 17)), []),
        "Gson": (list(range(1, 19)), []),
        "JacksonCore": (list(range(1, 27)), []),
        "JacksonDatabind": (list(range(1, 113)), []),
        "JacksonXml": (list(range(1, 7)), []),
        "Jsoup": (list(range(1, 94)), []),
    }
}

SELECTED_BUGS = {
    "d4j2.0.1": {
        "Chart": (list(range(1, 27)), [23]),
        "Closure": (
            list(range(1, 177)),
            [28, 63, 93, 137, 144, 149, 155, 162, 165, 169],
        ),
        "Lang": (list(range(1, 66)), [2, 23, 25, 56]),
        "Math": (list(range(1, 107)), [12, 104]),
        "Mockito": (list(range(1, 39)), [26]),
        "Time": (list(range(1, 28)), [11, 21, 26]),
        "Cli": (list(range(1, 41)), [6, 7, 13, 16, 21, 31, 34, 36]),
        "Codec": (list(range(1, 19)), [7, 12, 13, 14, 16]),
        "Collections": (list(range(1, 29)), list(range(1, 25))),
        "Compress": (list(range(1, 48)), [7, 8, 33, 42]),
        "Csv": (list(range(1, 17)), [12, 13]),
        "Gson": (list(range(1, 19)), [9]),
        "JacksonCore": (list(range(1, 27)), []),
        "JacksonDatabind": (
            list(range(1, 113)),
            [15, 20, 21, 26, 52, 53, 59, 89, 92, 103],
        ),
        "JacksonXml": (list(range(1, 7)), []),
        "Jsoup": (
            list(range(1, 94)),
            [9, 17, 23, 25, 28, 31, 58, 67, 71, 87, 92],
        ),
    }
}


def run_one(proj, bug_id, config_file):
    args = Namespace(project=proj, bugID=bug_id, config=config_file)
    bug_info = BugInfo(args)

    check_out(bug_info)

    # collect basic bug information
    get_properties(bug_info)
    test_failure_obj = get_failed_tests(bug_info)
    run_all_tests(bug_info, test_failure_obj)

    test_class_names = [
        test.name.split(".")[-1] for test in test_failure_obj.test_classes
    ]
    buggy_class_names = [
        m.class_name.split("$")[0] for m in test_failure_obj.buggy_methods
    ]
    test_class_names = set(test_class_names)
    buggy_class_names = set(buggy_class_names)
    is_simple = False
    for test_class_name in test_class_names:
        for buggy_class_name in buggy_class_names:
            if buggy_class_name in test_class_name:
                is_simple = True
                break

    # clean up
    shutil.rmtree(bug_info.proj_tmp_path)

    return (
        is_simple,
        f"{proj}_{bug_id},{'|'.join(buggy_class_names)},{'|'.join(test_class_names)}",
    )


def main(config, processes):
    version = "d4j2.0.1"
    root_path = Path(__file__).resolve().parent.parent

    bug_names = []
    for proj in ALL_BUGS[version]:
        for bug_id in ALL_BUGS[version][proj][0]:
            if bug_id in ALL_BUGS[version][proj][1]:
                continue

            if bug_id in SELECTED_BUGS[version][proj][1]:
                bug_path = (
                    root_path
                    / "dataset"
                    / "bugInfo"
                    / proj
                    / f"{proj}@{bug_id}"
                )
                if bug_path.exists():
                    shutil.rmtree(bug_path)
                continue
            bug_names.append(f"{proj}_{bug_id}")

    run_failed = []
    simple_bugs = []
    complex_bugs = []
    all_bugs = []
    if processes > 1:
        with multiprocessing.Pool(processes=processes) as pool:
            async_results = []
            for bug_name in bug_names:
                proj, bug_id = bug_name.split("_")
                async_result = pool.apply_async(
                    run_one, (proj, bug_id, config)
                )
                async_results.append(async_result)

            for i, async_result in enumerate(async_results):
                try:
                    is_simple, line = async_result.get()
                    all_bugs.append(line)
                    if is_simple:
                        simple_bugs.append(line)
                    else:
                        complex_bugs.append(line)
                except Exception as e:
                    run_failed.append(f"{bug_names[i]} {str(e)}")
    else:
        for bug_name in bug_names:
            proj, bug_id = bug_name.split("_")
            is_simple, line = run_one(proj, bug_id, config)
            all_bugs.append(line)
            if is_simple:
                simple_bugs.append(line)
            else:
                complex_bugs.append(line)

    run_failed_file = root_path / "dataset" / "bug_classification_failed.txt"
    simple_bugs_file = root_path / "dataset" / "simple_bugs.csv"
    complex_bugs_file = root_path / "dataset" / "complex_bugs.csv"
    all_bugs_file = root_path / "dataset" / "all_bugs.csv"
    with open(run_failed_file, "w") as f:
        f.write("\n".join(run_failed))
    with open(simple_bugs_file, "w") as f:
        f.write("\n".join(simple_bugs))
    with open(complex_bugs_file, "w") as f:
        f.write("\n".join(complex_bugs))
    with open(all_bugs_file, "w") as f:
        f.write("\n".join(all_bugs))

    # clean up
    checkout_tmp_path = (
        root_path / "DebugResult" / BugInfo.get_config_hash(config)
    )
    shutil.rmtree(checkout_tmp_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all bugs")
    parser.add_argument(
        "--config",
        type=str,
        help="config file",
        default="/home/qyh/projects/FixFL/config/preprocess.yml",
    )
    parser.add_argument(
        "--processes",
        type=int,
        help="processes",
        default=16,
    )
    args = parser.parse_args()
    main(args.config, args.processes)
