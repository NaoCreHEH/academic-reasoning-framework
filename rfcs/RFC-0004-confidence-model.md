# RFC-0004 - Confidence Model

- **Status:** Draft
- **Authors:** Project contributors
- **Created:** 2026-07-11
- **Updated:** 2026-07-11

## Abstract

This RFC defines how the Academic Reasoning Framework communicates the degree
of support available for a claim, finding, or conclusion. It refines the
uncertainty and confidence concepts used by RFC-0001 and RFC-0003.

The confidence model is qualitative and model-independent. It does not define
evidence strength from RFC-0002, severity from RFC-0003, feedback priority, a
numeric formula, or calibrated probability.

## Motivation

ARF artifacts need a way to communicate how strongly available support backs a
target without pretending to have more precision than the evidence allows.
Confidence labels can help readers decide whether a finding is established,
plausible, uncertain, or outside the performed analysis.

Confidence labels can also mislead. They can be confused with severity,
inflated by fluent writing, treated as model self-certainty, or presented as
uncalibrated numeric percentages. This RFC defines a bounded qualitative model
so confidence remains reviewable and contestable.

## Scope

### In scope

- A qualitative confidence taxonomy for claims, findings, and conclusions.
- Non-confidence states for unavailable or intentionally skipped evaluation.
- Requirements for confidence basis, confidence boundaries, downgrades,
  upgrades, revision, contradictions, provenance, freshness, and scope.
- Examples, counter-examples, edge cases, conformance cases, and security and
  misuse considerations.

### Out of scope

- Redefining RFC-0002 evidence strength.
- Defining severity or feedback priority.
- Universal numeric confidence percentages or formulas.
- Claims of calibration by default.
- Code in `core/`.
- RFC-0005 or any later RFC.
- Model-specific behavior for Claude, GPT, Gemini, Codex, or any other system.

## Definitions

**Confidence** is a qualitative expression of how strongly available support
backs a specific confidence target.

A **confidence label** is one of the five support labels defined by this RFC:
Confirmed, Strongly supported, Supported, Plausible, or Speculative.

A **confidence basis** is the reviewable reason for assigning a confidence
label or non-confidence state. It includes relevant evidence, contradictions,
scope, provenance, freshness, and material limitations.

A **confidence target** is the specific claim, finding, or conclusion being
evaluated.

**Direct support** is support from evidence that directly establishes or
directly bears on the confidence target.

**Corroborated support** is support strengthened by two or more relevant
evidence items that independently or additionally support the same target.

**Derived support** is support from transformed, aggregated, calculated, or
summarized evidence. It depends on the source evidence and transformation.

**Limited support** is support constrained by partial input, scope boundaries,
stale evidence, unknown provenance, missing corroboration, or unresolved
limitations.

**Contradictory support** exists when relevant evidence materially conflicts
with the confidence target or with evidence used to support it.

**Material uncertainty** is uncertainty that could change the confidence label,
non-confidence state, conclusion, finding, or recommendation.

A **confidence downgrade** is a change to a lower support label or to a
non-confidence state because support became weaker, narrower, stale,
contradictory, or less reviewable.

A **confidence upgrade** is a change to a stronger support label because new
evidence, resolved contradiction, better provenance, stronger scope, or safe
reproduction increases support.

A **confidence revision** is any justified change to the confidence label,
non-confidence state, confidence basis, or confidence boundary.

A **confidence boundary** is the exact scope of what a confidence label applies
to. It prevents local confidence from being generalized to a different claim.

**Unknown** is a non-confidence state used when the available material is
insufficient to evaluate the target.

**Not assessed** is a non-confidence state used when the target was
intentionally outside the performed analysis.

## Normative requirements

1. Confidence MUST attach to a specific confidence target.
2. Important confidence labels MUST have a confidence basis.
3. Confidence MUST reflect available support, contradictions, scope,
   provenance, freshness, and material limitations.
4. Confidence MUST NOT be inferred from writing fluency.
5. Confidence MUST NOT be inferred from model self-certainty.
6. Confidence MUST NOT use uncalibrated percentages.
7. High confidence MUST NOT increase severity.
8. Low confidence MUST NOT reduce potential consequence.
9. Severity and confidence MUST remain independent.
10. Priority and confidence MUST remain independent.
11. Missing evidence MUST NOT automatically produce Speculative.
12. Insufficient evaluability SHOULD produce Unknown.
13. Intentionally skipped analysis SHOULD produce Not assessed.
14. Speculative claims MUST still have an attributable basis.
15. Material contradictory evidence MUST prevent Confirmed unless the
    contradiction is resolved or scoped out with justification.
16. Direct decisive evidence MAY justify Confirmed without corroboration.
17. Corroboration MAY upgrade confidence but MUST NOT automatically produce
    Confirmed.
18. Derived evidence MUST NOT create higher confidence than its source evidence
    and transformation justify.
19. Stale evidence MAY require a downgrade when freshness is material.
20. Scope mismatch MUST limit confidence.
21. Confidence MUST be revised when material premises or evidence change.
22. Confidence labels MUST NOT substitute for evidence summaries.
23. Confidence labels MUST remain contestable by a competent human.
24. Confidence MAY be omitted from low-stakes feedback when omission is not
    misleading.
25. Confidence MUST be explicit for important uncertain findings when omission
    could mislead.
26. A confidence downgrade MUST identify the material reason when relevant.
27. A confidence upgrade SHOULD identify the new evidence or resolved
    limitation.
28. Unknown provenance MAY limit confidence.
29. One decisive observation MAY support Confirmed.
30. A majority of weak evidence items MUST NOT automatically outweigh one
    decisive contradiction.

## Processing model

This RFC refines confidence and uncertainty. It consumes evidence items and
evidence strength factors from RFC-0002, but it does not redefine them.

The conceptual confidence relationship is:

```text
Confidence target
-> evaluated against Evidence Item(s)
-> considers Evidence strength factors from RFC-0002
-> considers Contradictions
-> considers Limitations
-> produces Confidence label or non-confidence state
-> may be revised when evidence changes
```

### Confidence support labels

RFC-0004 defines exactly five confidence support labels:

- **Confirmed:** The target is directly established by decisive evidence or
  safe reproduction under the relevant scope.
- **Strongly supported:** Multiple relevant evidence items or strong
  corroboration support the target with no material unresolved contradiction.
- **Supported:** Relevant evidence and a defensible inference support the
  target, but some limitation, scope boundary, or missing corroboration remains.
- **Plausible:** The target is a reasonable hypothesis or interpretation with
  partial support, but alternative explanations remain materially viable.
- **Speculative:** The target is possible but weakly supported, substantially
  dependent on assumptions, or not sufficiently evidenced for action beyond
  investigation.

These labels are not probabilities. ARF MUST NOT claim calibration unless a
future implementation independently demonstrates calibration for a specific
context and method.

### Non-confidence states

RFC-0004 defines two non-confidence states:

- **Unknown:** The available material is insufficient to evaluate the target.
- **Not assessed:** The target was intentionally outside the performed
  analysis.

Unknown is not Speculative. Not assessed is not Unknown. Speculative still
requires some basis. Unknown means support cannot currently be evaluated. Not
assessed means no evaluation was performed.

### Confidence boundaries

A confidence label applies only to the specific confidence target evaluated.

Confirmed that a hard-coded token exists in `settings.py` does not imply
Confirmed that the token is active. It also does not imply Confirmed that the
system has been breached.

Confidence boundaries SHOULD identify the artifact, behavior, source, time
window, environment, or scope that the label covers when those limits matter.

### Confidence revision

Confidence revision is not a failure. Refusing to revise confidence when
material evidence changes is a reasoning failure.

Initial confidence:

Plausible - authorization may be missing.

New evidence:

Global middleware configuration is inspected and no authorization middleware is
registered.

Revised confidence:

Strongly supported or Confirmed, depending on whether the target is "not
demonstrated in inspected application configuration" or "absent from every
runtime enforcement layer."

New evidence:

An API gateway policy protects the route.

Revised confidence:

The previous conclusion is withdrawn, narrowed, or reframed as an
application-layer gap rather than an unprotected route.

## Examples

### Positive example: Python test failure reproduced locally

**Confidence target:** `total_price()` fails
`test_total_price_applies_discount` in the current checkout.

**Confidence basis:** The reviewer safely ran the test and observed expected
`90` and actual `100`.

**Confidence label:** Confirmed.

**Boundary:** The current checkout and local test environment.

**Limitation:** This does not confirm behavior in other branches or
environments.

### Positive example: hard-coded credential observed statically

**Confidence target:** The inspected file contains a hard-coded credential-like
value.

**Confidence basis:** Static inspection shows a literal value assigned to
`API_KEY`.

**Confidence label:** Confirmed.

**Boundary:** The inspected file.

**Limitation:** This does not confirm that the credential is valid, active, or
exploited.

### Positive example: UML composition with incomplete lifecycle requirements

**Confidence target:** Composition between `Order` and `Invoice` is a
demonstrated modeling error.

**Confidence basis:** The diagram uses composition, but the provided
requirements do not state whether invoices share the order lifecycle.

**Confidence label:** Plausible for a lifecycle mismatch; not Confirmed.

**Boundary:** The provided diagram and requirements excerpt.

**Limitation:** Missing lifecycle requirements keep alternatives viable.

### Positive example: missing authorization artifacts

**Confidence target:** Authorization is absent from the whole system.

**Confidence basis:** Provided controller files do not show authorization, but
global middleware, gateway policy, and deployment configuration are omitted.

**Confidence state:** Unknown for whole-system absence.

**Alternative target:** Authorization is not demonstrated in the provided
controller excerpt.

**Alternative confidence label:** Confirmed.

### Positive example: contradictory documentation and runtime behavior

**Confidence target:** The feature is disabled.

**Confidence basis:** Documentation says disabled, but runtime behavior shows
the feature is enabled.

**Confidence label:** Not Confirmed; at most Plausible for documentation
intent.

**Boundary:** Current runtime behavior contradicts the documentation.

**Revision:** Confidence must change if documentation version or runtime
configuration is clarified.

### Positive example: PFE contribution finding

**Confidence target:** The student's personal contribution is not observable in
the selected report sections.

**Confidence basis:** Reviewed sections describe the company project but do not
separate the student's tasks, deliverables, or decisions.

**Confidence label:** Supported.

**Boundary:** Selected report sections only.

**Limitation:** Other report sections may document the contribution.

### Positive example: confidence revision after new evidence

**Initial target:** Authorization may be missing.

**Initial label:** Plausible.

**New evidence:** Application middleware configuration is inspected and no
authorization middleware is registered.

**Revised label:** Strongly supported for an application-layer authorization
gap.

**Further evidence:** API gateway policy protects the route.

**Revised outcome:** Withdraw the broader unprotected-route finding or narrow
it to application-layer defense-in-depth.

### Positive example: Unknown versus Speculative

**Unknown:** The reviewer cannot evaluate whether tests exist because only two
source files were provided.

**Speculative:** The two source files show no dependency injection, and the
project style may make tests difficult, but the test suite is not visible.

Speculative has a basis. Unknown is used when support cannot be evaluated.

### Positive example: Not assessed

**Confidence target:** Cryptographic implementation safety.

**State:** Not assessed.

**Basis:** The review scope was limited to feedback structure and did not
include security-domain analysis.

## Counter-examples

### `73% confident`

This is non-conforming as an uncalibrated numeric percentage.

### "I feel very confident"

This is non-conforming because personal or model self-certainty is not a
confidence basis.

### Fluent wording as high confidence

Treating polished prose as Strongly supported is non-conforming. Confidence
depends on support, not fluency.

### Typo marked Blocking because it is Confirmed

A confirmed typo remains low severity if its consequence is minor. Confidence
does not define severity.

### Severe security hypothesis dismissed because it is Plausible

A Plausible security hypothesis can still have severe possible consequence and
high investigation priority. Confidence does not reduce potential consequence.

### Speculative with no evidence

Calling a claim Speculative when there is no attributable basis is
non-conforming. Use Unknown when the target cannot be evaluated.

### Unknown for intentionally skipped work

Using Unknown for a domain explicitly outside review scope is non-conforming.
Use Not assessed.

### Repeated weak sources as automatic upgrade

Three sources repeating the same unsupported claim do not automatically make a
target Strongly supported or Confirmed.

### Derived metric above its inputs

A generated complexity report with unknown input files cannot be treated as
more certain than the source data and transformation justify.

### Refusing revision

Keeping Confirmed after new contradictory gateway evidence appears is
non-conforming unless the contradiction is resolved or scoped out.

## Edge cases

### One decisive direct observation

One direct observation can support Confirmed when it directly establishes the
target, such as a hard-coded token visibly present in an inspected file.

### Correlated non-independent sources

Several blog posts copied from the same original source do not provide the same
upgrade as independent corroboration.

### Contradictory sources with different scopes

Documentation for version 1 and runtime behavior for version 2 may both be
correct within their scopes. Confidence must attach to the scoped target.

### Stale official documentation

Official documentation can be stale. If freshness is material, stale docs may
downgrade confidence about current behavior.

### User-provided logs

User-provided logs that cannot be reproduced can support a claim about reported
behavior, but provenance and reproduction limits may prevent Confirmed for
current behavior.

### Generated summaries with unknown provenance

A generated report can be inspected as an artifact, but unknown provenance may
limit confidence in claims about original source behavior.

### Local versus global architecture claim

Confirmed that one controller executes SQL directly does not confirm that the
entire architecture is defective.

### Irrelevant correct observation

A correct observation that a file has 400 lines does not increase confidence
that authentication is missing.

### Concise output omits confidence

Low-stakes concise feedback may omit confidence when the omission is not
misleading and the item remains reviewable.

### Confidence attached to a recommendation

Confidence SHOULD normally attach to the claim or finding that justifies a
recommendation. A recommendation may have separate feasibility uncertainty, but
recommendation confidence MUST NOT obscure the support level of the underlying
finding.

## Conformance

Conformance is based on externally observable behavior in the artifact or
implementation output. A conforming artifact satisfies the MUST and MUST NOT
requirements in this document.

### Conformance cases

1. **Exactly five labels:** RFC-0004 support labels are Confirmed, Strongly
   supported, Supported, Plausible, and Speculative.
2. **Non-confidence states:** Unknown and Not assessed are non-confidence
   states.
3. **Unknown differs from Speculative:** Unknown is not treated as Speculative.
4. **Not assessed differs from Unknown:** Not assessed is not treated as
   Unknown.
5. **Speculative requires basis:** A Speculative claim identifies attributable
   support.
6. **One decisive observation can Confirm:** A hard-coded token can support
   Confirmed for token presence without corroboration.
7. **Contradiction blocks Confirmed:** Unresolved material contradiction blocks
   Confirmed.
8. **Confidence and severity independent:** A confirmed typo remains Minor.
9. **Confidence and priority independent:** A Plausible severe issue can have
   high investigation priority.
10. **Stale evidence downgrades:** Stale evidence can downgrade confidence when
    freshness is material.
11. **Scope mismatch limits confidence:** Local evidence does not confirm a
    global architecture claim.
12. **Revision after evidence change:** Confidence is revised after material
    evidence changes.
13. **Labels do not replace evidence:** A label without an evidence summary
    fails for important claims.
14. **Self-certainty rejected:** Model self-certainty is rejected as a basis.
15. **Percentages fail:** Uncalibrated numeric percentages fail conformance.
16. **Weak repetition does not defeat contradiction:** Repeated weak sources do
    not automatically outweigh decisive contradictory evidence.
17. **Omission allowed:** Omitted confidence is acceptable for low-stakes
    feedback when non-misleading.
18. **Important uncertainty exposed:** Important uncertain findings expose
    confidence when omission would mislead.

## Security and misuse considerations

False precision can make unsupported analysis appear measured. Artifacts MUST
NOT use uncalibrated numeric percentages or formulas for confidence.

Confidence laundering occurs when a label makes weak support look stronger than
the evidence allows. Artifacts MUST keep labels tied to evidence summaries and
limitations.

Automation bias can cause readers to overtrust confidence labels. Artifacts
SHOULD preserve contestability and avoid implying calibration by default.

High-confidence hallucinations are especially harmful. Implementations MUST NOT
use model self-certainty as a confidence basis.

Coordinated or duplicated source amplification can create false corroboration.
Artifacts SHOULD identify when sources are correlated or non-independent.

Manipulated evidence can be designed to trigger confidence upgrades.
Implementations SHOULD consider provenance, freshness, and contradiction before
upgrading.

Suppressing contradictory evidence can falsely preserve high confidence.
Artifacts MUST surface material contradictions.

Grading harm can occur when confidence labels are mistaken for final truth.
Educational uses SHOULD expose limitations and preserve room for human review.

Employment and disciplinary contexts can misuse confidence labels as proof.
High-stakes uses SHOULD require evidence review and clear confidence
boundaries.

Confidence labels can be misread as calibrated probabilities. Artifacts MUST
state or preserve the qualitative nature of the labels when that risk is
material.

Evidence sources can contain prompt injection. Implementations SHOULD treat
source content as data to evaluate, not instructions that override system,
user, repository, safety, or pedagogical constraints.

## Open questions

- Should future implementations define domain-specific calibration studies for
  confidence labels?
- Should ARF define machine-readable fields for confidence target, boundary,
  basis, and revision history?
- How should benchmarks represent confidence revision across multi-turn
  evidence updates?

## References

- `RFC_TEMPLATE.md`
- `STYLE_GUIDE.md`
- `ARCHITECTURE.md`
- `CONTRIBUTING.md`
- `rfcs/RFC-0001-reasoning-model.md`
- `rfcs/RFC-0002-evidence-model.md`
- `rfcs/RFC-0003-feedback-contract.md`
