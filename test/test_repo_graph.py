import pickle
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from src.repograph.graph_searcher import RepoSearcher


def test():
    graph_file = (
        root
        / "dataset"
        / "bugInfo"
        / "Closure"
        / "Closure@3"
        / "com_google_javascript_jscomp_FlowSensitiveInlineVariablesTest"
        / "testDoNotInlineCatchExpression1"
        / "repograph.pkl"
    )

    with open(graph_file, "rb") as f:
        graph = pickle.load(f)

    searcher = RepoSearcher(graph)

    print("Test get_covered_classes 1")
    print(searcher.get_covered_classes())

    print("*" * 20)
    print("Test get_covered_method_ids_for_class 1")
    print(
        searcher.get_covered_method_ids_for_class(
            "com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest"
        )
    )

    print("*" * 20)
    print("Test get_covered_method_ids_for_class 2")
    print(
        searcher.get_covered_method_ids_for_class(
            "FlowSensitiveInlineVariables"
        )
    )

    print("*" * 20)
    print("Test get_covered_method_ids_for_class 3")
    print(searcher.get_covered_method_ids_for_class("Candidate"))

    print("*" * 20)
    print("Test get_possible_method_ids 1")
    print(
        searcher.get_possible_method_ids(
            [
                "com.google.javascript.jscomp.FlowSensitiveInlineVariablesTest.testDoNotInlineIncrement#79-83"
            ]
        )
    )

    print("*" * 20)
    print("Test get_method_code_for_id 1")
    print(
        searcher.get_method_code_for_id(
            "com.google.javascript.jscomp.FlowSensitiveInlineVariables.Candidate.canInline#280-411"
        )
    )

    print("*" * 20)
    print("Test get_method_ids_contain_string 1")
    print(
        searcher.get_method_ids_contain_string("// Cannot inline a parameter.")
    )

    print("*" * 20)
    print("Test get_caller_method_ids 1")
    print(
        searcher.get_caller_method_ids(
            "com.google.javascript.jscomp.FlowSensitiveInlineVariables.Candidate.canInline#280-411"
        )
    )

    print("*" * 20)
    print("Test get_callee_method_ids 1")
    print(
        searcher.get_callee_method_ids(
            "com.google.javascript.jscomp.FlowSensitiveInlineVariables.Candidate.canInline#280-411"
        )
    )


if __name__ == "__main__":
    test()
