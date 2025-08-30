import networkx as nx

graph = nx.DiGraph()

graph.add_node("A", label="yes")
graph.add_node("B", label="no")
graph.add_node("C", label="yes")
graph.add_node("D", label="yes")
graph.add_node("E", label="no")
graph.add_node("F", label="yes")

graph.add_edge("A", "B")
graph.add_edge("A", "C")
graph.add_edge("B", "D")
graph.add_edge("B", "E")
graph.add_edge("E", "F")
graph.add_edge("E", "B")


def is_yes(node):
    return graph.nodes[node]["label"] == "yes"


def get_all_matched_successors(node, visited_nodes):
    """Get all matched successors in the repo graph"""
    visited_nodes.add(node)
    matched_successors = []
    for successor in graph.successors(node):
        if successor in visited_nodes:
            continue
        if is_yes(successor):
            matched_successors.append(successor)
        else:
            matched = get_all_matched_successors(successor, visited_nodes)
            matched_successors.extend(matched)
    return matched_successors


visited_nodes = set()
matched = get_all_matched_successors("A", visited_nodes)
print("Visited nodes:", visited_nodes)
print("Matched successors:", matched)
