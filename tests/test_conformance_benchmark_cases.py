import re
import unittest

from benchmark.conformance import (
    CONFORMANCE_CASES,
    ConformanceDomain,
    ConformanceExpectation,
)


class ConformanceBenchmarkCasesTests(unittest.TestCase):
    def test_case_identifiers_unique(self) -> None:
        identifiers = [case.identifier for case in CONFORMANCE_CASES]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_every_case_tagged(self) -> None:
        for case in CONFORMANCE_CASES:
            with self.subTest(case=case.identifier):
                self.assertTrue(case.tags)

    def test_every_case_references_at_least_one_rfc(self) -> None:
        for case in CONFORMANCE_CASES:
            with self.subTest(case=case.identifier):
                self.assertTrue(case.rfc_references)

    def test_rfc_references_have_expected_format(self) -> None:
        pattern = re.compile(r"^RFC-\d{4}$")
        for case in CONFORMANCE_CASES:
            for reference in case.rfc_references:
                with self.subTest(case=case.identifier, reference=reference):
                    self.assertIsNotNone(pattern.fullmatch(reference))

    def test_all_domains_represented(self) -> None:
        self.assertEqual(
            {case.domain for case in CONFORMANCE_CASES},
            set(ConformanceDomain),
        )

    def test_accept_cases_do_not_specify_expected_error(self) -> None:
        for case in CONFORMANCE_CASES:
            if case.expectation is ConformanceExpectation.ACCEPT:
                with self.subTest(case=case.identifier):
                    self.assertIsNone(case.expected_error)

    def test_reject_cases_specify_expected_error(self) -> None:
        for case in CONFORMANCE_CASES:
            if case.expectation is ConformanceExpectation.REJECT:
                with self.subTest(case=case.identifier):
                    self.assertIsNotNone(case.expected_error)

    def test_required_case_identifiers_exist(self) -> None:
        identifiers = {case.identifier for case in CONFORMANCE_CASES}
        self.assertTrue(
            {
                "evidence-direct-observation-valid",
                "evidence-cycle-rejected",
                "claim-without-evidence-structurally-valid",
                "confidence-percentage-rejected",
                "feedback-demonstrated-error-without-evidence-rejected",
                "feedback-severity-confidence-independent-valid",
                "interpretation-unresolved-blocks-routing-conversion",
                "interpretation-unknown-explicit-capability-converts-valid",
                "minor-confirmed-feedback-valid",
                "major-plausible-feedback-valid",
            }.issubset(identifiers)
        )

    def test_required_tags_are_used(self) -> None:
        tags = {tag for case in CONFORMANCE_CASES for tag in case.tags}
        self.assertTrue(
            {
                "positive",
                "negative",
                "structural",
                "cross-contract",
                "evidence",
                "confidence",
                "feedback",
                "interpretation",
            }.issubset(tags)
        )

    def test_structural_limitation_cases_are_documented(self) -> None:
        descriptions = {
            case.identifier: case.description.lower()
            for case in CONFORMANCE_CASES
        }
        self.assertIn(
            "structurally valid only",
            descriptions["claim-without-evidence-structurally-valid"],
        )
        self.assertIn(
            "semantically sufficient",
            descriptions["confidence-speculative-with-basis-valid"],
        )
        self.assertIn(
            "semantic justification",
            descriptions["feedback-severe-plausible-valid"],
        )


if __name__ == "__main__":
    unittest.main()
