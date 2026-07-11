"""Dataclass ontology primitives for ARF RFC concepts.

Mappings:
- EvidenceReference and EvidenceItem -> RFC-0002 evidence model.
- Claim -> RFC-0002 claim-to-evidence relationship.
- FeedbackItem -> RFC-0003 feedback contract.
- ConfidenceAssessment -> RFC-0004 confidence model.
- RoutingTrace -> RFC-0005 routing model.

These models implement structural validation only. They do not implement full
RFC conformance, evidence sufficiency, AI reasoning, routing execution, or
model-specific behavior.
"""

from dataclasses import dataclass

from core.ontology.enums import (
    ConfidenceLabel,
    ConfidenceState,
    EvidenceCategory,
    FindingKind,
    Severity,
)
from core.ontology.validation import (
    OntologyValidationError,
    reject_percentage_confidence,
    require_non_empty,
)


@dataclass(frozen=True)
class EvidenceReference:
    """RFC-0002 evidence reference."""

    source: str
    locator: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.source, "source")


@dataclass(frozen=True)
class EvidenceItem:
    """RFC-0002 evidence item with local structural invariants."""

    identifier: str
    category: EvidenceCategory
    reference: EvidenceReference
    scope: str
    provenance: str
    limitations: tuple[str, ...] = ()
    derived_from: tuple[str, ...] = ()
    transformation: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.identifier, "identifier")
        require_non_empty(self.scope, "scope")
        require_non_empty(self.provenance, "provenance")
        if self.category is EvidenceCategory.DERIVED_EVIDENCE:
            if not self.derived_from:
                raise OntologyValidationError(
                    "derived_from is required for DERIVED_EVIDENCE"
                )
            require_non_empty(self.transformation, "transformation")


@dataclass(frozen=True)
class Claim:
    """RFC-0002 claim that may reference evidence items."""

    identifier: str
    text: str
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_non_empty(self.identifier, "identifier")
        require_non_empty(self.text, "text")


@dataclass(frozen=True)
class ConfidenceAssessment:
    """RFC-0004 confidence label or non-confidence state for one target."""

    target_id: str
    label: ConfidenceLabel | None = None
    state: ConfidenceState | None = None
    basis: str | None = None
    boundary: str | None = None
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_non_empty(self.target_id, "target_id")
        reject_percentage_confidence(self.basis, "basis")

        has_label = self.label is not None
        has_state = self.state is not None
        if has_label == has_state:
            raise OntologyValidationError(
                "exactly one of label or state must be set"
            )
        if has_label:
            require_non_empty(self.basis, "basis")


@dataclass(frozen=True)
class FeedbackItem:
    """RFC-0003 feedback item with structural validation."""

    identifier: str
    target: str
    finding: str
    finding_kind: FindingKind
    evidence_summary: str | None
    impact: str | None
    recommendation: str | None
    alternatives: tuple[str, ...] = ()
    severity: Severity = Severity.INFORMATIONAL
    confidence: ConfidenceAssessment | None = None
    limitations: tuple[str, ...] = ()
    priority: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.identifier, "identifier")
        if self.finding_kind is FindingKind.POSITIVE_FINDING:
            require_non_empty(self.target, "target")
            require_non_empty(self.finding, "finding")
            require_non_empty(self.evidence_summary, "evidence_summary")
            return

        require_non_empty(self.target, "target")
        require_non_empty(self.finding, "finding")
        if self.finding_kind is FindingKind.DEMONSTRATED_ERROR:
            require_non_empty(self.evidence_summary, "evidence_summary")


@dataclass(frozen=True)
class RoutingTrace:
    """RFC-0005 externally reviewable routing trace."""

    user_objective: str
    primary_artifact: str | None
    requested_output: str | None
    primary_capability: str | None
    supporting_capabilities: tuple[str, ...] = ()
    decisive_signals: tuple[str, ...] = ()
    negative_boundaries_evaluated: tuple[str, ...] = ()
    material_ambiguity: str | None = None
    revision_trigger: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.user_objective, "user_objective")
        if self.primary_capability is None:
            require_non_empty(self.material_ambiguity, "material_ambiguity")
        else:
            require_non_empty(self.primary_capability, "primary_capability")

        seen: set[str] = set()
        for capability in self.supporting_capabilities:
            require_non_empty(capability, "supporting_capabilities")
            if capability == self.primary_capability:
                raise OntologyValidationError(
                    "supporting_capabilities must not contain primary_capability"
                )
            if capability in seen:
                raise OntologyValidationError(
                    f"duplicate supporting capability: {capability}"
                )
            seen.add(capability)
