"""Validation helpers for ARF ontology primitives.

Validation uses a deliberate hybrid pattern:
- dataclass ``__post_init__`` methods enforce local structural invariants;
- explicit functions validate cross-reference invariants that require a graph
  or collection context.

The validators do not evaluate evidence relevance, evidence sufficiency, or
reasoning quality. Those require higher-level ARF behavior outside this
ontology layer.
"""

from collections.abc import Iterable
import re
from typing import Any


class OntologyValidationError(ValueError):
    """Raised when an ontology object violates a structural invariant."""


_PERCENT_CONFIDENCE_RE = re.compile(r"\b\d{1,3}%\s+confident\b", re.IGNORECASE)


def require_non_empty(value: str | None, field_name: str) -> None:
    """Reject missing or blank string fields."""

    if value is None or not value.strip():
        raise OntologyValidationError(f"{field_name} cannot be blank")


def reject_percentage_confidence(text: str | None, field_name: str) -> None:
    """Reject obvious uncalibrated percentage-confidence phrasing."""

    if text and _PERCENT_CONFIDENCE_RE.search(text):
        raise OntologyValidationError(
            f"{field_name} must not contain uncalibrated percentage confidence"
        )


def validate_evidence_graph(evidence_items: Iterable[Any]) -> None:
    """Validate evidence identifier uniqueness and derived-evidence references."""

    items = list(evidence_items)
    by_id: dict[str, Any] = {}

    for item in items:
        if item.identifier in by_id:
            raise OntologyValidationError(
                f"evidence identifier is duplicated: {item.identifier}"
            )
        by_id[item.identifier] = item

    graph: dict[str, tuple[str, ...]] = {}
    for item in items:
        graph[item.identifier] = tuple(item.derived_from)
        for source_id in item.derived_from:
            if source_id not in by_id:
                raise OntologyValidationError(
                    f"derived_from references unknown evidence id: {source_id}"
                )
            if source_id == item.identifier:
                raise OntologyValidationError(
                    f"evidence item cannot derive from itself: {item.identifier}"
                )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visited:
            return
        if identifier in visiting:
            raise OntologyValidationError(
                f"derived evidence cycle detected at: {identifier}"
            )
        visiting.add(identifier)
        for source_id in graph[identifier]:
            visit(source_id)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in graph:
        visit(identifier)


def validate_claim_references(claims: Iterable[Any], evidence_items: Iterable[Any]) -> None:
    """Validate claim IDs and claim-to-evidence references."""

    evidence_ids = {item.identifier for item in evidence_items}
    seen_claim_ids: set[str] = set()

    for claim in claims:
        if claim.identifier in seen_claim_ids:
            raise OntologyValidationError(
                f"claim identifier is duplicated: {claim.identifier}"
            )
        seen_claim_ids.add(claim.identifier)

        seen_evidence_ids: set[str] = set()
        for evidence_id in claim.evidence_ids:
            if evidence_id in seen_evidence_ids:
                raise OntologyValidationError(
                    f"claim {claim.identifier} has duplicate evidence id: {evidence_id}"
                )
            seen_evidence_ids.add(evidence_id)
            if evidence_id not in evidence_ids:
                raise OntologyValidationError(
                    f"claim {claim.identifier} references unknown evidence id: {evidence_id}"
                )


def validate_feedback_item(
    item: Any,
    *,
    require_impact: bool = False,
    require_recommendation: bool = False,
) -> None:
    """Validate optional feedback constraints that require caller context."""

    if require_impact:
        require_non_empty(item.impact, "impact")
    if require_recommendation:
        require_non_empty(item.recommendation, "recommendation")
