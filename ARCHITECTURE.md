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

### Implementations

Adapters translate the specifications into concrete prompts, skills, agents, or software components.

### Benchmark

Conformance and regression cases verify that changes improve behavior rather than merely changing wording.
