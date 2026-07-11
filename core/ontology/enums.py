"""Normative ontology enumerations.

Mappings:
- EvidenceCategory -> RFC-0002 evidence categories E1-E4.
- FindingKind and Severity -> RFC-0003 feedback contract.
- ConfidenceLabel and ConfidenceState -> RFC-0004 confidence model.

These enums are structural primitives only. They do not implement full RFC
conformance or any reasoning behavior.
"""

from enum import Enum


class EvidenceCategory(str, Enum):
    """RFC-0002 evidence item categories."""

    DIRECT_OBSERVATION = "direct_observation"
    EXECUTION_RESULT = "execution_result"
    MEASUREMENT = "measurement"
    DERIVED_EVIDENCE = "derived_evidence"


class FindingKind(str, Enum):
    """RFC-0003 feedback finding categories."""

    DEMONSTRATED_ERROR = "demonstrated_error"
    DEBATABLE_CHOICE = "debatable_choice"
    OPTIONAL_IMPROVEMENT = "optional_improvement"
    HYPOTHESIS = "hypothesis"
    POSITIVE_FINDING = "positive_finding"


class Severity(str, Enum):
    """RFC-0003 qualitative severity labels."""

    BLOCKING = "blocking"
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"
    INFORMATIONAL = "informational"


class ConfidenceLabel(str, Enum):
    """RFC-0004 qualitative confidence support labels."""

    CONFIRMED = "confirmed"
    STRONGLY_SUPPORTED = "strongly_supported"
    SUPPORTED = "supported"
    PLAUSIBLE = "plausible"
    SPECULATIVE = "speculative"


class ConfidenceState(str, Enum):
    """RFC-0004 non-confidence states.

    These states are intentionally separate from ConfidenceLabel.
    """

    UNKNOWN = "unknown"
    NOT_ASSESSED = "not_assessed"
