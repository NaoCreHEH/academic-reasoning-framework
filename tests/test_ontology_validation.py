import unittest

from core.ontology import (
    Claim,
    EvidenceCategory,
    EvidenceItem,
    EvidenceReference,
    OntologyValidationError,
    validate_claim_references,
    validate_evidence_graph,
)


def direct(identifier: str) -> EvidenceItem:
    return EvidenceItem(
        identifier=identifier,
        category=EvidenceCategory.DIRECT_OBSERVATION,
        reference=EvidenceReference(source=f"{identifier}.py"),
        scope=f"{identifier}.py",
        provenance="static inspection",
    )


def derived(identifier: str, *sources: str) -> EvidenceItem:
    return EvidenceItem(
        identifier=identifier,
        category=EvidenceCategory.DERIVED_EVIDENCE,
        reference=EvidenceReference(source="tool output"),
        scope="repository",
        provenance="measurement",
        derived_from=tuple(sources),
        transformation="aggregate source evidence",
    )


class EvidenceGraphValidationTests(unittest.TestCase):
    def test_unknown_derived_source_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            validate_evidence_graph([derived("d1", "missing")])

    def test_self_derivation_rejected(self) -> None:
        item = derived("d1", "d1")
        with self.assertRaises(OntologyValidationError):
            validate_evidence_graph([item])

    def test_two_node_cycle_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            validate_evidence_graph([derived("a", "b"), derived("b", "a")])

    def test_multi_node_cycle_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            validate_evidence_graph(
                [derived("a", "b"), derived("b", "c"), derived("c", "a")]
            )

    def test_valid_derived_chain_accepted(self) -> None:
        items = [direct("e1"), derived("d1", "e1"), derived("d2", "d1")]
        validate_evidence_graph(items)

    def test_duplicate_evidence_identifiers_rejected(self) -> None:
        with self.assertRaises(OntologyValidationError):
            validate_evidence_graph([direct("e1"), direct("e1")])


class ClaimReferenceValidationTests(unittest.TestCase):
    def test_valid_evidence_references_accepted(self) -> None:
        evidence = [direct("e1")]
        claims = [Claim(identifier="c1", text="Claim one", evidence_ids=("e1",))]
        validate_claim_references(claims, evidence)

    def test_unknown_evidence_reference_rejected(self) -> None:
        evidence = [direct("e1")]
        claims = [Claim(identifier="c1", text="Claim one", evidence_ids=("e2",))]
        with self.assertRaises(OntologyValidationError):
            validate_claim_references(claims, evidence)

    def test_duplicate_evidence_references_in_one_claim_rejected(self) -> None:
        evidence = [direct("e1")]
        claims = [Claim(identifier="c1", text="Claim one", evidence_ids=("e1", "e1"))]
        with self.assertRaises(OntologyValidationError):
            validate_claim_references(claims, evidence)

    def test_duplicate_claim_identifiers_rejected(self) -> None:
        evidence = [direct("e1")]
        claims = [
            Claim(identifier="c1", text="Claim one", evidence_ids=("e1",)),
            Claim(identifier="c1", text="Claim two", evidence_ids=("e1",)),
        ]
        with self.assertRaises(OntologyValidationError):
            validate_claim_references(claims, evidence)


if __name__ == "__main__":
    unittest.main()
