import networkx as nx


class MyNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"MyNode(value={self.value})"

G = nx.Graph()

node1 = MyNode(value='old_value')
node2 = MyNode(value='node2')
node3 = MyNode(value='node3')

G.add_node(node1)
G.add_node(node2)
G.add_node(node3)
G.add_edge(node1, node2)
G.add_edge(node1, node3)

print("Original Graph:")
print("nodes:", G.nodes)
print("edges:", G.edges)

node1.value = 'new_value'

print("\nNew Graph:")
print("nodes:", G.nodes)
print("edges:", G.edges)

print("\nnode 1 property:", node1.value)