import unittest

from core.interpretation import (
    InterpretationCandidate,
    InterpretationResult,
    InterpretationState,
    InterpretationValidationError,
    InterpretedSignal,
    InterpretedSubtask,
    SignalKind,
    SignalProvenance,
    SignalProvenanceKind,
    absent_signal,
    resolved_signal,
    unresolved_signal,
)
from core.ontology import ConfidenceState


def provenance(source: str = "current user utterance") -> SignalProvenance:
    return SignalProvenance(
        kind=SignalProvenanceKind.EXPLICIT_USER_STATEMENT,
        source=source,
    )


def candidate(value: str = "PFE report") -> InterpretationCandidate:
    return InterpretationCandidate(
        value=value,
        basis=f"{value} was stated as a possible artifact.",
        provenance=(provenance(),),
    )


def resolved(kind: SignalKind, value: str) -> InterpretedSignal:
    return resolved_signal(
        kind,
        value,
        provenance=(provenance(),),
        basis=f"{value} was explicitly provided.",
    )


def absent(kind: SignalKind) -> InterpretedSignal:
    return absent_signal(kind)


def valid_subtask(identifier: str = "task-1") -> InterpretedSubtask:
    return InterpretedSubtask(
        identifier=identifier,
        user_objective=resolved(SignalKind.USER_OBJECTIVE, "Review artifact"),
        primary_artifact=absent(SignalKind.PRIMARY_ARTIFACT),
        requested_output=absent(SignalKind.REQUESTED_OUTPUT),
        domain=absent(SignalKind.DOMAIN),
        explicit_capability=absent(SignalKind.EXPLICIT_CAPABILITY),
    )


def subtask_values(identifier: str = "task-1") -> dict[str, object]:
    task = valid_subtask(identifier)
    return {
        "identifier": task.identifier,
        "user_objective": task.user_objective,
        "primary_artifact": task.primary_artifact,
        "requested_output": task.requested_output,
        "domain": task.domain,
        "explicit_capability": task.explicit_capability,
    }


class InterpretationEnumTests(unittest.TestCase):
    def test_exact_interpretation_state_members(self) -> None:
        self.assertEqual(
            [(member.name, member.value) for member in InterpretationState],
            [
                ("RESOLVED", "resolved"),
                ("UNRESOLVED", "unresolved"),
                ("ABSENT", "absent"),
            ],
        )

    def test_no_unknown_state(self) -> None:
        self.assertNotIn("UNKNOWN", [member.name for member in InterpretationState])

    def test_interpretation_state_separate_from_confidence_state(self) -> None:
        self.assertNotIsInstance(InterpretationState.UNRESOLVED, ConfidenceState)

    def test_exact_signal_kind_members(self) -> None:
        self.assertEqual(
            [(member.name, member.value) for member in SignalKind],
            [
                ("USER_OBJECTIVE", "user_objective"),
                ("PRIMARY_ARTIFACT", "primary_artifact"),
                ("REQUESTED_OUTPUT", "requested_output"),
                ("DOMAIN", "domain"),
                ("EXPLICIT_CAPABILITY", "explicit_capability"),
            ],
        )

    def test_exact_provenance_kind_members(self) -> None:
        self.assertEqual(
            [(member.name, member.value) for member in SignalProvenanceKind],
            [
                ("EXPLICIT_USER_STATEMENT", "explicit_user_statement"),
                ("TRUSTED_STRUCTURED_CALLER", "trusted_structured_caller"),
                ("CONNECTOR_ARTIFACT_TYPE", "connector_artifact_type"),
                ("DIRECT_ARTIFACT_INSPECTION", "direct_artifact_inspection"),
                ("ARTIFACT_METADATA", "artifact_metadata"),
                ("CONVERSATION_CONTEXT", "conversation_context"),
                ("DERIVED_INTERPRETATION", "derived_interpretation"),
            ],
        )


class SignalProvenanceTests(unittest.TestCase):
    def test_valid_provenance(self) -> None:
        item = SignalProvenance(
            kind=SignalProvenanceKind.CONVERSATION_CONTEXT,
            source="conversation turn 12",
            detail="User clarified the artifact.",
        )
        self.assertEqual(item.source, "conversation turn 12")

    def test_blank_source_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            SignalProvenance(kind=SignalProvenanceKind.ARTIFACT_METADATA, source=" ")

    def test_blank_optional_detail_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            SignalProvenance(
                kind=SignalProvenanceKind.ARTIFACT_METADATA,
                source="attachment metadata",
                detail=" ",
            )


class InterpretationCandidateTests(unittest.TestCase):
    def test_valid_candidate(self) -> None:
        item = candidate("academic specification")
        self.assertEqual(item.value, "academic specification")

    def test_blank_value_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretationCandidate(value=" ", basis="basis", provenance=(provenance(),))

    def test_blank_basis_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretationCandidate(value="PFE report", basis=" ", provenance=(provenance(),))

    def test_no_provenance_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretationCandidate(value="PFE report", basis="basis", provenance=())

    def test_duplicate_provenance_rejected(self) -> None:
        item = provenance()
        with self.assertRaises(InterpretationValidationError):
            InterpretationCandidate(
                value="PFE report",
                basis="basis",
                provenance=(item, item),
            )

    def test_blank_limitation_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretationCandidate(
                value="PFE report",
                basis="basis",
                provenance=(provenance(),),
                limitations=(" ",),
            )

    def test_duplicate_limitation_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretationCandidate(
                value="PFE report",
                basis="basis",
                provenance=(provenance(),),
                limitations=("not inspected", "not inspected"),
            )


class ResolvedSignalTests(unittest.TestCase):
    def test_valid_resolved_signal(self) -> None:
        signal = resolved(SignalKind.REQUESTED_OUTPUT, "MCQ")
        self.assertEqual(signal.state, InterpretationState.RESOLVED)

    def test_missing_value_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.REQUESTED_OUTPUT,
                state=InterpretationState.RESOLVED,
                provenance=(provenance(),),
                basis="basis",
            )

    def test_blank_value_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            resolved(SignalKind.REQUESTED_OUTPUT, " ")

    def test_missing_provenance_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.REQUESTED_OUTPUT,
                state=InterpretationState.RESOLVED,
                value="MCQ",
                basis="basis",
            )

    def test_missing_basis_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.REQUESTED_OUTPUT,
                state=InterpretationState.RESOLVED,
                value="MCQ",
                provenance=(provenance(),),
            )

    def test_candidates_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.PRIMARY_ARTIFACT,
                state=InterpretationState.RESOLVED,
                value="PFE report",
                candidates=(candidate(),),
                provenance=(provenance(),),
                basis="basis",
            )


class UnresolvedSignalTests(unittest.TestCase):
    def test_valid_unresolved_signal_with_candidates(self) -> None:
        signal = unresolved_signal(
            SignalKind.PRIMARY_ARTIFACT,
            candidates=(candidate("PFE report"), candidate("academic specification")),
            basis="The phrase project document is ambiguous.",
        )
        self.assertEqual(signal.state, InterpretationState.UNRESOLVED)

    def test_valid_unresolved_signal_with_conflict_only(self) -> None:
        signal = unresolved_signal(
            SignalKind.PRIMARY_ARTIFACT,
            basis="User statement conflicts with observed content.",
            conflict="Explicit UML description conflicts with Python source.",
        )
        self.assertEqual(signal.conflict, "Explicit UML description conflicts with Python source.")

    def test_resolved_value_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.PRIMARY_ARTIFACT,
                state=InterpretationState.UNRESOLVED,
                value="PFE report",
                candidates=(candidate(),),
                basis="basis",
            )

    def test_no_candidate_and_no_conflict_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            unresolved_signal(SignalKind.PRIMARY_ARTIFACT, basis="basis")

    def test_missing_basis_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.PRIMARY_ARTIFACT,
                state=InterpretationState.UNRESOLVED,
                candidates=(candidate(),),
            )

    def test_several_competing_candidates_accepted(self) -> None:
        signal = unresolved_signal(
            SignalKind.PRIMARY_ARTIFACT,
            candidates=(
                candidate("PFE report"),
                candidate("academic specification"),
                candidate("thesis"),
            ),
            basis="Project document is not specific enough.",
        )
        self.assertEqual(len(signal.candidates), 3)


class AbsentSignalTests(unittest.TestCase):
    def test_valid_absent_signal(self) -> None:
        signal = absent(SignalKind.DOMAIN)
        self.assertEqual(signal.state, InterpretationState.ABSENT)

    def test_value_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.DOMAIN,
                state=InterpretationState.ABSENT,
                value="Python",
            )

    def test_candidates_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.DOMAIN,
                state=InterpretationState.ABSENT,
                candidates=(candidate("Python"),),
            )

    def test_provenance_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.DOMAIN,
                state=InterpretationState.ABSENT,
                provenance=(provenance(),),
            )

    def test_basis_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.DOMAIN,
                state=InterpretationState.ABSENT,
                basis="basis",
            )

    def test_conflict_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSignal(
                kind=SignalKind.DOMAIN,
                state=InterpretationState.ABSENT,
                conflict="conflict",
            )

    def test_limitation_explaining_unavailable_context_accepted(self) -> None:
        signal = absent_signal(
            SignalKind.PRIMARY_ARTIFACT,
            limitations=("No artifact was attached.",),
        )
        self.assertEqual(signal.limitations, ("No artifact was attached.",))


class InterpretedSubtaskTests(unittest.TestCase):
    def test_valid_single_subtask(self) -> None:
        task = valid_subtask()
        self.assertEqual(task.identifier, "task-1")

    def test_mismatched_user_objective_kind_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                identifier="task-1",
                user_objective=resolved(SignalKind.DOMAIN, "Python"),
                primary_artifact=absent(SignalKind.PRIMARY_ARTIFACT),
                requested_output=absent(SignalKind.REQUESTED_OUTPUT),
                domain=absent(SignalKind.DOMAIN),
                explicit_capability=absent(SignalKind.EXPLICIT_CAPABILITY),
            )

    def test_mismatched_artifact_kind_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                identifier="task-1",
                user_objective=resolved(SignalKind.USER_OBJECTIVE, "Review"),
                primary_artifact=absent(SignalKind.DOMAIN),
                requested_output=absent(SignalKind.REQUESTED_OUTPUT),
                domain=absent(SignalKind.DOMAIN),
                explicit_capability=absent(SignalKind.EXPLICIT_CAPABILITY),
            )

    def test_mismatched_output_kind_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                identifier="task-1",
                user_objective=resolved(SignalKind.USER_OBJECTIVE, "Review"),
                primary_artifact=absent(SignalKind.PRIMARY_ARTIFACT),
                requested_output=absent(SignalKind.DOMAIN),
                domain=absent(SignalKind.DOMAIN),
                explicit_capability=absent(SignalKind.EXPLICIT_CAPABILITY),
            )

    def test_mismatched_domain_kind_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                identifier="task-1",
                user_objective=resolved(SignalKind.USER_OBJECTIVE, "Review"),
                primary_artifact=absent(SignalKind.PRIMARY_ARTIFACT),
                requested_output=absent(SignalKind.REQUESTED_OUTPUT),
                domain=absent(SignalKind.REQUESTED_OUTPUT),
                explicit_capability=absent(SignalKind.EXPLICIT_CAPABILITY),
            )

    def test_mismatched_explicit_capability_kind_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                identifier="task-1",
                user_objective=resolved(SignalKind.USER_OBJECTIVE, "Review"),
                primary_artifact=absent(SignalKind.PRIMARY_ARTIFACT),
                requested_output=absent(SignalKind.REQUESTED_OUTPUT),
                domain=absent(SignalKind.DOMAIN),
                explicit_capability=absent(SignalKind.DOMAIN),
            )

    def test_blank_identifier_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            valid_subtask(identifier=" ")

    def test_duplicate_limitations_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                **subtask_values(),
                limitations=("limited", "limited"),
            )

    def test_duplicate_ambiguities_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                **subtask_values(),
                material_ambiguities=("ambiguous", "ambiguous"),
            )

    def test_duplicate_clarification_needs_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                **subtask_values(),
                clarification_needs=("Which artifact?", "Which artifact?"),
            )

    def test_unresolved_signal_does_not_require_clarification_need(self) -> None:
        task = InterpretedSubtask(
            identifier="task-1",
            user_objective=resolved(SignalKind.USER_OBJECTIVE, "Review artifact"),
            primary_artifact=unresolved_signal(
                SignalKind.PRIMARY_ARTIFACT,
                candidates=(candidate("PFE report"), candidate("academic specification")),
                basis="Project document is ambiguous.",
            ),
            requested_output=absent(SignalKind.REQUESTED_OUTPUT),
            domain=absent(SignalKind.DOMAIN),
            explicit_capability=absent(SignalKind.EXPLICIT_CAPABILITY),
        )
        self.assertEqual(task.clarification_needs, ())

    def test_blank_revision_trigger_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretedSubtask(
                **subtask_values(),
                revision_trigger=" ",
            )


class InterpretationResultTests(unittest.TestCase):
    def test_one_subtask_accepted(self) -> None:
        result = InterpretationResult(subtasks=(valid_subtask(),))
        self.assertEqual(len(result.subtasks), 1)

    def test_compound_request_with_three_subtasks_accepted(self) -> None:
        result = InterpretationResult(
            subtasks=(
                valid_subtask("review"),
                valid_subtask("architecture"),
                valid_subtask("questions"),
            )
        )
        self.assertEqual(len(result.subtasks), 3)

    def test_no_subtasks_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretationResult(subtasks=())

    def test_duplicate_subtask_identifiers_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretationResult(subtasks=(valid_subtask("same"), valid_subtask("same")))

    def test_duplicate_interaction_limitations_rejected(self) -> None:
        with self.assertRaises(InterpretationValidationError):
            InterpretationResult(
                subtasks=(valid_subtask(),),
                interaction_limitations=("limited", "limited"),
            )


if __name__ == "__main__":
    unittest.main()
