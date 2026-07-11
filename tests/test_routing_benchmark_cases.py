import unittest

from benchmark.routing.cases import ROUTING_REGRESSION_CASES
from core.interpretation import InterpretationState, SignalKind


class RoutingBenchmarkCasesTests(unittest.TestCase):
    def case_by_id(self, identifier: str):
        return {case.identifier: case for case in ROUTING_REGRESSION_CASES}[identifier]

    def test_identifiers_unique(self) -> None:
        identifiers = [case.identifier for case in ROUTING_REGRESSION_CASES]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_required_benchmark_identifiers_exist(self) -> None:
        identifiers = {case.identifier for case in ROUTING_REGRESSION_CASES}
        self.assertTrue(
            {
                "python-mcq",
                "uml-class-diagram-review",
                "pfe-oral-questions",
                "unresolved-project-document",
                "user-described-uml-observed-python",
                "unknown-explicit-capability",
                "lowercase-mcq",
                "compound-python-mcq",
                "compound-uml-review",
                "compound-pfe-oral",
            }.issubset(identifiers)
        )

    def test_every_case_has_tags(self) -> None:
        for case in ROUTING_REGRESSION_CASES:
            with self.subTest(case=case.identifier):
                self.assertTrue(case.tags)

    def test_every_signal_has_correct_kind(self) -> None:
        for case in ROUTING_REGRESSION_CASES:
            task = case.subtask
            with self.subTest(case=case.identifier):
                self.assertIs(task.user_objective.kind, SignalKind.USER_OBJECTIVE)
                self.assertIs(task.primary_artifact.kind, SignalKind.PRIMARY_ARTIFACT)
                self.assertIs(task.requested_output.kind, SignalKind.REQUESTED_OUTPUT)
                self.assertIs(task.domain.kind, SignalKind.DOMAIN)
                self.assertIs(
                    task.explicit_capability.kind,
                    SignalKind.EXPLICIT_CAPABILITY,
                )

    def test_unresolved_collision_cases_preserve_all_candidates(self) -> None:
        project = self.case_by_id("unresolved-project-document")
        conflict = self.case_by_id("user-described-uml-observed-python")
        self.assertEqual(project.subtask.primary_artifact.state, InterpretationState.UNRESOLVED)
        self.assertEqual(
            [candidate.value for candidate in project.subtask.primary_artifact.candidates],
            ["PFE report", "academic specification"],
        )
        self.assertEqual(
            [candidate.value for candidate in conflict.subtask.primary_artifact.candidates],
            ["UML diagram", "Python student code"],
        )

    def test_uml_collision_expected_owner_is_not_architecture_review(self) -> None:
        case = self.case_by_id("uml-class-diagram-review")
        self.assertEqual(case.expected_capability, "uml-analysis")
        self.assertNotEqual(case.expected_capability, "architecture-review")

    def test_unknown_capability_case_preserves_value(self) -> None:
        case = self.case_by_id("unknown-explicit-capability")
        self.assertEqual(case.subtask.explicit_capability.value, "quantum-professor")

    def test_lowercase_mcq_case_preserves_lowercase_value(self) -> None:
        case = self.case_by_id("lowercase-mcq")
        self.assertEqual(case.subtask.requested_output.value, "mcq")


if __name__ == "__main__":
    unittest.main()
