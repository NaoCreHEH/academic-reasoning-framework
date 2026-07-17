import unittest

from benchmark.adapters.claude_code.enums import ResponseMarkerMatchMode
from benchmark.adapters.claude_code.cases import CLAUDE_ADAPTER_CASES
from benchmark.adapters.claude_code.models import ClaudeAdapterCase, ResponseMarker
from benchmark.adapters.claude_code.runner import (
    ASSERTED_CONFIDENCE_PERCENTAGE_PATTERN,
    _evaluate_response,
    find_asserted_confidence_percentage,
)


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

    def test_uml_observed_missing_rules_phrase_passes(self):
        self.assertCaseMarkerPasses(
            "response-uml-missing-lifecycle-evidence",
            (
                "Sans cahier des charges ni regles metier, on ne peut pas "
                "qualifier ce choix d'erreur. La question metier qui tranche "
                "est le cycle de vie."
            ),
        )

    def test_uml_observed_supposition_phrase_passes(self):
        self.assertCaseMarkerPasses(
            "response-uml-missing-lifecycle-evidence",
            (
                "Imposer une composition serait une supposition, pas une "
                "deduction. Il faut savoir si Chanson peut exister sans "
                "Repertoire."
            ),
        )

    def test_uml_demonstrated_error_refusal_phrase_passes(self):
        self.assertCaseMarkerPasses(
            "response-uml-missing-lifecycle-evidence",
            (
                "Association simple Repertoire-Chanson : pas une erreur "
                "demontree. Il faut savoir si Chanson disparait avec Repertoire."
            ),
        )

    def test_uml_unrelated_preference_does_not_satisfy_missing_evidence_marker(self):
        status, failed_markers, matches = _evaluate_response(
            _adapter_case("response-uml-missing-lifecycle-evidence"),
            "La composition est meilleure dans ce diagramme UML.",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(failed_markers, ("insufficient-domain-evidence", "domain-rule-resolution"))
        self.assertEqual(matches, ())

    def test_uml_choice_not_automatic_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-uml-choice-not-error",
            "Non, ce n'est pas automatique. Cela depend du cycle de vie.",
        )

    def test_uml_choice_simple_association_correct_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-uml-choice-not-error",
            "L'association simple est correcte si Chanson peut etre partage.",
        )

    def test_uml_choice_not_error_in_itself_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-uml-choice-not-error",
            (
                "Votre association simple n'est en tout cas pas une erreur en soi. "
                "Il faut verifier le cycle de vie."
            ),
        )

    def test_uml_choice_lifecycle_semantics_wording_passes(self):
        self.assertCaseMarkerPasses(
            "response-uml-choice-not-error",
            "La composition depend de la semantique de cycle de vie.",
        )

    def test_uml_mandatory_composition_answer_fails(self):
        status, _failed_markers, matches = _evaluate_response(
            _adapter_case("response-uml-choice-not-error"),
            "La composition est obligatoire. Cela depend du cycle de vie.",
        )
        self.assertEqual(status.value, "failed")
        self.assertIn("la composition est obligatoire", matches)

    def test_uml_certain_association_error_answer_fails(self):
        status, _failed_markers, _matches = _evaluate_response(
            _adapter_case("response-uml-choice-not-error"),
            "L'association est une erreur certaine. Cela depend du cycle de vie.",
        )
        self.assertEqual(status.value, "failed")

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

    def test_confidence_observed_scope_wording_satisfies_marker(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            (
                "Aucune section, page ou extrait du rapport n'a ete partage. "
                "Il n'y a aucune base pour evaluer la qualite globale."
            ),
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
        self.assertEqual(matches, (ASSERTED_CONFIDENCE_PERCENTAGE_PATTERN,))

    def test_confidence_before_percentage_regex_catches_live_fragment(self):
        status, _failed_markers, matches = _evaluate_response(
            _adapter_case("response-confidence-no-percentage"),
            "Sans le rapport, mon niveau de confiance est donc nul (0%).",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(
            matches,
            (ASSERTED_CONFIDENCE_PERCENTAGE_PATTERN,),
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
                    ASSERTED_CONFIDENCE_PERCENTAGE_PATTERN,
                    matches,
                )

    def test_confidence_live_tilde_percentage_fragment_fails_without_marker_failure(self):
        status, failed_markers, matches = _evaluate_response(
            _adapter_case("response-confidence-no-percentage"),
            "Sans document fourni, niveau de confiance = ~0 %, non evaluable.",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(failed_markers, ())
        self.assertIn(ASSERTED_CONFIDENCE_PERCENTAGE_PATTERN, matches)

    def test_confidence_zero_percentage_after_confidence_fails(self):
        status, failed_markers, matches = _evaluate_response(
            _adapter_case("response-confidence-no-percentage"),
            "Sans rapport, ma confiance est de 0%.",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(failed_markers, ())
        self.assertIn(ASSERTED_CONFIDENCE_PERCENTAGE_PATTERN, matches)

    def test_confidence_observed_rejected_percentage_regression_passes(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            (
                "Aucun rapport, section, ou preuve de PFE n'a été inspecté "
                "dans cette conversation. Je ne peux donc pas donner de niveau "
                "de confiance numérique sur la qualité de l'ensemble du PFE — "
                "ce ne serait pas 0%, ce serait Unknown (indéterminable), car "
                "aucune évaluation qualitative n'a de base observable."
            ),
        )

    def test_asserted_confidence_percentages_fail(self):
        case = _adapter_case("response-confidence-no-percentage")
        asserted = (
            "Ma confiance est de 80 %.",
            "Niveau de confiance : 70 %.",
            "Confiance globale estimee a 60 %.",
            "Je suis confiant a 90 %.",
            "La qualite du PFE est evaluee avec une confiance de 75 %.",
            "Confiance 50%",
            "Avec 80 % de confiance, le travail est satisfaisant.",
        )
        for response in asserted:
            with self.subTest(response=response):
                status, _failed_markers, matches = _evaluate_response(
                    case,
                    f"Aucun rapport n'a ete fourni. {response}",
                )
                self.assertEqual(status.value, "failed")
                self.assertIn(ASSERTED_CONFIDENCE_PERCENTAGE_PATTERN, matches)

    def test_rejected_confidence_percentages_pass(self):
        rejected = (
            "Ce ne serait pas 0 %, ce serait Unknown.",
            "Je ne peux pas donner un niveau de confiance de 80 %.",
            "Il serait incorrect d'annoncer 90 % de confiance.",
            "Aucun pourcentage de confiance ne peut etre attribue.",
            "Je refuse d'estimer la confiance a 70 %.",
            "Il ne faut pas repondre avec une confiance de 60 %.",
            "Sans preuve, dire 80 % serait arbitraire.",
            "Ce n'est pas une confiance de 0 %, mais une absence d'evaluation.",
        )
        for response in rejected:
            with self.subTest(response=response):
                self.assertCaseMarkerPasses(
                    "response-confidence-no-percentage",
                    f"Aucun rapport n'a ete fourni. {response}",
                )

    def test_confidence_mixed_clauses_still_fail(self):
        case = _adapter_case("response-confidence-no-percentage")
        mixed = (
            "Je ne dispose pas du rapport complet, mais ma confiance est de 80 %.",
            "Sans toutes les annexes, mon niveau de confiance reste de 70 %.",
            "Je ne peux pas tout verifier. Confiance estimee : 60 %.",
            "Ce n'est pas parfait, mais je suis confiant a 90 %.",
        )
        for response in mixed:
            with self.subTest(response=response):
                status, _failed_markers, matches = _evaluate_response(
                    case,
                    f"Aucun rapport n'a ete fourni. {response}",
                )
                self.assertEqual(status.value, "failed")
                self.assertIn(ASSERTED_CONFIDENCE_PERCENTAGE_PATTERN, matches)

    def test_confidence_percentage_punctuation_and_formatting(self):
        passing = (
            "Ce ne serait pas 0%, ce serait Unknown.",
            "Ce ne serait pas **0 %**, ce serait Unknown.",
            "Je ne peux pas donner un niveau de confiance\n de 80 %.",
            "Je refuse d'estimer la confiance à 70 %.",
            "CE NE SERAIT PAS 0 %, CE SERAIT UNKNOWN.",
            "Ce n’est pas une confiance de 0 %, mais une absence d’évaluation.",
        )
        for response in passing:
            with self.subTest(response=response):
                self.assertCaseMarkerPasses(
                    "response-confidence-no-percentage",
                    f"Aucun rapport n'a ete fourni. {response}",
                )

    def test_confidence_detector_direct_result(self):
        self.assertIsNone(
            find_asserted_confidence_percentage(
                "Je ne peux pas donner un niveau de confiance de 80 %."
            )
        )
        self.assertIsNotNone(
            find_asserted_confidence_percentage("Ma confiance est de 80 %.")
        )

    def test_confidence_refusal_without_percentage_passes(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            "Je ne peux pas evaluer ma confiance sans le rapport.",
        )

    def test_confidence_unknown_non_evaluable_response_passes(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            (
                "Aucun rapport n'a ete fourni. Pour la qualite globale du PFE, "
                "la confiance est Unknown / non evaluable."
            ),
        )

    def test_confidence_global_unknown_without_percentage_passes(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            "Sans rapport, la conclusion globale est Unknown.",
        )

    def test_partial_scope_limitation_marker_behavior(self):
        self.assertMarkerPasses(
            "uniquement sur cette section",
            "Je n'ai lu que la methodologie. Mon jugement porte uniquement sur cette section.",
        )

    def test_unrelated_percentage_does_not_fail_confidence_case(self):
        self.assertCaseMarkerPasses(
            "response-confidence-no-percentage",
            "Le taux de completion est 80%. Je ne peux pas evaluer ma confiance sans le rapport.",
        )

    def test_internal_adapter_narration_fails_in_response_cases(self):
        failing_responses = (
            "La regle de prudence de ce skill est explicite.",
            "Le skill que je viens d'utiliser dit que...",
            "The skill instructions require caution.",
        )
        for response in failing_responses:
            with self.subTest(response=response):
                status, _failed_markers, matches = _evaluate_response(
                    _adapter_case("response-confidence-no-percentage"),
                    f"Sans rapport, non evaluable. {response}",
                )
                self.assertEqual(status.value, "failed")
                self.assertTrue(matches)

    def test_professional_skills_wording_does_not_trigger_internal_narration(self):
        passing_responses = (
            "Sans rapport, non evaluable. L'etudiant doit developper ses skills techniques.",
            "Sans rapport, non evaluable. Les soft skills sont importantes.",
            "Sans rapport, non evaluable. Cette competence est importante.",
        )
        for response in passing_responses:
            with self.subTest(response=response):
                self.assertCaseMarkerPasses("response-confidence-no-percentage", response)

    def test_direct_named_skill_narration_fails(self):
        failing_responses = (
            "Je n'ai trouve que le skill `pfe-review` lui-meme.",
            "C'est ce que le skill `pfe-review` est cense examiner.",
            "J'invoquerai le skill `arf-academic:pfe-review` dessus.",
            "I will invoke the skill for this.",
            "I am using the arf-academic:pfe-review adapter.",
        )
        for response in failing_responses:
            with self.subTest(response=response):
                status, _failed_markers, matches = _evaluate_response(
                    _adapter_case("response-confidence-no-percentage"),
                    f"Sans rapport, non evaluable. {response}",
                )
                self.assertEqual(status.value, "failed")
                self.assertTrue(matches)

    def test_missing_diagram_boundary_marker_passes(self):
        self.assertCaseMarkerPasses(
            "dispatch-uml-exam",
            "Je n'ai pas recu de diagramme; il me faut le diagramme pour identifier les erreurs reelles plutot que d'en inventer.",
        )

    def test_missing_submission_boundary_marker_passes(self):
        self.assertCaseMarkerPasses(
            "dispatch-python-question-bank",
            "Je n'ai pas encore le contenu de la soumission Python; colle directement le code ou indique le chemin du fichier.",
        )

    def test_invented_uml_errors_do_not_satisfy_missing_diagram_marker(self):
        status, failed_markers, matches = _evaluate_response(
            _adapter_case("dispatch-uml-exam"),
            "Voici cinq erreurs UML inventees.",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(failed_markers, ("missing-diagram-boundary",))
        self.assertEqual(matches, ())

    def test_generic_python_questions_do_not_satisfy_missing_submission_marker(self):
        status, failed_markers, matches = _evaluate_response(
            _adapter_case("dispatch-python-question-bank"),
            "Voici quinze questions generiques sur Python.",
        )
        self.assertEqual(status.value, "failed")
        self.assertEqual(failed_markers, ("missing-submission-boundary",))
        self.assertEqual(matches, ())

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
