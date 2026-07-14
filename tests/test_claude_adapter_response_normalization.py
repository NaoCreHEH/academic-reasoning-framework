import unittest

from benchmark.adapters.claude_code.enums import ResponseMarkerMatchMode
from benchmark.adapters.claude_code.cases import CLAUDE_ADAPTER_CASES
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

    def test_architecture_live_ne_prouve_rien_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-architecture-files-not-names",
            "la presence de ces dossiers ne prouve rien sur la qualite de l'architecture",
        )

    def test_architecture_live_ne_suffit_pas_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-architecture-files-not-names",
            "le nommage seul ne suffit pas",
        )

    def test_architecture_pas_une_preuve_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-architecture-files-not-names",
            "la structure de dossiers est une hypothese sur l'architecture, pas une preuve",
        )

    def test_architecture_unrelated_folder_presence_fails(self):
        status, failed_markers, _matches = _evaluate_response(
            _adapter_case("response-architecture-files-not-names"),
            "Les dossiers services et controllers sont presents.",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(failed_markers, ("structure-not-proof",))

    def test_confidence_aucune_partie_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            "Je n'ai en fait vu aucune partie d'un rapport de PFE",
        )

    def test_confidence_invente_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            "Je ne peux donc pas donner de niveau de confiance, meme partiel : ce serait invente.",
        )

    def test_confidence_sans_le_rapport_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            "Sans le rapport, impossible d'evaluer l'ensemble du PFE.",
        )

    def test_confidence_unjustified_global_confidence_fails(self):
        status, failed_markers, _matches = _evaluate_response(
            _adapter_case("response-confidence-no-percentage"),
            "Je suis confiant sur la qualite globale du PFE.",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(failed_markers, ("insufficient-review-scope",))

    def test_confidence_percentage_regex_remains_active(self):
        status, _failed_markers, matches = _evaluate_response(
            _adapter_case("response-confidence-no-percentage"),
            "Sans le rapport, je donne quand meme 80% de confiance.",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(matches, (r"\b\d{1,3}\s*%\s*(?:de\s+)?confiance\b",))

    def test_confidence_before_percentage_regex_catches_live_fragment(self):
        status, _failed_markers, matches = _evaluate_response(
            _adapter_case("response-confidence-no-percentage"),
            "Sans le rapport, mon niveau de confiance est donc nul (0%).",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(
            matches,
            (r"\bconfiance\b(?:(?!\.\s+[A-ZÀ-Ý])[\s\S]){0,80}\d{1,3}\s*%",),
        )

    def test_confidence_before_percentage_regex_catches_common_forms(self):
        case = _adapter_case("response-confidence-no-percentage")
        failing_responses = (
            "Sans le rapport, le niveau de confiance est de 0%.",
            "Sans le rapport, le niveau de confiance ... 0%.",
            "Sans le rapport, confiance : 80%.",
            "Sans le rapport, confiance de 50%.",
        )
        for response in failing_responses:
            with self.subTest(response=response):
                status, _failed_markers, matches = _evaluate_response(case, response)
                self.assertEqual(status.value, "failed")
                self.assertIn(
                    r"\bconfiance\b(?:(?!\.\s+[A-ZÀ-Ý])[\s\S]){0,80}\d{1,3}\s*%",
                    matches,
                )

    def test_confidence_refusal_without_percentage_passes(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            "Je ne peux pas evaluer ma confiance sans le rapport.",
        )

    def test_unrelated_percentage_does_not_fail_confidence_case(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            "Le taux de completion est 80%. Je ne peux pas evaluer ma confiance sans le rapport.",
        )

    def assertMarkerPasses(self, pattern, response):
        status, failed_markers, matches = _evaluate_response(_case(pattern), response)
        self.assertEqual(status.value, "passed")
        self.assertEqual(failed_markers, ())
        self.assertEqual(matches, ())

    def assertCaseMarkerPasses(self, identifier, response):
        status, failed_markers, matches = _evaluate_response(
            _adapter_case(identifier),
            response,
        )
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


def _adapter_case(identifier):
    return next(case for case in CLAUDE_ADAPTER_CASES if case.identifier == identifier)


if __name__ == "__main__":
    unittest.main()
