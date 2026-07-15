# First Live Matrix - 2026-07

This baseline records one observed run. It is not a golden output and is not
used as a deterministic CI expectation. Live Claude behavior may vary between
runs and model or CLI versions.

No observed wrong dispatch occurred in the 13 dispatch-PASSED cases. This does
not prove universal routing correctness.

## Environment

- Operating system: Windows
- Python: 3.13
- Invocation: local Claude Code CLI
- Plugin loading: ARF plugin loaded through `--plugin-dir`
- Command: `python scripts/run_claude_adapter_evaluation.py --timeout 180`

No local user path, session identifier, raw stream JSON, hidden reasoning, or
authentication material is included in this record.

## Aggregate Counts

- Cases: 16
- Dispatch passed: 13
- Dispatch failed: 0
- Dispatch skipped: 3
- Response contract passed: 4
- Response contract failed: 2
- Response contract skipped: 10
- Fully successful cases: 12

## Matrix

| Case | Dispatch | Observed Skill | Response Contract |
| --- | --- | --- | --- |
| `dispatch-python-mcq` | PASSED | `arf-academic:exam-generation` | SKIPPED |
| `dispatch-python-submission` | PASSED | `arf-academic:python-teaching` | SKIPPED |
| `dispatch-uml-architecture-wording` | PASSED | `arf-academic:uml-analysis` | SKIPPED |
| `dispatch-repository-architecture` | PASSED | `arf-academic:architecture-review` | SKIPPED |
| `dispatch-pfe-contribution` | PASSED | `arf-academic:pfe-review` | SKIPPED |
| `dispatch-pfe-oral-questions` | PASSED | `arf-academic:exam-generation` | SKIPPED |
| `dispatch-uml-exam` | SKIPPED | none observable | SKIPPED |
| `dispatch-python-question-bank` | SKIPPED | none observable | SKIPPED |
| `dispatch-repository-student-context` | PASSED | `arf-academic:architecture-review` | SKIPPED |
| `dispatch-misspelled-qcm` | PASSED | `arf-academic:exam-generation` | SKIPPED |
| `response-python-no-oop` | PASSED | `arf-academic:python-teaching` | PASSED |
| `response-uml-choice-not-error` | PASSED | `arf-academic:uml-analysis` | FAILED |
| `response-uml-missing-lifecycle-evidence` | PASSED | `arf-academic:uml-analysis` | PASSED |
| `response-architecture-files-not-names` | SKIPPED | none observable | PASSED |
| `response-pfe-company-vs-student` | PASSED | `arf-academic:pfe-review` | PASSED |
| `response-confidence-no-percentage` | PASSED | `arf-academic:pfe-review` | FAILED |

## Inspected Rerun Findings

- `response-uml-choice-not-error`: targeted rerun dispatched to
  `arf-academic:uml-analysis`. The public response said the composition was not
  automatic, depended on lifecycle semantics, and that the user's simple
  association was not an error in itself. Classification: `alternative-validity`
  marker false negative. The UML skill was not changed from this evidence.
- `response-confidence-no-percentage`: the full matrix detected a real
  confidence-percentage contract violation after observed `pfe-review`
  dispatch. A targeted rerun did not reproduce numeric confidence, but did
  expose direct named-skill narration that the older marker set missed.
- `dispatch-uml-exam`: the full matrix dispatch was SKIPPED. A targeted rerun
  later observed `arf-academic:exam-generation` and the response refused to
  invent diagram errors without a UML artifact. The initial SKIPPED result is
  not a demonstrated routing collision.
- `dispatch-python-question-bank`: the full matrix dispatch was SKIPPED. Two
  targeted reruns also produced SKIPPED dispatch while asking for the missing
  Python submission and discussing question-bank or assessment usage.
  Classification: reproduced dispatch non-observation under missing-artifact
  clarification. A plausible hypothesis is that Claude clarified a missing
  primary artifact before invoking a specialist skill; this is not demonstrated
  causal truth.
- `response-architecture-files-not-names`: the conceptual architecture response
  contract passed without observable Skill invocation.

## Interpretation Limits

The three full-matrix SKIPPED dispatch cases remain SKIPPED. Correct
missing-artifact clarification does not convert unobservable dispatch into
PASSED. Response topic, question vocabulary, cognitive-level language, and
artifact clarification are not dispatch evidence.
