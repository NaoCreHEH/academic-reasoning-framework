# Claude Adapter Evaluation

The Claude Code adapter evaluation harness is the first live behavioral layer
for the ARF Claude Code reference plugin.

It is separate from two deterministic layers:

- Structural plugin validation checks that the plugin files, skill descriptions,
  boundaries, and shared references exist.
- Deterministic routing benchmarks check ARF's structured routing behavior in
  Python without invoking Claude Code.
- Live Claude adapter evaluation checks observable behavior from a local Claude
  Code invocation when such an invocation is available.

These layers answer different questions. The routing benchmark does not prove
that Claude Code native skill dispatch selected the correct skill. Plugin
structure tests do not prove that Claude follows the skill boundaries.

The first real 15-case live run produced useful instrumentation evidence rather
than skill-quality conclusions: dispatch passed/failed/skipped was `0/2/13`,
with the two dispatch failures caused by live invocation timeouts; response
passed/failed/skipped was `2/5/8`; marker failures included
`alternative-validity`, `structure-not-proof`, and `limitation`. That evidence
is insufficient to conclude that the skills are wrong. A response-marker failure
should be inspected with public response evidence before editing a skill.

## Dispatch Observability

A correct answer does not prove the correct skill was dispatched.

Dispatch can be marked `PASSED` only when the selected skill identity is
externally observable through the invocation boundary. The evaluator MUST NOT
infer native skill selection from response topic, style, or phrases such as
"as a Python teacher".

Mentioning a skill name in prose is not dispatch evidence.

The local invoker attempts Claude Code `stream-json` output with verbose public
events. Only a public structured Skill tool invocation counts as dispatch
evidence. Debug text, plugin descriptions, system prompt text, final answer
wording, and hidden chain-of-thought are not dispatch evidence.

Plugin load state is observed from public `system/init` data when available.
Unknown plugin load state is not treated as loaded. If `system/init` explicitly
reports that `arf-academic` failed to load, the attempted evaluation fails.

When Claude Code returns a response but does not expose selected skill identity,
dispatch is reported as `SKIPPED` with an observability reason. Response-contract
evaluation may still run against the response.

## Response Markers

Response-contract evaluation uses shallow mechanical markers:

- `ANY` markers pass when at least one normalized pattern appears.
- `ALL` markers pass when every normalized pattern appears.
- Literal forbidden patterns fail when the normalized pattern appears.
- Regex forbidden patterns are reserved for mechanical checks such as obvious
  confidence percentages.

Normalization removes diacritic marks, uses Unicode casefolding, and normalizes
whitespace. This is orthographic normalization only: it does not stem, translate,
correct spelling, use edit distance, tokenize semantically, call an LLM judge,
use embeddings, or score semantic quality.

The evaluator does not produce aggregate quality percentages. It reports
dispatch and response-contract counts separately.

The stream parser prefers the public final result field when present. Otherwise
it reconstructs visible assistant text blocks. It excludes thinking blocks,
tool inputs, tool results, and stderr from response-marker evaluation.

## All-Skipped Results

All-skipped evaluation is not a pass. On a machine without Claude Code, the
live CLI reports skipped cases honestly and exits with code `3`.

`SKIPPED` is an observed limitation state, not an exception sink. It represents
an explicit environment or observability limitation such as a missing Claude
CLI, an unsupported `--plugin-dir` option, unsupported non-interactive print
mode, or unobservable native skill identity.

Unexpected harness or invoker exceptions are not converted to skipped results.
Programmer errors such as `TypeError`, `ValueError`, `AttributeError`, or
`RuntimeError` propagate normally.

Capability inspection and attempted evaluation are treated differently. A
timeout while inspecting `claude --help` means evaluation capability could not
be established and may be reported unavailable. A timeout during the actual
live invocation means evaluation was attempted and failed; it is reported as
`FAILED`, not `SKIPPED`.

Malformed non-empty structured output is a failed attempted evaluation, not a
skipped environment limitation.

## CLI Usage

```text
python scripts/run_claude_adapter_evaluation.py
python scripts/run_claude_adapter_evaluation.py --format json
python scripts/run_claude_adapter_evaluation.py --case dispatch-python-mcq
python scripts/run_claude_adapter_evaluation.py --tag collision
python scripts/run_claude_adapter_evaluation.py --show-responses --timeout 180
```

Exit codes:

- `0`: every evaluated dimension passed and at least one dimension was evaluated.
- `1`: at least one evaluated dimension failed.
- `2`: command-line selection error.
- `3`: all selected dimensions were skipped because live evaluation was
  unavailable.

The command does not print full model responses by default and does not inspect
hidden chain-of-thought.

Use `--show-responses` for local diagnostic runs when public response evidence
is needed. It applies only to text output and should not be used for automated
logs containing sensitive student data. The default live invocation timeout is
180 seconds.

Skill answer quality and dispatch remain separate. A good answer does not prove
that the expected skill was dispatched, and a dispatch observation does not prove
that the answer satisfies the response contract.
