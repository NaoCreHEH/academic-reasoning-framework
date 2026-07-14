import unittest

from benchmark.adapters.claude_code.cases import CLAUDE_ADAPTER_CASES


class ClaudeAdapterEvaluationCasesTests(unittest.TestCase):
    def test_builtin_identifiers_unique(self):
        identifiers = [case.identifier for case in CLAUDE_ADAPTER_CASES]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_at_least_ten_dispatch_cases_exist(self):
        dispatch_cases = [
            case for case in CLAUDE_ADAPTER_CASES if "dispatch" in case.tags
        ]
        self.assertGreaterEqual(len(dispatch_cases), 10)

    def test_all_five_expected_skills_represented(self):
        self.assertEqual(
            {case.expected_skill for case in CLAUDE_ADAPTER_CASES},
            {
                "arf-academic:uml-analysis",
                "arf-academic:architecture-review",
                "arf-academic:pfe-review",
                "arf-academic:exam-generation",
                "arf-academic:python-teaching",
            },
        )

    def test_collision_tag_exists(self):
        self.assertTrue(any("collision" in case.tags for case in CLAUDE_ADAPTER_CASES))

    def test_french_prompts_represented(self):
        self.assertTrue(all("french" in case.tags for case in CLAUDE_ADAPTER_CASES))

    def test_required_collision_case_identifiers_exist(self):
        self.assertTrue(
            {
                "dispatch-python-mcq",
                "dispatch-uml-architecture-wording",
                "dispatch-pfe-oral-questions",
                "dispatch-uml-exam",
                "dispatch-python-question-bank",
                "dispatch-repository-student-context",
                "dispatch-misspelled-qcm",
            }.issubset({case.identifier for case in CLAUDE_ADAPTER_CASES})
        )

    def test_confidence_case_contains_percentage_regex(self):
        case = _case("response-confidence-no-percentage")
        self.assertIn(
            r"\b\d{1,3}\s*%\s*(?:de\s+)?confiance\b",
            case.response_forbidden_regexes,
        )

    def test_architecture_case_is_conceptual_and_ignores_current_repo(self):
        prompt = _case("response-architecture-files-not-names").prompt.lower()
        self.assertIn("question conceptuelle", prompt)
        self.assertIn("imaginons un depot", prompt)
        self.assertIn("ne tiens pas compte du depot courant", prompt)

    def test_confidence_case_matches_fresh_invocation_context(self):
        prompt = _case("response-confidence-no-percentage").prompt.lower()
        self.assertIn("aucun rapport de pfe", prompt)
        self.assertNotIn("tu n'as vu qu'une partie", prompt)
        self.assertNotIn("partie du rapport", prompt)

    def test_python_b1_case_contains_oop_forbidden_patterns(self):
        case = _case("response-python-no-oop")
        self.assertIn("cree une classe", case.response_forbidden_patterns)
        self.assertIn("object-oriented solution", case.response_forbidden_patterns)


def _case(identifier):
    return next(case for case in CLAUDE_ADAPTER_CASES if case.identifier == identifier)


if __name__ == "__main__":
    unittest.main()
