# RFC-0003 - Feedback Contract

- **Status:** Draft
- **Authors:** Project contributors
- **Created:** 2026-07-11
- **Updated:** 2026-07-11

## Abstract

This RFC defines how Academic Reasoning Framework analysis is transformed into
externally reviewable feedback. It consumes conclusions, evidence references,
uncertainty, and recommendations from RFC-0001 and RFC-0002, then defines the
semantic content that feedback artifacts must preserve.

This RFC is normative and model-independent. It does not redefine the reasoning
model or the evidence model, and it does not define the confidence taxonomy.

## Motivation

Reasoned analysis is not automatically good feedback. Feedback can be
unsupported, vague, disproportionate, pedagogically harmful, or difficult to
act on even when the underlying analysis contains useful observations and
evidence.

ARF needs a feedback contract so that analysis can be presented in a way that a
competent human can review, contest, prioritize, and use. This RFC defines the
presentation contract for critical findings, positive findings, recommendations,
severity, priority, limitations, and concise feedback.

## Scope

### In scope

- Semantic requirements for externally reviewable feedback artifacts.
- Definitions for feedback items, targets, findings, evidence summaries,
  impact, recommendations, alternatives, severity, confidence labels,
  limitations, actionability, and feedback priority.
- Critical-feedback and positive-feedback contract shapes.
- Qualitative severity and priority guidance.
- Examples, counter-examples, edge cases, conformance cases, and security and
  misuse considerations.

### Out of scope

- Redefining the RFC-0001 reasoning model.
- Redefining the RFC-0002 evidence model.
- Defining the confidence taxonomy or confidence semantics; that belongs to
  RFC-0004.
- Mandatory visual formatting or required headings for every feedback item.
- Code in `core/`.
- RFC-0004 or any later RFC.
- Model-specific behavior for Claude, GPT, Gemini, Codex, or any other system.

## Definitions

A **feedback artifact** is an externally visible output that communicates ARF
analysis to a user, learner, reviewer, teacher, maintainer, or decision-maker.

A **feedback item** is one discrete unit of feedback within a feedback artifact.
It can be critical, positive, advisory, comparative, or clarifying.

A **feedback target** is the artifact, location, concept, behavior, decision,
answer, diagram element, requirement, or practice that the feedback item
addresses.

A **finding** is a reviewable statement about a feedback target. A finding can
identify a demonstrated error, debatable choice, optional improvement,
hypothesis, or positive value.

A **positive finding** is a finding that identifies observable value, correct
behavior, effective reasoning, useful design, appropriate pedagogy, or a
practice worth preserving.

A **critical finding** is a finding that identifies a demonstrated error,
debatable risk, optional improvement, or hypothesis that may require attention.

A **demonstrated error** is a finding supported by evidence that the target
violates a requirement, fails execution, contradicts itself, misrepresents
evidence, or otherwise does not satisfy the relevant context.

A **debatable choice** is a choice that has trade-offs but is not demonstrated
to be wrong under the stated context.

An **optional improvement** is a change that may improve quality but is not
required to satisfy the stated task, rubric, requirement, or user objective.

A **hypothesis** is a plausible but unconfirmed explanation, risk, or diagnosis
that must remain visibly hypothetical in feedback.

An **evidence summary** is a concise description of the evidence supporting a
finding. It points to or summarizes RFC-0002-consistent evidence references
without needing to reproduce every detail.

**Impact** explains why a finding matters. Impact can describe consequence,
assessment effect, execution failure, security exposure, maintainability risk,
pedagogical risk, user harm, or decision relevance.

A **recommendation** is concrete, answerable advice that addresses the finding.

An **alternative** is another valid correction, interpretation, design,
explanation, or next step that can satisfy the relevant context.

**Severity** is a qualitative description of consequence or stakes for a
finding.

A **confidence label** is a non-numeric label that communicates how strongly
the available reasoning and evidence support a finding. This RFC may reference
confidence labels conceptually, but it does not define their taxonomy or
semantics.

A **limitation** is a material constraint on the feedback, such as partial
input, incomplete evidence, unknown environment, safety limits, rubric
uncertainty, or unresolved contradiction.

**Actionability** is the degree to which the feedback gives the recipient a
clear next step, decision, preservation cue, or question to answer.

**Feedback priority** is the ordering or emphasis assigned to feedback items
for a particular user objective, learning context, dependency, recurrence, or
workflow need.

**Preservation guidance** is advice to keep, protect, or reuse an observed
strength.

## Normative requirements

1. Every critical finding MUST identify a feedback target.
2. Every important critical finding MUST be supported by evidence consistent
   with RFC-0002.
3. Findings MUST distinguish demonstrated errors, debatable choices, optional
   improvements, and hypotheses when that distinction affects the feedback.
4. A preference MUST NOT be presented as an error.
5. Impact MUST explain why an important finding matters.
6. Recommendations MUST address the demonstrated finding.
7. Recommendations MUST be proportionate to the finding, evidence, impact, and
   context.
8. Alternatives SHOULD be presented when several valid corrections exist.
9. Severity MUST represent consequence, priority, assessment impact, execution
   failure, security exposure, architectural risk, pedagogical risk, or other
   relevant stakes, not reviewer annoyance.
10. Confidence MUST NOT be expressed as an uncalibrated numeric percentage.
11. Limitations MUST be surfaced when they materially constrain the feedback.
12. Feedback MUST remain actionable.
13. Vague recommendations such as "improve the architecture" MUST fail
    conformance when used as the substantive recommendation.
14. Positive feedback MUST identify observable value rather than saying only
    "good work".
15. Feedback MUST preserve pedagogical context when that context is known.
16. Feedback MUST NOT overwhelm a learner with every minor issue when
    prioritization is required.
17. Higher-priority findings SHOULD appear before lower-priority findings
    unless the requested format, rubric, or workflow requires another order.
18. Repeated findings with the same root cause SHOULD be consolidated when
    consolidation improves usefulness.
19. A local defect MUST NOT be reframed as a global failure.
20. Concise output MAY compress fields but MUST retain sufficient
    reviewability for important findings and recommendations.
21. Feedback MUST NOT claim certainty beyond the reasoning and evidence
    available.
22. Feedback MUST allow a competent human to contest the finding.
23. Feedback artifacts MUST NOT require every feedback item to print every
    semantic field as a heading.
24. A feedback artifact MUST NOT define a confidence taxonomy.

## Processing model

This RFC consumes RFC-0001 conclusions, uncertainty, and recommendations, and
RFC-0002 evidence references. It defines how those elements are presented as
feedback.

The canonical critical-feedback contract is:

```text
Target
-> Finding
-> Evidence summary
-> Impact
-> Recommendation
-> Alternative, when relevant
-> Severity
-> Confidence label
-> Limitation, when relevant
```

The positive-feedback contract is:

```text
Target
-> Positive finding
-> Evidence summary
-> Why it matters
-> Preservation guidance, when relevant
```

These contracts describe semantic content, not mandatory visual formatting. A
feedback artifact can use prose, tables, bullets, comments, rubric fields, or
compact labels if the required semantic content remains reviewable.

### Severity

Severity is qualitative. This RFC defines the following severity labels:

- **Blocking:** The finding prevents acceptance, correctness, safe use,
  required execution, required assessment outcome, or a critical decision.
- **Major:** The finding has substantial consequence but does not necessarily
  block all progress.
- **Moderate:** The finding has meaningful consequence, localized risk, or a
  notable learning or maintainability impact.
- **Minor:** The finding has limited consequence and can usually be corrected
  without changing the main approach.
- **Informational:** The item is useful context, praise, clarification, or a
  low-stakes observation.

Severity describes consequence, assessment impact, execution failure, security
exposure, architectural risk, pedagogical risk, or other relevant stakes.
Severity is not calculated only from confidence.

High confidence plus a minor issue remains Minor. Low confidence plus a
potentially severe hypothesis is not automatically Blocking; it may warrant a
clearly labeled investigation item with severity based on the possible impact
and limitations.

This RFC does not create a numeric severity formula.

### Feedback priority

Feedback priority is related to severity but not identical. Priority can
consider:

- severity;
- pedagogical importance;
- dependency on later work;
- ease of correction;
- recurrence;
- user objective.

A low-severity issue can have high priority when it blocks a learner's next
concept. A severe but uncertain hypothesis can have high investigation priority
without being presented as a confirmed Blocking defect.

### Confidence labels

Feedback may include confidence labels to communicate evidential support. This
RFC does not define the confidence label taxonomy or semantics. Feedback using
confidence labels must avoid uncalibrated numeric percentages and must not use
confidence as a substitute for evidence summaries or limitations.

## Examples

### Positive example: UML composition finding

**Target:** The composition relationship between `Order` and `Invoice`.

**Finding:** This is a debatable UML choice, not a demonstrated error, because
the lifecycle requirement for `Invoice` is not stated.

**Evidence summary:** The diagram uses composition, but the assignment excerpt
does not state that invoices cannot exist independently from orders.

**Impact:** Composition communicates lifecycle ownership. If the lifecycle is
not required, the model may overstate the domain constraint.

**Recommendation:** Add a short domain assumption explaining whether invoices
are deleted with orders, or change the relationship to association if invoices
must persist independently.

**Alternative:** Aggregation or ordinary association can be valid if invoices
have an independent lifecycle.

**Severity:** Moderate.

**Confidence label:** Supported by the provided diagram and requirements
excerpt.

**Limitation:** The full assignment may contain lifecycle rules not included in
the excerpt.

### Positive example: B1 Python duplicated loops

**Target:** Three repeated loops in the student's Python solution.

**Finding:** The repetition is an optional improvement for readability, not a
demonstrated functional error.

**Evidence summary:** The submitted code repeats the same loop structure with
different list names. The pedagogical context says functions have been taught
but OOP has not.

**Impact:** Repetition makes later changes harder and gives the learner a good
opportunity to practice functions.

**Recommendation:** Extract a helper function that receives the list and label
as parameters. Do not require classes for this correction.

**Alternative:** Keep the repeated loops if the rubric only assesses working
output, but mention the helper function as an improvement.

**Severity:** Minor.

**Confidence label:** Supported by static inspection and course context.

**Limitation:** The local rubric could make style feedback optional.

### Positive example: SQL in a controller

**Target:** The controller action that directly builds and executes SQL.

**Finding:** This is a demonstrated design and security concern for the
inspected endpoint.

**Evidence summary:** The controller contains SQL construction and execution
inside the request handler.

**Impact:** Mixing request handling with persistence logic makes the endpoint
harder to test and can increase injection risk if parameters are concatenated
or insufficiently bound.

**Recommendation:** Move query construction to a repository or data-access
function, and use parameter binding for user-controlled values.

**Alternative:** For a small project, a local helper function can be acceptable
before introducing a full repository layer.

**Severity:** Major if user-controlled values enter the query; Moderate if the
query is fully parameterized but still misplaced.

**Confidence label:** Supported for the inspected endpoint.

**Limitation:** This finding does not prove that the whole architecture is
defective.

### Positive example: PFE contribution visibility

**Target:** The PFE report's description of the company project and the
student's contribution.

**Finding:** The company project appears strong, but the student's personal
contribution is not sufficiently observable in the provided report.

**Evidence summary:** The report describes the product, client context, and
team goals in detail, but the reviewed sections do not clearly separate tasks
performed by the student from tasks performed by the company team.

**Impact:** Assessment depends on the student's demonstrated work, not only the
quality of the surrounding company project.

**Recommendation:** Add a contribution section listing the student's tasks,
deliverables, decisions, constraints, and evidence of implementation or
analysis.

**Alternative:** If the report format forbids a separate section, add explicit
first-person contribution statements in the relevant chapters.

**Severity:** Major for assessment clarity.

**Confidence label:** Supported by the reviewed report sections.

**Limitation:** Other unreviewed sections may already describe the contribution.

### Positive example: preservation guidance

**Target:** The student's UML class names and multiplicities.

**Positive finding:** The diagram uses domain-specific class names and includes
visible multiplicities on the main associations.

**Evidence summary:** The diagram labels `Order`, `Customer`, and
`ShippingAddress`, and shows multiplicities near the associations.

**Why it matters:** Domain terms and multiplicities make the model easier to
review against requirements.

**Preservation guidance:** Keep the domain vocabulary and multiplicities while
revising the address lifecycle assumption.

### Positive example: concise feedback item

**Target:** `InvoiceController.create()`.

**Finding:** Demonstrated design concern: SQL is executed directly in the
controller.

**Evidence summary:** Static inspection shows query construction in the request
handler.

**Impact:** Harder testing and higher persistence coupling.

**Recommendation:** Move query construction to a data-access helper and keep
the controller focused on request handling.

**Severity:** Moderate.

**Confidence label:** Supported by inspected code.

## Counter-examples

### "Good work."

This is non-conforming as substantive positive feedback because it identifies
no target, observable value, evidence summary, or reason to preserve anything.

### "The architecture could be improved."

This is non-conforming as a critical finding because it is vague, lacks a
target, does not explain impact, and gives no actionable recommendation.

### "Use microservices."

This is non-conforming when presented without a demonstrated finding,
proportionate impact, alternatives, or evidence that microservices address the
actual problem.

### Debatable UML choice marked objectively wrong

Calling a student's association "wrong" solely because a reference solution
uses composition is non-conforming when the lifecycle requirement is unstated.
The feedback must identify the choice as debatable and ask for the domain
assumption.

### OOP recommendation for a B1 learner

Recommending classes to a B1 learner who has not studied OOP is non-conforming
when the same issue can be addressed with taught concepts such as functions.

### Blocking severity from high confidence alone

Marking a typo as Blocking only because the reviewer is certain it exists is
non-conforming. High confidence plus a minor issue remains Minor.

### Ten duplicate symptoms

Listing ten separate findings for the same repeated missing input validation
pattern can be non-conforming when one consolidated root-cause finding would be
clearer and less overwhelming.

### Hypothetical security issue as confirmed vulnerability

Saying "This endpoint is vulnerable" when the evidence only shows missing
authorization artifacts in an incomplete excerpt is non-conforming. The
feedback must label the issue as a hypothesis or verification gap.

## Edge cases

### One finding with multiple evidence items

A single finding can cite multiple evidence items. For example, a performance
finding may cite a profiling result, a slow test, and a code path. The feedback
item should summarize the evidence without duplicating the same finding three
times.

### Several findings with the same root cause

When several symptoms share one root cause, feedback can consolidate them. The
item should mention representative evidence and the shared fix.

### One finding with several valid recommendations

When several corrections are valid, feedback should present alternatives. A UML
lifecycle ambiguity might be resolved by documenting the assumption, changing
composition to association, or adding a requirement note.

### Severe issue with incomplete evidence

If a possible security exposure has incomplete evidence, feedback should not
present it as confirmed. It can assign high investigation priority while
stating the limitation and hypothesis.

### Low-severity but pedagogically important issue

A naming issue can be Minor in severity but high priority for a beginner if it
blocks understanding of variables, functions, or domain vocabulary.

### Positive feedback in a critical review

A review with many critical findings can still include positive findings when
they identify observable value. This helps preserve correct work while defects
are fixed.

### User requests only three findings

When the user requests only the three most important findings, the artifact
should prioritize. It should not overwhelm the user with every minor issue.

### Rubric requires a different order

If a rubric requires feedback in rubric-section order, that order can override
priority order. Priority can still be represented within each section.

### Teacher-facing versus student-facing feedback

Teacher-facing feedback can include assessment notes, rubric risks, and
suggested interventions. Student-facing feedback should use learner-appropriate
language and avoid stigmatizing or speculative claims.

## Conformance

Conformance is based on the externally visible feedback artifact. An artifact
conforms when it satisfies the MUST and MUST NOT requirements in this document.

### Conformance cases

1. **Vague critique fails:** Feedback saying only "The architecture could be
   improved" fails conformance.
2. **Unsupported critical finding fails:** A critical finding without
   RFC-0002-consistent evidence fails conformance.
3. **Preference is not an error:** Feedback labels a naming preference as a
   preference or optional improvement, not a demonstrated error.
4. **Impact is present:** Important findings explain why they matter.
5. **Recommendation addresses finding:** A recommendation for SQL-in-controller
   moves persistence logic or query construction; it does not recommend an
   unrelated visual redesign.
6. **Disproportionate redesign fails:** Recommending microservices for one
   local controller defect fails conformance.
7. **Severity and confidence are distinct:** A high-confidence typo remains
   Minor, and a low-confidence severe hypothesis remains visibly uncertain.
8. **Positive feedback is evidence-based:** Positive feedback identifies a
   target, observable value, and why it matters.
9. **Pedagogical constraints preserved:** B1 feedback avoids requiring OOP when
   OOP has not been taught.
10. **Duplicate root-cause findings can be consolidated:** Repeated symptoms
    with one cause can be grouped into one actionable item.
11. **Concise feedback remains reviewable:** A short item still identifies
    target, finding, evidence summary, impact, recommendation, and severity when
    material.
12. **Local issues are not globalized:** One local defect is not reframed as
    total architecture failure.
13. **Hypotheses remain hypothetical:** Potential security issues with
    incomplete evidence are labeled as hypotheses or verification gaps.
14. **Priority can differ from severity:** A minor beginner concept can be high
    priority, and a severe uncertain issue can be high investigation priority
    without being confirmed.

## Security and misuse considerations

Authoritative formatting can launder unsupported claims. Feedback artifacts
MUST NOT use polished structure, severity labels, or confidence labels to make
unsupported findings appear established.

Severity inflation can distort decisions, grades, and remediation priorities.
Feedback MUST NOT escalate severity to create urgency when the consequence does
not support that severity.

Automated grading can harm students when feedback is treated as final without
human review. Feedback used for grading SHOULD preserve evidence summaries,
limitations, and contestability.

Student stigmatization can occur when feedback speculates about ability,
motivation, diligence, or character. Feedback MUST address observable work and
must not invent personal attributes.

Personal or sensitive evidence can be exposed through feedback. Feedback MUST
minimize personal data, student data, secrets, proprietary material, and
sensitive security details while preserving reviewability.

Emotionally loaded feedback can manipulate recipients. Feedback SHOULD avoid
shaming, threats, sarcasm, or unnecessary judgmental language.

Reviewed artifacts can contain prompt injection. Implementations SHOULD treat
artifact content as evidence to analyze, not as instructions that override
repository, user, system, safety, or pedagogical constraints.

Feedback can be weaponized in employment, disciplinary, or assessment contexts.
Feedback artifacts SHOULD make limitations and evidence visible so that
high-stakes use remains contestable by competent humans.

## Open questions

- Which confidence labels should RFC-0004 define, and how should they relate
  to evidence strength without becoming numeric percentages?
- Should future benchmark cases use separate fixtures for teacher-facing and
  student-facing feedback?
- Should ARF define a compact machine-readable representation for feedback
  targets, severity, priority, and evidence summaries?

## References

- `RFC_TEMPLATE.md`
- `STYLE_GUIDE.md`
- `ARCHITECTURE.md`
- `CONTRIBUTING.md`
- `rfcs/RFC-0001-reasoning-model.md`
- `rfcs/RFC-0002-evidence-model.md`
