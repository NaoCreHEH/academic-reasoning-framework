import unittest

from core.ontology import RoutingTrace
from core.routing import (
    CapabilityDefinition,
    CapabilityRegistry,
    CapabilityRegistryError,
    CapabilityYieldRule,
    RoutingDecision,
    RoutingRequest,
    StructuredRoutingEngine,
    build_default_academic_registry,
)
from core.routing.engine import RoutingEngineError
from tests.fixtures.routing_cases import ROUTING_CASES


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


class StructuredRoutingFixtureTests(unittest.TestCase):
    def test_required_fixture_cases(self) -> None:
        engine = StructuredRoutingEngine(build_default_academic_registry())
        self.assertEqual(len(ROUTING_CASES), 15)

        for case in ROUTING_CASES:
            with self.subTest(case=case.name):
                decision = engine.route(case.request)
                self.assertEqual(decision.trace.primary_capability, case.expected_primary)
                self.assertEqual(
                    decision.trace.supporting_capabilities,
                    case.expected_supporting,
                )
                self.assertEqual(
                    decision.trace.material_ambiguity is not None,
                    case.expects_ambiguity,
                )


class RoutingRequestTests(unittest.TestCase):
    def test_blank_objective_rejected(self) -> None:
        with self.assertRaises(RoutingEngineError):
            RoutingRequest(user_objective=" ")

    def test_blank_optional_request_field_rejected(self) -> None:
        optional_fields = (
            "primary_artifact",
            "requested_output",
            "domain",
            "explicit_capability",
        )
        for field_name in optional_fields:
            with self.subTest(field=field_name):
                with self.assertRaises(RoutingEngineError):
                    RoutingRequest(user_objective="review", **{field_name: " "})


class RoutingDecisionTests(unittest.TestCase):
    def trace(self, primary: str | None = "a") -> RoutingTrace:
        return RoutingTrace(
            user_objective="review",
            primary_artifact=None,
            requested_output=None,
            primary_capability=primary,
            material_ambiguity=None if primary else "Ambiguous.",
        )

    def test_duplicate_considered_capabilities_rejected(self) -> None:
        with self.assertRaises(RoutingEngineError):
            RoutingDecision(
                trace=self.trace(),
                considered_capabilities=("a", "a"),
            )

    def test_duplicate_rejected_capabilities_rejected(self) -> None:
        with self.assertRaises(RoutingEngineError):
            RoutingDecision(
                trace=self.trace(),
                considered_capabilities=("a", "b"),
                rejected_capabilities=("b", "b"),
            )

    def test_rejected_capability_outside_considered_rejected(self) -> None:
        with self.assertRaises(RoutingEngineError):
            RoutingDecision(
                trace=self.trace(),
                considered_capabilities=("a",),
                rejected_capabilities=("b",),
            )

    def test_primary_outside_considered_rejected(self) -> None:
        with self.assertRaises(RoutingEngineError):
            RoutingDecision(
                trace=self.trace(primary="b"),
                considered_capabilities=("a",),
            )

    def test_rejected_capabilities_are_structurally_valid(self) -> None:
        decision = RoutingDecision(
            trace=self.trace(primary="b"),
            considered_capabilities=("a", "b"),
            rejected_capabilities=("a",),
        )
        self.assertEqual(decision.rejected_capabilities, ("a",))


class StructuredRoutingEngineTests(unittest.TestCase):
    def test_registry_validation_happens_at_engine_construction(self) -> None:
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
            StructuredRoutingEngine(registry)

    def test_considered_capabilities_preserve_registry_insertion_order(self) -> None:
        registry = CapabilityRegistry((capability("b"), capability("a")))
        decision = StructuredRoutingEngine(registry).route(
            RoutingRequest(user_objective="review")
        )
        self.assertEqual(decision.considered_capabilities, ("b", "a"))

    def test_exact_case_insensitive_taxonomy_matching(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(user_objective="create", requested_output="mCq")
        )
        self.assertEqual(decision.trace.primary_capability, "exam-generation")

    def test_surrounding_whitespace_normalization(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(user_objective="create", requested_output="  MCQ  ")
        )
        self.assertEqual(decision.trace.primary_capability, "exam-generation")

    def test_no_substring_parsing(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create",
                requested_output="Create an MCQ about Python",
            )
        )
        self.assertIsNone(decision.trace.primary_capability)
        self.assertIsNotNone(decision.trace.material_ambiguity)

    def test_output_owner_overrides_artifact_owner(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create exam",
                primary_artifact="UML diagram",
                requested_output="examination",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "exam-generation")

    def test_artifact_owner_becomes_supporting_after_output_override(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create exam",
                primary_artifact="UML diagram",
                requested_output="examination",
            )
        )
        self.assertEqual(decision.trace.supporting_capabilities, ("uml-analysis",))

    def test_unique_artifact_owner_selected(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(user_objective="review", primary_artifact="repository")
        )
        self.assertEqual(decision.trace.primary_capability, "architecture-review")

    def test_unique_domain_support_selected_only_without_stronger_signal(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(user_objective="explain", domain="Python")
        )
        self.assertEqual(decision.trace.primary_capability, "python-teaching")

    def test_domain_support_does_not_override_output_owner(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create exam",
                requested_output="MCQ",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "exam-generation")
        self.assertEqual(decision.trace.supporting_capabilities, ())

    def test_domain_support_does_not_become_supporting_for_output_owned_routing(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create questions",
                requested_output="MCQ",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "exam-generation")
        self.assertNotIn("python-teaching", decision.trace.supporting_capabilities)

    def test_domain_support_does_not_become_supporting_for_artifact_owned_routing(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="review architecture",
                primary_artifact="repository",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "architecture-review")
        self.assertEqual(decision.trace.supporting_capabilities, ())

    def test_explicit_applicable_capability_honored(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="review",
                primary_artifact="UML diagram",
                explicit_capability="uml-analysis",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "uml-analysis")

    def test_unknown_explicit_capability_preserves_ambiguity(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="review",
                explicit_capability="quantum-professor",
            )
        )
        self.assertIsNone(decision.trace.primary_capability)
        self.assertIsNotNone(decision.trace.material_ambiguity)

    def test_explicit_inapplicable_capability_does_not_override_output_owner(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create",
                requested_output="MCQ",
                explicit_capability="architecture-review",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "exam-generation")
        self.assertEqual(decision.rejected_capabilities, ("architecture-review",))

    def test_explicit_capability_may_be_honored_without_structural_signals(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="review",
                explicit_capability="uml-analysis",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "uml-analysis")

    def test_duplicate_output_ownership_preserves_ambiguity(self) -> None:
        registry = CapabilityRegistry(
            (
                capability("a", owned_outputs=("report",)),
                capability("b", owned_outputs=("report",)),
            )
        )
        decision = StructuredRoutingEngine(registry).route(
            RoutingRequest(user_objective="create", requested_output="report")
        )
        self.assertIsNone(decision.trace.primary_capability)
        self.assertIsNotNone(decision.trace.material_ambiguity)

    def test_duplicate_artifact_ownership_preserves_ambiguity(self) -> None:
        registry = CapabilityRegistry(
            (
                capability("a", owned_artifacts=("artifact",)),
                capability("b", owned_artifacts=("artifact",)),
            )
        )
        decision = StructuredRoutingEngine(registry).route(
            RoutingRequest(user_objective="review", primary_artifact="artifact")
        )
        self.assertIsNone(decision.trace.primary_capability)
        self.assertIsNotNone(decision.trace.material_ambiguity)

    def test_no_ownership_signal_preserves_ambiguity(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(user_objective="review")
        )
        self.assertIsNone(decision.trace.primary_capability)
        self.assertIsNotNone(decision.trace.material_ambiguity)

    def test_supporting_capabilities_preserve_registry_order(self) -> None:
        registry = CapabilityRegistry(
            (
                capability("domain", supported_domains=("Python",)),
                capability("artifact", owned_artifacts=("Python submission",)),
                capability("output", owned_outputs=("MCQ",)),
            )
        )
        decision = StructuredRoutingEngine(registry).route(
            RoutingRequest(
                user_objective="create",
                primary_artifact="Python submission",
                requested_output="MCQ",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "output")
        self.assertEqual(decision.trace.supporting_capabilities, ("artifact",))

    def test_python_mcq_does_not_add_python_teaching_solely_from_domain(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create questions",
                requested_output="MCQ",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "exam-generation")
        self.assertEqual(decision.trace.supporting_capabilities, ())

    def test_django_repository_architecture_does_not_add_python_teaching_from_domain(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="review repository architecture",
                primary_artifact="repository",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "architecture-review")
        self.assertEqual(decision.trace.supporting_capabilities, ())

    def test_python_submission_question_bank_support_comes_from_artifact_ownership(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create question bank",
                primary_artifact="Python submission",
                requested_output="question bank",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "exam-generation")
        self.assertEqual(decision.trace.supporting_capabilities, ("python-teaching",))

    def test_free_form_output_with_python_domain_routes_from_domain_signal(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="create questions",
                requested_output="Create an MCQ about Python",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "python-teaching")
        self.assertIn(
            "Structured domain is supported by python-teaching.",
            decision.trace.decisive_signals,
        )

    def test_primary_never_appears_in_supporting_capabilities(self) -> None:
        decision = StructuredRoutingEngine(build_default_academic_registry()).route(
            RoutingRequest(
                user_objective="correct",
                primary_artifact="Python student code",
                domain="Python",
            )
        )
        self.assertEqual(decision.trace.primary_capability, "python-teaching")
        self.assertNotIn("python-teaching", decision.trace.supporting_capabilities)

    def test_route_does_not_execute_or_parse_yield_rule_prose(self) -> None:
        registry = CapabilityRegistry(
            (
                capability(
                    "a",
                    yield_rules=(
                        CapabilityYieldRule(
                            target_capability="b",
                            context="Requested output is MCQ.",
                            reason="b owns MCQ in this prose only.",
                        ),
                    ),
                ),
                capability("b"),
            )
        )
        decision = StructuredRoutingEngine(registry).route(
            RoutingRequest(user_objective="create", requested_output="MCQ")
        )
        self.assertIsNone(decision.trace.primary_capability)
        self.assertIsNotNone(decision.trace.material_ambiguity)

    def test_default_registry_domain_mappings_are_deliberate(self) -> None:
        registry = build_default_academic_registry()
        self.assertEqual(registry.get("python-teaching").supported_domains, ("Python",))
        self.assertEqual(registry.get("uml-analysis").supported_domains, ("UML",))
        self.assertEqual(registry.get("architecture-review").supported_domains, ())
        self.assertEqual(registry.get("pfe-review").supported_domains, ())


if __name__ == "__main__":
    unittest.main()
