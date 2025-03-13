from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path

@dataclass
class Parameter:
    """Function/method parameter representation."""
    name: str
    type_annotation: str
    default_value: Optional[str] = None

@dataclass
class Attribute:
    """Class attribute representation."""
    name: str
    type_annotation: str
    visibility: str = "+"  # +: public, -: private, #: protected

@dataclass
class Method:
    """Method representation with signature information."""
    name: str
    parameters: List[Parameter]
    return_type: str
    visibility: str = "+"  # +: public, -: private, #: protected
    
    @property
    def signature(self) -> str:
        """Generate method signature string."""
        params = [
            f"{param.name}: {param.type_annotation}" +
            (f" = {param.default_value}" if param.default_value else "")
            for param in self.parameters
        ]
        return f"{self.name}({', '.join(params)}) -> {self.return_type}"

@dataclass
class Relationship:
    """Relationship between classes."""
    source: str
    target: str
    type: str  # -->: association, *-->: composition, etc.

@dataclass
class Import:
    """Import statement representation."""
    module: str
    name: str
    alias: Optional[str] = None

@dataclass
class ClassModel:
    """Class representation with methods, attributes and relationships."""
    name: str
    filename: str
    bases: List[str] = field(default_factory=list)
    methods: List[Method] = field(default_factory=list)
    attributes: List[Attribute] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    imports: List[Import] = field(default_factory=list)

@dataclass
class FunctionModel:
    """Standalone function representation."""
    name: str
    parameters: List[Parameter]
    return_type: str
    visibility: str = "+"
    
    @property
    def signature(self) -> str:
        """Generate function signature string."""
        params = [
            f"{param.name}: {param.type_annotation}" +
            (f" = {param.default_value}" if param.default_value else "")
            for param in self.parameters
        ]
        return f"{self.name}({', '.join(params)}) -> {self.return_type}"

@dataclass
class FileModel:
    """File representation containing classes and functions."""
    path: Path
    classes: List[ClassModel] = field(default_factory=list)
    functions: List[FunctionModel] = field(default_factory=list)
    imports: List[Import] = field(default_factory=list)
    
    @property
    def filename(self) -> str:
        """Get filename without extension."""
        return self.path.stem
