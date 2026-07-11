import unittest

from core.routing import (
    CapabilityDefinition,
    CapabilityRegistry,
    CapabilityRegistryError,
    CapabilityYieldRule,
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
            yield_rules=(
                CapabilityYieldRule(
                    target_capability="other-capability",
                    context="A specific adjacent context applies.",
                    reason="The other capability owns that context.",
                ),
            ),
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


class CapabilityYieldRuleTests(unittest.TestCase):
    def test_valid_contextual_yield_rule(self) -> None:
        rule = CapabilityYieldRule(
            target_capability="exam-generation",
            context="Requested output is an assessment instrument.",
            reason="Assessment instrument production is owned elsewhere.",
        )
        self.assertEqual(rule.target_capability, "exam-generation")

    def test_blank_target_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            CapabilityYieldRule(
                target_capability=" ",
                context="Specific context.",
                reason="Specific reason.",
            )

    def test_blank_context_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            CapabilityYieldRule(
                target_capability="exam-generation",
                context=" ",
                reason="Specific reason.",
            )

    def test_blank_reason_rejected(self) -> None:
        with self.assertRaises(CapabilityRegistryError):
            CapabilityYieldRule(
                target_capability="exam-generation",
                context="Specific context.",
                reason=" ",
            )

    def test_exact_duplicate_yield_rule_rejected(self) -> None:
        rule = CapabilityYieldRule(
            target_capability="exam-generation",
            context="Requested output is an assessment instrument.",
            reason="Assessment instrument production is owned elsewhere.",
        )
        with self.assertRaises(CapabilityRegistryError):
            capability("a", yield_rules=(rule, rule))

    def test_same_target_with_different_contexts_accepted(self) -> None:
        first = CapabilityYieldRule(
            target_capability="exam-generation",
            context="Requested output is an MCQ.",
            reason="MCQ production is owned by exam-generation.",
        )
        second = CapabilityYieldRule(
            target_capability="exam-generation",
            context="Requested output is a rubric.",
            reason="Rubric production is owned by exam-generation.",
        )
        item = capability("a", yield_rules=(first, second))
        self.assertEqual(item.yield_rules, (first, second))

    def test_multiple_contexts_to_same_target_regression(self) -> None:
        first = CapabilityYieldRule(
            target_capability="architecture-review",
            context="Primary artifact is a repository.",
            reason="Repository architecture is owned by architecture-review.",
        )
        second = CapabilityYieldRule(
            target_capability="architecture-review",
            context="Primary artifact is a running system.",
            reason="Running-system architecture is owned by architecture-review.",
        )
        registry = CapabilityRegistry(
            (
                capability("uml-analysis", yield_rules=(first, second)),
                capability("architecture-review"),
            )
        )
        validate_registry_references(registry)
        self.assertEqual(len(registry.get("uml-analysis").yield_rules), 2)


class RegistryReferenceValidationTests(unittest.TestCase):
    def test_unknown_target_capability_rejected(self) -> None:
        registry = CapabilityRegistry(
            (
                capability(
                    "a",
                    yield_rules=(
                        CapabilityYieldRule(
                            target_capability="missing",
                            context="Specific context.",
                            reason="Specific reason.",
                        ),
                    ),
                ),
            )
        )
        with self.assertRaises(CapabilityRegistryError):
            validate_registry_references(registry)

    def test_self_yield_rejected(self) -> None:
        registry = CapabilityRegistry(
            (
                capability(
                    "a",
                    yield_rules=(
                        CapabilityYieldRule(
                            target_capability="a",
                            context="Specific context.",
                            reason="Specific reason.",
                        ),
                    ),
                ),
            )
        )
        with self.assertRaises(CapabilityRegistryError):
            validate_registry_references(registry)

    def test_mutual_contextual_yields_allowed(self) -> None:
        registry = CapabilityRegistry(
            (
                capability(
                    "a",
                    yield_rules=(
                        CapabilityYieldRule(
                            target_capability="b",
                            context="Context owned by b.",
                            reason="b owns that context.",
                        ),
                    ),
                ),
                capability(
                    "b",
                    yield_rules=(
                        CapabilityYieldRule(
                            target_capability="a",
                            context="Context owned by a.",
                            reason="a owns that context.",
                        ),
                    ),
                ),
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

    def test_default_registry_owns_expected_artifacts_and_outputs(self) -> None:
        registry = build_default_academic_registry()
        self.assertIn("UML diagram", registry.get("uml-analysis").owned_artifacts)
        self.assertIn("repository", registry.get("architecture-review").owned_artifacts)
        self.assertIn("PFE report", registry.get("pfe-review").owned_artifacts)
        self.assertIn("MCQ", registry.get("exam-generation").owned_outputs)
        self.assertIn("Python student code", registry.get("python-teaching").owned_artifacts)

    def test_default_uml_contextual_yield_is_correct(self) -> None:
        rule = build_default_academic_registry().get("uml-analysis").yield_rules[0]
        self.assertEqual(rule.target_capability, "architecture-review")
        self.assertIn("repository, codebase, or running system", rule.context)
        self.assertIn("architecture-review", rule.reason)

    def test_default_architecture_contextual_yield_is_correct(self) -> None:
        rule = build_default_academic_registry().get("architecture-review").yield_rules[0]
        self.assertEqual(rule.target_capability, "uml-analysis")
        self.assertIn("UML diagram or UML model", rule.context)
        self.assertIn("uml-analysis", rule.reason)

    def test_pfe_review_has_no_generic_architecture_yield(self) -> None:
        registry = build_default_academic_registry()
        self.assertEqual(registry.get("pfe-review").yield_rules, ())
        self.assertIn(
            "repository code review",
            registry.get("pfe-review").negative_boundaries[0],
        )

    def test_exam_generation_contextual_yield_to_python_teaching_is_correct(self) -> None:
        rule = build_default_academic_registry().get("exam-generation").yield_rules[0]
        self.assertEqual(rule.target_capability, "python-teaching")
        self.assertIn("Python learner code", rule.context)
        self.assertIn("python-teaching", rule.reason)

    def test_python_teaching_contextual_yield_to_exam_generation_is_correct(self) -> None:
        rule = build_default_academic_registry().get("python-teaching").yield_rules[0]
        self.assertEqual(rule.target_capability, "exam-generation")
        self.assertIn("assessment instrument", rule.context)
        self.assertIn("exam-generation", rule.reason)

    def test_registry_exposes_no_bare_yield_field(self) -> None:
        registry = build_default_academic_registry()
        old_field_name = "yields" + "_to"
        for capability_item in registry:
            self.assertFalse(hasattr(capability_item, old_field_name))

    def test_default_registry_contains_no_numeric_routing_weights_or_scores(self) -> None:
        registry = build_default_academic_registry()
        for capability_item in registry:
            self.assertFalse(hasattr(capability_item, "weight"))
            self.assertFalse(hasattr(capability_item, "score"))
            self.assertFalse(hasattr(capability_item, "priority_weight"))


if __name__ == "__main__":
    unittest.main()
