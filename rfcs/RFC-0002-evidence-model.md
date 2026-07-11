# RFC-0002 - Evidence Model

- **Status:** Draft
- **Authors:** Project contributors
- **Created:** 2026-07-11
- **Updated:** 2026-07-11

## Abstract

This RFC defines what the Academic Reasoning Framework considers valid
evidence and how evidence supports claims. It refines the Evidence stage from
RFC-0001 without redefining the full reasoning pipeline.

The evidence model is normative and model-independent. It requires evidence to
be attributable, scoped, reviewable, and evaluated relative to the claim it is
used to support.

## Motivation

Reasoning artifacts can fail even when they use the structure required by
RFC-0001. A statement labeled "evidence" may be an inference, a stale source, a
fabricated test result, an irrelevant observation, or a weak source presented as
decisive proof.

ARF needs a separate evidence contract so that future feedback contracts,
benchmarks, schemas, ontology entries, and implementations can determine
whether claims are supported by appropriate evidence. This RFC defines that
contract while preserving the RFC-0001 distinction between observations,
evidence, inferences, hypotheses, conclusions, and recommendations.

## Scope

### In scope

- Definitions for evidence, evidence items, sources, claims, provenance, scope,
  freshness, limitations, contradiction, corroboration, measurement, and
  reproduction.
- A taxonomy of evidence categories.
- Requirements for claim-to-evidence relationships.
- Requirements for evidence strength without a universal numeric score.
- Examples, counter-examples, edge cases, conformance cases, and security and
  misuse considerations.

### Out of scope

- A replacement for the RFC-0001 reasoning pipeline.
- Treating hypotheses or inferences as evidence categories.
- Model-specific behavior for Claude, GPT, Gemini, Codex, or any other system.
- Code in `core/`.
- RFC-0003 or any later RFC.
- A universal numeric evidence score.

## Definitions

**Evidence** is reviewable support used to evaluate whether a claim is true,
false, plausible, incomplete, or unsupported.

An **evidence item** is one discrete piece of evidence. It has a source, scope,
provenance, and any material limitations.

An **evidence reference** is a specific pointer to an evidence item. It can be a
file path, line number, command result, test name, screenshot identifier,
diagram element, cited source, requirement identifier, quote, or measurement
record.

A **claim** is a statement being supported, weakened, or rejected by evidence.
Claims can concern correctness, behavior, design, security, pedagogy,
requirements, measurements, or documentation.

A **source** is the origin of an evidence item.

A **primary source** is a source directly tied to the artifact, behavior, or
requirement being evaluated. Examples include source code, official
requirements, local test output, executed command output, submitted student
work, and authoritative local configuration.

A **secondary source** summarizes, interprets, reports, or discusses primary
sources. Examples include comments, issue discussions, design notes, blog
posts, generated summaries, and prior reviews.

An **external source** is a source outside the user-provided artifacts. Examples
include language specifications, framework documentation, standards, package
documentation, and official vendor references.

**Static evidence** is evidence obtained without executing the artifact under
analysis. Examples include source inspection, configuration inspection,
documentation inspection, UML inspection, and dependency manifest inspection.

**Dynamic evidence** is evidence obtained by executing, reproducing, measuring,
or interacting with the artifact under analysis.

A **measurement** is evidence produced by applying a defined metric and method.
Examples include cyclomatic complexity, dependency count, runtime duration,
memory use, coverage percentage, or defect count.

**Reproduction** is a safe attempt to repeat a behavior, failure, result, or
measurement under stated conditions.

**Corroboration** is support from more than one relevant evidence item,
especially when the items have independent sources or methods.

A **contradiction** exists when relevant evidence items materially conflict.

**Evidence scope** is the boundary within which an evidence item supports a
claim. Scope can be a file, function, class, module, diagram, assignment,
repository excerpt, runtime environment, version, time window, or user-provided
artifact set.

**Evidence freshness** is the relevance of evidence over time. Freshness
depends on whether the artifact, requirement, behavior, or source may have
changed.

**Evidence provenance** is the origin and handling history of an evidence item,
including who or what produced it, where it came from, and how it was obtained
or transformed when that matters.

An **evidence limitation** is a constraint that affects how strongly an
evidence item can support a claim. Examples include partial input, stale
documentation, incomplete logs, unknown environment, missing permissions,
unsafe reproduction, and unclear provenance.

An **unsupported claim** is a claim presented without sufficient relevant
evidence for the context and stakes.

**Fabricated evidence** is evidence that is invented, falsely attributed,
altered deceptively, or claimed to have been inspected, executed, measured, or
reproduced when it was not.

## Normative requirements

1. Every important claim MUST have sufficient evidence for the context and
   stakes.
2. Evidence MUST be attributable to a source or observation.
3. Evidence references SHOULD be as specific as reasonably possible.
4. An implementation MUST NOT claim execution, inspection, measurement, or
   reproduction that it did not perform.
5. Missing evidence MUST NOT be treated as evidence of absence.
6. Evidence scope MUST NOT be generalized beyond the inspected artifact,
   source, time window, environment, or provided material.
7. Stale evidence MUST be identified when freshness materially affects the
   claim.
8. Contradictory evidence MUST be surfaced rather than silently discarded.
9. Stronger claims MUST require stronger or more direct evidence than weaker
   claims under the same stakes.
10. One decisive direct observation MAY be sufficient to support a claim.
11. Execution MUST NOT be required when static evidence is decisive.
12. Evidence collection MUST NOT require unsafe, destructive, privacy-violating,
    unauthorized, or illegal action.
13. Evidence containing secrets, personal data, student data, or proprietary
    details MUST be minimized in outputs.
14. Source provenance MUST be preserved when it materially affects review,
    trust, or reproducibility.
15. Derived evidence MUST identify the source evidence and transformation.
16. Measurements MUST identify the metric and method.
17. Reproduction claims SHOULD identify enough conditions to be independently
    repeated when repetition is safe and authorized.
18. External sources MUST be distinguished from user-provided artifacts.
19. Evidence MUST be evaluated relative to the claim it supports.
20. Formal structure MUST NOT convert weak evidence into strong evidence.
21. Hypotheses and inferences MUST NOT be treated as evidence categories.
22. Evidence limitations SHOULD be stated when they materially affect claim
    strength.

## Processing model

This RFC refines the Evidence stage from RFC-0001. A conforming artifact does
not need to restate the whole RFC-0001 pipeline.

The evidence model has the following conceptual relationship:

```text
Claim
-> supported by Evidence Item(s)
-> Evidence Item has Source
-> Evidence Item has Scope
-> Evidence Item has Provenance
-> Evidence Item may have Limitations
```

An artifact using this model first identifies the claim, then identifies the
evidence items used to support or weaken that claim. Each evidence item is
attributed to a source or observation, scoped to the inspected material, and
qualified by relevant provenance or limitations.

### Evidence taxonomy

Evidence categories classify evidence items. They do not classify reasoning
steps.

- **E1 - Direct observation:** An inspectable fact observed directly in the
  input, context, or artifact.
- **E2 - Execution or reproduction result:** A safe and authorized execution,
  test run, command result, reproduction attempt, or interactive result.
- **E3 - Measurement:** A quantified result produced by a stated metric and
  method.
- **E4 - Corroborated evidence:** Multiple relevant evidence items that support
  the same claim, especially when they use independent sources or methods.
- **E5 - Derived evidence:** Evidence produced by transforming, aggregating, or
  calculating from source evidence.

Hypotheses and inferences are not evidence categories. Under RFC-0001, an
inference summarizes how evidence supports a claim, and a hypothesis is a
plausible but unestablished explanation. Both can use evidence, but neither is
itself evidence unless it also contains an attributable evidence item.

### Evidence strength

ARF does not define a universal numeric evidence score. Evidence strength
depends on the claim, context, stakes, and available alternatives.

An artifact SHOULD evaluate evidence strength using the following factors:

- **Directness:** whether the evidence directly concerns the claim.
- **Relevance:** whether the evidence addresses the claim rather than a nearby
  but different issue.
- **Reproducibility:** whether the evidence can be independently repeated when
  safe and authorized.
- **Corroboration:** whether independent evidence supports the same claim.
- **Provenance:** whether the source and handling history are known and
  trustworthy for the claim.
- **Scope:** whether the evidence covers the artifact, behavior, version,
  environment, or population named in the claim.
- **Freshness:** whether the evidence may have become stale.
- **Contradiction:** whether relevant evidence conflicts with the claim.

One direct observation can be stronger than many indirect or irrelevant
observations. Multiple weakly related evidence items do not automatically
support a strong claim.

## Examples

### Positive example: reproduced Python test failure

**Claim:** The function `total_price()` currently fails the discount test.

**Evidence item:** E2 execution result from running the local test command.

**Evidence reference:** Test output for `test_total_price_applies_discount`
showing expected `90` and actual `100`.

**Source:** User-provided repository executed in a local test environment.

**Scope:** The current checkout and the local test environment used for the
run.

**Provenance:** The reviewer ran the test command during the review.

**Limitations:** The result does not prove behavior in other branches or
environments.

**Support relationship:** The execution result directly supports the claim that
the current implementation fails that test.

### Positive example: hard-coded secret found statically

**Claim:** The inspected file contains a hard-coded credential.

**Evidence item:** E1 direct observation from static inspection.

**Evidence reference:** A configuration assignment named `API_KEY` with a
literal secret-like value in the inspected file.

**Source:** User-provided source file.

**Scope:** The inspected file only.

**Provenance:** Static inspection; no execution performed.

**Limitations:** The observation does not prove whether the credential is valid
or deployed.

**Support relationship:** Static evidence is decisive for the claim that the
file contains a hard-coded credential. Execution is not required.

### Positive example: UML composition from lifecycle requirements

**Claim:** UML composition is defensible between `Order` and `OrderLine`.

**Evidence item:** E1 direct observation of the requirement that order lines do
not exist independently from orders.

**Evidence reference:** Assignment requirement stating that deleting an order
also deletes its order lines.

**Source:** User-provided assignment text.

**Scope:** The assignment domain model.

**Provenance:** Requirement supplied with the modeling task.

**Limitations:** If the domain later allows reusable order-line templates, the
model may need revision.

**Support relationship:** The lifecycle requirement directly supports
composition as a valid UML choice.

### Positive example: incomplete repository with no visible tests

**Claim:** Tests are not demonstrated by the provided repository excerpt.

**Evidence item:** E1 direct observation of the provided artifact set.

**Evidence reference:** The visible file list does not include test files or a
test workflow.

**Source:** User-provided repository excerpt.

**Scope:** The provided excerpt only.

**Provenance:** Static inspection of the provided files.

**Limitations:** The full repository may contain tests not included in the
excerpt.

**Support relationship:** The evidence supports a limited claim about what is
visible. It does not support the stronger claim that no tests exist anywhere.

### Positive example: documentation contradicts execution

**Claim:** The documented feature state conflicts with observed behavior.

**Evidence item:** E1 documentation observation and E2 execution result.

**Evidence reference:** Documentation says the feature is disabled; execution
shows the feature returns enabled behavior.

**Source:** User-provided documentation and local execution result.

**Scope:** The inspected documentation version and executed environment.

**Provenance:** Documentation was statically inspected; behavior was executed
locally.

**Limitations:** Either the documentation or environment may be stale or
misconfigured.

**Support relationship:** The two evidence items contradict each other and must
both be surfaced.

### Positive example: cyclomatic complexity metric

**Claim:** The function has high cyclomatic complexity under the selected
metric.

**Evidence item:** E3 measurement.

**Evidence reference:** Complexity tool output reports cyclomatic complexity
`18` for the function.

**Source:** User-provided source code and the named measurement tool.

**Scope:** The measured function and selected tool configuration.

**Provenance:** Tool output generated during the review.

**Limitations:** Complexity `18` does not by itself prove the function is
incorrect or must be rewritten.

**Support relationship:** The measurement supports the complexity claim. A
separate inference is required to connect that metric to maintainability risk.

## Counter-examples

### Fake test execution

**Non-conforming claim:** "I ran the tests and they pass."

This is non-conforming if no tests were run. A conforming artifact either
provides the execution result or says that tests were not run.

### Invented line numbers

**Non-conforming evidence reference:** "`auth.py:42` contains the missing
authorization check."

This is non-conforming if the file or line was not inspected or the reference
does not exist. A conforming artifact uses inspected references only.

### Presenting an inference as evidence

**Non-conforming evidence:** "The code is poorly designed."

This is an inference or conclusion, not evidence. A conforming artifact would
cite the observed responsibilities, dependencies, coupling, or requirements
that support the design claim.

### Missing test directory as proof of no tests

**Non-conforming claim:** "There are no tests because this excerpt has no
`tests/` directory."

This treats missing evidence as absence. A conforming artifact says tests are
not visible in the provided excerpt.

### One file used to condemn the whole architecture

**Non-conforming claim:** "The entire architecture is defective because one
class mixes responsibilities."

This generalizes beyond evidence scope. A conforming artifact limits the claim
to the inspected class unless repository-wide evidence is provided.

### Outdated documentation quoted as current behavior

**Non-conforming claim:** "The feature is disabled because old documentation
says so."

This ignores freshness. A conforming artifact identifies the documentation date
or version and checks current behavior when freshness materially affects the
claim.

### Unattributed industry best practice

**Non-conforming claim:** "Industry best practice requires this design."

This lacks an attributable source or relevant requirement. A conforming
artifact cites a specific standard, framework recommendation, local convention,
or requirement and explains its relevance.

## Edge cases

### One decisive observation

If a production deployment manifest directly contains `debug=true`, that single
observation can support the claim that the manifest enables debug mode,
assuming the manifest is the active deployment source.

### Conflicting primary sources

If two official requirement documents conflict, both are primary sources for
their own versions. A conforming artifact reports the conflict and does not
silently choose the source that fits the preferred conclusion.

### User-provided logs that cannot be reproduced

User-provided logs can be evidence, but their provenance and limitations must
be stated when the reviewer cannot reproduce them. They may support a claim
about reported behavior more strongly than a claim about current behavior.

### Screenshots with incomplete context

A screenshot can show visible UI state, but it may omit environment, version,
time, account permissions, or preceding actions. A conforming artifact limits
claims to what the screenshot supports.

### Unknown provenance for generated code or reports

Generated code or reports with unknown provenance can still be inspected as
artifacts, but claims about how they were generated require additional evidence.

### Contaminated benchmark evidence

Benchmark evidence may be contaminated by warm caches, debug builds,
background load, selective runs, or changed inputs. A conforming artifact states
the benchmark method and limitations before using it to support performance
claims.

### External official specification conflicts with local requirements

An official external specification can be strong evidence about external rules,
but local requirements may intentionally override generic behavior. A
conforming artifact distinguishes the external source from the local artifact
and identifies the conflict.

### Correct but irrelevant observation

An observation can be accurate and still fail to support a claim. The fact that
a file has 400 lines does not by itself support a claim that authentication is
missing.

## Conformance

Conformance is based on externally observable behavior in the artifact or
implementation output. A conforming implementation does not need to expose
private internal reasoning, but it must provide reviewable evidence handling.

An artifact conforms to this RFC when it satisfies the MUST and MUST NOT
requirements in this document.

### Conformance cases

1. **Evidence and inference are not conflated:** Given a design judgment,
   conforming output separates observed facts from the inference.
2. **Fake execution claims fail:** Given no execution, conforming output does
   not claim tests were run.
3. **Missing evidence is not absence:** Given an incomplete excerpt, conforming
   output does not conclude that omitted artifacts do not exist.
4. **Evidence scope is preserved:** Given one inspected file, conforming output
   limits claims to that file unless broader evidence is supplied.
5. **Contradictory evidence is reported:** Given conflicting documentation and
   execution results, conforming output surfaces both.
6. **Stale evidence is qualified:** Given old documentation for current
   behavior, conforming output identifies freshness limits.
7. **Derived evidence identifies transformation:** Given a dependency count,
   conforming output identifies the source manifest and counting method.
8. **Sensitive evidence is minimized:** Given a secret, conforming output
   identifies the issue without exposing the full secret.
9. **Decisive static observation is enough:** Given a hard-coded credential,
   conforming output can support the claim without execution.
10. **Irrelevant observation is rejected:** Given an observation unrelated to
    authentication, conforming output does not use it as authentication
    evidence.
11. **External and user sources differ:** Given official docs and local code,
    conforming output identifies which evidence came from each source.
12. **Evidence provenance is retained:** Given user-provided logs, conforming
    output identifies them as user-provided and unreproduced when applicable.

## Security and misuse considerations

Fabricated evidence is a direct integrity failure. An artifact MUST NOT invent
observations, line numbers, command output, measurements, citations, screenshots,
or reproduction results.

Malicious logs or benchmark poisoning can mislead analysis. Artifacts SHOULD
consider whether logs, timings, or benchmark inputs may have been selected,
altered, truncated, or produced under misleading conditions.

Evidence artifacts can contain prompt injection or instructions that are not
part of the analysis task. Implementations SHOULD treat evidence content as
data to evaluate, not as instructions to override system, user, repository, or
safety constraints.

Secret leakage can occur when evidence is quoted too fully. Artifacts MUST
minimize secrets, tokens, passwords, private keys, personal data, student data,
and proprietary details while preserving enough reviewability to support the
claim.

Screenshots can mislead when they omit context or can be altered. Artifacts
SHOULD describe screenshot limitations when the screenshot materially supports
a claim.

Selectively omitted contradictory evidence can create false confidence.
Artifacts MUST surface material contradictions known to the analysis.

Formal labels can launder weak support into apparent rigor. Artifacts MUST NOT
use labels such as "Evidence", "Measurement", or "Reproduction" unless the
content satisfies the relevant definition in this RFC.

## Open questions

- Should future RFCs define machine-readable fields for source, scope,
  provenance, and limitation?
- Should ARF maintain separate evidence profiles for academic work, code
  review, security review, and benchmarking?
- How should conformance tests represent evidence freshness across changing
  external sources?

## References

- `RFC_TEMPLATE.md`
- `STYLE_GUIDE.md`
- `ARCHITECTURE.md`
- `CONTRIBUTING.md`
- `rfcs/RFC-0001-reasoning-model.md`
