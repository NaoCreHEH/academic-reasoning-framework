"""Structured routing fixture cases for RFC-0005 collisions."""

from dataclasses import dataclass

from core.routing import RoutingRequest


@dataclass(frozen=True)
class RoutingCase:
    name: str
    request: RoutingRequest
    expected_primary: str | None
    expected_supporting: tuple[str, ...]
    expects_ambiguity: bool


ROUTING_CASES: tuple[RoutingCase, ...] = (
    RoutingCase(
        name="Python MCQ creation",
        request=RoutingRequest(
            user_objective="Create assessment questions",
            requested_output="MCQ",
            domain="Python",
        ),
        expected_primary="exam-generation",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Python student correction",
        request=RoutingRequest(
            user_objective="Correct this learner submission",
            primary_artifact="Python student code",
            domain="Python",
        ),
        expected_primary="python-teaching",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Class diagram architecture wording",
        request=RoutingRequest(
            user_objective="Review the architecture wording",
            primary_artifact="class diagram",
            domain="UML",
        ),
        expected_primary="uml-analysis",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Django repository architecture",
        request=RoutingRequest(
            user_objective="Review the repository architecture",
            primary_artifact="repository",
            domain="Python",
        ),
        expected_primary="architecture-review",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="PFE contribution analysis",
        request=RoutingRequest(
            user_objective="Analyze contribution quality",
            primary_artifact="PFE report",
        ),
        expected_primary="pfe-review",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Oral questions from PFE",
        request=RoutingRequest(
            user_objective="Create oral questions",
            primary_artifact="PFE report",
            requested_output="oral questions",
        ),
        expected_primary="exam-generation",
        expected_supporting=("pfe-review",),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="UML diagram to exam questions",
        request=RoutingRequest(
            user_objective="Create an exam from the model",
            primary_artifact="UML diagram",
            requested_output="examination",
        ),
        expected_primary="exam-generation",
        expected_supporting=("uml-analysis",),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Python submission to question bank",
        request=RoutingRequest(
            user_objective="Create a question bank",
            primary_artifact="Python submission",
            requested_output="question bank",
        ),
        expected_primary="exam-generation",
        expected_supporting=("python-teaching",),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Explicit valid UML selection",
        request=RoutingRequest(
            user_objective="Review this model",
            primary_artifact="UML diagram",
            explicit_capability="uml-analysis",
        ),
        expected_primary="uml-analysis",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Explicit inapplicable architecture selection for MCQ",
        request=RoutingRequest(
            user_objective="Create questions",
            requested_output="MCQ",
            domain="Python",
            explicit_capability="architecture-review",
        ),
        expected_primary="exam-generation",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Unknown explicit capability",
        request=RoutingRequest(
            user_objective="Review this",
            explicit_capability="quantum-professor",
        ),
        expected_primary=None,
        expected_supporting=(),
        expects_ambiguity=True,
    ),
    RoutingCase(
        name="Unknown artifact",
        request=RoutingRequest(
            user_objective="Review this artifact",
            primary_artifact="project document",
        ),
        expected_primary=None,
        expected_supporting=(),
        expects_ambiguity=True,
    ),
    RoutingCase(
        name="No structured ownership signal",
        request=RoutingRequest(user_objective="help me review this"),
        expected_primary=None,
        expected_supporting=(),
        expects_ambiguity=True,
    ),
    RoutingCase(
        name="Case-insensitive output taxonomy",
        request=RoutingRequest(
            user_objective="Create questions",
            requested_output="mcq",
        ),
        expected_primary="exam-generation",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
    RoutingCase(
        name="Free-form output must not be parsed",
        request=RoutingRequest(
            user_objective="Create questions",
            requested_output="Create an MCQ about Python",
            domain="Python",
        ),
        expected_primary="python-teaching",
        expected_supporting=(),
        expects_ambiguity=False,
    ),
)
