"""Built-in routing regression cases built from interpretation objects."""

from core.interpretation import (
    InterpretationCandidate,
    InterpretationResult,
    InterpretedSubtask,
    SignalKind,
    SignalProvenance,
    SignalProvenanceKind,
    absent_signal,
    resolved_signal,
    unresolved_signal,
)
from core.routing import RoutingStatus

from benchmark.routing.models import RoutingBenchmarkCase


USER = SignalProvenance(
    kind=SignalProvenanceKind.EXPLICIT_USER_STATEMENT,
    source="current user utterance",
)
INSPECTION = SignalProvenance(
    kind=SignalProvenanceKind.DIRECT_ARTIFACT_INSPECTION,
    source="direct artifact inspection",
)
STRUCTURED = SignalProvenance(
    kind=SignalProvenanceKind.TRUSTED_STRUCTURED_CALLER,
    source="benchmark structured fixture",
)


def _resolved(kind: SignalKind, value: str) -> object:
    return resolved_signal(
        kind,
        value,
        provenance=(USER,),
        basis=f"{value} is supplied as a structured benchmark signal.",
    )


def _absent(kind: SignalKind) -> object:
    return absent_signal(kind)


def _candidate(value: str, provenance: SignalProvenance = USER) -> InterpretationCandidate:
    return InterpretationCandidate(
        value=value,
        basis=f"{value} is represented as a benchmark candidate.",
        provenance=(provenance,),
    )


def _subtask(
    identifier: str,
    *,
    objective,
    artifact=None,
    output=None,
    domain=None,
    explicit=None,
) -> InterpretedSubtask:
    return InterpretedSubtask(
        identifier=identifier,
        user_objective=objective,
        primary_artifact=artifact or _absent(SignalKind.PRIMARY_ARTIFACT),
        requested_output=output or _absent(SignalKind.REQUESTED_OUTPUT),
        domain=domain or _absent(SignalKind.DOMAIN),
        explicit_capability=explicit or _absent(SignalKind.EXPLICIT_CAPABILITY),
    )


PYTHON_MCQ_SUBTASK = _subtask(
    "python-mcq",
    objective=_resolved(SignalKind.USER_OBJECTIVE, "Create assessment questions"),
    output=_resolved(SignalKind.REQUESTED_OUTPUT, "MCQ"),
    domain=_resolved(SignalKind.DOMAIN, "Python"),
)

UML_CLASS_DIAGRAM_REVIEW_SUBTASK = _subtask(
    "uml-class-diagram-review",
    objective=_resolved(SignalKind.USER_OBJECTIVE, "Review modeling coherence"),
    artifact=_resolved(SignalKind.PRIMARY_ARTIFACT, "class diagram"),
    domain=_resolved(SignalKind.DOMAIN, "UML"),
)

PFE_ORAL_QUESTIONS_SUBTASK = _subtask(
    "pfe-oral-questions",
    objective=_resolved(SignalKind.USER_OBJECTIVE, "Create oral questions"),
    artifact=_resolved(SignalKind.PRIMARY_ARTIFACT, "PFE report"),
    output=_resolved(SignalKind.REQUESTED_OUTPUT, "oral questions"),
)

COMPOUND_INTERPRETATION = InterpretationResult(
    subtasks=(
        PYTHON_MCQ_SUBTASK,
        UML_CLASS_DIAGRAM_REVIEW_SUBTASK,
        PFE_ORAL_QUESTIONS_SUBTASK,
    )
)


ROUTING_REGRESSION_CASES: tuple[RoutingBenchmarkCase, ...] = (
    RoutingBenchmarkCase(
        identifier="python-mcq",
        description="Structured Python MCQ request routes by requested output.",
        subtask=PYTHON_MCQ_SUBTASK,
        expected_conversion=True,
        expected_status=RoutingStatus.SELECTED,
        expected_capability="exam-generation",
        tags=("collision", "assessment", "python"),
    ),
    RoutingBenchmarkCase(
        identifier="uml-class-diagram-review",
        description="Architecture wording with class diagram routes to UML analysis.",
        subtask=UML_CLASS_DIAGRAM_REVIEW_SUBTASK,
        expected_conversion=True,
        expected_status=RoutingStatus.SELECTED,
        expected_capability="uml-analysis",
        tags=("collision", "uml", "architecture-wording"),
    ),
    RoutingBenchmarkCase(
        identifier="pfe-oral-questions",
        description="PFE source with oral question output routes by requested output.",
        subtask=PFE_ORAL_QUESTIONS_SUBTASK,
        expected_conversion=True,
        expected_status=RoutingStatus.SELECTED,
        expected_capability="exam-generation",
        tags=("collision", "pfe", "oral"),
    ),
    RoutingBenchmarkCase(
        identifier="unresolved-project-document",
        description="Ambiguous project document blocks conversion.",
        subtask=_subtask(
            "unresolved-project-document",
            objective=_resolved(SignalKind.USER_OBJECTIVE, "Review artifact"),
            artifact=unresolved_signal(
                SignalKind.PRIMARY_ARTIFACT,
                candidates=(
                    _candidate("PFE report"),
                    _candidate("academic specification"),
                ),
                basis="Project document does not resolve one artifact type.",
            ),
        ),
        expected_conversion=False,
        expected_conversion_error_signal=SignalKind.PRIMARY_ARTIFACT,
        tags=("unresolved", "artifact"),
    ),
    RoutingBenchmarkCase(
        identifier="user-described-uml-observed-python",
        description="Explicit UML description conflicts with observed Python source.",
        subtask=_subtask(
            "user-described-uml-observed-python",
            objective=_resolved(SignalKind.USER_OBJECTIVE, "Review artifact"),
            artifact=unresolved_signal(
                SignalKind.PRIMARY_ARTIFACT,
                candidates=(
                    _candidate("UML diagram", USER),
                    _candidate("Python student code", INSPECTION),
                ),
                basis="User-described artifact conflicts with inspected content.",
                conflict=(
                    "Explicit artifact description conflicts with observed "
                    "artifact characteristics."
                ),
            ),
        ),
        expected_conversion=False,
        expected_conversion_error_signal=SignalKind.PRIMARY_ARTIFACT,
        tags=("conflict", "provenance", "artifact"),
    ),
    RoutingBenchmarkCase(
        identifier="unknown-explicit-capability",
        description="Unknown explicit capability is preserved through conversion.",
        subtask=_subtask(
            "unknown-explicit-capability",
            objective=_resolved(SignalKind.USER_OBJECTIVE, "Review artifact"),
            explicit=_resolved(SignalKind.EXPLICIT_CAPABILITY, "quantum-professor"),
        ),
        expected_conversion=True,
        expected_status=RoutingStatus.NO_MATCH,
        tags=("explicit-capability", "unknown-capability"),
    ),
    RoutingBenchmarkCase(
        identifier="lowercase-mcq",
        description="Interpretation preserves lowercase output; router normalizes it.",
        subtask=_subtask(
            "lowercase-mcq",
            objective=_resolved(SignalKind.USER_OBJECTIVE, "Create assessment questions"),
            output=_resolved(SignalKind.REQUESTED_OUTPUT, "mcq"),
            domain=_resolved(SignalKind.DOMAIN, "Python"),
        ),
        expected_conversion=True,
        expected_status=RoutingStatus.SELECTED,
        expected_capability="exam-generation",
        tags=("normalization", "boundary"),
    ),
    RoutingBenchmarkCase(
        identifier="compound-python-mcq",
        description="First compound subtask routes independently.",
        subtask=COMPOUND_INTERPRETATION.subtasks[0],
        expected_conversion=True,
        expected_status=RoutingStatus.SELECTED,
        expected_capability="exam-generation",
        tags=("compound", "subtasks"),
    ),
    RoutingBenchmarkCase(
        identifier="compound-uml-review",
        description="Second compound subtask routes independently.",
        subtask=COMPOUND_INTERPRETATION.subtasks[1],
        expected_conversion=True,
        expected_status=RoutingStatus.SELECTED,
        expected_capability="uml-analysis",
        tags=("compound", "subtasks"),
    ),
    RoutingBenchmarkCase(
        identifier="compound-pfe-oral",
        description="Third compound subtask routes independently.",
        subtask=COMPOUND_INTERPRETATION.subtasks[2],
        expected_conversion=True,
        expected_status=RoutingStatus.SELECTED,
        expected_capability="exam-generation",
        tags=("compound", "subtasks"),
    ),
)
