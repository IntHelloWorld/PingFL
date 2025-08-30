import argparse
import json
from pathlib import Path


def main(result_dir):
    results = {
        "Top-1": [],
        "Top-3": [],
        "Top-5": [],
    }
    result_dir = Path(result_dir)
    result_files = list(result_dir.glob("*.json"))
    for result_file in result_files:
        bug_name = result_file.stem
        with result_file.open("r") as f:
            distances = json.load(f)

        for idx, d in enumerate(distances):
            if d == 1.0:
                if idx == 0:
                    if bug_name not in results["Top-1"]:
                        results["Top-1"].append(bug_name)
                if idx < 3:
                    if bug_name not in results["Top-3"]:
                        results["Top-3"].append(bug_name)
                if idx < 5:
                    if bug_name not in results["Top-5"]:
                        results["Top-5"].append(bug_name)
                break

    with open(f"{result_dir.name}_top_bugs.txt", "w") as f:
        for key in results:
            results[key] = sorted(results[key])
            f.write("-" * 20 + f"\n{key}\n" + "-" * 20 + "\n")
            f.write("\n".join(results[key]))
            f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all bugs")
    parser.add_argument(
        "--result_dir",
        type=str,
        help="result directory",
        # default="/home/qyh/projects/FixFL/EvaluationResult/deepseek",
        # default="/home/qyh/projects/FixFL/EvaluationResult/autofl_deepseek",
        # default="/home/qyh/projects/FixFL/EvaluationResult/autofl_deepseek_no_confidence",
        # default="/home/qyh/projects/FixFL/EvaluationResult/autofl_deepseek_rep5",
        # default="/home/qyh/projects/FixFL/EvaluationResult/autofl_deepseek_print_debugging",
        # default="/home/qyh/projects/FixFL/EvaluationResult/parallel_search_deepseek",
        # default="/home/qyh/projects/FixFL/EvaluationResult/gpt4o_gpt4turbo_enforce_print_debugging",
        # default="/home/qyh/projects/FixFL/EvaluationResult/parallel_gpt4o",
        # default="/home/qyh/projects/FixFL/EvaluationResult/enhanced_tools_gpt4o",
        default="/home/qyh/projects/FixFL/EvaluationResult/autofl_gpt4o-1",
        # default="/home/qyh/projects/FixFL/EvaluationResult/pingfl_gpt4o_gpt4turbo_no_enhanced_tools",
        # default="/home/qyh/projects/FixFL/EvaluationResult/pingfl_gpt4o_gpt4turbo_no_enhanced_tools-1",
    )
    args = parser.parse_args()
    main(args.result_dir)
