from collections import defaultdict
from difflib import SequenceMatcher
from typing import List


def get_highest_priority_candidates(
    false_method_id: str,
    possible_method_ids: List[str],
    num_max_candidates: int = 5,
):
    def _compute_similarity(method_id_1, method_id_2):
        name_strs_1 = method_id_1.split("#")[0].split(".")
        name_strs_2 = method_id_2.split("#")[0].split(".")
        return SequenceMatcher(None, name_strs_1, name_strs_2).ratio()

    similarities = []
    for possible_method_id in possible_method_ids:
        similarity = _compute_similarity(false_method_id, possible_method_id)
        similarities.append((similarity, possible_method_id))
    print(similarities)

    candidates = list(
        map(
            lambda t: t[1],
            sorted(similarities, key=lambda t: t[0], reverse=True),
        )
    )
    if num_max_candidates is not None:
        candidates = candidates[:num_max_candidates]
    return candidates


def test_get_highest_priority_candidates():
    false_method_id = (
        "org.apache.commons.math3.analysis.function.Gaussian.value"
    )
    possible_method_ids = [
        "org.apache.commons.math3.analysis.function.Gaussian.value#210-243",
        "org.apache.commons.math3.analysis.type.Gaussian.value#210-244",
        "org.apache.commons.math3.analysis.Gaussian.value#210-234",
        "org.apache.commons.math3.analysis.function.Gaussian.InnerClass.value#210-235",
        "org.apache.commons.math3.analysis.function.Gaussian.other#210-236",
    ]
    candidates = get_highest_priority_candidates(
        false_method_id, possible_method_ids
    )
    print("Candidates:")
    for candidate in candidates:
        print(candidate)


if __name__ == "__main__":
    test_get_highest_priority_candidates()
