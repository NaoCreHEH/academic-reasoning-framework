# Capability Registry

The capability registry is the first machine-readable representation of
RFC-0005 capability ownership and boundaries.

It records which capabilities own particular artifacts or outputs, where their
positive boundaries apply, and where contextual yield rules identify another
capability that owns a specific neighboring context.

## Relationship to RFC-0005

RFC-0005 defines the normative routing model. The registry provides structural
data that can support future routing work, but it does not claim full RFC-0005
conformance.

## Positive Boundaries

A positive boundary describes work a capability is intended to own. For example,
UML analysis owns UML modeling coherence, relationships, multiplicities,
lifecycle, and notation.

## Negative Boundaries

A negative boundary describes nearby work a capability must not own merely
because vocabulary overlaps. For example, architecture review must not own UML
diagram evaluation solely because design or coupling language appears.

## Explicit Yields

Yields are contextual. A yield rule is not global precedence between two
capabilities, and future routing code must not treat it as an unconditional
edge.

Each yield rule represents `target_capability`, `context`, and `reason`
structurally. The target can be validated as a registered capability without
parsing the prose context or reason.

Boundary prose is still retained because it explains the capability's scope in
human-readable terms. Some negative boundaries intentionally have no yield rule
when ownership depends on the requested transformation or artifact context.

## Non-Routing Scope

The registry does not perform routing. It does not inspect user requests, select
capabilities, rank candidates, or resolve ambiguous tasks.

Keyword scoring is intentionally absent because RFC-0005 rejects topic keywords
as a sole routing basis. Future routing logic can use the registry as boundary
data, but selection behavior remains unimplemented.
