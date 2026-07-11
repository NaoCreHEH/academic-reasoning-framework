import unittest

from core.routing import (
    CapabilityDefinition,
    CapabilityRegistry,
    CapabilityRegistryError,
    UnknownCapabilityError,
    build_default_academic_registry,
    validate_registry_references,
)


def capability(identifier: str, **overrides: object) -> CapabilityDefinition:
    values: dict[str, object] = {
        "identifier": identifier,
        "name": f"{identifier} name",
        "description": f"{identifier} description",
        "positive_boundaries": ("owns matching work",),
        "negative_boundaries": ("does not own adjacent work",),
    }
    values.update(overrides)
    return CapabilityDefinition(**values)


class CapabilityDefinitionTests(unittest.TestCase):
    def test_valid_capability_definition(self) -> None:
        item = capability(
            "capability",
            owned_artifacts=("repository",),
            owned_outputs=("feedback",),
            supported_domains=("software engineering",),
            yields_to=("other-capability",),
        )
        self.assertEqual(item.identifier, "capability")
        self.assertEqual(item.owned_artifacts, ("repository",))

    def test_blank_identifier_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability(" ")

    def test_blank_name_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", name=" ")

    def test_blank_description_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", description=" ")

    def test_positive_boundary_required(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", positive_boundaries=())

    def test_negative_boundary_required(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", negative_boundaries=())

    def test_blank_boundary_entry_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", positive_boundaries=(" ",))

    def test_blank_owned_artifact_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", owned_artifacts=("repository", " "))

    def test_blank_owned_output_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", owned_outputs=("MCQ", " "))

    def test_blank_supported_domain_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", supported_domains=("Python", " "))

    def test_duplicate_values_in_one_tuple_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", owned_outputs=("MCQ", "MCQ"))

    def test_duplicate_positive_boundary_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability(
                "capability",
                positive_boundaries=("owns work", "owns work"),
            )

    def test_duplicate_negative_boundary_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability(
                "capability",
                negative_boundaries=("does not own work", "does not own work"),
            )

    def test_duplicate_owned_artifact_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", owned_artifacts=("repository", "repository"))

    def test_duplicate_owned_output_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", owned_outputs=("MCQ", "MCQ"))

    def test_duplicate_supported_domain_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("capability", supported_domains=("Python", "Python"))

    def test_identifier_comparison_is_exact_and_case_sensitive(self) -> None:
        registry = CapabilityRegistry((capability("uml-analysis"), capability("UML-analysis")))
        self.assertEqual(len(registry), 2)
        self.assertTrue(registry.contains("uml-analysis"))
        self.assertTrue(registry.contains("UML-analysis"))


class CapabilityRegistryTests(unittest.TestCase):
    def test_duplicate_capability_identifiers_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            CapabilityRegistry((capability("a"), capability("a")))

    def test_preserves_insertion_order(self) -> None:
        registry = CapabilityRegistry((capability("a"), capability("b"), capability("c")))
        self.assertEqual([item.identifier for item in registry], ["a", "b", "c"])

    def test_get_returns_capability(self) -> None:
        registry = CapabilityRegistry((capability("a"),))
        self.assertEqual(registry.get("a").identifier, "a")

    def test_unknown_identifier_raises_specific_error(self) -> None:
        registry = CapabilityRegistry((capability("a"),))
        with self.assertRaises(UnknownCapabilityError):
            registry.get("missing")

    def test_contains_and_len(self) -> None:
        registry = CapabilityRegistry((capability("a"), capability("b")))
        self.assertTrue(registry.contains("a"))
        self.assertFalse(registry.contains("missing"))
        self.assertEqual(len(registry), 2)


class RegistryReferenceValidationTests(unittest.TestCase):
    def test_yields_to_unknown_capability_rejected(self) -> None:
        registry = CapabilityRegistry((capability("a", yields_to=("missing",)),))
        with self.assertRaises(CapabilityRegistryError):
            validate_registry_references(registry)

    def test_self_yield_rejected(self) -> None:
        registry = CapabilityRegistry((capability("a", yields_to=("a",)),))
        with self.assertRaises(CapabilityRegistryError):
            validate_registry_references(registry)

    def test_duplicate_yield_targets_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            capability("a", yields_to=("b", "b"))

    def test_mutual_yields_allowed(self) -> None:
        registry = CapabilityRegistry(
            (
                capability("a", yields_to=("b",)),
                capability("b", yields_to=("a",)),
            )
        )
        validate_registry_references(registry)


class DefaultAcademicRegistryTests(unittest.TestCase):
    def test_default_registry_has_exact_initial_capabilities(self) -> None:
        registry = build_default_academic_registry()
        self.assertEqual(
            [item.identifier for item in registry],
            [
                "uml-analysis",
                "architecture-review",
                "pfe-review",
                "exam-generation",
                "python-teaching",
            ],
        )

    def test_default_registry_boundaries_and_references_validate(self) -> None:
        registry = build_default_academic_registry()
        validate_registry_references(registry)
        self.assertEqual(len(registry), 5)
        self.assertEqual(registry.get("uml-analysis").yields_to, ("architecture-review",))
        self.assertEqual(registry.get("architecture-review").yields_to, ("uml-analysis",))
        self.assertEqual(registry.get("pfe-review").yields_to, ("architecture-review",))
        self.assertEqual(registry.get("exam-generation").yields_to, ("python-teaching",))
        self.assertEqual(registry.get("python-teaching").yields_to, ("exam-generation",))

    def test_default_registry_owns_expected_artifacts_and_outputs(self) -> None:
        registry = build_default_academic_registry()
        self.assertIn("UML diagram", registry.get("uml-analysis").owned_artifacts)
        self.assertIn("repository", registry.get("architecture-review").owned_artifacts)
        self.assertIn("PFE report", registry.get("pfe-review").owned_artifacts)
        self.assertIn("MCQ", registry.get("exam-generation").owned_outputs)
        self.assertIn("Python student code", registry.get("python-teaching").owned_artifacts)

    def test_default_registry_contains_no_numeric_routing_weights_or_scores(self) -> None:
        registry = build_default_academic_registry()
        for capability_item in registry:
            self.assertFalse(hasattr(capability_item, "weight"))
            self.assertFalse(hasattr(capability_item, "score"))
            self.assertFalse(hasattr(capability_item, "priority_weight"))


if __name__ == "__main__":
    unittest.main()
