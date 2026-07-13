# Architecture

ARF separates normative reasoning rules from model-specific implementations.

```text
Input
  -> Request Interpretation
  -> Router
  -> Evidence Model
  -> Ontology
  -> Pedagogical Context
  -> Feedback Contract
  -> Output
```

## Layers

### Specifications

Normative RFCs define required behavior using MUST, SHOULD, MAY, MUST NOT, and SHOULD NOT.

### Core contracts

Reusable, model-independent schemas for evidence, confidence, feedback, routing, and evaluation.

### Ontology

Definitions, observable indicators, exceptions, counter-examples, false positives, and false negatives.

The `core/ontology/` package provides the first machine-readable structural
primitives for stable RFC concepts. It is limited to data representation and
validation; it does not implement reasoning, routing execution, or
model-specific behavior.

The `core/routing/` package represents machine-readable capability ownership
and boundaries. It provides registry data for RFC-0005 concepts.

The structured routing engine consumes structured request signals and applies
deterministic ownership rules. Free-form request interpretation remains outside
the engine.

The interpretation layer produces structured signals from external
interaction, conversation context, and artifacts. Structured routing selects
capabilities from those signals, and capability execution remains separate.

The `core/interpretation/` package represents RFC-0006 interpretation state and
provenance. Conversion to `RoutingRequest` is strict: unresolved routing
signals are not silently omitted. Free-form interpretation and artifact
detectors remain unimplemented, and routing remains a separate layer.

The routing regression benchmark exercises the boundary from `InterpretedSubtask`
to `RoutingRequest` to `StructuredRoutingEngine` to expectation comparison. It
uses explicit interpretation objects rather than parsing benchmark descriptions.

The structural conformance benchmark evaluates implemented RFC invariants for
evidence, claims, confidence, feedback, and interpretation objects. It executes
explicit operations and compares validation outcomes; benchmark results do not
replace semantic reasoning review.

### Implementations

Adapters translate the specifications into concrete prompts, skills, agents, or software components.

### Benchmark

Conformance and regression cases verify that changes improve behavior rather than merely changing wording.
