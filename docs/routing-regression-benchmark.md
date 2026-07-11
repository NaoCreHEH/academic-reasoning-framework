# Routing Regression Benchmark

The routing regression benchmark validates the boundary between RFC-0006
interpretation objects and RFC-0005 structured routing.

Benchmark cases start from explicit `InterpretedSubtask` objects. Case
descriptions are documentation only and are never parsed.

## Purpose

The benchmark exercises known routing collision scenarios after interpretation
signals have already been represented. It checks conversion to `RoutingRequest`,
structured routing behavior, and expected benchmark outcomes.

It is model-independent. It does not use natural-language parsing, regex
classification, keyword scoring, embeddings, LLMs, or model-specific behavior.

## Boundary

The benchmark boundary is:

```text
InterpretedSubtask
  -> RoutingRequest
  -> StructuredRoutingEngine
  -> benchmark expectation comparison
```

Unresolved interpretation blocks routing. The benchmark verifies that
unresolved artifact signals are not silently omitted or converted into resolved
taxonomy values.

Normalization remains a routing concern. For example, interpretation can
preserve `mcq`, while the structured router may normalize it for exact
taxonomy matching.

## Regression Assets

The built-in cases cover collisions such as Python MCQ generation, UML class
diagram review with architecture wording, PFE oral questions, unresolved
project documents, conflicting artifact descriptions, unknown explicit
capabilities, lowercase taxonomy values, and compound independent subtasks.

Passing this benchmark does not prove natural-language interpretation quality.
It proves deterministic behavior after interpretation signals have been
represented.
