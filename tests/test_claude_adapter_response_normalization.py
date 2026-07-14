import unittest

from benchmark.adapters.claude_code.enums import ResponseMarkerMatchMode
from benchmark.adapters.claude_code.models import ClaudeAdapterCase, ResponseMarker
from benchmark.adapters.claude_code.runner import _evaluate_response


class ClaudeAdapterResponseNormalizationTests(unittest.TestCase):
    def test_forcement_matches_forcement_with_accent(self):
        self.assertMarkerPasses("forcement", "pas forcément")

    def test_depend_matches_depend_with_accent(self):
        self.assertMarkerPasses("depend", "cela dépend du cycle de vie")

    def test_depot_matches_depot_with_accent(self):
        self.assertMarkerPasses("depot", "le dépôt contient des fichiers")

    def test_perimetre_matches_perimetre_with_accent(self):
        self.assertMarkerPasses("perimetre", "dans ce périmètre")

    def test_etudiant_matches_etudiant_with_accent(self):
        self.assertMarkerPasses("etudiant", "travail de l'étudiant")

    def test_case_insensitive_matching_still_works(self):
        self.assertMarkerPasses("present", "PRESENT")

    def test_whitespace_normalization_still_works(self):
        self.assertMarkerPasses("cycle de vie", "cycle \n de \t vie")

    def test_misspellings_are_not_corrected(self):
        case = _case("forcement")
        status, failed_markers, _matches = _evaluate_response(case, "forcemant")
        self.assertEqual(failed_markers, ("marker",))
        self.assertEqual(status.value, "failed")

    def test_forcemant_does_not_match_forcement(self):
        case = _case("forcement")
        _status, failed_markers, _matches = _evaluate_response(case, "forcemant")
        self.assertEqual(failed_markers, ("marker",))

    def assertMarkerPasses(self, pattern, response):
        status, failed_markers, matches = _evaluate_response(_case(pattern), response)
        self.assertEqual(status.value, "passed")
        self.assertEqual(failed_markers, ())
        self.assertEqual(matches, ())


def _case(pattern):
    return ClaudeAdapterCase(
        identifier="case",
        prompt="Prompt",
        expected_skill="skill",
        response_markers=(
            ResponseMarker("marker", (pattern,), ResponseMarkerMatchMode.ANY),
        ),
    )


if __name__ == "__main__":
    unittest.main()
