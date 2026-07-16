# Claude Multi-Run Analytics

This document describes the offline analytics layer for repeated Claude Code
adapter evaluation reports.

The analyzer reads JSON reports produced by:

```text
python scripts/run_claude_adapter_evaluation.py --format json --output PATH
```

It does not invoke Claude, require Claude Code, use network access, or call any
model API. It uses existing JSON evidence only.

## Why This Exists

Raw `FAILED` counts in live adapter runs can mix different phenomena:

- observed wrong dispatch;
- dispatch non-observation;
- response-contract variation;
- invocation timeout;
- invocation return-code failure;
- encoding or stream parsing failure;
- plugin load failure;
- whole-run infrastructure failure.

Infrastructure failure records are evidence about the evaluation environment,
not evidence that the expected capability was routed incorrectly.

A run where every invocation returns code 1 is unusable for behavioral
conclusions.

## Run Usability

Runs are classified as:

- `usable`: no invocation or infrastructure failure records are present.
- `degraded`: at least one infrastructure failure is present, but at least one
  case still produced an eligible behavioral observation.
- `unusable`: no eligible behavioral observations are present because all
  records are infrastructure failures or evaluation-unavailable records.

Response-contract failures alone do not make a run degraded. Dispatch skipped
because a skill invocation was not externally observable also does not make a
run degraded.

## Behavioral Denominators

Behavioral stability uses eligible observations, not total input runs.

By default, unusable runs remain visible in run-level infrastructure counts but
are excluded from per-case behavioral denominators. Degraded runs contribute
their eligible cases, while their infrastructure-failed cases do not become
wrong dispatches or response-contract failures.

The `--include-unusable` option includes unusable-run infrastructure records in
per-case infrastructure counts. It still does not turn infrastructure failures
into behavioral dispatch or response failures.

## Case-Set Consistency

By default, all input reports must contain the same case identifiers. Case
order may differ.

If reports intentionally use different case sets, pass:

```text
python scripts/analyze_claude_adapter_runs.py live-runs --allow-case-set-differences
```

In union mode, missing case entries are not treated as skipped or failed. They
simply reduce the number of observations for that case.

## CLI Usage

Analyze all immediate JSON reports in a directory:

```text
python scripts/analyze_claude_adapter_runs.py live-runs
```

Analyze explicit files:

```text
python scripts/analyze_claude_adapter_runs.py live-runs/run-1.json live-runs/run-2.json
```

Write a text report while still printing to the console:

```text
python scripts/analyze_claude_adapter_runs.py live-runs --output reports/analytics.txt
```

Write JSON:

```text
python scripts/analyze_claude_adapter_runs.py live-runs --format json --output reports/analytics.json
```

The text report uses counts and fractions rather than percentages by default.
The JSON report includes denominators, run counts, infrastructure category
counts, and per-case summaries. It does not include raw model responses, raw
diagnostic lists, or raw input JSON.

Exit codes:

- `0`: successful analysis;
- `1`: analysis completed, but at least one source report's precomputed counts
  disagreed with counts recalculated from `results`;
- `2`: CLI, input, schema, or case-set error.

Infrastructure failures or model behavior failures are analysis data. They do
not by themselves make the analyzer fail.

## Conceptual Examples

A usable run may include correct observed dispatch, dispatch non-observation
with an otherwise valid response, and response-contract failures. These are
behavioral observations.

A degraded run may include a timeout for one case and valid behavioral
observations for other cases. The timeout is counted as infrastructure; the
other cases still contribute to behavioral stability.

An unusable run may contain only `Claude invocation failed with return code 1`
records. It remains visible as infrastructure evidence, but it contributes no
wrong dispatches and no response-contract failures.

A few repeated runs are not statistically significant. The analytics layer does
not produce one global ARF score and does not claim universal routing quality.
