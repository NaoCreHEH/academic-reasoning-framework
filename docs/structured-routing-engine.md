# Structured Routing Engine

The structured routing engine implements a deterministic subset of RFC-0005.
It consumes structured request fields and produces an externally reviewable
`RoutingTrace`.

It does not claim full RFC-0005 conformance.

## Structured Outcome

`RoutingDecision` exposes machine-readable routing outcome data:

- `status` is `SELECTED`, `AMBIGUOUS`, or `NO_MATCH`;
- `candidate_capabilities` contains only capabilities that matched the
  unresolved strongest routing signal;
- `considered_capabilities` contains the full ordered registry consideration
  set.

`RoutingTrace.material_ambiguity` is human-readable review prose. It may explain
an ambiguity, an unknown explicit capability, or why no route was selected. It
MUST NOT be parsed for machine semantics, and its presence does not imply
`AMBIGUOUS`.

## Structured Inputs Only

The engine accepts `user_objective`, `primary_artifact`, `requested_output`,
`domain`, and `explicit_capability` as already-structured values.

It does not infer a missing field from prose. For example, a free-form value
such as `Create an MCQ about Python` is not parsed as the taxonomy value `MCQ`.

## Ownership-Driven Routing

Executable selection is driven by capability ownership fields in the registry:
owned outputs, owned artifacts, and supported domains.

The precedence is:

1. valid applicable explicit selection;
2. unique requested output owner;
3. unique primary artifact owner;
4. unique domain support;
5. preserved ambiguity.

Requested output ownership overrides artifact ownership. When this happens, the
artifact owner can become a supporting capability.

Domain support is a fallback primary signal only when no stronger output or
artifact ownership signal exists. Domain support does not automatically imply
collaboration, and it does not create a supporting capability by itself.

When more than one capability matches the strongest applicable ownership signal,
the decision status is `AMBIGUOUS`. The candidates are exactly the matching
owners or supporters for that signal, in registry insertion order. Unrelated
considered capabilities are not candidates.

## Matching

Matching is exact after conservative normalization: surrounding whitespace is
trimmed and strings are casefolded.

The engine does not tokenize prose, search substrings, use fuzzy matching, apply
keyword routing, compute numeric scores, use embeddings, or call an LLM.

## Explicit Selection

A registered explicit capability is honored when it has structural support or
when no ownership or domain signal contradicts it.

An unknown explicit capability preserves ambiguity. An explicit capability that
conflicts with a unique requested output owner or artifact owner is not silently
forced.

## Supporting Capabilities

Supporting capabilities are conservative. The engine currently adds an artifact
owner when a different output owner is primary.

A capability never appears as both primary and supporting.

Future collaboration rules require explicit structured semantics. The engine
does not infer cross-domain collaboration from a technology domain alone.

## Contextual Yield Rules

Contextual yield rules are retained as traceable boundary metadata. Their
`context` and `reason` fields are not executable routing logic yet.

The engine does not parse or execute yield-rule prose. Future routing behavior
can make those rules executable only after their contexts become structured
machine-readable conditions.
