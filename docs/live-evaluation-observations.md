# Live Evaluation Observations

This document records the first three inspected live Claude Code adapter
evaluation cases. Three cases are insufficient to estimate adapter quality
statistically. They do not support success percentages and do not generalize
dispatch quality beyond the observed cases.

## response-uml-choice-not-error

- Case: `response-uml-choice-not-error`
- Observed dispatch: `arf-academic:uml-analysis`
- Response contract result: passed
- Public observation: the response said composition was not mandatory and
  correctly explained lifecycle semantics. It also moved from a typical musical
  domain assumption to stronger wording that the composition was semantically
  false, while stating that the diagram was not available and that the exact
  specification should be checked.
- Finding classification: optional improvement / debatable calibration issue
- Consequence: the response was broadly correct, but its strongest language was
  not fully supported by available lifecycle evidence. UML guidance now
  reinforces that typical or assumed domains should produce hypotheses or
  debatable choices, not demonstrated-error wording.

## response-architecture-files-not-names

- Case: `response-architecture-files-not-names`
- Observed dispatch: `arf-academic:architecture-review`
- Response contract result: marker failure
- Public observation: the response correctly said folder presence proves
  nothing about architecture quality, naming alone is insufficient, actual code
  and dependencies must be inspected, and directory structure is a hypothesis
  rather than evidence.
- Finding classification: benchmark false negative
- Consequence: the marker vocabulary was too narrow and missed equivalent
  wording such as "ne prouve rien", "ne suffit pas", and "pas une preuve". The
  prompt also contaminated the conceptual case with current-repository context,
  so the case now explicitly says not to use the current repository.

Additional observation:

- Finding classification: adapter presentation issue
- Public observation: the response narrated internal skill/example wording.
- Consequence: the shared contract now tells the adapter to apply skills and
  references silently while still explaining evidence, inspected files,
  limitations, and public reasoning conclusions.

## response-confidence-no-percentage

- Case: `response-confidence-no-percentage`
- Observed dispatch: skipped because no Skill tool invocation was externally
  observable
- Response contract result: marker failure
- Public observation: the response correctly said no PFE report had been
  supplied, no part of a report had been inspected, and giving confidence on
  the whole PFE would be invented.
- Finding classification: benchmark false negative
- Consequence: the prompt contained a false premise for a fresh invocation by
  claiming that part of the report had been seen. The case now states that no
  report was supplied and checks for conservative refusal or insufficient review
  scope.

## Live Rerun After Contract Narrowing

Three live reruns after the previous adapter hardening produced additional
evidence:

- `response-uml-choice-not-error`: dispatch to `arf-academic:uml-analysis`
  passed and the mechanical response contract passed. The public response again
  overclassified from a typical musical/playlist assumption by calling the
  association semantically false, then later said certainty was not possible.
  This reproduces the UML calibration issue after the prior narrow correction.
  The UML workflow now requires an evidence gate before classifying a relation
  as a demonstrated semantic error.
- `response-architecture-files-not-names`: dispatch was skipped because no
  Skill tool invocation was externally observable, while the response contract
  passed. The public response did not narrate internal skill instructions. No
  architecture skill correction is indicated by this rerun.
- `response-confidence-no-percentage`: dispatch was skipped because no Skill
  tool invocation was externally observable. The old mechanical contract passed,
  but the public response said the confidence level was `0%` and then said that
  assigning a number would be fabrication. Finding classification: benchmark
  false PASSED and response confidence-contract violation. Consequence: the
  regex now rejects confidence-before-percentage wording such as `confiance ...
  0%`. A false PASSED is more dangerous than a false FAILED because the harness
  may certify a violated contract.

The confidence rerun also said it would use `arf-academic:pfe-review` in prose,
but no public Skill tool invocation was observed. This is a pre-dispatch adapter
governance limitation, not a `pfe-review` skill defect. Skill-local contracts
cannot guarantee behavior before the skill is invoked. If ARF needs global
presentation, confidence, or evidence rules before dispatch, a skill-only
adapter may be insufficient. Future investigation may consider plugin hooks,
agent/system-level instructions where supported, or another model-specific
global adapter layer; this remains an unresolved v0.5 adapter question.

## Post-PR-20 Live Evaluations

Two live evaluations after PR #20 produced additional evidence:

- `response-uml-missing-lifecycle-evidence`: dispatch to
  `arf-academic:uml-analysis` passed. The mechanical response contract failed
  because `insufficient-domain-evidence` did not match the public wording. The
  public reasoning order matched the new evidence gate: without a specification
  or business rules, it did not classify the association as a demonstrated
  error; it treated composition as a possible supposition; it named the business
  question that would resolve the model; and it evaluated independent existence,
  sharing, and disappearance with `Repertoire` before introducing a
  typical-domain example. Finding classification: benchmark false negative.
  Conclusion: do not modify the UML skill from this observation.
- `response-confidence-no-percentage`: dispatch to
  `arf-academic:pfe-review` passed. The response contract failed because the
  public response used the contradiction `~0%, non evaluable`: it expressed a
  numeric confidence value while later saying no report, section, page, or
  extract had been supplied and that assigning confidence would be fabricated.
  The confidence percentage violation was detected. The same response narrated
  an internal skill rule. Finding classification: demonstrated
  confidence-contract violation and demonstrated adapter presentation issue.

The prior pre-dispatch limitation remains real, but this new run proves the PFE
confidence and narration behaviors can also occur after specialist skill
invocation. The PFE confidence issue is now reproduced across two live runs
under different dispatch-observability conditions. This is not a defect rate
and does not generalize to all skills.

## Instrumentation Open Issue

PowerShell diagnostic output displayed UTF-8 mojibake such as
`sÃƒÂ©mantique`, `dÃƒÂ©pÃƒÂ´t`, and `pÃƒÂ©rimÃƒÂ¨tre`. The parsed response markers
passed despite display corruption, indicating the internal Python string used
for evaluation may differ from terminal rendering. The PowerShell display
encoding path needs separate investigation. This is not evidence that source
text is corrupted without raw-byte evidence, and no encoding workaround is
implemented in this PR.
