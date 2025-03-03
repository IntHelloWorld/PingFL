import json
from typing import Dict, List

import networkx as nx

from src.exceptions import ClassNotFoundError, MethodNotFoundError, SnippetNotFoundError
from src.repograph.construct_graph_old import Tag


class RepoSearcher:
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph
        self.covered_classes_result = None
        
        # create a dictionary of methods for each class
        method_dict: Dict[str, List[Tag]] = {}
        
        # create a map of method ID to method node
        method_id_map: Dict[str, Tag] = {}
        
        for node in self.graph.nodes(data=True):
            if node[0].category == 'function':
                method_node: Tag = node[0]
                method_id_map[method_node.method_id] = method_node
                inner_class_names = []
                if method_node.inner_class:
                    inner_class_names = method_node.inner_class.split('$')
                class_names = [method_node.outer_class] + inner_class_names
                for i in range(1, len(class_names) + 1):
                    class_name = '$'.join(class_names[:i])
                    class_full_name = f'{method_node.pkg_name}.{class_name}'
                    try:
                        method_dict[class_full_name].append(method_node)
                    except KeyError:
                        method_dict[class_full_name] = [method_node]
        self.method_dict = method_dict
        self.method_id_map = method_id_map
    
    def get_method(self, method_id):
        return self.method_id_map[method_id]

    def one_hop_neighbors(self, query):
        # get one-hop neighbors from networkx graph
        return list(self.graph.neighbors(query))

    def two_hop_neighbors(self, query):
        # get two-hop neighbors from networkx graph
        one_hop = self.one_hop_neighbors(query)
        two_hop = []
        for node in one_hop:
            two_hop.extend(self.one_hop_neighbors(node))
        return list(set(two_hop))

    def dfs(self, query, depth):
        # perform depth-first search on networkx graph
        visited = []
        stack = [(query, 0)]
        while stack:
            node, level = stack.pop()
            if node not in visited:
                visited.append(node)
                if level < depth:
                    stack.extend(
                        [(n, level + 1) for n in self.one_hop_neighbors(node)]
                    )
        return visited
    
    def bfs(self, query, depth):
        # perform breadth-first search on networkx graph
        visited = []
        queue = [(query, 0)]
        while queue:
            node, level = queue.pop(0)
            if node not in visited:
                visited.append(node)
                if level < depth:
                    queue.extend(
                        [(n, level + 1) for n in self.one_hop_neighbors(node)]
                    )
        return visited
    
    def get_covered_classes(self):
        """Get a dictionary of all covered classes in the graph"""
        if self.covered_classes_result:
            return self.covered_classes_result
        
        covered_classes = {}
        covered_test_classes = {}
        for node in self.graph.nodes:
            if node.category == "class":
                if node.is_test:
                    try:
                        covered_test_classes[node.pkg_name].append(node.name)
                    except KeyError:
                        covered_test_classes[node.pkg_name] = [node.name]
                else:
                    try:
                        covered_classes[node.pkg_name].append(node.name)
                    except KeyError:
                        covered_classes[node.pkg_name] = [node.name]
        assert len(covered_classes) > 0 and len(covered_test_classes) > 0
        template = "Covered source classes:\n{covered_classes}\n\nCovered test classes:\n{covered_test_classes}"
        result = template.format(
            covered_classes=json.dumps(covered_classes, indent=2),
            covered_test_classes=json.dumps(covered_test_classes, indent=2)
        )
        self.covered_classes_result = result
        return result
    
    def get_covered_methods_of_class(self, class_name):
        """Get a list of all covered methods of a class"""
        try:
            # precise match
            if class_name in self.method_dict:
                return json.dumps({class_name: [m.method_pos for m in self.method_dict[class_name]]}, indent=2)
            # fuzzy match
            else:
                possible_classes = [c for c in self.method_dict if class_name in c]
                if not possible_classes:
                    raise ClassNotFoundError(class_name)
                result = {}
                for c in possible_classes:
                    result[c] = [m.method_pos for m in self.method_dict[c]]
                return json.dumps(result, indent=2)
        except Exception as e:
            return e.message
    
    def get_method_code(self, class_name, method_name):
        """Get the code of a method"""
        try:
            methods = []
            # precise match
            if class_name in self.method_dict:
                for m in self.method_dict[class_name]:
                    if m.name == method_name:
                        methods.append(m)
            # fuzzy match
            else:
                possible_classes = [c for c in self.method_dict if class_name in c]
                if not possible_classes:
                    raise ClassNotFoundError(class_name)
                for c in possible_classes:
                    for m in self.method_dict[c]:
                        if m.name == method_name:
                            methods.append(m)
            if not methods:
                raise MethodNotFoundError(method_name)
        except Exception as e:
            return e.message
        
        methods = list(set(methods))
        template = "\"Method ID\": \"{method_id}\"\n\"Method Code\": ```\n{method_code}\n```\n"
        result = '\n'.join([template.format(method_id=m.method_id, method_code=m.code) for m in methods])
        return result
    
    def search_code_snippet(self, code_snippet):
        """Search for a code snippet and return all methods containing the code_snippet"""
        try:
            methods = []
            for method in self.method_id_map.values():
                if code_snippet in method.code:
                    methods.append(method)
            if not methods:
                raise SnippetNotFoundError(code_snippet)
        except Exception as e:
            return e.message
        
        methods = list(set(methods))
        template = "\"Method ID\": \"{method_id}\""
        result = (
            'These covered methods contain the provided code snippet:\n'
            +
            '\n'.join([template.format(method_id=m.method_id) for m in methods])
        )
        return result