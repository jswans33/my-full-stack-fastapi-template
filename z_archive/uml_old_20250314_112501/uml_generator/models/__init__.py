"""UML generator model definitions."""

# Re-export models from modules
from .models import (
    AttributeModel,
    ClassModel,
    FileModel,
    FunctionModel,
    ImportModel,
    MethodModel,
    Parameter,
    RelationshipModel,
    Visibility,
)

# Make sequence models available
try:
    from .sequence import (
        ActivationBar,
        ArrowStyle,
        Message,
        Participant,
        ParticipantType,
        SequenceDiagram,
        SequenceGroup,
    )
except ImportError:
    pass  # Sequence models may not be available in all environments

# For backwards compatibility
ParameterModel = Parameter
