# RFC-0001 - Reasoning Model

- **Status:** Draft
- **Authors:** Project contributors
- **Created:** 2026-07-11
- **Updated:** 2026-07-11

## Abstract

This RFC defines the Academic Reasoning Framework reasoning model. It is a
normative, model-independent contract for reviewable academic and
software-engineering analysis.

The contract requires externally reviewable justification: inputs, context,
observations, evidence references, inference summaries, assumptions,
hypotheses, conclusions, recommendations, uncertainty, and falsifiers. It does
not require disclosure of private, hidden, or internal chain-of-thought.

## Motivation

Academic and software-engineering feedback can look precise while mixing facts,
interpretations, guesses, and advice. That makes the feedback difficult to
review, contest, teach from, or safely act on.

ARF separates normative reasoning rules from model-specific implementations.
This RFC defines the first normative reasoning contract. Later schemas,
benchmarks, ontology entries, and implementations can test against this
contract without depending on a specific model, prompt format, vendor, agent, or
hidden reasoning process.

## Scope

### In scope

- A model-independent reasoning contract for academic and software-engineering
  analysis.
- Definitions for input, context, observation, evidence, inference, hypothesis,
  conclusion, recommendation, uncertainty, falsifier, and pedagogical context.
- A normative reasoning pipeline from input through reviewability check.
- Requirements for traceability, uncertainty, falsifiability, proportionality,
  multiple valid solutions, pedagogy, and contestability.
- Positive examples, counter-examples, edge cases, conformance cases, and
  security and misuse considerations.

### Out of scope

- Model-specific behavior for Claude, GPT, Gemini, Codex, or any other system.
- Disclosure of hidden chain-of-thought or private internal reasoning.
- Code in `core/`.
- RFC-0002 or any later RFC.
- Domain-specific professional standards that override generic engineering or
  academic heuristics.

## Definitions

**Input** is the material the analysis is asked to evaluate. Input can include
code, prose, requirements, diagrams, logs, test results, screenshots,
assignments, rubrics, questions, or user instructions.

**Context** is the relevant frame for evaluating the input. Context includes the
task, audience, constraints, domain, repository conventions, pedagogical level,
known requirements, and decision stakes.

**Observation** is an externally inspectable statement about the input or
context. An observation describes what is present, absent, quoted, executed,
measured, reproduced, configured, or otherwise available for review.

**Evidence** is the support used to evaluate a claim. Evidence can include
observations, citations, source references, test outputs, static inspection,
execution results, documentation, requirements, diagrams, or other reviewable
materials.

**Evidence reference** is a pointer to evidence that a competent reviewer can
inspect, such as a file path, line number, command result, cited source, diagram
element, requirement identifier, or quoted excerpt.

**Inference** is a summarized reasoning step from evidence to a claim. An
inference explains why the evidence supports, weakens, or fails to establish a
claim.

**Hypothesis** is a plausible but not established explanation, diagnosis,
prediction, interpretation, or design option.

**Hypothesis management** is the practice of keeping hypotheses separate from
facts, comparing plausible alternatives, and revising or rejecting hypotheses
when evidence changes.

**Validation** is the process of checking whether evidence, assumptions,
inferences, hypotheses, conclusions, or recommendations are supported by the
available material.

**Conclusion** is a supported judgment derived from the input, context,
evidence, assumptions, and inferences.

**Recommendation** is answerable advice about what to do next. A recommendation
can include a change, investigation, acceptance, rejection, warning, or decision.

**Uncertainty** is a material limit on what is known, tested, observed, or
reasonably inferred.

**Falsifier** is a foreseeable observation, test result, source, or condition
that would weaken, overturn, or require revision of a debatable conclusion or
hypothesis.

**Pedagogical context** is the learner-facing frame for analysis. It includes
the learner's expected level, taught concepts, allowed techniques, assignment
scope, rubric, and appropriate next learning step.

**Assumption** is a premise accepted for the analysis without being directly
demonstrated by the available evidence.

**Traceability** is the ability to follow a recommendation or conclusion back to
the input, context, observations, evidence references, assumptions, and
inference summaries that support it.

**Reviewability** is the property that a competent human can inspect,
challenge, reproduce where appropriate, and revise the justification from the
externally visible artifact.

**Multiple valid solutions** means that different answers, designs, diagrams,
or corrections can be defensible when they satisfy the same relevant
requirements under different priorities or modeling choices.

**Demonstrated error** is a defect directly supported by evidence.

**Debatable choice** is a choice that has trade-offs but is not shown to be
incorrect.

**Optional improvement** is a change that may improve quality but is not
required to satisfy the stated task or constraints.

## Normative requirements

1. An analysis artifact MUST establish relevant context before evaluating the
   input.
2. An analysis artifact MUST separate observations from interpretations.
3. An analysis artifact MUST preserve a traceable reasoning path from
   recommendation or conclusion back to context, observations, evidence
   references, assumptions, and inference summaries.
4. An analysis artifact MUST NOT infer presence or absence solely from missing
   evidence.
5. An analysis artifact MUST express material uncertainty explicitly.
6. A conclusion MUST NOT introduce a new premise that was not present in the
   input, context, evidence, assumptions, hypotheses, or inference summaries.
7. Important debatable conclusions SHOULD state at least one foreseeable
   falsifier.
8. Recommendations MUST be proportionate to the demonstrated problem, risk,
   cost, and reversibility.
9. An analysis artifact SHOULD recognize multiple valid solutions when the
   input, context, or requirements allow them.
10. An analysis artifact MUST respect pedagogical-level constraints when giving
    educational feedback.
11. Important recommendations MUST be concrete and answerable.
12. Reasoning artifacts MUST remain contestable by a competent human reviewer.
13. An analysis artifact MUST distinguish demonstrated errors, debatable
    choices, optional improvements, and hypotheses when those categories affect
    the feedback.
14. Conclusions MUST be re-evaluated when a material premise changes.
15. An analysis artifact MUST provide reviewable justification without
    requesting, requiring, or exposing hidden chain-of-thought.
16. Evidence references SHOULD be as specific as the context reasonably allows.
17. Validation SHOULD use static inspection when static evidence is sufficient.
18. Validation MUST NOT require unsafe, destructive, privacy-violating, or
    unauthorized execution.
19. Concise output MAY omit detailed explanation when requested, but it MUST
    retain enough reviewable justification for material conclusions and
    recommendations.
20. Domain requirements MUST override generic engineering heuristics when the
    domain requirement is identified and relevant.

## Processing model

The normative reasoning pipeline is:

```text
Input
-> Context
-> Observation
-> Evidence
-> Inference
-> Hypothesis management
-> Validation
-> Conclusion
-> Recommendation
-> Reviewability check
```

A conforming artifact can combine stages in presentation, but it must preserve
the conceptual distinctions required by this RFC.

### Input

The artifact identifies the material under analysis. If the input is partial,
the artifact states that limitation when it materially affects the analysis.

### Context

The artifact identifies the evaluation frame before judging correctness or
quality. Context can include assignment level, repository rules, architecture,
user goal, risk level, security expectations, or accepted constraints.

### Observation

The artifact records externally inspectable facts about the input or context.
Observations are not causal explanations unless the cause itself is directly
shown by the evidence.

### Evidence

The artifact links observations and claims to evidence references. Evidence can
come from static inspection, execution, documentation, tests, requirements, or
quoted material.

### Inference

The artifact summarizes why the evidence supports or weakens a claim. It keeps
the reasoning reviewable without requiring private chain-of-thought.

### Hypothesis management

The artifact labels plausible but unproven explanations as hypotheses. It
keeps alternative hypotheses available when the evidence does not decide between
them.

### Validation

The artifact checks whether the evidence supports the claim. Validation can be
static, dynamic, comparative, source-based, rubric-based, or constrained by
safety and access limits.

### Conclusion

The artifact states only what follows from the validated evidence, assumptions,
and inference summaries. It includes uncertainty when uncertainty is material.

### Recommendation

The artifact proposes concrete next steps when action is appropriate. The
recommendation addresses the demonstrated problem and remains proportionate to
the evidence.

### Reviewability check

The artifact checks whether a competent human can contest the reasoning. The
check verifies that material claims have evidence references, assumptions are
visible, important debatable conclusions have falsifiers when relevant, and no
hidden chain-of-thought is required.

## Examples

### Positive example: software design review

**Input:** A class named `InvoiceService` calculates prices, sends customer
email, and creates PDF invoices.

**Context:** The review is for a maintainability pass in a small application.
The repository has no explicit service-layer standard, and the feature works.

**Observation:** The same class contains price calculation methods, SMTP email
calls, and PDF rendering calls.

**Evidence:** Static inspection of `InvoiceService` shows methods for pricing,
email delivery, and PDF generation in one class.

**Inference:** The class combines three responsibilities that are likely to
change for different reasons. This increases coupling and makes isolated tests
or future changes harder.

**Hypothesis:** Separating pricing, notification, and document rendering could
reduce coupling.

**Validation:** Static evidence is sufficient to identify mixed
responsibilities. Execution is not required to support that design observation.

**Conclusion:** The class has a local maintainability concern. The evidence
does not prove that the whole architecture is defective.

**Recommendation:** Extract pricing, email delivery, and PDF generation behind
separate collaborators when the next related change is made, or earlier if
tests are being added now. Do not rewrite the whole architecture solely from
this observation.

**Uncertainty:** The review has not inspected the whole repository, so it
cannot determine whether this pattern is widespread.

**Falsifier:** If repository conventions intentionally require this class to
coordinate all invoice side effects and tests show the responsibilities are
already isolated through injected dependencies, the recommendation should be
revised.

**Reviewability check:** A reviewer can inspect the class responsibilities and
contest whether extraction is worth the cost.

### Positive example: B1 Python correction

**Input:** A B1-level student solution repeats similar code in several
functions.

**Context:** The course has taught variables, conditionals, loops, lists, and
functions. Object-oriented programming has not been taught.

**Observation:** The solution repeats three similar loops with small changes.

**Evidence:** The submitted file shows repeated loop bodies. The course plan
does not include classes before this assignment.

**Inference:** The repetition is a readability and maintainability issue, but
requiring classes would exceed the taught concepts.

**Hypothesis:** A helper function with parameters can reduce repetition while
staying within the course scope.

**Validation:** The proposed correction uses only functions, parameters, loops,
and lists.

**Conclusion:** The solution can be improved without introducing OOP.

**Recommendation:** Show the student how to extract a helper function and call
it with different arguments. Do not mark the solution wrong for failing to use a
class.

**Uncertainty:** If the local rubric rewards any working solution over style,
the feedback should be framed as an optional improvement.

**Falsifier:** If the assignment instructions explicitly require a class, the
pedagogical constraint changes and the recommendation must be re-evaluated.

**Reviewability check:** A teacher can verify the taught concepts and inspect
whether the suggested correction stays within them.

### Positive example: missing authorization artifacts

**Input:** A repository excerpt includes controller files but no route guard or
authorization middleware.

**Context:** The review asks whether protected data is adequately secured. Only
a subset of files is available.

**Observation:** The inspected files do not contain an authorization check for
the protected endpoint.

**Evidence:** Static inspection of the provided controller files shows no guard
call near the endpoint. The repository excerpt does not include global
middleware configuration.

**Inference:** The provided files do not demonstrate authorization for this
endpoint. The available evidence is insufficient to prove that authorization is
absent globally.

**Hypothesis:** Authorization may be implemented in omitted middleware, gateway
configuration, route policy, or infrastructure.

**Validation:** The reviewer can request the routing configuration, middleware
registration, policy files, or deployment gateway rules. The reviewer should
not claim absence from the incomplete file set.

**Conclusion:** Authorization is not demonstrated by the provided evidence.
There is a security verification gap.

**Recommendation:** Ask for the authorization layer evidence before approving
the endpoint. If no such evidence exists, add an authorization check and tests.

**Uncertainty:** The conclusion is limited by the incomplete file set.

**Falsifier:** A route policy, middleware registration, or gateway rule that
protects the endpoint would falsify the claim that authorization is missing in
the system.

**Reviewability check:** A security reviewer can see that the finding is about
missing demonstration, not proven absence.

### Positive example: UML with two defensible models

**Input:** A UML exercise asks students to model orders, customers, and
shipping addresses.

**Context:** The assignment accepts class diagrams and asks students to justify
associations. It does not prescribe whether addresses are value objects or
entities.

**Observation:** Model A represents `ShippingAddress` as a value object owned by
`Order`. Model B represents `Address` as an entity associated with `Customer`
and referenced by `Order`.

**Evidence:** Both diagrams include order, customer, and address information.
The assignment does not require shared address identity.

**Inference:** Model A emphasizes the address snapshot used for fulfillment.
Model B emphasizes reusable customer address records.

**Hypothesis:** Both models can be defensible under different domain
assumptions.

**Validation:** Model A is valid if orders need immutable delivery snapshots.
Model B is valid if customers manage reusable address records.

**Conclusion:** Neither model should be rejected solely because it differs from
the reference answer.

**Recommendation:** Ask the student to state the domain assumption and ensure
the multiplicities match that assumption.

**Uncertainty:** If the hidden domain requirement says addresses must be reused
across orders, Model A may need revision.

**Falsifier:** A requirement that addresses are shared customer records would
weaken Model A. A requirement that orders preserve historical delivery
snapshots would weaken a mutable shared-address model.

**Reviewability check:** A competent instructor can compare the models against
the stated assumptions and assignment text.

## Counter-examples

### Unsupported global architecture judgment

**Non-conforming feedback:** "This class mixes pricing, email, and PDF logic,
so the whole architecture is bad and must be rewritten."

This fails because a local observation is used to make a global architecture
judgment. A conforming artifact would identify the local design concern, state
uncertainty about repository-wide patterns, and recommend a proportionate next
step.

### Developer motivation invented from code

**Non-conforming feedback:** "The developer clearly did not care about
security."

This fails because motivation is not externally observable from the code. A
conforming artifact would say which security evidence is missing or which
security control is defective.

### Missing tests inferred from incomplete files

**Non-conforming feedback:** "There are no tests because the provided excerpt
does not include a test directory."

This fails because absence is inferred solely from missing evidence. A
conforming artifact would say that tests were not present in the provided
excerpt and request the full repository or test configuration.

### Pedagogical over-engineering

**Non-conforming feedback:** "Rewrite this B1 Python exercise using classes,
interfaces, and dependency injection."

This fails because the recommendation ignores the pedagogical context. A
conforming artifact would use concepts already taught or mark advanced
alternatives as out of scope.

### Rejecting a different valid solution

**Non-conforming feedback:** "The student's UML model is wrong because it does
not match the reference diagram."

This fails when the assignment allows more than one defensible model. A
conforming artifact would evaluate whether the student's model satisfies the
requirements and whether its assumptions are coherent.

## Anti-patterns

- **Evidence laundering:** labeling an unsupported assertion as evidence.
- **Observation inflation:** presenting an interpretation as if it were directly
  observed.
- **Premise injection:** adding a new premise in the conclusion.
- **Certainty inflation:** stating a conclusion more strongly than the evidence
  supports.
- **Absence overreach:** treating missing evidence as proof of absence.
- **Premature closure:** choosing one hypothesis before checking plausible
  alternatives.
- **Disproportionate redesign:** recommending broad redesign for a local defect.
- **False pedagogy:** simplifying feedback by overstating certainty or using
  concepts outside the learner's level.
- **Single-answer bias:** rejecting a valid solution only because it differs
  from a reference answer.
- **Hidden-reasoning dependency:** making the conclusion impossible to review
  without private chain-of-thought.

## Edge cases

### Strong conclusion from one direct observation

One direct observation can justify a strong conclusion when the observation is
decisive. If a required configuration file contains `debug=true` in a production
deployment manifest, the artifact can conclude that production debug mode is
enabled, assuming the manifest is the active deployment source.

### Static evidence that does not require execution

Execution is not required when static evidence is sufficient. A hard-coded
secret in a committed file, a syntax error visible in source code, or a UML
multiplicity contradiction can be valid evidence without running the system.

### Contradictory documentation and execution results

When documentation says a feature is disabled but execution results show it is
enabled, the artifact must surface the contradiction. It should not hide either
source to produce a cleaner conclusion.

### Intentionally open-ended requirements

When requirements are intentionally open-ended, the artifact should evaluate
coherence, stated assumptions, and trade-offs rather than enforce a single
reference solution.

### Concise user-requested output

When the user requests concise output, the artifact can be brief. It still must
identify the evidence basis for important claims, for example by using compact
labels such as "Observed", "Inference", and "Recommendation".

### Unsafe or destructive validation

If validation would require deleting data, exploiting a system, disclosing
secrets, running untrusted code, or exceeding authorization, the artifact must
not require that validation. It should propose a safe substitute such as static
inspection, sandboxed reproduction, read-only checks, or owner-approved testing.

### Domain requirements overriding heuristics

Generic engineering heuristics do not override domain requirements. For
example, a domain rule requiring audit retention can justify additional
complexity that would otherwise look like over-engineering.

## Conformance

Conformance is based on externally observable behavior in the analysis
artifact, not on claimed internal reasoning.

An artifact conforms to this RFC when it satisfies the MUST and MUST NOT
requirements in this document. An implementation conforms when its observable
outputs satisfy the contract for applicable tasks without requiring hidden
chain-of-thought.

### Conformance cases

1. **Observation and inference separation:** Given a class containing pricing,
   email, and PDF methods, conforming feedback identifies the observed
   responsibilities separately from the inferred maintainability concern.
2. **Unsupported conclusions qualified:** Given one local design issue,
   conforming feedback rejects or qualifies a global architecture conclusion.
3. **Missing evidence is not proof:** Given an incomplete repository excerpt,
   conforming feedback says tests or authorization are not demonstrated, not
   that they are absent from the whole system.
4. **Contradictory evidence surfaced:** Given documentation that conflicts with
   execution results, conforming feedback reports the contradiction.
5. **Important conclusions traceable:** Given a security recommendation,
   conforming feedback links it to observations and evidence references.
6. **Falsifiers stated when relevant:** Given an important debatable conclusion,
   conforming feedback identifies foreseeable evidence that would change it.
7. **Local defects do not force redesign:** Given one mixed-responsibility
   class, conforming feedback recommends a proportionate local improvement or
   investigation rather than a full rewrite.
8. **Multiple valid solutions acknowledged:** Given two coherent UML models,
   conforming feedback evaluates assumptions instead of rejecting one only for
   differing from the reference answer.
9. **Pedagogical constraints respected:** Given a B1 Python task before OOP,
   conforming feedback avoids requiring classes.
10. **Recommendations address demonstrated problems:** Given repeated loops,
    conforming feedback recommends a helper function because repetition is
    observed.
11. **Hypotheses are not facts:** Given a possible missing middleware, conforming
    feedback labels omitted middleware as a hypothesis.
12. **Changed premises trigger re-evaluation:** Given a newly supplied rubric
    requiring OOP, conforming feedback revises the earlier B1 recommendation.
13. **Concise output remains reviewable:** Given a request for a short answer,
    conforming feedback still includes enough evidence basis for material
    claims.
14. **Unsafe execution is not required:** Given a destructive validation path,
    conforming feedback proposes a safe alternative or states the limitation.

## Security and misuse considerations

Fabricated observations or fake test execution can create false confidence. An
artifact MUST NOT claim to have inspected, executed, measured, or reproduced
evidence that was not actually inspected, executed, measured, or reproduced.

Sensitive evidence can be necessary but unsafe to expose. An artifact SHOULD
summarize sensitive evidence at the safest useful level and identify access or
verification constraints when direct quotation would expose secrets, private
data, proprietary material, or security details.

Structured feedback can look authoritative even when unsupported. An artifact
MUST NOT use headings, labels, confidence language, or formal structure to make
unsupported claims appear established.

Benchmark gaming can satisfy visible checks while degrading actual reasoning.
Conformance cases SHOULD include varied examples, counter-examples, and edge
cases that test behavior rather than wording alone.

Pedagogical harm can occur when feedback overstates certainty, rejects valid
student reasoning, or introduces concepts outside the learner's level. An
artifact MUST respect pedagogical context when that context is known.

## Open questions

- Should later RFCs define a machine-readable traceability schema for ARF
  artifacts?
- Should benchmark cases be stored under `benchmark/`, `tests/`, or both?
- What severity levels should distinguish demonstrated errors, debatable
  choices, optional improvements, and hypotheses?

## References

- `RFC_TEMPLATE.md`
- `STYLE_GUIDE.md`
- `ARCHITECTURE.md`
- `CONTRIBUTING.md`
