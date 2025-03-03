import argparse
import json
import os
import pickle
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set, Tuple

import networkx as nx
from tqdm import tqdm
from tree_sitter_languages import get_language, get_parser

from src.config import BugInfo
from src.interfaces.d4j import get_test_case_dataset_path, parse_coverage
from src.schema import Tag, TestFailure


class CodeGraph:
    """Constructs and manages code dependency graphs for Python/Java projects"""
    
    SUPPORTED_LANGS = {
        '.py': 'python',
        '.java': 'java'
    }
    
    def __init__(self, src_dir: str, test_dir: str, language: str = None):
        self.src_dir = src_dir
        self.test_dir = test_dir
        self.language = language
        if language and language not in self.SUPPORTED_LANGS.values():
            raise ValueError(f"Unsupported language: {language}. Supported languages are: {list(self.SUPPORTED_LANGS.values())}")
        
        # Cache for tag locations
        self.location = {}
        
        # Cache for def tags
        self.def_tags = {}

    def get_code_graph(self, src_files: List[str], test_files: List[str]) -> Tuple[List[Tag], nx.MultiDiGraph]:
        """Construct code graph from given files"""
        if not src_files or not test_files:
            raise ValueError("No source or test files found")
            
        src_tags = self.get_file_tags(src_files, False)
        test_tags = self.get_file_tags(test_files, True)
        tags = src_tags + test_tags
        graph = self.build_graph(tags)
        return tags, graph

    def get_file_tags(self, files: List[str], is_test: bool) -> List[Tag]:
        """Extract tags from source files"""
        all_tags = []
        for fname in tqdm(files, desc="Parsing tags"):
            if not Path(fname).is_file():
                continue
            
            if is_test:
                rel_fname = os.path.relpath(fname, self.test_dir)
            else:
                rel_fname = os.path.relpath(fname, self.src_dir)
            ext = Path(fname).suffix
            
            lang = self.SUPPORTED_LANGS[ext]
            tags = self.parse_file(fname, rel_fname, lang, is_test)
            all_tags.extend(tags)
            
        return all_tags

    def parse_file(self, fname: str, rel_fname: str, lang: str, is_test: bool) -> List[Tag]:
        """Parse single source file and extract tags"""
        with open(fname, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        parser = get_parser(lang)
        language = get_language(lang)
        tree = parser.parse(bytes(file_content, 'utf-8'))
        
        # Get language-specific query
        query = self.get_query(lang)
        captures = language.query(query).captures(tree.root_node)
        
        tags = []
        for node, tag_type in captures:
            tag = self.create_tag(node, tag_type, fname, rel_fname, file_content, is_test)
            if tag:
                tags.append(tag)
                
        return tags
    
    def get_node_code(self, node, code: str) -> str:
        """Get code for AST node, keep the indentation"""
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1
        return "\n".join(code.splitlines()[start_line-1:end_line])

    def create_tag(self, node, tag_type: str, fname: str, rel_fname: str, file_content: str, is_test: bool) -> Optional[Tag]:
        """Create tag from AST node"""
        pkg_name = '.'.join(rel_fname.split('.')[0].split('/')[:-1])
        parent_class = None
        interfaces = []
        
        if tag_type == "definition.interface":
            kind = "def"
            name_node = node.child_by_field_name("name")
            code = self.get_node_code(node, file_content)
            category = 'interface'
            if name_node:
                name = name_node.text.decode("utf-8")
            else:
                raise ValueError(f"Missing name node in {tag_type}")
        elif tag_type == "definition.enum":
            kind = "def"
            name_node = node.child_by_field_name("name")
            code = self.get_node_code(node, file_content)
            category = 'enum'
            if name_node:
                name = name_node.text.decode("utf-8")
            else:
                raise ValueError(f"Missing name node in {tag_type}")
        elif tag_type == "definition.class":
            kind = "def"
            name_node = node.child_by_field_name("name")
            code = self.get_node_code(node, file_content)
            category = 'class'
            if name_node:
                name = name_node.text.decode("utf-8")
                if self.language == 'python':
                    bases_node = node.child_by_field_name("bases")
                    if bases_node and bases_node.named_children:
                        parent_class = bases_node.named_children[0].text.decode("utf-8")
                elif self.language == 'java':
                    superclass_node = node.child_by_field_name("superclass")
                    if superclass_node and superclass_node.named_children:
                        parent_class = superclass_node.named_children[0].text.decode("utf-8")
                    interfaces_node = node.child_by_field_name("interfaces")
                    if interfaces_node:
                        interfaces = [child.text.decode("utf-8") for child in interfaces_node.named_children]
        elif tag_type in ["definition.function", "definition.constructor"]:
            kind = "def"
            category = 'function'
            name_node = node.child_by_field_name("name")
            code = self.get_node_code(node, file_content)
            if name_node:
                name = name_node.text.decode("utf-8")
            else:
                raise ValueError(f"Missing name node in {tag_type}")
        elif tag_type == "definition.class.field":
            kind = "def"
            category = 'field'
            name_node = node.child_by_field_name("declarator").child_by_field_name("name")
            code = self.get_node_code(node, file_content)
            if name_node:
                name = name_node.text.decode("utf-8")
            else:
                raise ValueError(f"Missing name node in {tag_type}")
        elif tag_type.startswith("name.reference."):
            kind = "ref"
            name = node.text.decode("utf-8")
            category = None
            code = None
        else:
            return None
        
        lines = (node.start_point[0] + 1, node.end_point[0] + 1)
        tag = Tag(rel_fname, fname, lines, name, kind, category, code, pkg_name, parent_class, tuple(interfaces), is_test)
        try:
            self.location[fname][lines] = tag
        except:
            self.location[fname] = {lines: tag}
        
        if kind == 'def':
            try:
                self.def_tags[name].append(tag)
            except:
                self.def_tags[name] = [tag]
        return tag

    def build_graph(self, tags: List[Tag]) -> nx.MultiDiGraph:
        """Build dependency graph from tags"""
        
        def find_def_tag(ref_tag, categories=[]):
            """Find definition tag for reference"""
            ref_fname = ref_tag.fname
            ref_line = ref_tag.line
            if ref_fname not in self.location:
                return None
            for lines, def_tag in self.location[ref_fname].items():
                if lines[0] <= ref_line[0] and ref_line[1] <= lines[1]:
                    if categories and def_tag.category not in categories:
                        continue
                    return def_tag
            return None
        
        G = nx.MultiDiGraph()
        
        
        # Add edges for references
        tags_ref = [tag for tag in tags if tag.kind == 'ref']
        tags_def = [tag for tag in tags if tag.kind == 'def']
        tags_class = [tag for tag in tags if tag.category == 'class']
        tags_function = [tag for tag in tags if tag.category == 'function']
        tags_field = [tag for tag in tags if tag.category == 'field']
        tags_interface = [tag for tag in tags if tag.category == 'interface']
        
        # Add nodes
        for tag in tqdm(tags_def, desc="Adding definition nodes"):
            G.add_node(tag)
        
        # Add edges
        for tag in tqdm(tags_function, desc="Adding function-class edges"):
            tgt_tag = find_def_tag(tag, ['class', 'interface', 'enum'])
            if tgt_tag:
                G.add_edge(tgt_tag, tag, rel='defines_function')
            else:
                if self.language == 'java':
                    raise ValueError(f"Missing class definition for function {tag.name}")
        
        for tag in tqdm(tags_field, desc="Adding field-class edges"):
            tgt_tag = find_def_tag(tag, ['class', 'interface', 'enum'])
            if tgt_tag:
                G.add_edge(tgt_tag, tag, rel='defines_field')
            else:
                if self.language == 'java':
                    raise ValueError(f"Missing class definition for field {tag.name}")
        
        for tag in tqdm(tags_ref, desc="Adding function call edges"):
            src_tag = find_def_tag(tag, ['function', 'field'])
            if src_tag:
                tgt_tags = self.def_tags.get(tag.name, [])
                for tgt_tag in tgt_tags:
                    if tgt_tag != src_tag:
                        G.add_edge(src_tag, tgt_tag, rel='calls')
        
        for tag in tqdm(tags_class, desc="Adding inherits and implements edges"):
            if tag.parent_class:
                for parent_tag in tags_class:
                    if parent_tag.name == tag.parent_class:
                        G.add_edge(tag, parent_tag, rel='inherits')
            if tag.interfaces:
                for interface in tag.interfaces:
                    for interface_tag in tags_interface:
                        if interface_tag.name == interface:
                            G.add_edge(tag, interface_tag, rel='implements')
        return G

    @staticmethod 
    def get_query(lang: str) -> str:
        """Get AST query for specified language"""
        queries = {
            'python': """
                (class_definition 
                    name: (identifier) @name.definition.class
                    bases: (argument_list 
                        (identifier)? @name.inherit.class)?) @definition.class
                (function_definition name: (identifier) @name.definition.function) @definition.function
                (class_definition
                    body: (block 
                        (expression_statement
                            (assignment 
                                left: (identifier) @name.definition.field)))) @definition.class.field
                (call function: [(identifier) @name.reference.call (attribute attribute: (identifier) @name.reference.call)]) @reference.call
            """,
            'java': """
                (interface_declaration 
                    name: (identifier) @name.definition.interface) @definition.interface
                    
                (class_declaration 
                    name: (identifier) @name.definition.class) @definition.class
                
                (enum_declaration
                    name: (identifier) @name.definition.enum) @definition.enum

                (method_declaration 
                    name: (identifier) @name.definition.function) @definition.function
                    
                (constructor_declaration 
                    name: (identifier) @name.definition.constructor) @definition.constructor
                    
                (field_declaration 
                    declarator: (variable_declarator 
                        name: (identifier) @name.definition.field)) @definition.class.field
                        
                (method_invocation 
                    name: (identifier) @name.reference.call) @reference.call
                    
                (object_creation_expression 
                    type: (type_identifier) @name.reference.constructor) @reference.call
            """
        }
        return queries.get(lang, '')


def split_graph(bugInfo: BugInfo, graph: nx.MultiDiGraph, test_failure: TestFailure):
    """Split the graph for each failing test"""
    for test_class in test_failure.test_classes:
        for test_case in test_class.test_cases:
            bugInfo.logger.info(f"[split graph] test case: {bugInfo.project}-{bugInfo.bug_id} {test_case.name}")
            test_cache_dir = get_test_case_dataset_path(bugInfo, test_case)
            test_cache_dir.mkdir(parents=True, exist_ok=True)
            test_graph_file = test_cache_dir / "graph.pkl"
            if test_graph_file.exists():
                with open(test_graph_file, 'rb') as f:
                    test_graph = pickle.load(f)
                print_graph_infos(test_graph, logger=bugInfo.logger)
                continue
            
            # parse instrument file
            run_log_file = test_cache_dir / "run.log"
            coverage_info = parse_coverage(bugInfo, run_log_file)

            # check each node
            test_graph = deepcopy(graph)
            need_remove_nodes = []
            for node in tqdm(test_graph.nodes, desc="Spliting graph"):
                # jump field nodes
                if node.category == 'field':
                    continue
                flag = False
                if node.rel_fname in coverage_info:
                    for start_line, end_line, package, outer_class, inner_class in coverage_info[node.rel_fname]:
                        if node.line[0] <= start_line and end_line <= node.line[1]:
                            flag = True
                            if node.category == 'function':  # update method_id
                                node.outer_class = outer_class
                                node.inner_class = inner_class
                            break
                if not flag:
                    need_remove_nodes.append(node)
            
            test_graph.remove_nodes_from(need_remove_nodes)
            with open(test_graph_file, 'wb') as f:
                pickle.dump(test_graph, f)
            print_graph_infos(test_graph, logger=bugInfo.logger)


def print_graph_infos(G: nx.MultiDiGraph, logger=None):
    """Print graph statistics"""
    if logger:
        logger.info(f"Generated graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
        logger.info(f"function-class edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'defines_function'])}")
        logger.info(f"field-class edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'defines_field'])}")
        logger.info(f"function call edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'calls'])}")
        logger.info(f"inheritance edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'inherits'])}")
        logger.info(f"interface implementation edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'implements'])}")
    else:
        print(f"Generated graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
        print(f"function-class edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'defines_function'])}")
        print(f"field-class edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'defines_field'])}")
        print(f"function call edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'calls'])}")
        print(f"inheritance edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'inherits'])}")
        print(f"interface implementation edges: {len([e for e in G.edges(data=True) if e[2]['rel'] == 'implements'])}")


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_dir", help="Repository directory", default="/home/qyh/projects/FixFL/repograph/Closure-10/src")
    parser.add_argument("--test_dir", help="Test directory", default="/home/qyh/projects/FixFL/repograph/Closure-10/test")
    parser.add_argument("--language", help="Programming language (python/java)", default="java")
    args = parser.parse_args()
    
    if args.language not in CodeGraph.SUPPORTED_LANGS.values():
        raise ValueError(f"Unsupported language: {args.language}")
    
    graph = CodeGraph(args.src_dir, args.test_dir, args.language)
    
    ext = [ext for ext, lang in CodeGraph.SUPPORTED_LANGS.items() if lang == args.language][0]
    src_files = [str(f) for f in Path(args.src_dir).rglob(f'*{ext}')]
    test_files = [str(f) for f in Path(args.test_dir).rglob(f'*{ext}')]
    
    tags, G = graph.get_code_graph(src_files, test_files)
    
    # Save outputs
    output_dir = Path.cwd()
    with open(output_dir / 'graph.pkl', 'wb') as f:
        pickle.dump(G, f)
        
    with open(output_dir / 'tags.jsonl', 'w') as f:
        for tag in tags:
            json.dump(tag._asdict(), f)
            f.write('\n')
            
    print_graph_infos(G)


def create_code_graph(bug_info: BugInfo, language):
    """Programmatic interface"""
    
    graph_file = bug_info.bug_path / "repo_graph.pkl"
    if graph_file.exists():
        with open(graph_file, 'rb') as f:
            G = pickle.load(f)
        print_graph_infos(G, logger=bug_info.logger)
        return G
    
    src_dir = bug_info.buggy_path / bug_info.src_prefix
    test_dir = bug_info.buggy_path / bug_info.test_prefix
    graph = CodeGraph(src_dir, test_dir, language)
    
    ext = [ext for ext, lang in CodeGraph.SUPPORTED_LANGS.items() if lang == language][0]
    src_files = [str(f) for f in Path(src_dir).rglob(f'*{ext}')]
    test_files = [str(f) for f in Path(test_dir).rglob(f'*{ext}')]
    
    tags, G = graph.get_code_graph(src_files, test_files)
    
    with open(graph_file, 'wb') as f:
        pickle.dump(G, f)

    with open(bug_info.bug_path / "tags.jsonl", 'w') as f:
        for tag in tags:
            json.dump(asdict(tag), f)
            f.write('\n')
            
    print_graph_infos(G, logger=bug_info.logger)
    return G


if __name__ == '__main__':
    main()