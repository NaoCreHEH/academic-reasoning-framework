---
description: Use when the requested output is an MCQ, QCM, examination, oral questions, question bank, rubric, grading instrument, or assessment instrument, even when the subject is Python, UML, architecture, PFE, or security; do not use merely to correct learner code or review an artifact when no assessment instrument is requested.
---

# Exam Generation

You produce academic assessment artifacts using ARF reasoning contracts.

Before generating, read:

- `${CLAUDE_PLUGIN_ROOT}/references/arf-reasoning-contract.md`
- `${CLAUDE_PLUGIN_ROOT}/references/academic-levels.md`

## Responsibility

Own the requested output when producing MCQ, QCM, examinations, oral questions,
question banks, rubrics, grading instruments, or assessment instruments.

Assessment output ownership applies even when the topic is Python, UML,
architecture, PFE, or security. Domain capabilities may provide subject-matter
reasoning, but this skill owns the assessment artifact.

Do not use merely to correct learner code or review an artifact when no
assessment instrument is requested.

## Workflow

1. Identify audience and pedagogical level.
2. Identify source material and assessed competencies.
3. Identify requested assessment format.
4. Set scope and difficulty distribution.
5. Generate questions that test understanding rather than wording recall.
6. Ensure answers are defensible from source material or stated curriculum.
7. Avoid accidental clues and ambiguous distractors.
8. Review coverage and redundancy.
9. Provide answer key or expected-answer guidance when requested.

## MCQ And QCM Rules

Use one clearly best answer unless a multiple-answer format is explicitly
requested. Distractors must be plausible but wrong for a reason. Avoid `all of
the above` by default. Avoid pure trivia unless the objective is knowledge
recall. Do not make the longest answer systematically correct.

## Oral Question Rules

Prioritize analysis, justification, trade-offs, debugging, limitations, and
personal contribution. Avoid questions answered verbatim by one report
sentence. When useful, include expected reasoning rather than a scripted exact
answer.

## Default Response

Deliver the requested assessment artifact, then include answer key, expected
reasoning, or grading guidance when requested or necessary for usability.

## Positive Example

`Create 20 MCQs on Python dictionaries` is owned by this skill because the
requested output is an assessment instrument.

## Counter-Example

`Correct this Python submission` is owned by `/arf-academic:python-teaching`,
not this skill, because no assessment artifact is requested.
