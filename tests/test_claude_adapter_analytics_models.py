from pathlib import Path
import unittest

from benchmark.adapters.claude_code.enums import ClaudeEvaluationStatus
from benchmark.adapters.claude_code.analytics.enums import (
    BehavioralEligibility,
    CaseOutcomeCategory,
    RunUsabilityStatus,
)
from benchmark.adapters.claude_code.analytics.models import (
    AnalyticsValidationError,
    CaseStabilitySummary,
    ParsedCaseRunResult,
    ParsedLiveRun,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "claude_adapter_analytics"


class ClaudeAdapterAnalyticsModelTests(unittest.TestCase):
    def test_exact_run_usability_values(self):
        self.assertEqual(RunUsabilityStatus.USABLE.value, "usable")
        self.assertEqual(RunUsabilityStatus.DEGRADED.value, "degraded")
        self.assertEqual(RunUsabilityStatus.UNUSABLE.value, "unusable")

    def test_exact_behavioral_eligibility_values(self):
        self.assertEqual(BehavioralEligibility.ELIGIBLE.value, "eligible")
        self.assertEqual(
            BehavioralEligibility.INELIGIBLE_INFRASTRUCTURE.value,
            "ineligible_infrastructure",
        )
        self.assertEqual(
            BehavioralEligibility.INELIGIBLE_UNAVAILABLE.value,
            "ineligible_unavailable",
        )

    def test_case_outcome_values_are_snake_case(self):
        for category in CaseOutcomeCategory:
            self.assertEqual(category.value, category.value.lower())
            self.assertNotIn("-", category.value)
            self.assertNotIn(" ", category.value)

    def test_parsed_case_rejects_blank_identifier(self):
        with self.assertRaises(AnalyticsValidationError):
            _case(case_identifier=" ")

    def test_parsed_case_rejects_duplicate_categories(self):
        with self.assertRaises(AnalyticsValidationError):
            _case(
                outcome_categories=(
                    CaseOutcomeCategory.DISPATCH_PASSED,
                    CaseOutcomeCategory.DISPATCH_PASSED,
                )
            )

    def test_parsed_case_rejects_duplicate_markers(self):
        with self.assertRaises(AnalyticsValidationError):
            _case(failed_markers=("x", "x"))

    def test_parsed_run_properties(self):
        case = _case()
        run = ParsedLiveRun(
            source_path=FIXTURE_DIR / "usable-run.json",
            results=(case,),
            usability_status=RunUsabilityStatus.USABLE,
            source_counts_consistent=True,
        )
        self.assertEqual(run.total_cases, 1)
        self.assertEqual(run.behaviorally_eligible_case_count, 1)
        self.assertEqual(run.infrastructure_failure_count, 0)

    def test_parsed_run_rejects_duplicate_cases(self):
        case = _case()
        with self.assertRaises(AnalyticsValidationError):
            ParsedLiveRun(
                source_path=FIXTURE_DIR / "usable-run.json",
                results=(case, case),
                usability_status=RunUsabilityStatus.USABLE,
                source_counts_consistent=True,
            )

    def test_case_summary_qualitative_properties(self):
        summary = CaseStabilitySummary(
            case_identifier="case",
            total_input_runs=2,
            usable_or_degraded_runs=2,
            unusable_runs_excluded=0,
            eligible_observations=2,
            dispatch_passed=2,
            dispatch_wrong=0,
            dispatch_skipped=0,
            response_passed=1,
            response_failed=1,
            response_skipped=0,
            infrastructure_failures=0,
            unavailable_observations=0,
            observed_skill_counts=(("skill", 2),),
            failed_marker_counts=(("marker", 1),),
            forbidden_pattern_counts=(),
        )
        self.assertIn("stable", summary.dispatch_observation_stability)
        self.assertIn("varied", summary.response_contract_stability)
        self.assertIn("no infrastructure", summary.infrastructure_reliability)


def _case(**overrides):
    values = {
        "case_identifier": "case",
        "dispatch_status": ClaudeEvaluationStatus.PASSED,
        "response_contract_status": ClaudeEvaluationStatus.SKIPPED,
        "observed_skill": "skill",
        "failed_markers": (),
        "matched_forbidden_patterns": (),
        "diagnostic": "observed skill",
        "outcome_categories": (
            CaseOutcomeCategory.DISPATCH_PASSED,
            CaseOutcomeCategory.RESPONSE_SKIPPED,
        ),
        "behavioral_eligibility": BehavioralEligibility.ELIGIBLE,
    }
    values.update(overrides)
    return ParsedCaseRunResult(**values)


if __name__ == "__main__":
    unittest.main()
