# Academic Reasoning Framework

**A standard for transparent, evidence-based AI reasoning in education and software engineering.**

Academic Reasoning Framework (ARF) defines how AI systems should observe, infer, explain uncertainty, and produce reviewable recommendations. It is model-agnostic: Claude, GPT, Gemini, local models, and future systems can implement the same reasoning contracts.

## Core principles

1. Every important critique must be justified by evidence.
2. Conclusions must be traceable to observations.
3. Uncertainty is part of the answer.
4. Multiple valid solutions must be acknowledged.
5. Pedagogical level takes precedence over unnecessary technical sophistication.

## Project status

ARF is in early specification work. The initial milestones focus on governance, normative RFCs, evidence and feedback contracts, ontology, benchmarks, and reference implementations.

## Repository structure

- `rfcs/`: normative specifications
- `core/`: model-independent reasoning contracts
- `ontology/`: shared technical and pedagogical concepts
- `benchmark/`: evaluation datasets and scoring rules
- `implementations/`: model-specific adapters
- `tests/`: conformance and regression tests
- `docs/`: architecture and contributor documentation

See [ROADMAP.md](ROADMAP.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [CONTRIBUTING.md](CONTRIBUTING.md).

## Running benchmarks

```text
python scripts/run_benchmarks.py
```

## License

MIT. See [LICENSE](LICENSE).
