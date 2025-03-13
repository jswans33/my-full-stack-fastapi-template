from pathlib import Path

from models import (
    Attribute,
    ClassModel,
    FileModel,
    FunctionModel,
    Import,
    Method,
    Parameter,
    Relationship,
)


def test_parameter():
    # Test required fields
    param = Parameter(name="test", type_annotation="str")
    assert param.name == "test"
    assert param.type_annotation == "str"
    assert param.default_value is None

    # Test with default value
    param_with_default = Parameter(
        name="test",
        type_annotation="str",
        default_value="'default'",
    )
    assert param_with_default.default_value == "'default'"


def test_attribute():
    # Test required fields
    attr = Attribute(name="test", type_annotation="str")
    assert attr.name == "test"
    assert attr.type_annotation == "str"
    assert attr.visibility == "+"  # Default visibility

    # Test with custom visibility
    private_attr = Attribute(name="test", type_annotation="str", visibility="-")
    assert private_attr.visibility == "-"


def test_method_signature():
    # Test without parameters
    method = Method(name="test", parameters=[], return_type="None")
    assert method.signature == "test() -> None"

    # Test with single parameter
    param = Parameter(name="arg", type_annotation="str")
    method = Method(name="test", parameters=[param], return_type="str")
    assert method.signature == "test(arg: str) -> str"

    # Test with multiple parameters and default value
    params = [
        Parameter(name="arg1", type_annotation="str"),
        Parameter(name="arg2", type_annotation="int", default_value="0"),
    ]
    method = Method(name="test", parameters=params, return_type="tuple")
    assert method.signature == "test(arg1: str, arg2: int = 0) -> tuple"

    # Test visibility
    private_method = Method(
        name="test",
        parameters=[],
        return_type="None",
        visibility="-",
    )
    assert private_method.visibility == "-"


def test_relationship():
    rel = Relationship(source="ClassA", target="ClassB", type="-->")
    assert rel.source == "ClassA"
    assert rel.target == "ClassB"
    assert rel.type == "-->"


def test_import():
    # Test required fields
    imp = Import(module="module", name="name")
    assert imp.module == "module"
    assert imp.name == "name"
    assert imp.alias is None

    # Test with alias
    aliased_import = Import(module="module", name="name", alias="alias")
    assert aliased_import.alias == "alias"


def test_class_model():
    # Test minimal class
    cls = ClassModel(name="TestClass", filename="test.py")
    assert cls.name == "TestClass"
    assert cls.filename == "test.py"
    assert cls.bases == []
    assert cls.methods == []
    assert cls.attributes == []
    assert cls.relationships == []
    assert cls.imports == []

    # Test with all fields
    method = Method(name="test", parameters=[], return_type="None")
    attr = Attribute(name="attr", type_annotation="str")
    rel = Relationship(source="TestClass", target="OtherClass", type="-->")
    imp = Import(module="module", name="name")

    cls = ClassModel(
        name="TestClass",
        filename="test.py",
        bases=["BaseClass"],
        methods=[method],
        attributes=[attr],
        relationships=[rel],
        imports=[imp],
    )
    assert cls.bases == ["BaseClass"]
    assert len(cls.methods) == 1
    assert len(cls.attributes) == 1
    assert len(cls.relationships) == 1
    assert len(cls.imports) == 1


def test_function_model_signature():
    # Test without parameters
    func = FunctionModel(name="test", parameters=[], return_type="None")
    assert func.signature == "test() -> None"

    # Test with single parameter
    param = Parameter(name="arg", type_annotation="str")
    func = FunctionModel(name="test", parameters=[param], return_type="str")
    assert func.signature == "test(arg: str) -> str"

    # Test with multiple parameters and default value
    params = [
        Parameter(name="arg1", type_annotation="str"),
        Parameter(name="arg2", type_annotation="int", default_value="0"),
    ]
    func = FunctionModel(name="test", parameters=params, return_type="tuple")
    assert func.signature == "test(arg1: str, arg2: int = 0) -> tuple"


def test_file_model():
    # Test minimal file
    path = Path("test.py")
    file_model = FileModel(path=path)
    assert file_model.path == path
    assert file_model.classes == []
    assert file_model.functions == []
    assert file_model.imports == []
    assert file_model.filename == "test"

    # Test with all fields
    cls = ClassModel(name="TestClass", filename="test.py")
    func = FunctionModel(name="test", parameters=[], return_type="None")
    imp = Import(module="module", name="name")

    file_model = FileModel(
        path=path,
        classes=[cls],
        functions=[func],
        imports=[imp],
    )
    assert len(file_model.classes) == 1
    assert len(file_model.functions) == 1
    assert len(file_model.imports) == 1
    assert file_model.filename == "test"
