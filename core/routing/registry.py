"""Machine-readable capability registry for RFC-0005 ownership boundaries.

The registry records capability ownership and explicit yield relationships. It
does not perform natural-language routing, keyword scoring, embeddings, or
model-based classification.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass


class CapabilityRegistryError(ValueError):
    """Raised when a capability registry violates a structural invariant."""


class UnknownCapabilityError(CapabilityRegistryError, KeyError):
    """Raised when a requested capability identifier is absent."""


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise CapabilityRegistryError(f"{field_name} cannot be blank")


def _validate_tuple_values(values: tuple[str, ...], field_name: str) -> None:
    seen: set[str] = set()
    for value in values:
        _require_non_empty(value, field_name)
        if value in seen:
            raise CapabilityRegistryError(
                f"{field_name} contains duplicate value: {value}"
            )
        seen.add(value)


@dataclass(frozen=True)
class CapabilityDefinition:
    """A structural capability boundary definition."""

    identifier: str
    name: str
    description: str
    positive_boundaries: tuple[str, ...]
    negative_boundaries: tuple[str, ...]
    owned_artifacts: tuple[str, ...] = ()
    owned_outputs: tuple[str, ...] = ()
    supported_domains: tuple[str, ...] = ()
    yields_to: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_non_empty(self.identifier, "identifier")
        _require_non_empty(self.name, "name")
        _require_non_empty(self.description, "description")
        if not self.positive_boundaries:
            raise CapabilityRegistryError("positive_boundaries requires at least one entry")
        if not self.negative_boundaries:
            raise CapabilityRegistryError("negative_boundaries requires at least one entry")

        _validate_tuple_values(self.positive_boundaries, "positive_boundaries")
        _validate_tuple_values(self.negative_boundaries, "negative_boundaries")
        _validate_tuple_values(self.owned_artifacts, "owned_artifacts")
        _validate_tuple_values(self.owned_outputs, "owned_outputs")
        _validate_tuple_values(self.supported_domains, "supported_domains")
        _validate_tuple_values(self.yields_to, "yields_to")


class CapabilityRegistry:
    """Ordered collection of capability definitions."""

    def __init__(self, capabilities: Iterable[CapabilityDefinition]) -> None:
        self._capabilities: dict[str, CapabilityDefinition] = {}
        for capability in capabilities:
            if capability.identifier in self._capabilities:
                raise CapabilityRegistryError(
                    f"duplicate capability identifier: {capability.identifier}"
                )
            self._capabilities[capability.identifier] = capability

    def get(self, identifier: str) -> CapabilityDefinition:
        try:
            return self._capabilities[identifier]
        except KeyError as error:
            raise UnknownCapabilityError(
                f"unknown capability identifier: {identifier}"
            ) from error

    def contains(self, identifier: str) -> bool:
        return identifier in self._capabilities

    def __iter__(self) -> Iterator[CapabilityDefinition]:
        return iter(self._capabilities.values())

    def __len__(self) -> int:
        return len(self._capabilities)


def validate_registry_references(registry: CapabilityRegistry) -> None:
    """Validate explicit capability yield references."""

    for capability in registry:
        for target in capability.yields_to:
            if target == capability.identifier:
                raise CapabilityRegistryError(
                    f"capability cannot yield to itself: {capability.identifier}"
                )
            if not registry.contains(target):
                raise CapabilityRegistryError(
                    f"capability {capability.identifier} yields to unknown capability: {target}"
                )


def build_default_academic_registry() -> CapabilityRegistry:
    """Build the initial RFC-0005 academic capability registry."""

    registry = CapabilityRegistry(
        (
            CapabilityDefinition(
                identifier="uml-analysis",
                name="UML analysis",
                description="Reviews UML modeling choices and notation boundaries.",
                positive_boundaries=(
                    "UML modeling coherence, relationships, multiplicities, lifecycle, and notation.",
                ),
                negative_boundaries=(
                    "Must yield repository or running-system architecture review to architecture-review.",
                ),
                owned_artifacts=(
                    "UML diagram",
                    "class diagram",
                    "sequence diagram",
                    "UML model",
                ),
                yields_to=("architecture-review",),
            ),
            CapabilityDefinition(
                identifier="architecture-review",
                name="Architecture review",
                description="Reviews repository-wide and running-system architecture.",
                positive_boundaries=(
                    "Repository-wide or system architecture, components, dependencies, coupling, deployment, maintainability.",
                ),
                negative_boundaries=(
                    "Must not own UML diagram evaluation solely because architecture, design, coupling, or maintainability vocabulary appears.",
                ),
                owned_artifacts=("repository", "codebase", "running system"),
                yields_to=("uml-analysis",),
            ),
            CapabilityDefinition(
                identifier="pfe-review",
                name="PFE review",
                description="Reviews academic project framing and documentation.",
                positive_boundaries=(
                    "Academic evaluation of scope, methodology, personal contribution, critical analysis, documentation, and project framing.",
                ),
                negative_boundaries=(
                    "Must not own repository code review solely because the repository belongs to a student project.",
                ),
                owned_artifacts=(
                    "PFE report",
                    "thesis",
                    "internship report",
                    "statement of work",
                    "academic specification",
                ),
                yields_to=("architecture-review",),
            ),
            CapabilityDefinition(
                identifier="exam-generation",
                name="Exam generation",
                description="Produces academic assessment instruments.",
                positive_boundaries=("Production of assessment instruments.",),
                negative_boundaries=(
                    "Must not own learner code correction merely because the correction could inspire questions.",
                ),
                owned_outputs=(
                    "MCQ",
                    "QCM",
                    "examination",
                    "oral questions",
                    "question bank",
                    "rubric",
                    "assessment instrument",
                ),
                yields_to=("python-teaching",),
            ),
            CapabilityDefinition(
                identifier="python-teaching",
                name="Python teaching",
                description="Provides learner-facing Python correction and pedagogy.",
                positive_boundaries=(
                    "Learner-facing Python explanation, correction, procedural refactoring, exercise review, and pedagogical feedback.",
                ),
                negative_boundaries=(
                    "Must yield MCQ, QCM, examination, grading instrument, and question-bank production to exam-generation.",
                ),
                owned_artifacts=(
                    "Python student code",
                    "Python exercise",
                    "Python submission",
                ),
                yields_to=("exam-generation",),
            ),
        )
    )
    validate_registry_references(registry)
    return registry
