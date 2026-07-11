import unittest

from benchmark.routing import ROUTING_REGRESSION_CASES, run_routing_benchmark
from benchmark.routing.cases import (
    PFE_ORAL_QUESTIONS_SUBTASK,
    PYTHON_MCQ_SUBTASK,
    UML_CLASS_DIAGRAM_REVIEW_SUBTASK,
)
from benchmark.routing.models import RoutingBenchmarkCase
from core.interpretation import (
    InterpretationConversionError,
    SignalKind,
    to_routing_request,
    unresolved_signal,
)
from core.routing import (
    RoutingStatus,
    StructuredRoutingEngine,
    build_default_academic_registry,
)
from tests.test_interpretation_validation import candidate, subtask


class CountingEngine:
    def __init__(self) -> None:
        self.calls = 0

    def route(self, request):
        self.calls += 1
        return StructuredRoutingEngine(build_default_academic_registry()).route(request)


class RoutingBenchmarkRunnerTests(unittest.TestCase):
    def engine(self) -> StructuredRoutingEngine:
        return StructuredRoutingEngine(build_default_academic_registry())

    def test_all_builtin_regression_cases_pass(self) -> None:
        summary = run_routing_benchmark(ROUTING_REGRESSION_CASES, self.engine())
        self.assertTrue(summary.success)
        self.assertEqual(summary.passed, summary.total)

    def test_total_passed_failed_success_properties_correct(self) -> None:
        summary = run_routing_benchmark(ROUTING_REGRESSION_CASES, self.engine())
        self.assertEqual(summary.total, len(ROUTING_REGRESSION_CASES))
        self.assertEqual(summary.failed, 0)
        self.assertTrue(summary.success)

    def test_failed_expectation_produces_diagnostic(self) -> None:
        case = RoutingBenchmarkCase(
            identifier="bad",
            description="bad expectation",
            subtask=PYTHON_MCQ_SUBTASK,
            expected_conversion=True,
            expected_status=RoutingStatus.SELECTED,
            expected_capability="uml-analysis",
            tags=("failure",),
        )
        result = run_routing_benchmark((case,), self.engine()).results[0]
        self.assertFalse(result.passed)
        self.assertIn("expected status", result.diagnostic)

    def test_conversion_failure_is_evaluated_correctly(self) -> None:
        case = next(
            item for item in ROUTING_REGRESSION_CASES if item.identifier == "unresolved-project-document"
        )
        result = run_routing_benchmark((case,), self.engine()).results[0]
        self.assertFalse(result.actual_conversion)
        self.assertTrue(result.passed)
        self.assertIs(result.conversion_error_signal, SignalKind.PRIMARY_ARTIFACT)

    def test_conversion_error_signal_uses_structured_exception_data(self) -> None:
        failing_subtask = subtask(
            primary_artifact=unresolved_signal(
                SignalKind.PRIMARY_ARTIFACT,
                candidates=(candidate("PFE report"),),
                basis="Artifact is unresolved.",
            )
        )
        with self.assertRaises(InterpretationConversionError) as context:
            to_routing_request(failing_subtask)
        self.assertIs(context.exception.signal_kind, SignalKind.PRIMARY_ARTIFACT)
        self.assertIn("primary_artifact", str(context.exception))

    def test_runner_does_not_invoke_routing_when_conversion_fails(self) -> None:
        case = next(
            item for item in ROUTING_REGRESSION_CASES if item.identifier == "unresolved-project-document"
        )
        engine = CountingEngine()
        result = run_routing_benchmark((case,), engine).results[0]
        self.assertTrue(result.passed)
        self.assertEqual(engine.calls, 0)

    def test_selected_capability_mismatch_fails(self) -> None:
        case = RoutingBenchmarkCase(
            identifier="mismatch",
            description="capability mismatch",
            subtask=PYTHON_MCQ_SUBTASK,
            expected_conversion=True,
            expected_status=RoutingStatus.SELECTED,
            expected_capability="python-teaching",
            tags=("failure",),
        )
        self.assertFalse(run_routing_benchmark((case,), self.engine()).success)

    def test_status_mismatch_fails(self) -> None:
        case = RoutingBenchmarkCase(
            identifier="status-mismatch",
            description="status mismatch",
            subtask=PYTHON_MCQ_SUBTASK,
            expected_conversion=True,
            expected_status=RoutingStatus.NO_MATCH,
            tags=("failure",),
        )
        self.assertFalse(run_routing_benchmark((case,), self.engine()).success)

    def test_candidate_mismatch_fails(self) -> None:
        registry_engine = self.engine()
        case = RoutingBenchmarkCase(
            identifier="candidate-mismatch",
            description="candidate mismatch",
            subtask=subtask(),
            expected_conversion=True,
            expected_status=RoutingStatus.AMBIGUOUS,
            expected_candidates=("a", "b"),
            tags=("failure",),
        )
        self.assertFalse(run_routing_benchmark((case,), registry_engine).success)

    def test_compound_subtasks_route_independently(self) -> None:
        cases = tuple(
            RoutingBenchmarkCase(
                identifier=f"compound-{index}",
                description="compound subtask",
                subtask=subtask_item,
                expected_conversion=True,
                expected_status=RoutingStatus.SELECTED,
                expected_capability=expected,
                tags=("compound",),
            )
            for index, (subtask_item, expected) in enumerate(
                (
                    (PYTHON_MCQ_SUBTASK, "exam-generation"),
                    (UML_CLASS_DIAGRAM_REVIEW_SUBTASK, "uml-analysis"),
                    (PFE_ORAL_QUESTIONS_SUBTASK, "exam-generation"),
                )
            )
        )
        self.assertTrue(run_routing_benchmark(cases, self.engine()).success)


if __name__ == "__main__":
    unittest.main()
