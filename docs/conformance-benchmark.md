# Structural Conformance Benchmark

The structural conformance benchmark validates explicit machine-readable ARF
objects and validation outcomes. It covers implemented structural contracts for
RFC-0002 Evidence Model, RFC-0003 Feedback Contract, RFC-0004 Confidence Model,
and RFC-0006 Request Interpretation Model.

It does not implement an AI reasoning engine, natural-language semantic
grading, embeddings, model calls, or full RFC conformance.

## Purpose

The benchmark executes named operations that construct ARF objects or call
existing validation helpers. Each case declares whether the operation should be
accepted or rejected, and rejected cases declare the expected exception type.

Operations are explicit fixtures. They are never generated from descriptions,
and case descriptions are documentation only.

## Relationship To RFCs

RFC-0002 is represented through evidence items, evidence graphs, claims, and
claim-to-evidence references.

RFC-0003 is represented through feedback items and optional validation
requirements such as required impact or recommendation.

RFC-0004 is represented through confidence labels, non-confidence states, and
structural confidence-basis validation.

RFC-0006 is represented through interpreted signals, interpretation candidates,
subtasks, and strict conversion to routing requests.

RFC-0001 full reasoning conformance is not benchmarked because the repository
does not yet implement a reasoning execution layer.

RFC-0005 routing behavior is covered by the separate routing regression
benchmark. This benchmark may include conversion-boundary cases, but it does
not replace the routing benchmark.

## Expectations

`ACCEPT` means the operation should return normally.

`REJECT` means the operation should raise the expected exception type or a
subclass.

The runner compares exception types, not exception message text. It does not
inspect tracebacks.

## Structural Only

Structural acceptance does not imply semantic conformance. For example:

- a `Claim` with no evidence may be structurally valid but fail RFC-0002 if it
  is an important claim requiring evidence;
- a `FeedbackItem` recommendation may be non-empty but semantically irrelevant;
- a confidence basis may exist but still be poor evidence;
- an interpretation candidate may have provenance but still be incorrectly
  inferred.

The benchmark only evaluates invariants implemented in code. It performs no
semantic scoring, uses no percentages as calibrated confidence, and makes no
model-specific claims.

## What This Benchmark Does Not Prove

This benchmark does not prove evidence relevance, evidence sufficiency for
important claims, recommendation quality, pedagogical appropriateness, semantic
confidence calibration, natural-language interpretation quality, or full RFC
conformance.
