import argparse
import json
import multiprocessing
import pickle
import re
import sys
from argparse import Namespace
from copy import deepcopy
from pathlib import Path
from pprint import pprint
from typing import List

import networkx as nx
import pandas as pd

from src.interfaces.method_extractor import JMethod
from src.schema import Tag, TestFailure

root = Path(__file__).resolve().parent
sys.path.append(str(root))

from src.config import BugInfo
from src.interfaces.d4j import get_failed_tests, get_properties


def get_node_distance(
    graph: nx.MultiDiGraph, node1: Tag, node2: Tag, simple=False
):
    # if the two nodes are the same, return 0
    if node1 == node2:
        return 0

    if simple:
        return 0.1

    dynamic_graph = nx.Graph()
    combined_graph = nx.Graph()
    for edge in graph.edges(data=True):
        combined_graph.add_edge(edge[0], edge[1])
        if edge[2]["rel"] == "calls":
            dynamic_graph.add_edge(edge[0], edge[1])

    # first try to find the shortest path in dynamic graph
    try:
        shortest_path = nx.shortest_path(dynamic_graph, node1, node2)
        return len(shortest_path)
    except Exception:
        # if not found, try to find the shortest path in combined graph
        try:
            shortest_path = nx.shortest_path(combined_graph, node1, node2)
            return len(shortest_path)
        except Exception:
            # if still not found, return -1
            return -1


def get_relative_distance(
    combined_graph: nx.MultiDiGraph,
    modified_methods: List[JMethod],
    method_id: str,
):
    """
    Get the relative distance between buggy methods and the predicted method.

    For example, if the number of buggy methods is 3,
    the output will be a list contains 3 distances such as [2, 3, 4].
    """

    def fuzzy_match(method_id_1: str, method_id_2: str):
        if method_id_1 == method_id_2:
            return True
        if method_id_1.split(".")[-1] == method_id_2.split(".")[-1]:
            return True
        return False

    buggy_nodes = []
    predict_node = None
    should_find_methods = deepcopy(modified_methods)
    for nodes in combined_graph.nodes(data=True):
        if nodes[0].category == "function":
            method_node: Tag = nodes[0]
            for m in should_find_methods:
                if method_node.outer_class in m.class_name:
                    if m.name == method_node.name:
                        if (
                            m.loc[0][0] + 1 <= method_node.line[0]
                            and m.loc[1][0] + 1 >= method_node.line[1]
                        ):
                            buggy_nodes.append(method_node)
                            should_find_methods.remove(m)
                            break
            if fuzzy_match(method_node.method_id, method_id):
                predict_node = method_node

    assert (
        len(should_find_methods) == 0
    ), f"Buggy methods not found in graph: {[m.get_signature() for m in should_find_methods]}"

    if predict_node is None:
        print(f"Predict method not found: {method_id}")
        return []

    distances = []
    for buggy_node in buggy_nodes:
        distance = get_node_distance(
            combined_graph,
            buggy_node,
            predict_node,
            simple=True,
        )
        if distance != -1:
            distances.append(distance)
    return distances


def get_distance(
    test_failure_obj: TestFailure,
    ranked_methods: List[str],
    combined_graph: nx.MultiDiGraph,
):
    modified_methods = test_failure_obj.buggy_methods
    evaluate_result = []
    for method_id in ranked_methods:
        distances = get_relative_distance(
            combined_graph, modified_methods, method_id
        )
        if distances:
            rd = max([1 / (d + 1) for d in distances])
            evaluate_result.append(rd)
        else:
            # if the method is not found in the graph
            evaluate_result.append(0)
    return evaluate_result


def get_ranked(bug_info: BugInfo, combined_graph):
    """
    Get the ranked methods from the combined graph.
    """

    ranked_result_file = bug_info.res_path / "method_rank_list.json"
    if ranked_result_file.exists():
        with ranked_result_file.open("r") as f:
            ranked_methods = json.load(f)
            return ranked_methods

    debug_result_file = bug_info.res_path / "debug_result.json"
    debug_result = json.loads(debug_result_file.read_text())

    id_dict = {}
    for node in combined_graph.nodes(data=True):
        if node[0].category == "function":
            id_dict[node[0].method_id] = node[0]

    result = {}
    n_test = len(debug_result)
    for test_name in debug_result:
        n_process = len(debug_result[test_name])
        for process_id in debug_result[test_name]:
            pred_lines = debug_result[test_name][process_id]["prediction"]
            pred_method_ids = []
            for line in pred_lines.split("\n"):
                if line:
                    line = line.strip()
                    if line in id_dict:
                        pred_method_ids.append(line)
                    else:
                        print(f"Method ID {line} not found in graph")

            n_pred = len(pred_method_ids)
            for pred_id in pred_method_ids:
                if pred_id not in result:
                    result[pred_id] = 0
                result[pred_id] = 1 / (n_pred * n_process * n_test)

    suspicious_method_list = []
    for key in result:
        suspicious_method_list.append((key, result[key]))
    suspicious_method_list = sorted(
        suspicious_method_list, key=lambda x: x[1], reverse=True
    )
    if not suspicious_method_list:
        ranked_methods = []
    else:
        ranked_methods = list(zip(*suspicious_method_list))[0]

    with ranked_result_file.open("w") as f:
        json.dump(ranked_methods, f, indent=4)
    return ranked_methods


def get_ranked_with_confidence(bug_info: BugInfo, combined_graph):
    """
    Get the ranked methods from the combined graph.
    """

    def parse_line(line: str):
        match = re.match(r"(\S+) \((\w+)\)", line)
        if match:
            method_id = match.group(1)
            confidence = match.group(2)
            score = 0
            if confidence == "low":
                score = 1
            elif confidence == "medium":
                score = 2
            elif confidence == "high":
                score = 3
            return method_id, score
        return None

    ranked_result_file = bug_info.res_path / "debug_result.json"
    if ranked_result_file.exists():
        with ranked_result_file.open("r") as f:
            ranked_methods = json.load(f)
            return ranked_methods

    result = {}
    result_files = bug_info.res_path.rglob("search.json")
    pred_lines = [
        json.loads(f.read_text())["memory"]["messages"][-1]["content"].split(
            "\n"
        )
        for f in result_files
    ]
    pred_methods = []
    for lines in pred_lines:
        parsed_lines = []
        for line in lines:
            if line:
                parsed = parse_line(line)
                if parsed:
                    parsed_lines.append(parsed)
        pred_methods.append(parsed_lines)

    id_dict = {}
    for node in combined_graph.nodes(data=True):
        if node[0].category == "function":
            id_dict[node[0].method_id] = node[0]

    n_test_cases = len(pred_methods)
    for methods in pred_methods:
        n_pred = len(methods)
        for method in methods:
            id, confidence = method
            if id not in id_dict:
                print(f"Method {id} not found in graph")
                continue
            if method not in result:
                result[method] = 0
            result[method] += 1 / n_pred

    suspicious_method_list = []
    for key in result:
        score = result[key] / n_test_cases
        suspicious_method_list.append((key[0], key[1], score))
    suspicious_method_list = sorted(
        suspicious_method_list, key=lambda x: (x[2], x[1]), reverse=True
    )
    if not suspicious_method_list:
        ranked_methods = []
    else:
        ranked_methods = list(zip(*suspicious_method_list))[0]

    with ranked_result_file.open("w") as f:
        json.dump(ranked_methods, f, indent=4)
    return ranked_methods


def evaluate(project, bugID, config):
    args = Namespace(project=project, bugID=bugID, config=config)
    bug_info = BugInfo(args, eval=True)
    result_path: Path = bug_info.evaluation_path / Path(config).stem
    if not result_path.exists():
        result_path.mkdir(parents=True, exist_ok=True)
    result_file = result_path / f"{project}-{bugID}.json"
    if result_file.exists():
        return

    print(f"Evaluating {project}-{bugID}")
    # collect basic bug information from cache
    # For preprocessing please run `preprocess.py`
    get_properties(bug_info)
    test_failure_obj = get_failed_tests(bug_info)

    graph_file = bug_info.bug_path / "combined_graph.pkl"
    with graph_file.open("rb") as f:
        combined_graph = pickle.load(f)

    # combine the result for all test cases to get the ranked methods
    ranked_methods = get_ranked(bug_info, combined_graph)
    # ranked_methods = get_ranked_with_confidence(bug_info, combined_graph)

    # get the distance between the ranked methods and the buggy methods
    distances = get_distance(test_failure_obj, ranked_methods, combined_graph)
    with result_file.open("w") as f:
        json.dump(distances, f)


def print_result(bug_names, config_file):
    root_path = Path(__file__).resolve().parent
    config_name = Path(config_file).stem
    output = {}
    overall_metrics = {
        "MAP": [],
        "MRR": [],
        "RD@1": [],
        "RD@3": [],
        "RD@5": [],
    }
    top_5_bugs = []

    for bug_name in bug_names:
        proj, bug_id = bug_name.split("_")
        distance_file = (
            root_path
            / "EvaluationResult"
            / config_name
            / f"{proj}-{bug_id}.json"
        )
        if not distance_file.exists():
            raise FileNotFoundError(f"{distance_file} not found, please check")
        with distance_file.open("r") as f:
            distance = json.load(f)

        if proj not in output:
            output[proj] = {
                "Top-1": 0,
                "Top-3": 0,
                "Top-5": 0,
                "MAP": [],
                "MRR": [],
                "RD@1": [],
                "RD@3": [],
                "RD@5": [],
            }

        # Calculate MAP and MRR for this bug
        if distance:
            # Find all positions where distance is 1.0 (correct predictions)
            correct_positions = [i for i, d in enumerate(distance) if d == 1.0]

            if correct_positions:
                # Calculate Average Precision for this bug
                ap = 0.0
                num_correct = 0
                for i in range(len(distance)):
                    if distance[i] == 1.0:
                        num_correct += 1
                        ap += num_correct / (i + 1)
                ap = ap / len(correct_positions) if correct_positions else 0.0

                # Calculate Reciprocal Rank (using the first correct prediction)
                rr = 1.0 / (correct_positions[0] + 1)

                output[proj]["MAP"].append(ap)
                output[proj]["MRR"].append(rr)
                overall_metrics["MAP"].append(ap)
                overall_metrics["MRR"].append(rr)
            else:
                # No correct predictions
                output[proj]["MAP"].append(0.0)
                output[proj]["MRR"].append(0.0)
                overall_metrics["MAP"].append(0.0)
                overall_metrics["MRR"].append(0.0)
        else:
            print(f"Warning: {proj}-{bug_id} no results!")
            output[proj]["MAP"].append(0.0)
            output[proj]["MRR"].append(0.0)
            overall_metrics["MAP"].append(0.0)
            overall_metrics["MRR"].append(0.0)

        for idx, d in enumerate(distance):
            if d == 1.0:
                if idx == 0:
                    output[proj]["Top-1"] += 1
                if idx < 3:
                    output[proj]["Top-3"] += 1
                if idx < 5:
                    output[proj]["Top-5"] += 1
                    top_5_bugs.append(f"{proj}-{bug_id}")
                break
        for i in [1, 3, 5]:
            if distance[:i]:
                rd_value = max(distance[:i])
                output[proj][f"RD@{i}"].append(rd_value)
                overall_metrics[f"RD@{i}"].append(rd_value)
            else:
                print(f"Warning: {proj}-{bug_id} no results!")

    # Calculate final metrics for each project
    for proj in output:
        # Calculate average MAP and MRR
        output[proj]["MAP"] = (
            sum(output[proj]["MAP"]) / len(output[proj]["MAP"])
            if output[proj]["MAP"]
            else 0.0
        )
        output[proj]["MRR"] = (
            sum(output[proj]["MRR"]) / len(output[proj]["MRR"])
            if output[proj]["MRR"]
            else 0.0
        )

        for i in [1, 3, 5]:
            output[proj][f"RD@{i}"] = (
                sum(output[proj][f"RD@{i}"]) / len(output[proj][f"RD@{i}"])
                if output[proj][f"RD@{i}"]
                else 0.0
            )

    # Calculate overall metrics
    overall_summary = {
        "MAP": (
            sum(overall_metrics["MAP"]) / len(overall_metrics["MAP"])
            if overall_metrics["MAP"]
            else 0.0
        ),
        "MRR": (
            sum(overall_metrics["MRR"]) / len(overall_metrics["MRR"])
            if overall_metrics["MRR"]
            else 0.0
        ),
        "RD@1": (
            sum(overall_metrics["RD@1"]) / len(overall_metrics["RD@1"])
            if overall_metrics["RD@1"]
            else 0.0
        ),
        "RD@3": (
            sum(overall_metrics["RD@3"]) / len(overall_metrics["RD@3"])
            if overall_metrics["RD@3"]
            else 0.0
        ),
        "RD@5": (
            sum(overall_metrics["RD@5"]) / len(overall_metrics["RD@5"])
            if overall_metrics["RD@5"]
            else 0.0
        ),
    }

    top_5_file = root_path / "utils" / f"{config_name}_top_5_bugs.txt"
    with open(top_5_file, "w") as f:
        f.write("\n".join(top_5_bugs))

    print("\n=== Project-wise Results ===")
    pprint(output)
    print("\n=== Overall Results ===")
    pprint(overall_summary)


def main(dataset_file, config_file, processes):
    df = pd.read_csv(dataset_file, header=None)
    bug_names = df.iloc[:, 0].tolist()

    # TODO: evaluation: control bug for test
    # bug_names = ["Closure_1"]
    # bug_names = [
    #     b for b in bug_names if b.startswith("Cli") or b.startswith("Csv")
    # ]
    # bug_names = [
    #     b
    #     for b in bug_names
    #     if not b.startswith("Closure") and not b.startswith("Chart")
    # ]

    if processes > 1:
        with multiprocessing.Pool(processes=processes) as pool:
            async_results = []
            for bug_name in bug_names:
                proj, bug_id = bug_name.split("_")
                async_result = pool.apply_async(
                    evaluate, (proj, bug_id, config_file)
                )
                async_results.append(async_result)

            for i, async_result in enumerate(async_results):
                try:
                    async_result.get()
                except Exception as e:
                    print(f"{bug_names[i]} error: {str(e)}")
                    return
    else:
        for bug_name in bug_names:
            proj, bug_id = bug_name.split("_")
            evaluate(proj, bug_id, config_file)

    print_result(bug_names, config_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run all bugs")
    parser.add_argument(
        "--dataset",
        type=str,
        help="dataset file",
        # default="/home/qyh/projects/FixFL/dataset/complex_bugs_v2.csv",
        default="/home/qyh/projects/FixFL/dataset/all_bugs.csv",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="config file",
        # default="/home/qyh/projects/FixFL/config/pingfl_gpt4o_gpt4turbo.yml",
        # default="/home/qyh/projects/FixFL/config/pingfl_gpt4o_gpt4turbo_no_test_code.yml",
        # default="/home/qyh/projects/FixFL/config/pingfl_gpt4o_gpt4turbo_no_test_output.yml",
        # default="/home/qyh/projects/FixFL/config/pingfl_gpt4o_gpt4turbo_no_stack_trace.yml",
        # default="/home/qyh/projects/FixFL/config/pingfl_gpt4o_gpt4turbo_no_suspected_issue.yml",
        # default="/home/qyh/projects/FixFL/config/pingfl_gpt4o_gpt4turbo_no_thought.yml",
        # default="config_old/pingfl_gpt4o_gpt4turbo_no_PDagent.yml",
    )
    parser.add_argument(
        "--processes",
        type=int,
        help="processes",
        default=12,
    )
    args = parser.parse_args()
    main(args.dataset, args.config, args.processes)
