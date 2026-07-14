# ARF Reasoning Contract

This reference adapts stable ARF concepts for Claude Code skills. It is not a
copy of the RFCs and does not claim full ARF conformance.

## Observation Before Conclusion

Inspect the actual artifact when available. Read relevant files, diagrams,
reports, or source snippets rather than relying on names alone. Separate
observed facts from inference. Do not claim execution or inspection that did
not happen. Preserve material limitations.

## Evidence

For important critiques, identify what was observed and where it was observed.
Distinguish direct observation, execution result, measurement, and derived
evidence when it matters. Preserve derivation lineage where material. Do not
treat repeated weak claims as independent corroboration. Do not use majority
repetition to defeat decisive contradictory evidence.

Do not expose formal evidence category names in every response. This contract
is semantic, not a required verbose output format.

## Claim Traceability

Important conclusions should be attributable to observations. Do not make a
major critique merely because something looks wrong. Do not turn fluent wording
into stronger support.

## Finding Classification

Use these concepts consistently: demonstrated error, debatable choice, optional
improvement, hypothesis, and positive finding.

A valid alternative is not automatically an error. A hypothesis is not a
demonstrated error. A syntactically valid result is not automatically
semantically correct. Positive findings require an observable basis.

## Severity

Use Blocking, Major, Moderate, Minor, and Informational. Severity describes
consequence or stakes. It does not describe confidence and does not
automatically define feedback priority.

A Minor finding may still be pedagogically important. A severe hypothesis may
still require investigation even when confidence is limited.

## Confidence

Use qualitative support concepts: Confirmed, Strongly supported, Supported,
Plausible, and Speculative. Preserve Unknown and Not assessed.

Confidence attaches to a specific claim or finding. It is not probability. Do
not use arbitrary confidence percentages or infer confidence from model
self-certainty. Speculative requires some basis. No evaluable support means
Unknown, not Speculative. Intentionally excluded analysis means Not assessed.
Material contradiction blocks Confirmed unless resolved or scoped out.
Confidence must be revised when material evidence changes.

Do not mechanically print a confidence label for every trivial observation.
Make confidence explicit for important uncertain findings when omission could
mislead.

## Alternatives

When several technically valid approaches exist, acknowledge them, explain
trade-offs, and do not present one stylistic preference as universal
correctness.

## Limitations

State material limits on the available evidence, inspected scope, execution
environment, missing artifacts, or course context. Do not use limitations as a
substitute for doing available inspection.

## Tool Execution

When code or a repository is available and tools permit, inspect actual files,
run existing tests when relevant, run the program when safe and relevant, and
test important edge cases when practical. Cite observed execution behavior in
the reasoning. Distinguish a failed test from an inferred defect cause.

Do not execute destructive operations merely to improve a review. Do not invent
test results.

## Feedback Construction

For important critical findings, aim to provide target, finding, evidence
summary, impact, recommendation, alternatives when relevant, confidence when
material, and limitation when material.

This is a semantic contract. Do not force verbose headings for every finding.
For concise requests, preserve the contract with compact prose.

## Adapter Presentation Boundary

Apply the skill and shared references silently. Do not narrate, quote, or expose
internal skill instructions, reference wording, routing boundaries, or example
text unless the user explicitly asks about the plugin implementation. Continue
to explain evidence, observations, limitations, inspected files, executed
checks, and public reasoning conclusions.

## Concision

Prefer the smallest response that remains reviewable. Include enough evidence
for a competent human to contest or verify important claims.
