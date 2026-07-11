# Interpretation Ontology

The `core/interpretation/` package provides machine-readable structural
primitives for RFC-0006 request interpretation.

It implements interpretation state, provenance, candidates, subtasks,
limitations, ambiguity, clarification needs, and strict conversion boundaries.
It does not claim full RFC-0006 conformance.

## States

Interpretation signals use exactly three states:

- `RESOLVED`
- `UNRESOLVED`
- `ABSENT`

`UNKNOWN` is intentionally not used. RFC-0004 confidence states remain separate
from RFC-0006 interpretation states.

## Candidates and Resolved Values

An `InterpretationCandidate` records a possible value with basis, provenance,
and limitations. A candidate is not automatically a resolved signal.

A resolved signal must contain a value, provenance, and basis. An unresolved
signal preserves candidates or conflict without choosing a value. An absent
signal represents a signal that is not present in the available input.

## Provenance

`SignalProvenance` records where a signal or candidate came from, such as an
explicit user statement, trusted structured caller field, connector artifact
type, direct artifact inspection, artifact metadata, conversation context, or
derived interpretation.

The package does not define a universal provenance authority ranking.

## Compound Subtasks

`InterpretedSubtask` represents one independently interpretable subtask.
`InterpretationResult` groups one or more subtasks, so compound requests can
preserve their boundaries.

The ontology does not automatically decompose prose.

## Conversion Boundary

`to_routing_request` converts one subtask to `RoutingRequest` only when the
user objective is resolved and every optional routing signal is either resolved
or absent.

Unresolved optional signals block conversion rather than being silently
omitted. This preserves the RFC-0006 boundary that unresolved values must not
enter structured routing as resolved taxonomy values.

Explicit capability applicability remains a routing concern. Conversion
preserves a resolved explicit capability value unchanged, even when it is not a
registered capability.

## Non-Goals

This package does not parse prose, detect artifacts, inspect files, call a
model, use an LLM, use embeddings, apply keyword scoring, or perform routing.
