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

from src.interfaces.method_extractor import JMethod
from src.schema import Tag, TestFailure

root = Path(__file__).resolve().parent
sys.path.append(str(root))

from src.config import BugInfo
from src.interfaces.d4j import get_failed_tests, get_properties


def get_node_distance(graph: nx.MultiDiGraph, node1: Tag, node2: Tag):
    dynamic_graph = nx.Graph()
    combined_graph = nx.Graph()
    for edge in graph.edges(data=True):
        combined_graph.add_edge(edge[0], edge[1])
        if edge[2]['rel'] == 'calls':
            dynamic_graph.add_edge(edge[0], edge[1])
    
    # if the two nodes are the same, return 0
    if node1 == node2:
        return 0
    
    # first try to find the shortest path in dynamic graph
    try:
        shortest_path = nx.shortest_path(dynamic_graph, node1, node2)
        return len(shortest_path)
    except nx.NetworkXNoPath:
        # if not found, try to find the shortest path in combined graph
        try:
            shortest_path = nx.shortest_path(combined_graph, node1, node2)
            return len(shortest_path)
        except nx.NetworkXNoPath:
            # if still not found, return -1
            return -1

def get_relative_distance(
        bug_info: BugInfo,
        test_names: List[str],
        modified_methods: List[JMethod],
        method_id: str
    ):
    """
    Get the relative distance between buggy methods and the predicted method.
    Note that the predicted method may related to multiple test cases (call graphs).
    
    For example, if the number of buggy methods is 3,
    and the predicted method is related to 2 test cases,
    the output will be a list of 2 lists, each list contains 3 distances.
    Such as [[1, 2, 3], [2, 3, 4]]
    """
    graph_files = [(bug_info.bug_path / t / "repograph.pkl") for t in test_names]
    all_distances = []
    for graph_file in graph_files:
        if not graph_file.exists():
            raise FileNotFoundError(f"{graph_file} not found, please check")
        with graph_file.open("rb") as f:
            graph: nx.MultiDiGraph = pickle.load(f)
        buggy_nodes = []
        predict_node = None
        should_find_methods = deepcopy(modified_methods)
        for nodes in graph.nodes(data=True):
            if nodes[0].category == "function":
                method_node: Tag = nodes[0]
                for m in should_find_methods:
                    if m.class_name == method_node.outer_class:
                        if m.name == method_node.name:
                            if m.loc[0][0] <= method_node.line[0] and m.loc[1][0] >= method_node.line[1]:
                                buggy_nodes.append(method_node)
                                should_find_methods.remove(m)
                                break
                if method_node.method_id == method_id:
                    predict_node = method_node
        
        assert len(should_find_methods) == 0, f"some buggy methods not found in {graph_file}"
        assert predict_node is not None, f"predict method not found in {graph_file}"
        
        distances = []
        for buggy_node in buggy_nodes:
            distance = get_node_distance(graph, buggy_node, predict_node)
            if distance != -1:
                distances.append(distance)
        
        if distances:
            all_distances.append(distances)
    return all_distances

def get_distance(bug_info: BugInfo, test_failure_obj: TestFailure):
    method_to_test = {}
    res_path: Path = bug_info.res_path
    result_paths = list(res_path.glob("verify_results.json"))
    for result_path in result_paths:
        methods = json.loads(result_path.read_text())["results"]
        buggy_methods = [m for m in methods if m["category"] == "buggy"]
        test_method_name = result_path.parent.name
        test_class_name = result_path.parent.parent.name
        test_name = f"{test_class_name}/{test_method_name}"
        for buggy_method in buggy_methods:
            if buggy_method["method_id"] not in method_to_test:
                method_to_test[buggy_method["method_id"]] = [test_name]
            else:
                method_to_test[buggy_method["method_id"]].append(test_name)
    
    final_result_path = res_path / "debug_result.json"
    ranked_methods = json.loads(final_result_path.read_text())["results"]
    modified_methods = test_failure_obj.buggy_methods
    
    evaluate_result = []
    for ranked_method in ranked_methods:
        method_id = ranked_method["method_id"]
        assert method_id in method_to_test, f"{method_id} not in verify results, please check"
        test_names = method_to_test[method_id]
        
        distances = get_relative_distance(test_names, modified_methods, method_id)
        if distances:
            # TODO: Do we have better way to evaluate the distance?
            min_distance = min([min(d) for d in distances])
            evaluate_result.append(min_distance)
        else:
            evaluate_result.append(-1)
    return evaluate_result


def evaluate(project, bugID, config):
    args = Namespace(project=project, bugID=bugID, config=config)
    bug_info = BugInfo(args)
    result_file: Path = bug_info.res_path / "distance.json"
    if result_file.exists():
        return
    
    # collect basic bug information from cache
    # For preprocessing please run `preprocess.py`
    get_properties(bug_info)
    test_failure_obj = get_failed_tests(bug_info)
    
    distances = get_distance(bug_info, test_failure_obj)
    with result_file.open("w") as f:
        json.dump(distances, f)


def print_result(bug_names, config_file):
    root_path = Path(__file__).resolve().parent
    config_name = Path(config_file).stem
    output = {}
    for bug_name in bug_names:
        proj, bug_id = bug_name.split("_")
        distance_file = root_path / "DebugResult" / config_name / proj / f"{proj}-{bug_id}" / "distance.json"
        if not distance_file.exists():
            raise FileNotFoundError(f"{distance_file} not found, please check")
        with distance_file.open("r") as f:
            distance = json.load(f)
        
        if proj not in output:
            output[proj] = {"Top-1": 0, "Top-3": 0, "Top-5": 0, "RD@1": [], "RD@3": [], "RD@5": []}
        for idx, d in enumerate(distance):
            if d == 0:
                if idx == 0:
                    output[proj]["Top-1"] += 1
                if idx < 3:
                    output[proj]["Top-3"] += 1
                if idx < 5:
                    output[proj]["Top-5"] += 1
        for i in [1, 3, 5]:
            output[proj][f"RD@{i}"].append(min(distance[:i]))
        
    for proj in output:
        for i in [1, 3, 5]:
            output[proj][f"RD@{i}"] = sum(output[proj][f"RD@{i}"]) / len(output[proj][f"RD@{i}"])
    
    print(output)


def main(dataset_file, config_file):
    df = pd.read_csv(dataset_file)
    bug_names = df.iloc[:, 0].tolist()
    
    pool = multiprocessing.Pool(processes=5)
    for bug_name in bug_names[:2]:
        proj, bug_id = bug_name.split("_")
        pool.apply_async(evaluate, (proj, bug_id, config_file))
    pool.close()
    pool.join()
    
    print_result(bug_names, config_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run all bugs')
    parser.add_argument(
        '--dataset',
        type=str,
        help='dataset file',
        default="/home/qyh/projects/FixFL/dataset/complex_bugs_v2.csv"
    )
    parser.add_argument(
        '--config',
        type=str,
        help='config file',
        default="/home/qyh/projects/FixFL/config/gpt4o_gpt4turbo.yml"
    )
    args = parser.parse_args()
    main(args.dataset, args.config)
