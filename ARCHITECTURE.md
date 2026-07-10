# Architecture

ARF separates normative reasoning rules from model-specific implementations.

```text
Input
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

### Implementations

Adapters translate the specifications into concrete prompts, skills, agents, or software components.

### Benchmark

Conformance and regression cases verify that changes improve behavior rather than merely changing wording.
