import unittest

from core.interpretation import (
    InterpretationCandidate,
    InterpretationConversionError,
    InterpretedSubtask,
    SignalKind,
    SignalProvenance,
    SignalProvenanceKind,
    absent_signal,
    resolved_signal,
    to_routing_request,
    unresolved_signal,
)
from core.routing import RoutingRequest


def provenance(
    kind: SignalProvenanceKind = SignalProvenanceKind.EXPLICIT_USER_STATEMENT,
    source: str = "current user utterance",
) -> SignalProvenance:
    return SignalProvenance(kind=kind, source=source)


def candidate(
    value: str,
    *,
    source: str = "current user utterance",
    kind: SignalProvenanceKind = SignalProvenanceKind.EXPLICIT_USER_STATEMENT,
) -> InterpretationCandidate:
    return InterpretationCandidate(
        value=value,
        basis=f"{value} is a possible interpretation.",
        provenance=(provenance(kind=kind, source=source),),
    )


def resolved(kind: SignalKind, value: str):
    return resolved_signal(
        kind,
        value,
        provenance=(provenance(),),
        basis=f"{value} was provided explicitly.",
    )


def absent(kind: SignalKind):
    return absent_signal(kind)


def subtask(
    *,
    user_objective=None,
    primary_artifact=None,
    requested_output=None,
    domain=None,
    explicit_capability=None,
) -> InterpretedSubtask:
    return InterpretedSubtask(
        identifier="task-1",
        user_objective=user_objective
        or resolved(SignalKind.USER_OBJECTIVE, "Create assessment questions"),
        primary_artifact=primary_artifact or absent(SignalKind.PRIMARY_ARTIFACT),
        requested_output=requested_output or absent(SignalKind.REQUESTED_OUTPUT),
        domain=domain or absent(SignalKind.DOMAIN),
        explicit_capability=explicit_capability
        or absent(SignalKind.EXPLICIT_CAPABILITY),
    )


class RoutingConversionTests(unittest.TestCase):
    def test_fully_resolved_python_mcq_interpretation_converts(self) -> None:
        request = to_routing_request(
            subtask(
                requested_output=resolved(SignalKind.REQUESTED_OUTPUT, "MCQ"),
                domain=resolved(SignalKind.DOMAIN, "Python"),
            )
        )
        self.assertEqual(
            request,
            RoutingRequest(
                user_objective="Create assessment questions",
                primary_artifact=None,
                requested_output="MCQ",
                domain="Python",
                explicit_capability=None,
            ),
        )

    def test_pfe_oral_questions_conversion_preserves_artifact_and_output(self) -> None:
        request = to_routing_request(
            subtask(
                user_objective=resolved(SignalKind.USER_OBJECTIVE, "Create oral questions"),
                primary_artifact=resolved(SignalKind.PRIMARY_ARTIFACT, "PFE report"),
                requested_output=resolved(SignalKind.REQUESTED_OUTPUT, "oral questions"),
            )
        )
        self.assertEqual(request.primary_artifact, "PFE report")
        self.assertEqual(request.requested_output, "oral questions")

    def test_absent_optional_signal_becomes_none(self) -> None:
        request = to_routing_request(subtask())
        self.assertIsNone(request.primary_artifact)
        self.assertIsNone(request.requested_output)
        self.assertIsNone(request.domain)
        self.assertIsNone(request.explicit_capability)

    def test_unresolved_primary_artifact_blocks_conversion(self) -> None:
        with self.assertRaises(InterpretationConversionError):
            to_routing_request(
                subtask(
                    primary_artifact=unresolved_signal(
                        SignalKind.PRIMARY_ARTIFACT,
                        candidates=(candidate("PFE report"), candidate("academic specification")),
                        basis="Project document is ambiguous.",
                    )
                )
            )

    def test_unresolved_requested_output_blocks_conversion(self) -> None:
        with self.assertRaises(InterpretationConversionError):
            to_routing_request(
                subtask(
                    requested_output=unresolved_signal(
                        SignalKind.REQUESTED_OUTPUT,
                        candidates=(candidate("feedback"), candidate("oral questions")),
                        basis="Requested output is ambiguous.",
                    )
                )
            )

    def test_unresolved_domain_blocks_conversion(self) -> None:
        with self.assertRaises(InterpretationConversionError):
            to_routing_request(
                subtask(
                    domain=unresolved_signal(
                        SignalKind.DOMAIN,
                        candidates=(candidate("Python"), candidate("UML")),
                        basis="Domain is ambiguous.",
                    )
                )
            )

    def test_unresolved_explicit_capability_blocks_conversion(self) -> None:
        with self.assertRaises(InterpretationConversionError):
            to_routing_request(
                subtask(
                    explicit_capability=unresolved_signal(
                        SignalKind.EXPLICIT_CAPABILITY,
                        candidates=(candidate("uml-analysis"), candidate("exam-generation")),
                        basis="Capability alias is ambiguous.",
                    )
                )
            )

    def test_unresolved_user_objective_blocks_conversion(self) -> None:
        with self.assertRaises(InterpretationConversionError):
            to_routing_request(
                subtask(
                    user_objective=unresolved_signal(
                        SignalKind.USER_OBJECTIVE,
                        candidates=(candidate("review"), candidate("generate")),
                        basis="Objective is ambiguous.",
                    )
                )
            )

    def test_conversion_error_identifies_signal_kind(self) -> None:
        with self.assertRaisesRegex(InterpretationConversionError, "primary_artifact"):
            to_routing_request(
                subtask(
                    primary_artifact=unresolved_signal(
                        SignalKind.PRIMARY_ARTIFACT,
                        candidates=(candidate("PFE report"),),
                        basis="Artifact is ambiguous.",
                    )
                )
            )

    def test_unknown_explicit_capability_value_preserved_unchanged(self) -> None:
        request = to_routing_request(
            subtask(
                explicit_capability=resolved(
                    SignalKind.EXPLICIT_CAPABILITY,
                    "quantum-professor",
                )
            )
        )
        self.assertEqual(request.explicit_capability, "quantum-professor")

    def test_conversion_does_not_invoke_routing(self) -> None:
        request = to_routing_request(
            subtask(
                explicit_capability=resolved(
                    SignalKind.EXPLICIT_CAPABILITY,
                    "quantum-professor",
                )
            )
        )
        self.assertIsInstance(request, RoutingRequest)

    def test_conversion_does_not_normalize_mcq(self) -> None:
        request = to_routing_request(
            subtask(requested_output=resolved(SignalKind.REQUESTED_OUTPUT, "mcq"))
        )
        self.assertEqual(request.requested_output, "mcq")

    def test_compound_result_subtasks_can_be_converted_independently(self) -> None:
        first = subtask(requested_output=resolved(SignalKind.REQUESTED_OUTPUT, "MCQ"))
        second = subtask(
            primary_artifact=resolved(SignalKind.PRIMARY_ARTIFACT, "PFE report"),
            requested_output=resolved(SignalKind.REQUESTED_OUTPUT, "oral questions"),
        )
        self.assertEqual(to_routing_request(first).requested_output, "MCQ")
        self.assertEqual(to_routing_request(second).primary_artifact, "PFE report")


class CollisionRegressionTests(unittest.TestCase):
    def test_python_mcq_conversion(self) -> None:
        request = to_routing_request(
            subtask(
                requested_output=resolved(SignalKind.REQUESTED_OUTPUT, "MCQ"),
                domain=resolved(SignalKind.DOMAIN, "Python"),
            )
        )
        self.assertEqual(request.requested_output, "MCQ")
        self.assertEqual(request.domain, "Python")

    def test_class_diagram_architecture_wording_does_not_create_capability(self) -> None:
        request = to_routing_request(
            subtask(
                user_objective=resolved(
                    SignalKind.USER_OBJECTIVE,
                    "Review modeling coherence",
                ),
                primary_artifact=resolved(SignalKind.PRIMARY_ARTIFACT, "class diagram"),
                domain=resolved(SignalKind.DOMAIN, "UML"),
            )
        )
        self.assertIsNone(request.explicit_capability)

    def test_pfe_oral_questions_conversion(self) -> None:
        request = to_routing_request(
            subtask(
                user_objective=resolved(SignalKind.USER_OBJECTIVE, "Create oral questions"),
                primary_artifact=resolved(SignalKind.PRIMARY_ARTIFACT, "PFE report"),
                requested_output=resolved(SignalKind.REQUESTED_OUTPUT, "oral questions"),
            )
        )
        self.assertEqual(request.primary_artifact, "PFE report")
        self.assertEqual(request.requested_output, "oral questions")

    def test_unresolved_project_document_does_not_choose_first_candidate(self) -> None:
        with self.assertRaises(InterpretationConversionError):
            to_routing_request(
                subtask(
                    user_objective=resolved(SignalKind.USER_OBJECTIVE, "Review artifact"),
                    primary_artifact=unresolved_signal(
                        SignalKind.PRIMARY_ARTIFACT,
                        candidates=(
                            candidate("PFE report"),
                            candidate("academic specification"),
                        ),
                        basis="Project document does not identify one artifact type.",
                    ),
                )
            )

    def test_user_described_uml_vs_observed_python_blocks_conversion(self) -> None:
        with self.assertRaises(InterpretationConversionError):
            to_routing_request(
                subtask(
                    primary_artifact=unresolved_signal(
                        SignalKind.PRIMARY_ARTIFACT,
                        candidates=(
                            candidate("UML diagram"),
                            candidate(
                                "Python student code",
                                source="direct artifact inspection",
                                kind=SignalProvenanceKind.DIRECT_ARTIFACT_INSPECTION,
                            ),
                        ),
                        basis="Artifact description conflicts with observed content.",
                        conflict=(
                            "Explicit artifact description conflicts with observed "
                            "artifact characteristics."
                        ),
                    )
                )
            )

    def test_unknown_explicit_capability_conversion_succeeds(self) -> None:
        request = to_routing_request(
            subtask(
                explicit_capability=resolved(
                    SignalKind.EXPLICIT_CAPABILITY,
                    "quantum-professor",
                )
            )
        )
        self.assertEqual(request.explicit_capability, "quantum-professor")


if __name__ == "__main__":
    unittest.main()
