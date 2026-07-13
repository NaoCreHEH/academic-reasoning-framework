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

## Dispatch Observability

A correct answer does not prove the correct skill was dispatched.

Dispatch can be marked `PASSED` only when the selected skill identity is
externally observable through the invocation boundary. The evaluator MUST NOT
infer native skill selection from response topic, style, or phrases such as
"as a Python teacher".

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

Normalization uses Unicode casefolding and whitespace normalization only. It
does not stem, tokenize semantically, call an LLM judge, use embeddings, or
score semantic quality.

The evaluator does not produce aggregate quality percentages. It reports
dispatch and response-contract counts separately.

## All-Skipped Results

All-skipped evaluation is not a pass. On a machine without Claude Code, the
live CLI reports skipped cases honestly and exits with code `3`.

## CLI Usage

```text
python scripts/run_claude_adapter_evaluation.py
python scripts/run_claude_adapter_evaluation.py --format json
python scripts/run_claude_adapter_evaluation.py --case dispatch-python-mcq
python scripts/run_claude_adapter_evaluation.py --tag collision
```

Exit codes:

- `0`: every evaluated dimension passed and at least one dimension was evaluated.
- `1`: at least one evaluated dimension failed.
- `2`: command-line selection error.
- `3`: all selected dimensions were skipped because live evaluation was
  unavailable.

The command does not print full model responses by default and does not inspect
hidden chain-of-thought.
