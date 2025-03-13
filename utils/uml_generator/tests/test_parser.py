"""Tests for Python AST parser."""

import textwrap
from pathlib import Path

import pytest

from ..interfaces import FileSystem
from ..models import (
    Visibility,
)
from ..parsers.python_parser import PythonAstParser


class MockFileSystem(FileSystem):
    """Mock file system for testing."""

    def __init__(self, files: dict[str, str]):
        self.files = files

    def read_file(self, path: Path) -> str:
        return self.files.get(str(path), "")

    def write_file(self, path: Path, content: str) -> None:
        self.files[str(path)] = content

    def ensure_directory(self, path: Path) -> None:
        pass


@pytest.fixture
def parser():
    """Create parser instance with mock filesystem."""
    return PythonAstParser(MockFileSystem({}))


def test_parse_simple_class(parser):
    """Test parsing a simple class definition."""
    code = textwrap.dedent("""
        class SimpleClass:
            x: int
            y: str = "test"
            
            def method(self, arg: int) -> str:
                return str(arg)
    """)

    model = parser.parse_file(Path("test.py"))
    assert len(model.classes) == 1

    cls = model.classes[0]
    assert cls.name == "SimpleClass"
    assert len(cls.attributes) == 2
    assert len(cls.methods) == 1

    # Check attributes
    attrs = {attr.name: attr for attr in cls.attributes}
    assert attrs["x"].type_annotation == "int"
    assert attrs["y"].type_annotation == "str"

    # Check method
    method = cls.methods[0]
    assert method.name == "method"
    assert method.return_type == "str"
    assert len(method.parameters) == 2  # self + arg
    assert method.parameters[1].name == "arg"
    assert method.parameters[1].type_annotation == "int"


def test_parse_inheritance(parser):
    """Test parsing class inheritance."""
    code = textwrap.dedent("""
        class Base:
            pass
            
        class Child(Base):
            pass
    """)

    model = parser.parse_file(Path("test.py"))
    assert len(model.classes) == 2

    child = next(c for c in model.classes if c.name == "Child")
    assert len(child.bases) == 1
    assert child.bases[0] == "Base"


def test_parse_relationships(parser):
    """Test parsing class relationships."""
    code = textwrap.dedent("""
        class User:
            pass
            
        class Post:
            author: User
            comments: List[Comment]
            tags: Optional[List[Tag]]
    """)

    model = parser.parse_file(Path("test.py"))
    post = next(c for c in model.classes if c.name == "Post")

    # Check relationships
    rels = {(r.source, r.target): r.type for r in post.relationships}
    assert ("Post", "User") in rels
    assert rels[("Post", "User")] == "-->"
    assert ("Post", "Comment") in rels
    assert rels[("Post", "Comment")] == "*-->"


def test_parse_visibility(parser):
    """Test parsing member visibility."""
    code = textwrap.dedent("""
        class TestClass:
            public_attr: int
            _protected_attr: str
            __private_attr: bool
            
            def public_method(self):
                pass
                
            def _protected_method(self):
                pass
                
            def __private_method(self):
                pass
    """)

    model = parser.parse_file(Path("test.py"))
    cls = model.classes[0]

    # Check attribute visibility
    attrs = {attr.name: attr.visibility for attr in cls.attributes}
    assert attrs["public_attr"] == Visibility.PUBLIC
    assert attrs["_protected_attr"] == Visibility.PROTECTED
    assert attrs["__private_attr"] == Visibility.PRIVATE

    # Check method visibility
    methods = {method.name: method.visibility for method in cls.methods}
    assert methods["public_method"] == Visibility.PUBLIC
    assert methods["_protected_method"] == Visibility.PROTECTED
    assert methods["__private_method"] == Visibility.PRIVATE


def test_parse_imports(parser):
    """Test parsing import statements."""
    code = textwrap.dedent("""
        import os
        import sys as system
        from typing import List, Optional
        from .models import User as UserModel
    """)

    model = parser.parse_file(Path("test.py"))
    imports = {(imp.module, imp.name): imp.alias for imp in model.imports}

    assert ("os", "os") in imports
    assert imports[("sys", "sys")] == "system"
    assert ("typing.List", "List") in imports
    assert ("typing.Optional", "Optional") in imports
    assert (".models.User", "User") in imports
    assert imports[(".models.User", "User")] == "UserModel"


def test_parse_module_functions(parser):
    """Test parsing module-level functions."""
    code = textwrap.dedent("""
        def simple_function(x: int) -> str:
            return str(x)
            
        async def async_function(y: str, *args: int, **kwargs: dict) -> None:
            pass
    """)

    model = parser.parse_file(Path("test.py"))
    assert len(model.functions) == 2

    funcs = {f.name: f for f in model.functions}

    # Check simple function
    simple = funcs["simple_function"]
    assert simple.return_type == "str"
    assert len(simple.parameters) == 1
    assert simple.parameters[0].name == "x"
    assert simple.parameters[0].type_annotation == "int"

    # Check async function with *args and **kwargs
    async_func = funcs["async_function"]
    assert async_func.return_type == "None"
    params = {p.name: p for p in async_func.parameters}
    assert "y" in params
    assert "*args" in params
    assert "**kwargs" in params
    assert params["*args"].type_annotation == "int"
    assert params["**kwargs"].type_annotation == "dict"
