"""Built-in structural conformance benchmark cases."""

from core.interpretation import (
    InterpretationCandidate,
    InterpretationConversionError,
    InterpretationState,
    InterpretationValidationError,
    InterpretedSignal,
    InterpretedSubtask,
    SignalKind,
    SignalProvenance,
    SignalProvenanceKind,
    absent_signal,
    resolved_signal,
    to_routing_request,
    unresolved_signal,
)
from core.ontology import (
    Claim,
    ConfidenceAssessment,
    ConfidenceLabel,
    ConfidenceState,
    EvidenceCategory,
    EvidenceItem,
    EvidenceReference,
    FeedbackItem,
    FindingKind,
    OntologyValidationError,
    Severity,
    validate_claim_references,
    validate_evidence_graph,
    validate_feedback_item,
)

from benchmark.conformance.enums import (
    ConformanceDomain,
    ConformanceExpectation,
)
from benchmark.conformance.models import ConformanceCase


def _reference() -> EvidenceReference:
    return EvidenceReference(
        source="repository fixture",
        locator="tests/fixtures",
        description="Machine-readable benchmark fixture.",
    )


def _direct_evidence(identifier: str = "E1") -> EvidenceItem:
    return EvidenceItem(
        identifier=identifier,
        category=EvidenceCategory.DIRECT_OBSERVATION,
        reference=_reference(),
        scope="Single explicit benchmark fixture.",
        provenance="Constructed by conformance benchmark.",
    )


def _derived_evidence(identifier: str = "E2", source_id: str = "E1") -> EvidenceItem:
    return EvidenceItem(
        identifier=identifier,
        category=EvidenceCategory.DERIVED_EVIDENCE,
        reference=_reference(),
        scope="Derived benchmark fixture.",
        provenance="Constructed by conformance benchmark.",
        derived_from=(source_id,),
        transformation="Summarized explicit source evidence.",
    )


def _confidence(
    label: ConfidenceLabel = ConfidenceLabel.CONFIRMED,
) -> ConfidenceAssessment:
    return ConfidenceAssessment(
        target_id="finding-1",
        label=label,
        basis="Direct benchmark evidence supports the structural target.",
    )


def _feedback(
    *,
    identifier: str = "F1",
    finding_kind: FindingKind = FindingKind.DEMONSTRATED_ERROR,
    evidence_summary: str | None = "Direct evidence summary.",
    impact: str | None = "The issue can affect the reviewed outcome.",
    recommendation: str | None = "Address the demonstrated structural issue.",
    severity: Severity = Severity.MAJOR,
    confidence: ConfidenceAssessment | None = None,
) -> FeedbackItem:
    return FeedbackItem(
        identifier=identifier,
        target="target artifact",
        finding="The benchmark finding is structurally represented.",
        finding_kind=finding_kind,
        evidence_summary=evidence_summary,
        impact=impact,
        recommendation=recommendation,
        severity=severity,
        confidence=confidence,
    )


def _provenance() -> SignalProvenance:
    return SignalProvenance(
        kind=SignalProvenanceKind.EXPLICIT_USER_STATEMENT,
        source="benchmark input",
    )


def _candidate(value: str) -> InterpretationCandidate:
    return InterpretationCandidate(
        value=value,
        basis=f"{value} is an explicit benchmark candidate.",
        provenance=(_provenance(),),
    )


def _resolved(kind: SignalKind, value: str) -> InterpretedSignal:
    return resolved_signal(
        kind,
        value,
        provenance=(_provenance(),),
        basis=f"{value} is explicitly supplied.",
    )


def _subtask(**signals: InterpretedSignal) -> InterpretedSubtask:
    return InterpretedSubtask(
        identifier="task-1",
        user_objective=signals.get(
            "user_objective",
            _resolved(SignalKind.USER_OBJECTIVE, "Review the artifact"),
        ),
        primary_artifact=signals.get(
            "primary_artifact",
            absent_signal(SignalKind.PRIMARY_ARTIFACT),
        ),
        requested_output=signals.get(
            "requested_output",
            absent_signal(SignalKind.REQUESTED_OUTPUT),
        ),
        domain=signals.get("domain", absent_signal(SignalKind.DOMAIN)),
        explicit_capability=signals.get(
            "explicit_capability",
            absent_signal(SignalKind.EXPLICIT_CAPABILITY),
        ),
    )


def evidence_direct_observation_valid() -> EvidenceItem:
    return _direct_evidence()


def evidence_derived_valid() -> None:
    source = _direct_evidence("source")
    derived = _derived_evidence("derived", "source")
    validate_evidence_graph((source, derived))


def evidence_derived_without_source_rejected() -> EvidenceItem:
    return EvidenceItem(
        identifier="derived",
        category=EvidenceCategory.DERIVED_EVIDENCE,
        reference=_reference(),
        scope="Invalid derived evidence.",
        provenance="Constructed by conformance benchmark.",
        transformation="Summarized missing source.",
    )


def evidence_derived_without_transformation_rejected() -> EvidenceItem:
    return EvidenceItem(
        identifier="derived",
        category=EvidenceCategory.DERIVED_EVIDENCE,
        reference=_reference(),
        scope="Invalid derived evidence.",
        provenance="Constructed by conformance benchmark.",
        derived_from=("source",),
    )


def evidence_direct_with_lineage_rejected() -> EvidenceItem:
    return EvidenceItem(
        identifier="direct",
        category=EvidenceCategory.DIRECT_OBSERVATION,
        reference=_reference(),
        scope="Invalid direct evidence.",
        provenance="Constructed by conformance benchmark.",
        derived_from=("source",),
    )


def evidence_self_derivation_rejected() -> None:
    evidence = _derived_evidence("self", "self")
    validate_evidence_graph((evidence,))


def evidence_cycle_rejected() -> None:
    first = _derived_evidence("first", "second")
    second = _derived_evidence("second", "first")
    validate_evidence_graph((first, second))


def evidence_unknown_source_rejected() -> None:
    validate_evidence_graph((_derived_evidence("derived", "missing"),))


def claim_without_evidence_structurally_valid() -> Claim:
    return Claim(
        identifier="claim-1",
        text=(
            "This structurally valid claim has no evidence references; the "
            "benchmark does not assess evidence sufficiency."
        ),
    )


def claim_valid_reference() -> None:
    evidence = _direct_evidence("E1")
    claim = Claim(
        identifier="claim-1",
        text="Claim references known evidence.",
        evidence_ids=("E1",),
    )
    validate_claim_references((claim,), (evidence,))


def claim_unknown_evidence_rejected() -> None:
    claim = Claim(
        identifier="claim-1",
        text="Claim references missing evidence.",
        evidence_ids=("missing",),
    )
    validate_claim_references((claim,), ())


def claim_duplicate_evidence_reference_rejected() -> None:
    evidence = _direct_evidence("E1")
    claim = Claim(
        identifier="claim-1",
        text="Claim repeats an evidence reference.",
        evidence_ids=("E1", "E1"),
    )
    validate_claim_references((claim,), (evidence,))


def claim_duplicate_identifier_rejected() -> None:
    first = Claim(identifier="claim-1", text="First claim.")
    second = Claim(identifier="claim-1", text="Second claim.")
    validate_claim_references((first, second), ())


def confidence_confirmed_with_basis_valid() -> ConfidenceAssessment:
    return _confidence(ConfidenceLabel.CONFIRMED)


def confidence_unknown_state_valid() -> ConfidenceAssessment:
    return ConfidenceAssessment(target_id="target-1", state=ConfidenceState.UNKNOWN)


def confidence_not_assessed_state_valid() -> ConfidenceAssessment:
    return ConfidenceAssessment(
        target_id="target-1",
        state=ConfidenceState.NOT_ASSESSED,
    )


def confidence_label_and_state_rejected() -> ConfidenceAssessment:
    return ConfidenceAssessment(
        target_id="target-1",
        label=ConfidenceLabel.CONFIRMED,
        state=ConfidenceState.UNKNOWN,
        basis="Both label and state are set.",
    )


def confidence_neither_label_nor_state_rejected() -> ConfidenceAssessment:
    return ConfidenceAssessment(target_id="target-1")


def confidence_label_without_basis_rejected() -> ConfidenceAssessment:
    return ConfidenceAssessment(
        target_id="target-1",
        label=ConfidenceLabel.CONFIRMED,
    )


def confidence_percentage_rejected() -> ConfidenceAssessment:
    return ConfidenceAssessment(
        target_id="target-1",
        label=ConfidenceLabel.PLAUSIBLE,
        basis="73% confident based on inspection.",
    )


def confidence_speculative_with_basis_valid() -> ConfidenceAssessment:
    return _confidence(ConfidenceLabel.SPECULATIVE)


def feedback_demonstrated_error_valid() -> FeedbackItem:
    return _feedback()


def feedback_demonstrated_error_without_evidence_rejected() -> FeedbackItem:
    return _feedback(evidence_summary=None)


def feedback_debatable_choice_valid() -> FeedbackItem:
    return _feedback(
        finding_kind=FindingKind.DEBATABLE_CHOICE,
        evidence_summary=None,
        recommendation="Describe the trade-off without forcing an error label.",
    )


def feedback_positive_with_evidence_valid() -> FeedbackItem:
    return _feedback(
        finding_kind=FindingKind.POSITIVE_FINDING,
        evidence_summary="Directly observed positive behavior.",
        impact=None,
        recommendation=None,
        severity=Severity.INFORMATIONAL,
    )


def feedback_positive_without_evidence_rejected() -> FeedbackItem:
    return _feedback(
        finding_kind=FindingKind.POSITIVE_FINDING,
        evidence_summary=None,
        impact=None,
        recommendation=None,
    )


def feedback_required_impact_missing_rejected() -> None:
    item = _feedback(impact=None, severity=Severity.BLOCKING)
    validate_feedback_item(item, require_impact=True)


def feedback_required_recommendation_missing_rejected() -> None:
    item = _feedback(recommendation=None, severity=Severity.BLOCKING)
    validate_feedback_item(item, require_recommendation=True)


def feedback_severity_confidence_independent_valid() -> FeedbackItem:
    return _feedback(
        identifier="minor-confirmed",
        severity=Severity.MINOR,
        confidence=_confidence(ConfidenceLabel.CONFIRMED),
    )


def feedback_severe_plausible_valid() -> FeedbackItem:
    return _feedback(
        identifier="major-plausible",
        severity=Severity.MAJOR,
        confidence=_confidence(ConfidenceLabel.PLAUSIBLE),
    )


def interpretation_resolved_valid() -> InterpretedSignal:
    return _resolved(SignalKind.REQUESTED_OUTPUT, "MCQ")


def interpretation_unresolved_candidates_valid() -> InterpretedSignal:
    return unresolved_signal(
        SignalKind.PRIMARY_ARTIFACT,
        candidates=(_candidate("PFE report"), _candidate("academic specification")),
        basis="Two explicit artifact candidates remain possible.",
    )


def interpretation_absent_valid() -> InterpretedSignal:
    return absent_signal(SignalKind.DOMAIN)


def interpretation_resolved_without_provenance_rejected() -> InterpretedSignal:
    return InterpretedSignal(
        kind=SignalKind.REQUESTED_OUTPUT,
        state=InterpretationState.RESOLVED,
        value="MCQ",
        basis="Value supplied without provenance.",
    )


def interpretation_unresolved_with_resolved_value_rejected() -> InterpretedSignal:
    return InterpretedSignal(
        kind=SignalKind.PRIMARY_ARTIFACT,
        state=InterpretationState.UNRESOLVED,
        value="PFE report",
        candidates=(_candidate("PFE report"),),
        basis="Unresolved signal incorrectly has a resolved value.",
    )


def interpretation_unresolved_without_candidate_or_conflict_rejected() -> InterpretedSignal:
    return unresolved_signal(
        SignalKind.PRIMARY_ARTIFACT,
        basis="Unresolved signal lacks candidates or conflict.",
    )


def interpretation_absent_with_value_rejected() -> InterpretedSignal:
    return InterpretedSignal(
        kind=SignalKind.DOMAIN,
        state=InterpretationState.ABSENT,
        value="Python",
    )


def interpretation_unresolved_blocks_routing_conversion() -> None:
    subtask = _subtask(
        primary_artifact=unresolved_signal(
            SignalKind.PRIMARY_ARTIFACT,
            candidates=(_candidate("PFE report"), _candidate("UML diagram")),
            basis="Primary artifact remains unresolved.",
        )
    )
    to_routing_request(subtask)


def interpretation_absent_optional_converts_valid() -> object:
    return to_routing_request(_subtask())


def interpretation_unknown_explicit_capability_converts_valid() -> object:
    subtask = _subtask(
        explicit_capability=_resolved(
            SignalKind.EXPLICIT_CAPABILITY,
            "quantum-professor",
        )
    )
    return to_routing_request(subtask)


def derived_evidence_lineage_preserved() -> None:
    evidence_derived_valid()


CONFORMANCE_CASES: tuple[ConformanceCase, ...] = (
    ConformanceCase(
        identifier="evidence-direct-observation-valid",
        description="Direct observation evidence with no derivation lineage is structurally valid.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.ACCEPT,
        operation=evidence_direct_observation_valid,
        tags=("positive", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="evidence-derived-valid",
        description="Derived evidence with a known source and transformation is structurally valid.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.ACCEPT,
        operation=evidence_derived_valid,
        tags=("positive", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="evidence-derived-without-source-rejected",
        description="Derived evidence without source lineage violates structural invariants.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=evidence_derived_without_source_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="evidence-derived-without-transformation-rejected",
        description="Derived evidence without a transformation violates structural invariants.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=evidence_derived_without_transformation_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="evidence-direct-with-lineage-rejected",
        description="Direct observation evidence must not carry derivation lineage.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=evidence_direct_with_lineage_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="evidence-self-derivation-rejected",
        description="Evidence graph validation rejects self-derivation.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=evidence_self_derivation_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="evidence-cycle-rejected",
        description="Evidence graph validation rejects a derived evidence cycle.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=evidence_cycle_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="evidence-unknown-source-rejected",
        description="Derived evidence cannot reference an unknown source identifier.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=evidence_unknown_source_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="claim-without-evidence-structurally-valid",
        description=(
            "A claim with no evidence IDs is structurally valid only; this "
            "does not prove RFC-0002 evidence sufficiency."
        ),
        domain=ConformanceDomain.CLAIM,
        expectation=ConformanceExpectation.ACCEPT,
        operation=claim_without_evidence_structurally_valid,
        tags=("positive", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="claim-valid-reference",
        description="A claim may reference a known evidence identifier.",
        domain=ConformanceDomain.CLAIM,
        expectation=ConformanceExpectation.ACCEPT,
        operation=claim_valid_reference,
        tags=("positive", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="claim-unknown-evidence-rejected",
        description="Claim reference validation rejects missing evidence IDs.",
        domain=ConformanceDomain.CLAIM,
        expectation=ConformanceExpectation.REJECT,
        operation=claim_unknown_evidence_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="claim-duplicate-evidence-reference-rejected",
        description="Claim reference validation rejects duplicate evidence references.",
        domain=ConformanceDomain.CLAIM,
        expectation=ConformanceExpectation.REJECT,
        operation=claim_duplicate_evidence_reference_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="claim-duplicate-identifier-rejected",
        description="Claim reference validation rejects duplicate claim identifiers.",
        domain=ConformanceDomain.CLAIM,
        expectation=ConformanceExpectation.REJECT,
        operation=claim_duplicate_identifier_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "evidence"),
        rfc_references=("RFC-0002",),
    ),
    ConformanceCase(
        identifier="confidence-confirmed-with-basis-valid",
        description="A Confirmed confidence label with a basis is structurally valid.",
        domain=ConformanceDomain.CONFIDENCE,
        expectation=ConformanceExpectation.ACCEPT,
        operation=confidence_confirmed_with_basis_valid,
        tags=("positive", "structural", "confidence"),
        rfc_references=("RFC-0004",),
    ),
    ConformanceCase(
        identifier="confidence-unknown-state-valid",
        description="Unknown is a valid non-confidence state.",
        domain=ConformanceDomain.CONFIDENCE,
        expectation=ConformanceExpectation.ACCEPT,
        operation=confidence_unknown_state_valid,
        tags=("positive", "structural", "confidence"),
        rfc_references=("RFC-0004",),
    ),
    ConformanceCase(
        identifier="confidence-not-assessed-state-valid",
        description="Not assessed is a valid non-confidence state.",
        domain=ConformanceDomain.CONFIDENCE,
        expectation=ConformanceExpectation.ACCEPT,
        operation=confidence_not_assessed_state_valid,
        tags=("positive", "structural", "confidence"),
        rfc_references=("RFC-0004",),
    ),
    ConformanceCase(
        identifier="confidence-label-and-state-rejected",
        description="Confidence assessment cannot set both label and state.",
        domain=ConformanceDomain.CONFIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=confidence_label_and_state_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "confidence"),
        rfc_references=("RFC-0004",),
    ),
    ConformanceCase(
        identifier="confidence-neither-label-nor-state-rejected",
        description="Confidence assessment requires either a label or a state.",
        domain=ConformanceDomain.CONFIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=confidence_neither_label_nor_state_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "confidence"),
        rfc_references=("RFC-0004",),
    ),
    ConformanceCase(
        identifier="confidence-label-without-basis-rejected",
        description="A confidence label requires a non-empty basis.",
        domain=ConformanceDomain.CONFIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=confidence_label_without_basis_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "confidence"),
        rfc_references=("RFC-0004",),
    ),
    ConformanceCase(
        identifier="confidence-percentage-rejected",
        description="Obvious percentage-confidence phrasing is structurally rejected.",
        domain=ConformanceDomain.CONFIDENCE,
        expectation=ConformanceExpectation.REJECT,
        operation=confidence_percentage_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "confidence"),
        rfc_references=("RFC-0004",),
    ),
    ConformanceCase(
        identifier="confidence-speculative-with-basis-valid",
        description=(
            "Speculative confidence with a basis is structurally valid; the "
            "benchmark does not assess whether that basis is semantically sufficient."
        ),
        domain=ConformanceDomain.CONFIDENCE,
        expectation=ConformanceExpectation.ACCEPT,
        operation=confidence_speculative_with_basis_valid,
        tags=("positive", "structural", "confidence"),
        rfc_references=("RFC-0004",),
    ),
    ConformanceCase(
        identifier="feedback-demonstrated-error-valid",
        description="A demonstrated error with evidence summary is structurally valid.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.ACCEPT,
        operation=feedback_demonstrated_error_valid,
        tags=("positive", "structural", "feedback"),
        rfc_references=("RFC-0003",),
    ),
    ConformanceCase(
        identifier="feedback-demonstrated-error-without-evidence-rejected",
        description="A demonstrated error requires an evidence summary.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.REJECT,
        operation=feedback_demonstrated_error_without_evidence_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "feedback"),
        rfc_references=("RFC-0003",),
    ),
    ConformanceCase(
        identifier="feedback-debatable-choice-valid",
        description=(
            "A debatable choice is structurally valid and is not forced into "
            "DEMONSTRATED_ERROR."
        ),
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.ACCEPT,
        operation=feedback_debatable_choice_valid,
        tags=("positive", "structural", "feedback"),
        rfc_references=("RFC-0003",),
    ),
    ConformanceCase(
        identifier="feedback-positive-with-evidence-valid",
        description="Positive findings require and accept an evidence summary.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.ACCEPT,
        operation=feedback_positive_with_evidence_valid,
        tags=("positive", "structural", "feedback"),
        rfc_references=("RFC-0003",),
    ),
    ConformanceCase(
        identifier="feedback-positive-without-evidence-rejected",
        description="Positive findings without evidence summary are structurally rejected.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.REJECT,
        operation=feedback_positive_without_evidence_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "feedback"),
        rfc_references=("RFC-0003",),
    ),
    ConformanceCase(
        identifier="feedback-required-impact-missing-rejected",
        description="Caller-required impact validation rejects missing impact.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.REJECT,
        operation=feedback_required_impact_missing_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "feedback"),
        rfc_references=("RFC-0003",),
    ),
    ConformanceCase(
        identifier="feedback-required-recommendation-missing-rejected",
        description="Caller-required recommendation validation rejects missing recommendation.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.REJECT,
        operation=feedback_required_recommendation_missing_rejected,
        expected_error=OntologyValidationError,
        tags=("negative", "structural", "feedback"),
        rfc_references=("RFC-0003",),
    ),
    ConformanceCase(
        identifier="feedback-severity-confidence-independent-valid",
        description="Severity.MINOR and ConfidenceLabel.CONFIRMED can coexist structurally.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.ACCEPT,
        operation=feedback_severity_confidence_independent_valid,
        tags=("positive", "structural", "feedback", "confidence"),
        rfc_references=("RFC-0003", "RFC-0004"),
    ),
    ConformanceCase(
        identifier="feedback-severe-plausible-valid",
        description=(
            "Severity.MAJOR and ConfidenceLabel.PLAUSIBLE can coexist structurally; "
            "the benchmark does not claim semantic justification."
        ),
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.ACCEPT,
        operation=feedback_severe_plausible_valid,
        tags=("positive", "structural", "feedback", "confidence"),
        rfc_references=("RFC-0003", "RFC-0004"),
    ),
    ConformanceCase(
        identifier="interpretation-resolved-valid",
        description="A resolved requested-output signal with provenance and basis is valid.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.ACCEPT,
        operation=interpretation_resolved_valid,
        tags=("positive", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-unresolved-candidates-valid",
        description="An unresolved artifact signal with explicit candidates is valid.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.ACCEPT,
        operation=interpretation_unresolved_candidates_valid,
        tags=("positive", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-absent-valid",
        description="An absent domain signal is structurally valid.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.ACCEPT,
        operation=interpretation_absent_valid,
        tags=("positive", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-resolved-without-provenance-rejected",
        description="Resolved interpretation signals require provenance.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.REJECT,
        operation=interpretation_resolved_without_provenance_rejected,
        expected_error=InterpretationValidationError,
        tags=("negative", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-unresolved-with-resolved-value-rejected",
        description="Unresolved interpretation signals must not contain a resolved value.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.REJECT,
        operation=interpretation_unresolved_with_resolved_value_rejected,
        expected_error=InterpretationValidationError,
        tags=("negative", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-unresolved-without-candidate-or-conflict-rejected",
        description="Unresolved signals require candidates or a conflict.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.REJECT,
        operation=interpretation_unresolved_without_candidate_or_conflict_rejected,
        expected_error=InterpretationValidationError,
        tags=("negative", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-absent-with-value-rejected",
        description="Absent interpretation signals must not contain a value.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.REJECT,
        operation=interpretation_absent_with_value_rejected,
        expected_error=InterpretationValidationError,
        tags=("negative", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-unresolved-blocks-routing-conversion",
        description="Unresolved primary artifact signals cannot enter routing conversion.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.REJECT,
        operation=interpretation_unresolved_blocks_routing_conversion,
        expected_error=InterpretationConversionError,
        tags=("negative", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-absent-optional-converts-valid",
        description="Absent optional interpretation signals convert to a routing request.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.ACCEPT,
        operation=interpretation_absent_optional_converts_valid,
        tags=("positive", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="interpretation-unknown-explicit-capability-converts-valid",
        description="Unknown explicit capability values convert without registry validation.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.ACCEPT,
        operation=interpretation_unknown_explicit_capability_converts_valid,
        tags=("positive", "structural", "interpretation"),
        rfc_references=("RFC-0006",),
    ),
    ConformanceCase(
        identifier="minor-confirmed-feedback-valid",
        description="Cross-contract case: Minor severity can coexist with Confirmed confidence.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.ACCEPT,
        operation=feedback_severity_confidence_independent_valid,
        tags=("positive", "structural", "feedback", "confidence", "cross-contract"),
        rfc_references=("RFC-0003", "RFC-0004"),
    ),
    ConformanceCase(
        identifier="major-plausible-feedback-valid",
        description="Cross-contract case: Major severity can coexist with Plausible confidence.",
        domain=ConformanceDomain.FEEDBACK,
        expectation=ConformanceExpectation.ACCEPT,
        operation=feedback_severe_plausible_valid,
        tags=("positive", "structural", "feedback", "confidence", "cross-contract"),
        rfc_references=("RFC-0003", "RFC-0004"),
    ),
    ConformanceCase(
        identifier="unresolved-artifact-does-not-enter-routing",
        description="Cross-contract case: unresolved interpretation artifact is rejected before routing.",
        domain=ConformanceDomain.INTERPRETATION,
        expectation=ConformanceExpectation.REJECT,
        operation=interpretation_unresolved_blocks_routing_conversion,
        expected_error=InterpretationConversionError,
        tags=("negative", "structural", "interpretation", "cross-contract"),
        rfc_references=("RFC-0005", "RFC-0006"),
    ),
    ConformanceCase(
        identifier="derived-evidence-lineage-preserved",
        description="Cross-contract case: valid derived evidence lineage is graph-validated.",
        domain=ConformanceDomain.EVIDENCE,
        expectation=ConformanceExpectation.ACCEPT,
        operation=derived_evidence_lineage_preserved,
        tags=("positive", "structural", "evidence", "cross-contract"),
        rfc_references=("RFC-0002",),
    ),
)
