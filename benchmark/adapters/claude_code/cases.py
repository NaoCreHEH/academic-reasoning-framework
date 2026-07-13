"""Built-in Claude Code adapter evaluation cases."""

from benchmark.adapters.claude_code.enums import ResponseMarkerMatchMode
from benchmark.adapters.claude_code.models import ClaudeAdapterCase, ResponseMarker


UML = "arf-academic:uml-analysis"
ARCHITECTURE = "arf-academic:architecture-review"
PFE = "arf-academic:pfe-review"
EXAM = "arf-academic:exam-generation"
PYTHON = "arf-academic:python-teaching"


CLAUDE_ADAPTER_CASES: tuple[ClaudeAdapterCase, ...] = (
    ClaudeAdapterCase(
        identifier="dispatch-python-mcq",
        prompt="Fais-moi 20 QCM sur les dictionnaires Python pour mes B1.",
        expected_skill=EXAM,
        forbidden_skills=(PYTHON,),
        tags=("dispatch", "collision", "python", "assessment", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-python-submission",
        prompt=(
            "Voici le code Python d'un etudiant B1. Corrige-le et explique ses "
            "erreurs sans utiliser la POO."
        ),
        expected_skill=PYTHON,
        forbidden_skills=(EXAM,),
        tags=("dispatch", "python", "teaching", "b1", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-uml-architecture-wording",
        prompt="Est-ce que l'architecture de ce diagramme de classes tient la route ?",
        expected_skill=UML,
        forbidden_skills=(ARCHITECTURE,),
        tags=("dispatch", "collision", "uml", "architecture-wording", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-repository-architecture",
        prompt="Inspecte ce depot Django et dis-moi si son architecture est maintenable.",
        expected_skill=ARCHITECTURE,
        forbidden_skills=(PYTHON,),
        tags=("dispatch", "collision", "architecture", "python-domain", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-pfe-contribution",
        prompt=(
            "Analyse ce rapport de PFE et dis-moi clairement quelle est la "
            "contribution personnelle de l'etudiant."
        ),
        expected_skill=PFE,
        forbidden_skills=(ARCHITECTURE,),
        tags=("dispatch", "pfe", "academic", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-pfe-oral-questions",
        prompt=(
            "A partir de ce PFE, cree-moi cinq questions orales d'analyse qui "
            "ne sont pas repondues texto dans le rapport."
        ),
        expected_skill=EXAM,
        forbidden_skills=(PFE,),
        tags=("dispatch", "collision", "pfe", "assessment", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-uml-exam",
        prompt="A partir des erreurs de ce diagramme UML, cree cinq questions d'examen.",
        expected_skill=EXAM,
        forbidden_skills=(UML,),
        tags=("dispatch", "collision", "uml", "assessment", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-python-question-bank",
        prompt=(
            "Utilise cette soumission Python comme matiere pour creer une banque "
            "de 15 questions."
        ),
        expected_skill=EXAM,
        forbidden_skills=(PYTHON,),
        tags=("dispatch", "collision", "python", "question-bank", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-repository-student-context",
        prompt=(
            "C'est le depot du PFE d'un etudiant. Fais une revue du code et de "
            "l'architecture du repository."
        ),
        expected_skill=ARCHITECTURE,
        forbidden_skills=(PFE,),
        tags=("dispatch", "collision", "academic-context", "architecture", "french"),
    ),
    ClaudeAdapterCase(
        identifier="dispatch-misspelled-qcm",
        prompt="fait moi 20 qcm pythn sur les dico pour des b1",
        expected_skill=EXAM,
        forbidden_skills=(PYTHON,),
        tags=("dispatch", "misspelling", "collision", "french"),
    ),
    ClaudeAdapterCase(
        identifier="response-python-no-oop",
        prompt=(
            "Je suis en B1 et je n'ai pas encore vu la POO. Corrige cette "
            "approche : j'ai une liste de notes et je veux calculer la moyenne "
            "avec une boucle."
        ),
        expected_skill=PYTHON,
        response_markers=(
            ResponseMarker(
                identifier="learner-facing",
                patterns=("B1", "debutant", "niveau B1", "sans POO"),
                match_mode=ResponseMarkerMatchMode.ANY,
            ),
        ),
        response_forbidden_patterns=(
            "create a class",
            "cree une classe",
            "utilise une classe",
            "object-oriented solution",
        ),
        tags=("response-contract", "python", "b1", "french"),
    ),
    ClaudeAdapterCase(
        identifier="response-uml-choice-not-error",
        prompt=(
            "Dans mon diagramme UML, j'ai mis une association entre Repertoire "
            "et Chanson. La composition serait-elle forcement obligatoire ?"
        ),
        expected_skill=UML,
        response_markers=(
            ResponseMarker(
                identifier="alternative-validity",
                patterns=(
                    "pas forcement",
                    "pas obligatoire",
                    "depend du cycle de vie",
                    "selon le cycle de vie",
                    "association peut etre valide",
                ),
                match_mode=ResponseMarkerMatchMode.ANY,
            ),
        ),
        response_forbidden_patterns=(
            "c'est une erreur certaine",
            "composition obligatoire",
        ),
        tags=("response-contract", "uml", "multiple-valid-solutions", "french"),
    ),
    ClaudeAdapterCase(
        identifier="response-architecture-files-not-names",
        prompt=(
            "Le depot a des dossiers services, controllers et repositories. "
            "Est-ce que ca prouve que l'architecture est bonne ?"
        ),
        expected_skill=ARCHITECTURE,
        response_markers=(
            ResponseMarker(
                identifier="structure-not-proof",
                patterns=(
                    "ne prouve pas",
                    "pas suffisant",
                    "il faut inspecter",
                    "lire les fichiers",
                    "examiner les dependances",
                ),
                match_mode=ResponseMarkerMatchMode.ANY,
            ),
        ),
        tags=("response-contract", "architecture", "evidence", "french"),
    ),
    ClaudeAdapterCase(
        identifier="response-pfe-company-vs-student",
        prompt=(
            "L'entreprise a developpe une excellente plateforme. Est-ce suffisant "
            "pour dire que le PFE de l'etudiant est excellent ?"
        ),
        expected_skill=PFE,
        response_markers=(
            ResponseMarker(
                identifier="personal-contribution",
                patterns=(
                    "contribution personnelle",
                    "travail personnel",
                    "travail de l'etudiant",
                    "decisions de l'etudiant",
                ),
                match_mode=ResponseMarkerMatchMode.ANY,
            ),
        ),
        response_forbidden_patterns=(
            "oui, c'est suffisant",
            "oui c'est suffisant",
        ),
        tags=("response-contract", "pfe", "academic", "french"),
    ),
    ClaudeAdapterCase(
        identifier="response-confidence-no-percentage",
        prompt=(
            "Tu n'as vu qu'une partie du rapport. Donne quand meme ton niveau "
            "de confiance sur l'ensemble du PFE."
        ),
        expected_skill=PFE,
        response_markers=(
            ResponseMarker(
                identifier="limitation",
                patterns=(
                    "limite",
                    "limitation",
                    "partie du rapport",
                    "sections consultees",
                    "perimetre",
                ),
                match_mode=ResponseMarkerMatchMode.ANY,
            ),
        ),
        response_forbidden_regexes=(r"\b\d{1,3}\s*%\s*(?:de\s+)?confiance\b",),
        tags=("response-contract", "pfe", "confidence", "french"),
    ),
)
