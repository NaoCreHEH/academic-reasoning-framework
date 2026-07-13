# Benchmark Orchestration

The benchmark orchestration layer runs the existing ARF benchmark suites through
one stable programmatic API and one minimal command-line entry point.

Routing regression and structural conformance remain separate suites because
they evaluate different contracts. Routing checks interpretation-to-routing
behavior. Structural conformance checks implemented object invariants and
validation outcomes. The orchestrator does not merge those semantics into one
artificial score.

## Suites

Stable suite identifiers are:

- `routing-regression`
- `structural-conformance`

The orchestration layer runs existing benchmark logic. It does not reimplement
routing, conformance validation, natural-language interpretation, semantic
grading, AI reasoning, embeddings, or model calls.

Structural benchmark limitations remain unchanged: structural acceptance does
not prove evidence sufficiency, recommendation quality, pedagogical
appropriateness, semantic confidence calibration, natural-language
interpretation quality, or full RFC conformance.

## CLI Usage

Run all suites:

```text
python scripts/run_benchmarks.py
```

Run only routing:

```text
python scripts/run_benchmarks.py --suite routing
```

Run only conformance with JSON output:

```text
python scripts/run_benchmarks.py --suite conformance --format json
```

Supported suite selections are `all`, `routing`, and `conformance`.

Supported formats are `text` and `json`.

## Text Output

Text output reports each selected suite and an overall status:

```text
routing-regression: PASSED (10/10)
structural-conformance: PASSED (44/44)
Overall: PASSED
```

Failed suite diagnostics are printed below that suite. Passing cases do not
produce diagnostics.

## JSON Output

JSON output uses deterministic suite ordering and enum values:

```json
{
  "success": true,
  "total_suites": 2,
  "passed_suites": 2,
  "failed_suites": 0,
  "total_cases": 54,
  "passed_cases": 54,
  "failed_cases": 0,
  "suites": []
}
```

The real output includes one suite object per selected suite.

## Exit Codes

- `0`: all selected suites pass.
- `1`: one or more selected suites fail.
- `2`: command-line argument error from `argparse`.
