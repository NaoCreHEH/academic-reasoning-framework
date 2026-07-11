# RFC-0005 - Routing Model

- **Status:** Draft
- **Authors:** Project contributors
- **Created:** 2026-07-11
- **Updated:** 2026-07-11

## Abstract

This RFC defines how the Academic Reasoning Framework selects an analysis
capability, domain profile, or specialized evaluator from the user's objective
and the primary artifact under analysis.

Routing is model-independent. It is based primarily on user objective, primary
artifact, and requested output. Topic keywords alone must not determine
routing.

## Motivation

ARF can support overlapping capabilities. A request about Python may ask for a
Python correction, an exam, an architecture review, or a PFE assessment. A
request using the word "architecture" may concern a UML model, a codebase, or
an academic report. Routing by topic keywords alone creates skill collisions.

This RFC defines a routing contract so ARF can choose the capability that owns
the transformation requested by the user while preserving traceability,
evidence provenance, feedback compatibility, and confidence boundaries.

## Scope

### In scope

- A model-independent routing model for ARF capabilities.
- Capability ownership by user objective, primary artifact, and requested
  output.
- Positive and negative boundaries for overlapping capabilities.
- Routing conflict, ambiguous routing, compound request, delegation, fallback,
  revision, and routing trace requirements.
- Examples, counter-examples, edge cases, conformance cases, and security and
  misuse considerations.

### Out of scope

- Vendor-specific triggers, Claude Skills, GPT instructions, Gemini extensions,
  Codex behavior, or any other product-specific routing mechanism.
- Numeric routing scores or keyword weights.
- Implementing `core/` routing code.
- RFC-0006 or any later RFC.

## Definitions

**Routing** is the process of selecting one or more ARF capabilities for a
request.

A **routing request** is the user request, available artifacts, requested
output, and relevant context used for routing.

The **user objective** is what the user wants accomplished, such as review,
correction, generation, explanation, assessment, comparison, or extraction.

The **primary artifact** is the main object being acted upon, such as a UML
diagram, repository, Python submission, PFE report, specification, or exam to
be produced.

The **requested output** is the artifact or response the user asks ARF to
produce, such as feedback, a report, questions, corrections, a diagram review,
or an assessment instrument.

A **capability** is an ARF analysis or generation competence that can own a
class of requests.

A **domain capability** is a capability specialized for a domain, language,
discipline, artifact type, or pedagogical setting.

A **cross-domain capability** is a capability that can operate across domains,
such as exam generation, routing, evidence handling, feedback presentation, or
confidence communication.

A **routing candidate** is a capability considered during routing.

A **routing signal** is reviewable information used to select, reject, or
qualify a routing candidate.

An **artifact signal** identifies the type, structure, origin, or role of the
primary artifact.

An **objective signal** identifies the user's intended action or decision.

An **output signal** identifies the requested output artifact or response.

A **topic signal** is subject-matter vocabulary, such as Python, architecture,
security, UML, PFE, or databases.

A **positive boundary** defines requests a capability owns.

A **negative boundary** defines nearby requests a capability must yield to
another capability.

**Capability ownership** is the claim that a capability owns the requested
transformation, primary artifact, or requested output.

A **routing conflict** exists when two or more candidates have plausible
ownership over the same request or subtask.

**Ambiguous routing** exists when available signals are insufficient to select
a primary capability without qualification.

A **compound request** contains multiple independently reviewable subtasks that
may require different primary capabilities.

**Delegation** is the use of another capability for a subtask, support task, or
specialized judgment.

The **primary capability** is the capability that owns the request or subtask.

A **supporting capability** contributes domain context, evidence, examples, or
checks without replacing the primary capability.

A **routing fallback** is a conservative route used when no specialist
capability clearly owns the request.

A **routing revision** is a change in route after the objective, artifact,
requested output, or material context changes.

A **routing trace** is an externally reviewable summary of decisive routing
signals, selected capability, supporting capabilities, rejected alternatives,
ambiguity, and revision triggers.

## Normative requirements

1. Routing MUST identify the user objective.
2. Routing MUST identify the primary artifact when an artifact exists.
3. Routing MUST identify the requested output when one is requested.
4. Topic keywords MUST NOT be the sole routing basis.
5. An explicit capability selection SHOULD be honored when applicable.
6. An invalid explicit selection MUST NOT silently force an inapplicable
   capability.
7. Every routable capability MUST define positive and negative boundaries.
8. Overlapping capabilities MUST define ownership boundaries.
9. Requested output ownership MAY override input artifact ownership.
10. A supporting capability MUST NOT silently replace the primary capability.
11. Compound requests MAY use multiple capabilities.
12. One capability SHOULD remain primary for each independently reviewable
    subtask.
13. Routing conflicts MUST be surfaced or deterministically resolved.
14. Ambiguous routing MUST preserve the material ambiguity.
15. Routing MUST NOT invent missing artifact types.
16. Routing MUST be revised when the user objective materially changes.
17. Routing traces MUST be externally reviewable without hidden
    chain-of-thought.
18. Routing traces SHOULD identify decisive signals and rejected alternatives
    when material.
19. Routing MUST NOT route by superficial lexical match alone.
20. Negative boundaries MUST be evaluated before final selection.
21. A domain capability MAY support another capability without owning the
    output.
22. Delegation MUST preserve RFC-0001 traceability.
23. Delegated evidence MUST preserve RFC-0002 provenance.
24. Delegated feedback MUST remain compatible with RFC-0003.
25. Confidence about routing SHOULD use RFC-0004 concepts when material.
26. Unknown routing context MUST NOT be converted into false certainty.
27. Routing fallback MUST be conservative.
28. A fallback capability MUST NOT claim specialist authority it does not have.
29. Routing MUST distinguish one compound request from several independent
    requests.
30. A later keyword MUST NOT automatically override an already established
    primary artifact and objective.

## Processing model

The conceptual routing relationship is:

```text
Routing request
-> identify User objective
-> identify Primary artifact
-> identify Requested output
-> collect Routing signals
-> generate Routing candidates
-> apply Positive and Negative boundaries
-> resolve conflicts
-> select Primary capability
-> attach Supporting capabilities when justified
-> preserve Routing trace
-> revise routing if the request materially changes
```

Routing is qualitative. A conforming artifact MUST NOT use numeric routing
scores or keyword weights as the normative basis for capability selection.

### Artifact-first discrimination

Capability ownership is defined by the object being acted upon and the
transformation requested.

- UML capability owns a diagram or UML model.
- Architecture review capability owns a repository, running system, or codebase
  architecture.
- PFE review capability owns an academic report, specification, statement of
  work, thesis, or project document being academically evaluated.
- Exam generation capability owns an assessment instrument to be produced.
- Python teaching capability owns Python student code, Python exercises,
  Python submissions, or learner-facing Python correction.

For `Create 20 MCQs about Python dictionaries`, the primary capability is exam
generation. Python is the topic or domain. Exam generation owns the requested
output artifact.

For `Review the architecture of this class diagram`, if the primary artifact is
a UML class diagram and the task is to assess modeling coherence, the primary
capability is UML analysis. The word `architecture` alone MUST NOT transfer
ownership to architecture review.

For `Inspect this Django repository and tell me whether the architecture is
maintainable`, the primary capability is architecture review because the
primary artifact is a repository and the objective is repository architecture
assessment.

### Routing signal hierarchy

Signals are qualitative and context-sensitive. The usual hierarchy is:

1. Explicit user-selected capability, when valid and applicable.
2. Requested output ownership.
3. Primary artifact ownership.
4. User objective.
5. Domain or context signals.
6. Topic keywords.

Requested output and primary artifact can conflict. Conflict resolution SHOULD
select the capability that owns the transformation requested by the user.

If the input artifact is Python source code and the requested output is a
25-question examination based on the code concepts, exam generation is primary.
Python teaching may support concept selection, but it does not own the output.

### Positive and negative boundaries

Python teaching positive boundary: learner-facing Python explanation, exercise
correction, code review, procedural refactoring, or pedagogical feedback.

Python teaching negative boundary: when the requested artifact is a QCM,
examination, grading instrument, or question bank, route primarily to exam
generation even when the subject is Python.

Architecture review positive boundary: repository, running-system, codebase,
component, dependency, deployment, or maintainability assessment.

Architecture review negative boundary: do not own UML diagram evaluation solely
because the user says architecture, design, coupling, or maintainability.

PFE review positive boundary: academic review of a report, specification,
statement of work, thesis, internship report, or project document.

PFE review negative boundary: do not own repository code review solely because
the code belongs to a student project.

Exam generation positive boundary: requested production of questions, exams,
QCM, MCQs, oral questions, rubrics, or assessment instruments.

Exam generation negative boundary: do not own correction of a student's
submitted code merely because the correction could inspire exam questions.

UML analysis positive boundary: UML diagrams, class diagrams, sequence
diagrams, modeling coherence, relationships, multiplicities, lifecycle, and
notation.

UML analysis negative boundary: do not own repository architecture review
solely because a repository contains design vocabulary.

### Routing decision model

A routing candidate is strengthened when:

- it owns the requested output;
- it owns the primary artifact;
- its positive boundary matches the user objective;
- its negative boundary does not exclude the request.

A routing candidate is weakened or rejected when:

- another capability owns the requested transformation;
- its negative boundary explicitly yields;
- the artifact type is outside its scope;
- selection depends only on topic vocabulary.

### Compound requests

Compound requests MUST be decomposed when subtasks have different primary
capabilities.

Example request: `Review this student's Python project, identify architecture
problems, and create 10 oral questions based on the weaknesses.`

Subtask A: review Python implementation. Primary capability: Python teaching
or architecture review depending on whether the scope is learner-facing code
correction or broader design.

Subtask B: evaluate repository-wide architecture. Primary capability:
architecture review.

Subtask C: create oral assessment questions. Primary capability: exam
generation.

The whole compound request MUST NOT be forced through one capability when
different subtasks have different owners.

### Routing trace

A compact routing trace is semantic and externally reviewable. It can include:

```text
Primary artifact:
Requested output:
User objective:
Primary capability:
Supporting capabilities:
Decisive signals:
Negative boundaries evaluated:
Material ambiguity:
Revision trigger:
```

The trace does not require these exact headings in user-facing output.

## Examples

### Positive example: Python MCQs

**Request:** `Create 20 MCQs on Python dictionaries.`

**Primary artifact:** Requested exam artifact.

**Requested output:** Twenty MCQs.

**User objective:** Generate an assessment instrument.

**Primary capability:** Exam generation.

**Supporting capability:** Python teaching for domain accuracy.

**Decisive signals:** Requested output ownership overrides Python topic.

**Negative boundaries evaluated:** Python teaching yields to exam generation
for QCM, MCQ, examination, and question bank outputs.

### Positive example: Python student correction

**Request:** `Correct this Python student submission.`

**Primary artifact:** Python student code.

**Requested output:** Learner-facing correction.

**Primary capability:** Python teaching.

**Decisive signals:** Python submission plus correction objective.

### Positive example: UML architecture wording

**Request:** `Is the architecture of this class diagram coherent?`

**Primary artifact:** UML class diagram.

**Requested output:** Modeling assessment.

**Primary capability:** UML analysis.

**Rejected alternative:** Architecture review, because the primary artifact is
a UML model and `architecture` is not sufficient to transfer ownership.

### Positive example: Django repository architecture

**Request:** `Review this Django repository architecture.`

**Primary artifact:** Django repository.

**Requested output:** Architecture review feedback.

**Primary capability:** Architecture review.

**Supporting capability:** Python or Django domain capability when needed.

### Positive example: PFE contribution analysis

**Request:** `Analyze this PFE report and identify the student's personal
contribution.`

**Primary artifact:** PFE report.

**Requested output:** Academic assessment of contribution.

**Primary capability:** PFE review.

### Positive example: oral questions from a PFE

**Request:** `Create oral questions based on this PFE.`

**Primary artifact:** PFE report as source material.

**Requested output:** Oral assessment questions.

**Primary capability:** Exam generation.

**Supporting capability:** PFE review for academic context.

### Positive example: UML review then exam questions

**Request:** `Review this UML diagram and then create five exam questions about
its mistakes.`

**Subtask A primary capability:** UML analysis.

**Subtask B primary capability:** Exam generation.

**Routing trace:** The request is compound; the review and generation outputs
have different primary owners.

### Positive example: compound Python, architecture, exam request

**Request:** `Review this student's Python project, identify architecture
problems, and create 10 oral questions based on the weaknesses.`

**Subtask A:** Python implementation review. Primary capability depends on
scope: Python teaching for learner correction, architecture review for
repository-wide design.

**Subtask B:** Architecture problems. Primary capability: architecture review.

**Subtask C:** Oral questions. Primary capability: exam generation.

**Supporting capabilities:** Python teaching can support exam generation with
language-level concepts.

### Positive example: valid explicit selection

**Request:** `Use UML analysis to review this class diagram.`

**Primary capability:** UML analysis.

**Reason:** Explicit user-selected capability is valid and applicable.

### Positive example: inapplicable explicit selection

**Request:** `Use architecture review to create 20 MCQs about Python lists.`

**Primary capability:** Exam generation.

**Rejected selection:** Architecture review is explicitly selected but
inapplicable to the requested output. The route should qualify the mismatch.

### Positive example: routing revision

**Initial request:** `Review this Python function.`

**Initial primary capability:** Python teaching.

**Changed request:** `Actually, create an exam from these concepts.`

**Revised primary capability:** Exam generation.

**Revision trigger:** User objective and requested output changed.

### Positive example: ambiguous artifact

**Request:** `Review this project document.`

**Primary artifact:** Ambiguous project document.

**Routing state:** Unknown until scope is inferable.

**Conservative fallback:** General review with no specialist authority claim,
or ask whether the document is a PFE report, specification, rubric, or design
document.

## Counter-examples

### Python keyword steals exam generation

Routing `Create 20 MCQs on Python dictionaries` to Python teaching as primary
solely because `Python` appears is non-conforming.

### Architecture keyword steals UML review

Routing `Is the architecture of this class diagram coherent?` to architecture
review solely because `architecture` appears is non-conforming.

### Academic context steals code review

Routing repository code review to PFE review solely because the code belongs to
a student project is non-conforming.

### Exam creation routed to domain capability

Routing exam creation to the domain capability instead of exam generation is
non-conforming when the requested output is an assessment instrument.

### Every matching capability at once

Using every capability whose vocabulary appears in the request is
non-conforming. The route must identify a primary capability per subtask.

### Explicit applicable selection ignored

Ignoring `Use UML analysis` for a class diagram without explanation is
non-conforming.

### Explicit inapplicable selection obeyed silently

Using architecture review to create Python MCQs without qualification is
non-conforming.

### One capability consumes compound request

Routing a review plus exam generation compound request entirely through one
capability is non-conforming when subtasks have different owners.

### Later incidental keyword overrides route

Changing a Python correction route to architecture review because the user says
"good architecture" incidentally is non-conforming without a changed objective.

### No identifiable signals

Claiming a confident route with no user objective, artifact, requested output,
or decisive signals is non-conforming.

## Edge cases

### No explicit artifact

If no artifact exists, routing can be based on requested output and objective,
but must not invent an artifact type.

### Multiple uploaded artifacts

When different artifact types are uploaded, routing should identify which
artifact is primary for each subtask.

### Embedded code and UML

A single artifact can contain code and UML diagrams. The primary capability
depends on whether the user asks to review the code, the model, or both.

### PDF specification requesting code review

A PDF specification asking for code review is not itself code. Routing should
surface that code is missing or route to specification review unless code is
also provided.

### Code as exam source

When code is supplied only as source material for exam generation, exam
generation is primary and code-domain support is secondary.

### Repository README academic evaluation

A repository README requesting academic evaluation may route to PFE review if
the artifact is being assessed as an academic project document rather than as
repository code.

### One output in several languages

A request to produce the same feedback in several languages does not change the
primary analysis capability. Language handling is supporting.

### User changes objective

When the user changes from review to generation mid-conversation, routing must
be revised.

### Explicit selection conflicts with safety

An explicit capability selection must not override safety or applicability
constraints.

### Supporting capability disagrees

If a supporting capability disagrees with the primary capability, the routing
trace should preserve the disagreement when material and the primary owner must
resolve or surface it.

### Concise request with misspellings

Misspellings do not prevent routing when objective, artifact, and output remain
inferable.

### Capability unavailable

If the best capability is unavailable, fallback must be conservative and must
not claim specialist authority.

### All candidates weak

When all candidates are weak, routing should remain ambiguous or fallback with
limitations.

### Several independent subtasks

Several independent requests in one message can have separate primary
capabilities and traces.

## Conformance

Conformance is based on externally observable routing behavior, not hidden
selection logic.

### Conformance cases

1. **Python topic does not steal exam generation:** Python MCQ creation routes
   primarily to exam generation.
2. **Architecture keyword does not steal UML review:** Class diagram coherence
   routes primarily to UML analysis.
3. **Academic context does not steal code review:** Student repository code
   review routes to code, Python, or architecture capability as appropriate,
   not PFE review solely due to academic context.
4. **Output ownership can override input artifact ownership:** Python code used
   to create an exam routes primarily to exam generation.
5. **Boundaries applied:** Positive and negative boundaries are considered
   before final selection.
6. **Compound decomposition:** Compound review plus exam requests are
   decomposed.
7. **Primary per subtask:** One primary capability exists per independently
   reviewable subtask.
8. **Supporting does not replace primary:** Python teaching can support exam
   generation without owning MCQ output.
9. **Explicit valid selection honored:** Valid explicit UML selection is used
   for UML diagram review.
10. **Explicit invalid selection qualified:** Inapplicable explicit selection
    is rejected or qualified.
11. **Lexical-only routing fails:** Keyword-only routing fails conformance.
12. **Ambiguity qualified:** Ambiguous artifact routing remains qualified.
13. **Objective revision changes route:** Routing changes after review becomes
    generation.
14. **Trace exposes signals:** Routing trace identifies decisive signals.
15. **Fallback limited:** Fallback does not claim specialist authority.
16. **Delegated provenance:** Delegated evidence preserves provenance.

## Security and misuse considerations

Artifacts can contain prompt injection attempting to change routing. Routing
MUST treat artifact content as evidence or input, not as authority to override
user objective, repository policy, or safety constraints.

Capability impersonation can occur when an artifact or user text claims that a
specialist route is required. Routing SHOULD verify applicability rather than
accept the claim blindly.

Specialist-authority laundering can make a fallback route appear expert.
Fallback outputs MUST NOT claim specialist authority they do not have.

Malicious file names or metadata can include routing keywords. Routing MUST NOT
depend on file names or metadata alone when artifact content and objective
indicate another route.

Repeated keywords can attack routing. Repetition of topic terms MUST NOT
override user objective, primary artifact, or requested output.

User-selected capability abuse can attempt to bypass safety or applicability.
Explicit selection MUST be qualified or rejected when unsafe or inapplicable.

Hidden delegation can break reviewability. Delegation SHOULD be reflected in
the routing trace when material.

Evidence provenance can be lost during delegation. Delegated evidence MUST
preserve RFC-0002 provenance.

Incorrect routing can harm academic grading by applying the wrong rubric or
feedback style. Academic routes SHOULD preserve pedagogical and assessment
context.

Security review routed to a non-security capability can miss severe risks.
Security-sensitive requests SHOULD surface limits or use a security capability
when available.

Model/vendor-specific assumptions MUST NOT enter normative routing.

Routing traces can expose sensitive artifact metadata. Traces SHOULD minimize
sensitive file names, private project names, personal data, and confidential
context while preserving reviewability.

## Open questions

- Should ARF define a registry format for capability positive and negative
  boundaries?
- How should routing traces be represented in compact user-facing output?
- Which benchmark fixtures should test compound requests with multiple primary
  capabilities?

## References

- `RFC_TEMPLATE.md`
- `STYLE_GUIDE.md`
- `ARCHITECTURE.md`
- `CONTRIBUTING.md`
- `rfcs/RFC-0001-reasoning-model.md`
- `rfcs/RFC-0002-evidence-model.md`
- `rfcs/RFC-0003-feedback-contract.md`
- `rfcs/RFC-0004-confidence-model.md`
