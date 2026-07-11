"""Deterministic structured routing engine for RFC-0005 signals.

The engine consumes already-structured request fields. It does not parse
free-form prose, execute contextual yield-rule text, compute scores, use
embeddings, or call a model.
"""

from dataclasses import dataclass
from enum import Enum

from core.ontology import RoutingTrace
from core.routing.registry import (
    CapabilityDefinition,
    CapabilityRegistry,
    validate_registry_references,
)


class RoutingEngineError(ValueError):
    """Raised when structured routing objects violate local invariants."""


class RoutingStatus(str, Enum):
    """Qualitative routing outcome status."""

    SELECTED = "selected"
    AMBIGUOUS = "ambiguous"
    NO_MATCH = "no_match"


def _require_non_empty(value: str | None, field_name: str) -> None:
    if value is None or not value.strip():
        raise RoutingEngineError(f"{field_name} cannot be blank")


def _normalize(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().casefold()


def _dedupe(values: tuple[str, ...], field_name: str) -> None:
    seen: set[str] = set()
    for value in values:
        _require_non_empty(value, field_name)
        if value in seen:
            raise RoutingEngineError(f"{field_name} contains duplicate value: {value}")
        seen.add(value)


@dataclass(frozen=True)
class RoutingRequest:
    """Already-structured routing request signals."""

    user_objective: str
    primary_artifact: str | None = None
    requested_output: str | None = None
    domain: str | None = None
    explicit_capability: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.user_objective, "user_objective")
        for field_name in (
            "primary_artifact",
            "requested_output",
            "domain",
            "explicit_capability",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_non_empty(value, field_name)


@dataclass(frozen=True)
class RoutingDecision:
    """Structured routing result plus externally reviewable trace."""

    trace: RoutingTrace
    considered_capabilities: tuple[str, ...]
    rejected_capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _dedupe(self.considered_capabilities, "considered_capabilities")
        _dedupe(self.rejected_capabilities, "rejected_capabilities")
        considered = set(self.considered_capabilities)
        for rejected in self.rejected_capabilities:
            if rejected not in considered:
                raise RoutingEngineError(
                    f"rejected capability was not considered: {rejected}"
                )
        primary = self.trace.primary_capability
        if primary is not None and primary not in considered:
            raise RoutingEngineError(
                f"primary capability was not considered: {primary}"
            )


class StructuredRoutingEngine:
    """Apply deterministic ownership rules to structured routing signals."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        validate_registry_references(registry)
        self._registry = registry

    def route(self, request: RoutingRequest) -> RoutingDecision:
        capabilities = tuple(self._registry)
        considered = tuple(capability.identifier for capability in capabilities)
        output_owners = self._owners_by_output(capabilities, request.requested_output)
        artifact_owners = self._owners_by_artifact(capabilities, request.primary_artifact)
        domain_supporters = self._supporters_by_domain(capabilities, request.domain)

        primary: str | None = None
        supporting: list[str] = []
        decisive_signals: list[str] = []
        negative_boundaries: list[str] = []
        ambiguity: str | None = None
        rejected: list[str] = []

        explicit = request.explicit_capability
        if explicit is not None:
            if not self._registry.contains(explicit):
                ambiguity = f"Explicit capability is unknown: {explicit}."
                decisive_signals.append("Unknown explicit capability preserved ambiguity.")
            else:
                explicit_capability = self._registry.get(explicit)
                output_conflict = (
                    len(output_owners) == 1 and output_owners[0].identifier != explicit
                )
                artifact_conflict = (
                    len(output_owners) == 0
                    and len(artifact_owners) == 1
                    and artifact_owners[0].identifier != explicit
                )
                if output_conflict:
                    owner = output_owners[0]
                    primary = owner.identifier
                    rejected.append(explicit)
                    decisive_signals.append(
                        f"Explicit capability {explicit} was inapplicable; requested output is owned by {owner.identifier}."
                    )
                    negative_boundaries.extend(
                        self._matching_negative_boundaries(explicit_capability, owner.identifier)
                    )
                elif artifact_conflict:
                    owner = artifact_owners[0]
                    primary = owner.identifier
                    rejected.append(explicit)
                    decisive_signals.append(
                        f"Explicit capability {explicit} was inapplicable; primary artifact is owned by {owner.identifier}."
                    )
                    negative_boundaries.extend(
                        self._matching_negative_boundaries(explicit_capability, owner.identifier)
                    )
                elif self._capability_has_structural_support(explicit_capability, request):
                    primary = explicit
                    decisive_signals.append(
                        f"Explicit capability {explicit} was supported by structured request signals."
                    )
                elif not self._has_any_structural_signal(request):
                    primary = explicit
                    decisive_signals.append(
                        f"Explicit capability {explicit} was honored with limited applicability evidence."
                    )

        if primary is None and ambiguity is None:
            primary, ambiguity = self._select_from_ownership(
                output_owners,
                artifact_owners,
                domain_supporters,
                decisive_signals,
            )

        if primary is not None:
            self._add_supporting_capabilities(
                primary,
                supporting,
                output_owners,
                artifact_owners,
            )

        if primary is None and ambiguity is None:
            ambiguity = "No unique structured ownership signal was available."

        trace = RoutingTrace(
            user_objective=request.user_objective,
            primary_artifact=request.primary_artifact,
            requested_output=request.requested_output,
            primary_capability=primary,
            supporting_capabilities=tuple(supporting),
            decisive_signals=tuple(decisive_signals),
            negative_boundaries_evaluated=tuple(negative_boundaries),
            material_ambiguity=ambiguity,
        )
        return RoutingDecision(
            trace=trace,
            considered_capabilities=considered,
            rejected_capabilities=tuple(rejected),
        )

    def _owners_by_output(
        self,
        capabilities: tuple[CapabilityDefinition, ...],
        requested_output: str | None,
    ) -> tuple[CapabilityDefinition, ...]:
        output = _normalize(requested_output)
        if output is None:
            return ()
        return tuple(
            capability
            for capability in capabilities
            if output in {_normalize(value) for value in capability.owned_outputs}
        )

    def _owners_by_artifact(
        self,
        capabilities: tuple[CapabilityDefinition, ...],
        primary_artifact: str | None,
    ) -> tuple[CapabilityDefinition, ...]:
        artifact = _normalize(primary_artifact)
        if artifact is None:
            return ()
        return tuple(
            capability
            for capability in capabilities
            if artifact in {_normalize(value) for value in capability.owned_artifacts}
        )

    def _supporters_by_domain(
        self,
        capabilities: tuple[CapabilityDefinition, ...],
        domain: str | None,
    ) -> tuple[CapabilityDefinition, ...]:
        normalized_domain = _normalize(domain)
        if normalized_domain is None:
            return ()
        return tuple(
            capability
            for capability in capabilities
            if normalized_domain in {_normalize(value) for value in capability.supported_domains}
        )

    def _select_from_ownership(
        self,
        output_owners: tuple[CapabilityDefinition, ...],
        artifact_owners: tuple[CapabilityDefinition, ...],
        domain_supporters: tuple[CapabilityDefinition, ...],
        decisive_signals: list[str],
    ) -> tuple[str | None, str | None]:
        if len(output_owners) > 1:
            return None, "Requested output has multiple capability owners."
        if len(output_owners) == 1:
            owner = output_owners[0]
            if len(artifact_owners) == 1 and artifact_owners[0].identifier != owner.identifier:
                decisive_signals.append(
                    f"Requested output owner {owner.identifier} overrides artifact owner {artifact_owners[0].identifier}."
                )
            else:
                decisive_signals.append(
                    f"Requested output is owned by {owner.identifier}."
                )
            return owner.identifier, None

        if len(artifact_owners) > 1:
            return None, "Primary artifact has multiple capability owners."
        if len(artifact_owners) == 1:
            owner = artifact_owners[0]
            decisive_signals.append(f"Primary artifact is owned by {owner.identifier}.")
            return owner.identifier, None

        if len(domain_supporters) > 1:
            return None, "Structured domain has multiple capability supporters."
        if len(domain_supporters) == 1:
            supporter = domain_supporters[0]
            decisive_signals.append(
                f"Structured domain is supported by {supporter.identifier}."
            )
            return supporter.identifier, None

        return None, "No structured ownership signal was available."

    def _add_supporting_capabilities(
        self,
        primary: str,
        supporting: list[str],
        output_owners: tuple[CapabilityDefinition, ...],
        artifact_owners: tuple[CapabilityDefinition, ...],
    ) -> None:
        output_primary = len(output_owners) == 1 and output_owners[0].identifier == primary
        if output_primary and len(artifact_owners) == 1:
            self._append_supporting(supporting, artifact_owners[0].identifier, primary)

    def _append_supporting(
        self,
        supporting: list[str],
        candidate: str,
        primary: str,
    ) -> None:
        if candidate != primary and candidate not in supporting:
            supporting.append(candidate)

    def _capability_has_structural_support(
        self,
        capability: CapabilityDefinition,
        request: RoutingRequest,
    ) -> bool:
        output = _normalize(request.requested_output)
        artifact = _normalize(request.primary_artifact)
        domain = _normalize(request.domain)
        return (
            (output is not None and output in {_normalize(value) for value in capability.owned_outputs})
            or (
                artifact is not None
                and artifact in {_normalize(value) for value in capability.owned_artifacts}
            )
            or (
                domain is not None
                and domain in {_normalize(value) for value in capability.supported_domains}
            )
        )

    def _has_any_structural_signal(self, request: RoutingRequest) -> bool:
        return any(
            value is not None
            for value in (request.primary_artifact, request.requested_output, request.domain)
        )

    def _matching_negative_boundaries(
        self,
        capability: CapabilityDefinition,
        target_capability: str,
    ) -> tuple[str, ...]:
        return tuple(
            boundary
            for boundary in capability.negative_boundaries
            if target_capability in boundary
        )
