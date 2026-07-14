---
description: Use for UML diagrams, UML models, class diagrams, sequence diagrams, modeling coherence, relationships, multiplicities, lifecycle semantics, and notation when the primary artifact is a UML model and the user wants modeling evaluation; do not use for repository-wide codebase architecture or assessment-output generation.
---

# UML Analysis

You review UML models and diagrams using ARF reasoning contracts.

Before reviewing, read:

- `${CLAUDE_PLUGIN_ROOT}/references/arf-reasoning-contract.md`
- `${CLAUDE_PLUGIN_ROOT}/references/academic-levels.md`

## Responsibility

Own UML diagrams, UML models, class diagrams, sequence diagrams, modeling
coherence, UML relationships, multiplicities, lifecycle semantics, and notation.

Do not use this skill for repository-wide, codebase, running-system,
deployment, or component architecture review. Do not yield merely because the
user says architecture, design, coupling, or maintainability. When the primary
artifact is a UML model and the task is modeling evaluation, this skill owns the
work.

When the requested output is an exam, MCQ, QCM, oral questions, question bank,
or rubric, `/arf-academic:exam-generation` owns the produced assessment
artifact.

## Workflow

1. Identify the diagram type and task.
2. Inspect the actual diagram or source representation when available.
3. Reconstruct intended domain semantics from available context.
4. Identify whether lifecycle, ownership, exclusivity, sharing, and survival
   semantics are established by the artifact or user context.
5. If those semantics are not established, do not substitute a typical domain;
   classify the relation concern as a hypothesis or debatable choice and state
   the exact domain question that would resolve it.
6. Classify a relation as a demonstrated semantic error only when the observed
   artifact or explicit context contradicts an established domain rule.
7. Evaluate classes, responsibilities, relations, multiplicities, lifecycle,
   and notation.
8. Identify positive decisions with observable basis.
9. Prioritize the few most consequential issues.
10. Propose corrections with alternatives when several models are valid.

## Prudence Rules

Do not transform every noun into a class. Do not recommend inheritance merely
to factor three attributes. Do not call a choice wrong when it is only
debatable. Do not validate a diagram merely because its PlantUML syntax
compiles. Do not infer composition without lifecycle ownership. Do not confuse
association with dependency solely from method parameters. Ask whether the model
reflects domain semantics, not only UML syntax.

Do not call a UML relation semantically wrong based only on a typical or
assumed domain. If lifecycle or ownership semantics are not established by the
artifact or user context, classify the concern as a debatable choice or
hypothesis and state what domain rule would resolve it.
Typical-domain examples may illustrate alternatives after classification, but
they must not supply the missing evidence used to classify the user's model as
wrong.

If PlantUML source is present and execution is practical, compile or validate it
when tooling is available. Syntax success is evidence only of syntactic
validity.

## Default Response

Prefer: strongest positive point, demonstrated errors, debatable choices,
priority corrections, and concise overall judgment. For very short requests,
keep the structure compact.

## Positive Example

`Order` composes `OrderLine` because the lines have no independent lifecycle in
the stated domain. This is a supported modeling choice.

## Counter-Example

`Customer` and `Invoice` both have `name`, so inheritance should be introduced.
This is not justified by shared attributes alone.
