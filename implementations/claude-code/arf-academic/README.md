# ARF Academic Claude Code Plugin

This plugin is an experimental reference implementation for Academic Reasoning
Framework v0.5. It packages five Claude Code skills that adapt ARF reasoning
contracts for academic and software-engineering work.

It is model-specific. The ARF core remains model-independent, and this plugin
does not claim full ARF conformance.

## Included Skills

- `/arf-academic:uml-analysis`
- `/arf-academic:architecture-review`
- `/arf-academic:pfe-review`
- `/arf-academic:exam-generation`
- `/arf-academic:python-teaching`

## Ownership Boundaries

The skill descriptions encode RFC-0005-style ownership boundaries. Exam
generation owns assessment artifacts such as MCQs, QCMs, oral questions,
question banks, rubrics, grading instruments, and examinations. UML analysis
owns UML models and diagram semantics. Architecture review owns repositories,
codebases, and running systems. PFE review owns academic project documents.
Python teaching owns learner-facing Python correction.

## Local Validation

Structural repository tests do not require Claude Code to be installed:

```text
python -m unittest discover -s tests -v
python scripts/validate_claude_plugin.py
```

If Claude Code is installed, the helper attempts:

```text
claude plugin validate implementations/claude-code/arf-academic
```

If the local Claude version uses different validation syntax, the helper will
report that through the native command result. The structural tests remain the
CI authority for this repository.

## Local Loading

For local development, use the current Claude Code plugin directory option:

```text
claude --plugin-dir ./implementations/claude-code/arf-academic
```

After changing plugin files in an active Claude Code session, run:

```text
/reload-plugins
```

This plugin is not yet published in a public marketplace.
