# Claude Code Reference Plugin

The ARF Academic Claude Code plugin is the first v0.5 reference
implementation. It is located at:

```text
implementations/claude-code/arf-academic
```

This plugin is model-specific. The ARF core remains model-independent.

## Purpose

The plugin uses Claude Code native skill dispatch to expose five academically
focused skills:

- `uml-analysis`
- `architecture-review`
- `pfe-review`
- `exam-generation`
- `python-teaching`

Skill descriptions encode RFC-0005 capability boundaries to reduce collisions.
Shared skill instructions adapt RFC-0001 through RFC-0004 reasoning, evidence,
feedback, severity, confidence, alternatives, and limitation principles.

The plugin does not execute the Python `StructuredRoutingEngine`, does not
duplicate benchmark logic, does not intercept every prompt, does not run an LLM
server, and does not prove full ARF conformance.

It is not yet published in a public marketplace.

## Local Validation

Structural validation does not require Claude Code:

```text
python -m unittest discover -s tests -v
python scripts/validate_claude_plugin.py
```

If the Claude CLI is installed, the helper attempts:

```text
claude plugin validate implementations/claude-code/arf-academic
```

If the Claude CLI is absent, the helper prints a SKIP message and exits
successfully.

## Local Loading

For local development, use:

```text
claude --plugin-dir ./implementations/claude-code/arf-academic
```

After changing plugin files in an active Claude Code session, run:

```text
/reload-plugins
```

## Boundaries

The plugin operationalizes ARF contracts in skill instructions. It is an
adapter, not a normative source. The RFCs and model-independent core remain the
contract authority.
