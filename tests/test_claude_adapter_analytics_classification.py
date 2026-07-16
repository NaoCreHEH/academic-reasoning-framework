import unittest

from benchmark.adapters.claude_code.enums import ClaudeEvaluationStatus
from benchmark.adapters.claude_code.analytics.classification import (
    classify_case_result,
    classify_run_usability,
)
from benchmark.adapters.claude_code.analytics.enums import (
    BehavioralEligibility,
    CaseOutcomeCategory,
    RunUsabilityStatus,
)
from benchmark.adapters.claude_code.analytics.loading import load_live_run_report
from benchmark.adapters.claude_code.analytics.models import ParsedCaseRunResult


class ClaudeAdapterAnalyticsClassificationTests(unittest.TestCase):
    def test_timeout_classified_as_infrastructure(self):
        categories, eligibility = _classify(
            "Claude invocation failed: live call timed out after 180s"
        )
        self.assertEqual(categories, (CaseOutcomeCategory.INVOCATION_TIMEOUT,))
        self.assertEqual(
            eligibility,
            BehavioralEligibility.INELIGIBLE_INFRASTRUCTURE,
        )

    def test_return_code_classified_as_process_failure(self):
        categories, _eligibility = _classify(
            "Claude invocation failed with return code 1"
        )
        self.assertEqual(
            categories,
            (CaseOutcomeCategory.INVOCATION_PROCESS_FAILURE,),
        )

    def test_invalid_utf8_classified_as_encoding_failure(self):
        categories, _eligibility = _classify(
            "Claude invocation failed: output was not valid UTF-8"
        )
        self.assertEqual(
            categories,
            (CaseOutcomeCategory.INVOCATION_ENCODING_FAILURE,),
        )

    def test_stream_parse_failure_classified(self):
        categories, _eligibility = _classify(
            "Claude invocation failed: stream parsing failed: bad event"
        )
        self.assertEqual(
            categories,
            (CaseOutcomeCategory.INVOCATION_STREAM_PARSE_FAILURE,),
        )

    def test_plugin_load_failure_classified(self):
        categories, _eligibility = _classify(
            "ARF plugin failed to load: invalid manifest"
        )
        self.assertEqual(categories, (CaseOutcomeCategory.PLUGIN_LOAD_FAILURE,))

    def test_generic_invocation_failure_classified(self):
        categories, _eligibility = _classify("Claude invocation failed: boom")
        self.assertEqual(
            categories,
            (CaseOutcomeCategory.OTHER_INVOCATION_FAILURE,),
        )

    def test_wrong_observed_skill_remains_behavioral_dispatch_wrong(self):
        categories, eligibility = classify_case_result(
            ClaudeEvaluationStatus.FAILED,
            ClaudeEvaluationStatus.SKIPPED,
            "expected skill-a; observed skills: skill-b",
        )
        self.assertIn(CaseOutcomeCategory.DISPATCH_WRONG, categories)
        self.assertEqual(eligibility, BehavioralEligibility.ELIGIBLE)

    def test_skipped_observable_dispatch_remains_eligible(self):
        categories, eligibility = classify_case_result(
            ClaudeEvaluationStatus.SKIPPED,
            ClaudeEvaluationStatus.SKIPPED,
            "skill identity not observable",
        )
        self.assertIn(CaseOutcomeCategory.DISPATCH_SKIPPED, categories)
        self.assertEqual(eligibility, BehavioralEligibility.ELIGIBLE)

    def test_response_marker_failure_remains_behavioral(self):
        categories, eligibility = classify_case_result(
            ClaudeEvaluationStatus.PASSED,
            ClaudeEvaluationStatus.FAILED,
            "failed markers: missing",
        )
        self.assertIn(CaseOutcomeCategory.RESPONSE_FAILED, categories)
        self.assertEqual(eligibility, BehavioralEligibility.ELIGIBLE)

    def test_evaluation_unavailable_is_ineligible_unavailable(self):
        categories, eligibility = classify_case_result(
            ClaudeEvaluationStatus.SKIPPED,
            ClaudeEvaluationStatus.SKIPPED,
            "evaluation unavailable: Claude CLI not found",
        )
        self.assertEqual(categories, (CaseOutcomeCategory.EVALUATION_UNAVAILABLE,))
        self.assertEqual(
            eligibility,
            BehavioralEligibility.INELIGIBLE_UNAVAILABLE,
        )

    def test_run_usability_classification(self):
        from pathlib import Path

        fixture_dir = Path(__file__).parent / "fixtures" / "claude_adapter_analytics"
        usable = load_live_run_report(fixture_dir / "usable-run.json")
        degraded = load_live_run_report(fixture_dir / "degraded-run.json")
        unusable = load_live_run_report(
            fixture_dir / "unusable-return-code-run.json"
        )
        self.assertEqual(
            classify_run_usability(usable.results),
            RunUsabilityStatus.USABLE,
        )
        self.assertEqual(
            classify_run_usability(degraded.results),
            RunUsabilityStatus.DEGRADED,
        )
        self.assertEqual(
            classify_run_usability(unusable.results),
            RunUsabilityStatus.UNUSABLE,
        )

    def test_response_contract_failure_alone_does_not_degrade_run(self):
        from pathlib import Path

        fixture_dir = Path(__file__).parent / "fixtures" / "claude_adapter_analytics"
        usable = load_live_run_report(fixture_dir / "usable-run.json")
        self.assertEqual(usable.usability_status, RunUsabilityStatus.USABLE)

    def test_all_unavailable_run_is_unusable(self):
        categories, eligibility = classify_case_result(
            ClaudeEvaluationStatus.SKIPPED,
            ClaudeEvaluationStatus.SKIPPED,
            "evaluation unavailable: Claude CLI not found",
        )
        result = ParsedCaseRunResult(
            case_identifier="case",
            dispatch_status=ClaudeEvaluationStatus.SKIPPED,
            response_contract_status=ClaudeEvaluationStatus.SKIPPED,
            observed_skill=None,
            failed_markers=(),
            matched_forbidden_patterns=(),
            diagnostic="evaluation unavailable: Claude CLI not found",
            outcome_categories=categories,
            behavioral_eligibility=eligibility,
        )
        self.assertEqual(
            classify_run_usability((result,)),
            RunUsabilityStatus.UNUSABLE,
        )


def _classify(diagnostic):
    return classify_case_result(
        ClaudeEvaluationStatus.FAILED,
        ClaudeEvaluationStatus.FAILED,
        diagnostic,
    )


if __name__ == "__main__":
    unittest.main()
