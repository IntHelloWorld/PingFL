from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import networkx as nx

from interfaces.method_extractor import JMethod


@dataclass
class Tag():
    """Represents a code element tag"""
    rel_fname: str
    fname: str 
    line: Tuple[int, int]
    name: str
    kind: str  # 'def' or 'ref'
    category: str  # 'class', 'function', 'field', 'interface', or 'enum'
    code: str
    pkg_name: str = None
    parent_class: str = None
    interfaces: Tuple[str] = ()
    is_test: bool = False
    
    # these fields are for methods, they will be filled after instrumentation
    outer_class: str = None
    inner_class: str = None
    
    def __hash__(self):
        return hash((self.rel_fname, self.line, self.name, self.kind, self.category))
    
    @property
    def method_id(self):
        if self.category != 'function':
            return None
        if self.inner_class:
            return f'{self.pkg_name}.{self.outer_class}.{self.inner_class}.{self.name}#{self.line[0]}-{self.line[1]}'
        return f'{self.pkg_name}.{self.outer_class}.{self.name}#{self.line[0]}-{self.line[1]}'
    
    @property
    def method_pos(self):
        if self.category != 'function':
            return None
        if self.inner_class:
            return f'{self.inner_class}.{self.name}#{self.line[0]}-{self.line[1]}'
        return f'{self.name}#{self.line[0]}-{self.line[1]}'


@dataclass
class TestCase:
    name: str
    test_method: Optional[JMethod] = None
    test_output: Optional[str] = None
    stack_trace: Optional[str] = None
    test_class_name: Optional[str] = None
    test_method_name: Optional[str] = None
    
    def __str__(self) -> str:
        return self.name
    
    def __post_init__(self):
        self.test_class_name, self.test_method_name = self.name.split("::")


@dataclass
class TestClass:
    name: str 
    test_cases: List[TestCase]
    
    def __str__(self) -> str:
        return f"{self.name}: {str(self.test_cases)}"


@dataclass
class TestFailure:
    project: str
    bug_ID: int
    test_classes: List[TestClass]
    buggy_methods: Optional[List[JMethod]] = None


@dataclass
class DebugInput:
    test_name: str
    test_code: str
    error_message: str
    test_graph: nx.Graph
    output_path: Path


@dataclass
class SearchInput:
    test_name: str
    test_code: str
    error_message: str
    experience: str


@dataclass
class SearchResult:
    error_analysis: str
    method_id: str


@dataclass
class VerifyInput:
    bug_name: str
    test_name: str
    test_code: str
    error_message: str
    method_id: str
    hypotheses: str
    method_code: str
    output_dir: Path
    method: Tag


@dataclass
class VerifyResult:
    method_id: str
    is_buggy: bool
    explanation: str


@dataclass
class RoundResult:
    search_results: List[SearchResult]
    verify_results: List[VerifyResult]
