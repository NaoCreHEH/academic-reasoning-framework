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

## Instrumentation Open Issue

PowerShell diagnostic output displayed UTF-8 mojibake such as
`sÃƒÂ©mantique`, `dÃƒÂ©pÃƒÂ´t`, and `pÃƒÂ©rimÃƒÂ¨tre`. The parsed response markers
passed despite display corruption, indicating the internal Python string used
for evaluation may differ from terminal rendering. The PowerShell display
encoding path needs separate investigation. This is not evidence that source
text is corrupted without raw-byte evidence, and no encoding workaround is
implemented in this PR.
