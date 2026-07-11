"""Machine-readable structural primitives for RFC-0006 interpretation."""

from dataclasses import dataclass

from core.interpretation.enums import (
    InterpretationState,
    SignalKind,
    SignalProvenanceKind,
)
from core.interpretation.validation import (
    InterpretationConversionError,
    InterpretationValidationError,
    require_non_empty,
    validate_string_tuple,
    validate_unique_identifiers,
    validate_unique_items,
)
from core.routing import RoutingRequest


@dataclass(frozen=True)
class SignalProvenance:
    """Source provenance for one interpretation signal or candidate."""

    kind: SignalProvenanceKind
    source: str
    detail: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.source, "source")
        if self.detail is not None:
            require_non_empty(self.detail, "detail")


@dataclass(frozen=True)
class InterpretationCandidate:
    """Candidate value that may support an unresolved or resolved signal."""

    value: str
    basis: str
    provenance: tuple[SignalProvenance, ...]
    limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        require_non_empty(self.value, "value")
        require_non_empty(self.basis, "basis")
        if not self.provenance:
            raise InterpretationValidationError(
                "provenance requires at least one item"
            )
        validate_unique_items(self.provenance, "provenance")
        validate_string_tuple(self.limitations, "limitations")


@dataclass(frozen=True)
class InterpretedSignal:
    """One interpreted RFC-0006 signal."""

    kind: SignalKind
    state: InterpretationState
    value: str | None = None
    candidates: tuple[InterpretationCandidate, ...] = ()
    provenance: tuple[SignalProvenance, ...] = ()
    basis: str | None = None
    limitations: tuple[str, ...] = ()
    conflict: str | None = None

    def __post_init__(self) -> None:
        validate_unique_items(self.provenance, "provenance")
        validate_unique_items(self.candidates, "candidates")
        validate_string_tuple(self.limitations, "limitations")
        if self.value is not None:
            require_non_empty(self.value, "value")
        if self.basis is not None:
            require_non_empty(self.basis, "basis")
        if self.conflict is not None:
            require_non_empty(self.conflict, "conflict")

        if self.state is InterpretationState.RESOLVED:
            self._validate_resolved()
        elif self.state is InterpretationState.UNRESOLVED:
            self._validate_unresolved()
        elif self.state is InterpretationState.ABSENT:
            self._validate_absent()

    def _validate_resolved(self) -> None:
        require_non_empty(self.value, "value")
        if not self.provenance:
            raise InterpretationValidationError(
                "resolved signal requires provenance"
            )
        require_non_empty(self.basis, "basis")
        if self.candidates:
            raise InterpretationValidationError(
                "resolved signal must not contain candidates"
            )

    def _validate_unresolved(self) -> None:
        if self.value is not None:
            raise InterpretationValidationError(
                "unresolved signal must not contain a resolved value"
            )
        require_non_empty(self.basis, "basis")
        if not self.candidates and self.conflict is None:
            raise InterpretationValidationError(
                "unresolved signal requires candidates or conflict"
            )

    def _validate_absent(self) -> None:
        if self.value is not None:
            raise InterpretationValidationError(
                "absent signal must not contain a value"
            )
        if self.candidates:
            raise InterpretationValidationError(
                "absent signal must not contain candidates"
            )
        if self.provenance:
            raise InterpretationValidationError(
                "absent signal must not contain provenance"
            )
        if self.basis is not None:
            raise InterpretationValidationError(
                "absent signal must not contain basis"
            )
        if self.conflict is not None:
            raise InterpretationValidationError(
                "absent signal must not contain conflict"
            )


@dataclass(frozen=True)
class InterpretedSubtask:
    """One independently interpretable RFC-0006 subtask."""

    identifier: str
    user_objective: InterpretedSignal
    primary_artifact: InterpretedSignal
    requested_output: InterpretedSignal
    domain: InterpretedSignal
    explicit_capability: InterpretedSignal
    limitations: tuple[str, ...] = ()
    material_ambiguities: tuple[str, ...] = ()
    clarification_needs: tuple[str, ...] = ()
    revision_trigger: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.identifier, "identifier")
        self._require_signal_kind(self.user_objective, SignalKind.USER_OBJECTIVE)
        self._require_signal_kind(self.primary_artifact, SignalKind.PRIMARY_ARTIFACT)
        self._require_signal_kind(self.requested_output, SignalKind.REQUESTED_OUTPUT)
        self._require_signal_kind(self.domain, SignalKind.DOMAIN)
        self._require_signal_kind(
            self.explicit_capability,
            SignalKind.EXPLICIT_CAPABILITY,
        )
        validate_string_tuple(self.limitations, "limitations")
        validate_string_tuple(self.material_ambiguities, "material_ambiguities")
        validate_string_tuple(self.clarification_needs, "clarification_needs")
        if self.revision_trigger is not None:
            require_non_empty(self.revision_trigger, "revision_trigger")

    def _require_signal_kind(
        self,
        signal: InterpretedSignal,
        expected: SignalKind,
    ) -> None:
        if signal.kind is not expected:
            raise InterpretationValidationError(
                f"{expected.value} signal has mismatched kind: {signal.kind.value}"
            )


@dataclass(frozen=True)
class InterpretationResult:
    """A complete interpretation result with one or more subtasks."""

    subtasks: tuple[InterpretedSubtask, ...]
    interaction_limitations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.subtasks:
            raise InterpretationValidationError(
                "subtasks requires at least one item"
            )
        validate_unique_identifiers(self.subtasks, "subtasks")
        validate_string_tuple(
            self.interaction_limitations,
            "interaction_limitations",
        )


def to_routing_request(subtask: InterpretedSubtask) -> RoutingRequest:
    """Strictly convert a fully routable subtask into ``RoutingRequest``."""

    objective = _required_resolved_value(subtask.user_objective)
    return RoutingRequest(
        user_objective=objective,
        primary_artifact=_optional_routing_value(subtask.primary_artifact),
        requested_output=_optional_routing_value(subtask.requested_output),
        domain=_optional_routing_value(subtask.domain),
        explicit_capability=_optional_routing_value(subtask.explicit_capability),
    )


def _required_resolved_value(signal: InterpretedSignal) -> str:
    if signal.state is not InterpretationState.RESOLVED:
        raise InterpretationConversionError(
            signal.kind,
            f"{signal.kind.value} must be resolved before routing conversion"
        )
    if signal.value is None:
        raise InterpretationConversionError(
            signal.kind,
            f"{signal.kind.value} resolved signal has no value"
        )
    return signal.value


def _optional_routing_value(signal: InterpretedSignal) -> str | None:
    if signal.state is InterpretationState.RESOLVED:
        if signal.value is None:
            raise InterpretationConversionError(
                signal.kind,
                f"{signal.kind.value} resolved signal has no value"
            )
        return signal.value
    if signal.state is InterpretationState.ABSENT:
        return None
    raise InterpretationConversionError(
        signal.kind,
        f"{signal.kind.value} is unresolved and cannot be silently omitted"
    )


def resolved_signal(
    kind: SignalKind,
    value: str,
    *,
    provenance: tuple[SignalProvenance, ...],
    basis: str,
    limitations: tuple[str, ...] = (),
    conflict: str | None = None,
) -> InterpretedSignal:
    """Construct a resolved signal without inferring or parsing content."""

    return InterpretedSignal(
        kind=kind,
        state=InterpretationState.RESOLVED,
        value=value,
        provenance=provenance,
        basis=basis,
        limitations=limitations,
        conflict=conflict,
    )


def unresolved_signal(
    kind: SignalKind,
    *,
    candidates: tuple[InterpretationCandidate, ...] = (),
    provenance: tuple[SignalProvenance, ...] = (),
    basis: str,
    limitations: tuple[str, ...] = (),
    conflict: str | None = None,
) -> InterpretedSignal:
    """Construct an unresolved signal without choosing a candidate."""

    return InterpretedSignal(
        kind=kind,
        state=InterpretationState.UNRESOLVED,
        candidates=candidates,
        provenance=provenance,
        basis=basis,
        limitations=limitations,
        conflict=conflict,
    )


def absent_signal(
    kind: SignalKind,
    *,
    limitations: tuple[str, ...] = (),
) -> InterpretedSignal:
    """Construct an absent signal."""

    return InterpretedSignal(
        kind=kind,
        state=InterpretationState.ABSENT,
        limitations=limitations,
    )
