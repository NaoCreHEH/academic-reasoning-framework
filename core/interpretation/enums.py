"""RFC-0006 interpretation enumerations."""

from enum import Enum


class InterpretationState(str, Enum):
    """Three-state interpretation signal status."""

    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    ABSENT = "absent"


class SignalKind(str, Enum):
    """Structured signal kinds consumed by routing requests."""

    USER_OBJECTIVE = "user_objective"
    PRIMARY_ARTIFACT = "primary_artifact"
    REQUESTED_OUTPUT = "requested_output"
    DOMAIN = "domain"
    EXPLICIT_CAPABILITY = "explicit_capability"


class SignalProvenanceKind(str, Enum):
    """Kinds of provenance that may support interpretation signals."""

    EXPLICIT_USER_STATEMENT = "explicit_user_statement"
    TRUSTED_STRUCTURED_CALLER = "trusted_structured_caller"
    CONNECTOR_ARTIFACT_TYPE = "connector_artifact_type"
    DIRECT_ARTIFACT_INSPECTION = "direct_artifact_inspection"
    ARTIFACT_METADATA = "artifact_metadata"
    CONVERSATION_CONTEXT = "conversation_context"
    DERIVED_INTERPRETATION = "derived_interpretation"
