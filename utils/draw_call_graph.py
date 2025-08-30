import pickle
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import networkx as nx

graph_file = (
    "/home/qyh/projects/FixFL/dataset/bugInfo/Math/Math@7/combined_graph.pkl"
)
with open(graph_file, "rb") as f:
    G: nx.MultiDiGraph = pickle.load(f)

plt.figure(figsize=(12, 8))

nodes = list(G.nodes)[:500]
subgraph = G.subgraph(nodes)

pos = nx.spring_layout(subgraph, k=1, seed=42)

print("draw nodes")
nx.draw_networkx_nodes(subgraph, pos, node_size=5)

print("draw edges")
nx.draw_networkx_edges(subgraph, pos, width=1.0, alpha=0.5)

plt.title("Call Graph", fontsize=16, pad=20)
plt.axis("off")

plt.tight_layout()
plt.savefig("network_visualization.png", format="PNG")
