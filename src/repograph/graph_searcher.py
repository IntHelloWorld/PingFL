import json
from typing import Dict, List

import networkx as nx

from src.config import BugInfo
from src.exceptions import (
    ArgumentError,
    ClassNotFoundError,
    MethodIDNotFoundError,
    MethodNotFoundError,
    SnippetNotFoundError,
)
from src.schema import Tag


class RepoSearcher:
    def __init__(self, graph: nx.MultiDiGraph, loaded_classes: List[str]):
        self.graph = graph
        self.loaded_classes = loaded_classes
        self.covered_classes_result = None
        
        # create a dictionary of methods grouped by class name
        # note that this supports fuzzy matching
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

    def get_predecessors(self, node, edge_type):
        predecessors = [
            u for u in self.graph.pred[node]
            for key in self.graph[u][node]
            if self.graph[u][node][key]['rel'] == edge_type
        ]
        return predecessors

    def get_successors(self, node, edge_type):
        successors = [
            v for v in self.graph.succ[node]
            for key in self.graph[node][v]
            if self.graph[node][v][key]['rel'] == edge_type
        ]
        return successors
    
    def get_covered_classes(self):
        """Get a dictionary of all covered classes in the graph"""
        if self.covered_classes_result:
            return self.covered_classes_result
        
        covered_classes = {}
        for loaded_class in self.loaded_classes:
            if loaded_class == '':
                continue
            class_name = loaded_class.split('.')[-1]
            pkg_name = '.'.join(loaded_class.split('.')[:-1])
            try:
                covered_classes[pkg_name].append(class_name)
            except KeyError:
                covered_classes[pkg_name] = [class_name]
        assert len(covered_classes) > 0
        
        template = "Covered classes grouped with package name:\n{covered_classes}"
        result = template.format(
            covered_classes=json.dumps(covered_classes, indent=2),
        )
        self.covered_classes_result = result
        return result
    
    def get_covered_methods_of_class(self, class_name):
        """Get a list of all covered methods of a class"""
        try:
            # precise match
            if class_name in self.method_dict:
                return json.dumps({class_name: [m.method_pos for m in self.method_dict[class_name] if m.is_covered]}, indent=2)
            # fuzzy match
            else:
                possible_classes = [c for c in self.method_dict if class_name in c]
                if not possible_classes:
                    raise ClassNotFoundError(class_name)
                result = {}
                for c in possible_classes:
                    result[c] = [m.method_pos for m in self.method_dict[c] if m.is_covered]
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
        template = "\"Method ID\": \"{method_id}\"\n\"Is Covered\": \"{is_covered}\"\n\"Method Code\": ```\n{method_code}\n```\n"
        result = '\n'.join([template.format(method_id=m.method_id, is_covered=m.is_covered, method_code=m.code) for m in methods])
        return result
    
    def search_methods_contain_string(self, string_content):
        """
        Get a list of all production methods containing a specific string content.
        This tool is particularly useful when the test output contains some special strings.",
        """
        try:
            methods = []
            for method in self.method_id_map.values():
                if method.is_test:  # skip test methods
                    continue
                if string_content in method.code:
                    methods.append(method)
            if not methods:
                raise SnippetNotFoundError(string_content)
        except Exception as e:
            return e.message
        
        methods = list(set(methods))
        template = "{idx}. \"{method_id}\"{is_covered}"
        prefix = (
            'The following methods contain the provided string content, '
            'we exclude all test methods, '
            'the method executed during runtime is marked with (COVERED):\n'
        )
        result = (
            prefix
            +
            '\n'.join(
                [
                    template.format(
                        idx=i+1,
                        method_id=m.method_id,
                        is_covered=' (COVERED)' if m.is_covered else ''
                    ) for i, m in enumerate(methods)
                ]
            )
        )
        return result
    
    def get_caller_methods(self, method_id):
        """Get all covered methods that have called the provided method during the test"""
        
        try:
            if method_id not in self.method_id_map:
                raise MethodIDNotFoundError(method_id)
            current_method = self.method_id_map[method_id]
            caller_methods = list(self.get_predecessors(current_method, 'calls'))
        except Exception as e:
            return e.message
        
        if not caller_methods:
            return (
                "No caller methods found, this method may not be executed during testing. "
                "If you want to get all callers that may call this method, "
                "try to use the `search_methods_contain_string` tool."
            )
            
        template = "{idx}. \"{method_id}\""
        prefix = "The following methods have called the method {method_id} during the test:\n"
        result = (
            prefix.format(method_id=method_id)
            +
            '\n'.join(
                [
                    template.format(
                        idx=i+1,
                        method_id=m.method_id
                    ) for i, m in enumerate(caller_methods)
                ]
            )
        )
        return result
    
    def get_callee_methods(self, method_id):
        """Get all covered methods that have been called by the provided method during the test"""

        try:
            if method_id not in self.method_id_map:
                raise MethodIDNotFoundError(method_id)
            current_method = self.method_id_map[method_id]
            callee_methods = list(self.get_successors(current_method, 'calls'))
        except Exception as e:
            return e.message

        if not callee_methods:
            return f"No callee methods found, this method may not be executed or call other methods at runtime."
            
        template = "\"{method_id}\""
        prefix = "The following methods have been called by the method {method_id} during the test:\n"
        result = (
            prefix.format(method_id=method_id)
            +
            '\n'.join(
                [
                    template.format(
                        idx=i+1,
                        method_id=m.method_id
                    ) for i, m in enumerate(callee_methods)
                ]
            )
        )
        return result