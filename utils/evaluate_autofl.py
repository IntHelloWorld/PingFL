import argparse
import json
import multiprocessing
import pickle
import sys
from argparse import Namespace
from copy import deepcopy
from pathlib import Path
from typing import List

import networkx as nx
import pandas as pd

root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from src.config import BugInfo
from src.interfaces.d4j import get_failed_tests, get_properties
from src.interfaces.method_extractor import JMethod
from src.schema import Tag, TestFailure


def get_node_distance(graph: nx.MultiDiGraph, node1: Tag, node2: Tag):
    dynamic_graph = nx.Graph()
    combined_graph = nx.Graph()
    for edge in graph.edges(data=True):
        combined_graph.add_edge(edge[0], edge[1])
        if edge[2]["rel"] == "calls":
            dynamic_graph.add_edge(edge[0], edge[1])

    # if the two nodes are the same, return 0
    if node1 == node2:
        return 0

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
    pred_method_sig: str,
):
    """
    Get the relative distance between buggy (modified) methods and the predicted method.

    For example, if the number of buggy methods is 3,
    the output will be a list contains 3 distances such as [2, 3, 4].
    """

    def fuzzy_match(method_tag: Tag, method_sig: str):
        identifiers = method_sig.split("(")[0].split(".")
        buggy_class = method_tag.outer_class
        buggy_method_name = method_tag.name
        if buggy_class in identifiers and buggy_method_name in identifiers:
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
            if fuzzy_match(method_node, pred_method_sig):
                predict_node = method_node

    assert (
        len(should_find_methods) == 0
    ), f"Buggy methods not found in graph: {[m.get_signature() for m in should_find_methods]}"

    if predict_node is None:
        print(f"Predict method not found: {pred_method_sig}")
        return []

    distances = []
    for buggy_node in buggy_nodes:
        distance = get_node_distance(combined_graph, buggy_node, predict_node)
        if distance != -1:
            distances.append(distance)
    return distances


def get_distance(
    bug_info: BugInfo, test_failure_obj: TestFailure, autofl_res_file: Path
):
    modified_methods = test_failure_obj.buggy_methods

    graph_file = bug_info.bug_path / "combined_graph.pkl"
    with graph_file.open("rb") as f:
        combined_graph = pickle.load(f)

    with autofl_res_file.open("r") as f:
        pred_method_sigs = json.load(f)

    if not pred_method_sigs:
        return [0]

    evaluate_result = []
    for pred_method_sig in pred_method_sigs:
        distances = get_relative_distance(
            combined_graph, modified_methods, pred_method_sig
        )
        if distances:
            rd = max([1 / (d + 1) for d in distances])
            evaluate_result.append(rd)
        else:
            # if the method is not found in the graph
            evaluate_result.append(0)
    return evaluate_result


def evaluate(project, bugID, config, autofl_res_file):
    args = Namespace(project=project, bugID=bugID, config=config)
    bug_info = BugInfo(args, eval=True)
    result_path: Path = bug_info.evaluation_path / Path(config).stem
    if not result_path.exists():
        result_path.mkdir(parents=True, exist_ok=True)
    result_file = result_path / f"{project}-{bugID}.json"
    if result_file.exists():
        return

    # collect basic bug information from cache
    # For preprocessing please run `preprocess.py`
    get_properties(bug_info)
    test_failure_obj = get_failed_tests(bug_info)

    distances = get_distance(bug_info, test_failure_obj, autofl_res_file)
    with result_file.open("w") as f:
        json.dump(distances, f)


def print_result(bug_names, config_file):
    config_name = Path(config_file).stem
    output = {}
    for bug_name in bug_names:
        proj, bug_id = bug_name.split("_")
        distance_file = (
            root / "EvaluationResult" / config_name / f"{proj}-{bug_id}.json"
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
                "RD@1": [],
                "RD@3": [],
                "RD@5": [],
            }
        for idx, d in enumerate(distance):
            if d == 1.0:
                if idx == 0:
                    output[proj]["Top-1"] += 1
                if idx < 3:
                    output[proj]["Top-3"] += 1
                if idx < 5:
                    output[proj]["Top-5"] += 1
                break
        for i in [1, 3, 5]:
            if distance[:i]:
                output[proj][f"RD@{i}"].append(max(distance[:i]))
            else:
                print(f"Warning: {proj}-{bug_id} no results!")

    for proj in output:
        for i in [1, 3, 5]:
            output[proj][f"RD@{i}"] = sum(output[proj][f"RD@{i}"])

    print(output)


def main(dataset_file, autofl_res_dir, config_file, processes):
    df = pd.read_csv(dataset_file, header=None)
    bug_names = df.iloc[:, 0].tolist()

    # TODO: evaluation: control bug for test
    # bug_names = ["Closure_1"]
    bug_names = [b for b in bug_names if b.startswith("Closure")]

    with multiprocessing.Pool(processes=processes) as pool:
        async_results = []
        for bug_name in bug_names:
            proj, bug_id = bug_name.split("_")
            autofl_res_file = Path(autofl_res_dir) / f"{bug_name}.json"
            async_result = pool.apply_async(
                evaluate, (proj, bug_id, config_file, autofl_res_file)
            )
            async_results.append(async_result)

        for async_result in async_results:
            try:
                async_result.get()
            except Exception as e:
                print(e)
                return

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
        "--autofl_res_dir",
        type=str,
        help="autoFL result directory",
        # default="/home/qyh/projects/autofl/gpt-4o-2024-11-20",
        default="/home/qyh/projects/autofl/deepseek-v3-250324_rep5",
        # default="/home/qyh/projects/autofl/deepseek-v3-250324",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="config file",
        default="/home/qyh/projects/FixFL/config/autofl_deepseek_rep5.yml",
        # default="/home/qyh/projects/FixFL/config/autofl_deepseek.yml",
        # default="/home/qyh/projects/FixFL/config/autofl_gpt4o_rep5.yml",
    )
    parser.add_argument(
        "--processes",
        type=int,
        help="processes",
        default=16,
    )
    args = parser.parse_args()
    main(args.dataset, args.autofl_res_dir, args.config, args.processes)
