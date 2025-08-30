import pickle
import sys
from argparse import Namespace
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from src.config import BugInfo
from src.core.verify_agent import VerifyAgent
from src.interfaces.d4j import (
    get_failed_tests,
    get_properties,
    get_test_case_dataset_path,
)
from src.repograph.graph_searcher import RepoSearcher
from src.schema import DebugInput, VerifyInput

args = Namespace(
    project="Chart",
    bugID="1",
    config="/home/qyh/projects/FixFL/config/pingfl_gpt4o_gpt4turbo.yml",
)
bug_info = BugInfo(args)
get_properties(bug_info)
test_failure = get_failed_tests(bug_info)

test_class = test_failure.test_classes[0]
test_case = test_class.test_cases[0]

dataset_path = get_test_case_dataset_path(bug_info, test_case)
repo_graph_file = dataset_path / "repograph.pkl"
with repo_graph_file.open("rb") as f:
    repo_graph = pickle.load(f)
loaded_classes_file = dataset_path / "loaded_classes.txt"
loaded_classes = loaded_classes_file.read_text().split("\n")

stack_trace_file = dataset_path / "stack_trace.txt"
test_output_file = dataset_path / "test_output.txt"
test_name = test_case.name
test_code = test_case.test_method.text
error_message = (
    stack_trace_file.read_text() + "\n\n" + test_output_file.read_text()
)
output_path = root / "test" / "test_verify_agent"
if not output_path.exists():
    output_path.mkdir(parents=True)

debug_input = DebugInput(
    test_name=test_name,
    test_code=test_code,
    error_message=error_message,
    repo_graph=repo_graph,
    loaded_classes=loaded_classes,
    output_path=output_path,
)

repo_searcher = RepoSearcher(repo_graph)
method_node = repo_searcher.get_method(
    "org.jfree.chart.renderer.category.AbstractCategoryItemRenderer.getLegendItems#1790-1822"
)
suspected_issue = """The `AbstractCategoryItemRenderer` does not have a `datasetChanged` method or explicit handling for dataset change events, which seems to confirm that it does not respond to dataset updates. This could explain why its `getLegendItems` method does not regenerate legend items dynamically after a dataset update.\n\nThe issue likely lies in the lack of synchronization between dataset updates and the renderer's behavior. To confirm this as the root cause and propose a fix, I'll nominate the `getLegendItems` method in `AbstractCategoryItemRenderer` as suspicious."""

verify_input = VerifyInput(
    test_name=test_name,
    test_code=test_code,
    error_message=error_message,
    method_id=method_node.method_id,
    suspected_issue=suspected_issue,
    method_code=method_node.code,
    output_dir=output_path,
    process_id="0",
    method=method_node,
)

verify_agent = VerifyAgent(bug_info, "openai")
verify_agent.run(verify_input)
