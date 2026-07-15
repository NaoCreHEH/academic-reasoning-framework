from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "README.md",
    "ROADMAP.md",
    "ARCHITECTURE.md",
    "STYLE_GUIDE.md",
    "RFC_TEMPLATE.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "LICENSE",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/markdown.yml",
    ".github/workflows/links.yml",
    ".github/workflows/structure.yml",
    ".github/workflows/tests.yml",
    "benchmark/__init__.py",
    "benchmark/adapters/__init__.py",
    "benchmark/adapters/claude_code/__init__.py",
    "benchmark/adapters/claude_code/cases.py",
    "benchmark/adapters/claude_code/enums.py",
    "benchmark/adapters/claude_code/models.py",
    "benchmark/adapters/claude_code/reporting.py",
    "benchmark/adapters/claude_code/runner.py",
    "benchmark/adapters/claude_code/stream.py",
    "benchmark/adapters/claude_code/baselines/README.md",
    "benchmark/adapters/claude_code/baselines/first-live-matrix-2026-07.md",
    "benchmark/conformance/__init__.py",
    "benchmark/conformance/cases.py",
    "benchmark/conformance/enums.py",
    "benchmark/conformance/models.py",
    "benchmark/conformance/runner.py",
    "benchmark/orchestration/__init__.py",
    "benchmark/orchestration/models.py",
    "benchmark/orchestration/runner.py",
    "benchmark/routing/__init__.py",
    "benchmark/routing/cases.py",
    "benchmark/routing/models.py",
    "benchmark/routing/runner.py",
    "core/__init__.py",
    "core/interpretation/__init__.py",
    "core/interpretation/enums.py",
    "core/interpretation/models.py",
    "core/interpretation/validation.py",
    "core/ontology/__init__.py",
    "core/ontology/enums.py",
    "core/ontology/models.py",
    "core/ontology/validation.py",
    "core/routing/__init__.py",
    "core/routing/engine.py",
    "core/routing/registry.py",
    "docs/capability-registry.md",
    "docs/claude-adapter-evaluation.md",
    "docs/claude-code-reference-plugin.md",
    "docs/conformance-benchmark.md",
    "docs/benchmark-orchestration.md",
    "docs/interpretation-ontology.md",
    "docs/live-evaluation-observations.md",
    "docs/routing-regression-benchmark.md",
    "docs/structured-routing-engine.md",
    "implementations/claude-code/arf-academic/.claude-plugin/plugin.json",
    "implementations/claude-code/arf-academic/README.md",
    "implementations/claude-code/arf-academic/references/academic-levels.md",
    "implementations/claude-code/arf-academic/references/arf-reasoning-contract.md",
    "implementations/claude-code/arf-academic/skills/architecture-review/SKILL.md",
    "implementations/claude-code/arf-academic/skills/exam-generation/SKILL.md",
    "implementations/claude-code/arf-academic/skills/pfe-review/SKILL.md",
    "implementations/claude-code/arf-academic/skills/python-teaching/SKILL.md",
    "implementations/claude-code/arf-academic/skills/uml-analysis/SKILL.md",
    "rfcs/RFC-0001-reasoning-model.md",
    "rfcs/RFC-0002-evidence-model.md",
    "rfcs/RFC-0003-feedback-contract.md",
    "rfcs/RFC-0004-confidence-model.md",
    "rfcs/RFC-0005-routing-model.md",
    "rfcs/RFC-0006-request-interpretation-model.md",
    "tests/test_capability_registry.py",
    "tests/test_benchmark_cli.py",
    "tests/test_benchmark_orchestration_models.py",
    "tests/test_benchmark_orchestration_runner.py",
    "tests/test_claude_adapter_evaluation_cases.py",
    "tests/test_claude_adapter_evaluation_cli.py",
    "tests/test_claude_adapter_evaluation_models.py",
    "tests/test_claude_adapter_evaluation_runner.py",
    "tests/test_claude_adapter_reporting.py",
    "tests/test_claude_adapter_response_normalization.py",
    "tests/test_claude_adapter_stream_parser.py",
    "tests/test_claude_code_plugin.py",
    "tests/test_claude_plugin_validator.py",
    "tests/test_conformance_benchmark_cases.py",
    "tests/test_conformance_benchmark_models.py",
    "tests/test_conformance_benchmark_runner.py",
    "tests/test_interpretation_models.py",
    "tests/test_interpretation_validation.py",
    "tests/test_routing_benchmark_cases.py",
    "tests/test_routing_benchmark_models.py",
    "tests/test_routing_benchmark_runner.py",
    "tests/test_routing_engine.py",
    "tests/fixtures/__init__.py",
    "tests/fixtures/routing_cases.py",
    "tests/test_ontology_models.py",
    "tests/test_ontology_validation.py",
    "scripts/run_claude_adapter_evaluation.py",
    "scripts/validate_claude_plugin.py",
}

missing = sorted(path for path in REQUIRED if not (ROOT / path).exists())
empty_dirs = [
    "docs",
    "rfcs",
    "core",
    "ontology",
    "benchmark",
    "examples",
    "implementations",
    "tests",
    "assets",
]

for directory in empty_dirs:
    marker = ROOT / directory / ".gitkeep"
    marker.touch(exist_ok=True)

if missing:
    print("Missing required files:")
    for path in missing:
        print(f"- {path}")
    sys.exit(1)

required_rfc_sections = [
    "## Abstract",
    "## Motivation",
    "## Scope",
    "## Definitions",
    "## Normative requirements",
    "## Processing model",
    "## Examples",
    "## Counter-examples",
    "## Edge cases",
    "## Conformance",
    "## Security and misuse considerations",
    "## Open questions",
    "## References",
]

rfc_0001_required_terms = [
    "input",
    "context",
    "observation",
    "evidence",
    "inference",
    "hypothesis",
    "conclusion",
    "recommendation",
    "uncertainty",
    "falsifier",
    "pedagogical context",
    "reviewability",
    "anti-pattern",
]

normative_terms = ["MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY"]
rfc_errors = []
rfc_0001 = ROOT / "rfcs" / "RFC-0001-reasoning-model.md"
rfc_0002 = ROOT / "rfcs" / "RFC-0002-evidence-model.md"
rfc_0003 = ROOT / "rfcs" / "RFC-0003-feedback-contract.md"
rfc_0004 = ROOT / "rfcs" / "RFC-0004-confidence-model.md"
rfc_0005 = ROOT / "rfcs" / "RFC-0005-routing-model.md"
rfc_0006 = ROOT / "rfcs" / "RFC-0006-request-interpretation-model.md"

rfc_0002_required_terms = [
    "evidence item",
    "evidence reference",
    "claim",
    "source",
    "primary source",
    "secondary source",
    "external source",
    "static evidence",
    "dynamic evidence",
    "measurement",
    "reproduction",
    "corroboration",
    "contradiction",
    "evidence scope",
    "evidence freshness",
    "evidence provenance",
    "evidence limitation",
    "unsupported claim",
    "fabricated evidence",
    "E1 - Direct observation",
    "E2 - Execution or reproduction result",
    "E3 - Measurement",
    "E4 - Derived evidence",
    "Corroboration is not an E-category",
]

rfc_0003_required_terms = [
    "feedback artifact",
    "feedback item",
    "feedback target",
    "finding",
    "positive finding",
    "critical finding",
    "demonstrated error",
    "debatable choice",
    "optional improvement",
    "hypothesis",
    "evidence summary",
    "impact",
    "recommendation",
    "alternative",
    "severity",
    "confidence label",
    "limitation",
    "actionability",
    "feedback priority",
    "Blocking",
    "Major",
    "Moderate",
    "Minor",
    "Informational",
    "does not define the confidence taxonomy",
]

rfc_0004_support_labels = [
    "Confirmed",
    "Strongly supported",
    "Supported",
    "Plausible",
    "Speculative",
]

rfc_0004_required_terms = [
    "confidence",
    "confidence label",
    "confidence basis",
    "confidence target",
    "direct support",
    "corroborated support",
    "derived support",
    "limited support",
    "contradictory support",
    "material uncertainty",
    "confidence downgrade",
    "confidence upgrade",
    "confidence revision",
    "confidence boundary",
    "Unknown",
    "Not assessed",
    "Unknown is not Speculative",
    "Not assessed is not Unknown",
    "non-confidence state",
]

rfc_0005_required_terms = [
    "user objective",
    "primary artifact",
    "requested output",
    "capability",
    "routing candidate",
    "routing signal",
    "positive boundary",
    "negative boundary",
    "capability ownership",
    "routing conflict",
    "ambiguous routing",
    "compound request",
    "delegation",
    "primary capability",
    "supporting capability",
    "routing fallback",
    "routing revision",
    "routing trace",
    "Topic keywords MUST NOT be the sole routing basis",
]

rfc_0006_required_terms = [
    "request interpretation",
    "interpretation input",
    "user utterance",
    "interaction context",
    "attached artifact",
    "observable artifact type",
    "inferred artifact type",
    "interpretation candidate",
    "interpretation basis",
    "interpretation ambiguity",
    "interpretation conflict",
    "interpretation limitation",
    "resolved signal",
    "unresolved signal",
    "absent signal",
    "signal provenance",
    "signal revision",
    "clarification need",
    "conservative interpretation",
    "structured routing request",
]

rfc_0006_required_states = ["Resolved", "Unresolved", "Absent"]

for rfc in sorted((ROOT / "rfcs").glob("*.md")):
    try:
        text = rfc.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        rfc_errors.append(f"{rfc.relative_to(ROOT)} is not readable as UTF-8: {error}")
        continue

    for section in required_rfc_sections:
        if section not in text:
            rfc_errors.append(f"{rfc.relative_to(ROOT)} missing section: {section}")

    if not any(term in text for term in normative_terms):
        rfc_errors.append(f"{rfc.relative_to(ROOT)} missing normative language")

if rfc_0001.exists():
    text = rfc_0001.read_text(encoding="utf-8")
    lower_text = text.lower()
    if "## Anti-patterns" not in text:
        rfc_errors.append(f"{rfc_0001.relative_to(ROOT)} missing section: ## Anti-patterns")
    for term in rfc_0001_required_terms:
        if term not in lower_text:
            rfc_errors.append(f"{rfc_0001.relative_to(ROOT)} missing term: {term}")

if rfc_0002.exists():
    text = rfc_0002.read_text(encoding="utf-8")
    lower_text = text.lower()
    for term in rfc_0002_required_terms:
        if term.lower() not in lower_text:
            rfc_errors.append(f"{rfc_0002.relative_to(ROOT)} missing term: {term}")

if rfc_0003.exists():
    text = rfc_0003.read_text(encoding="utf-8")
    lower_text = text.lower()
    for term in rfc_0003_required_terms:
        if term.lower() not in lower_text:
            rfc_errors.append(f"{rfc_0003.relative_to(ROOT)} missing term: {term}")

if rfc_0004.exists():
    text = rfc_0004.read_text(encoding="utf-8")
    lower_text = text.lower()
    for term in rfc_0004_required_terms:
        if term.lower() not in lower_text:
            rfc_errors.append(f"{rfc_0004.relative_to(ROOT)} missing term: {term}")
    for label in rfc_0004_support_labels:
        marker = f"- **{label}:**"
        if text.count(marker) != 1:
            rfc_errors.append(
                f"{rfc_0004.relative_to(ROOT)} must define support label once: {label}"
            )

if rfc_0005.exists():
    text = rfc_0005.read_text(encoding="utf-8")
    lower_text = text.lower()
    for term in rfc_0005_required_terms:
        if term.lower() not in lower_text:
            rfc_errors.append(f"{rfc_0005.relative_to(ROOT)} missing term: {term}")

if rfc_0006.exists():
    text = rfc_0006.read_text(encoding="utf-8")
    lower_text = text.lower()
    for term in rfc_0006_required_terms:
        if term.lower() not in lower_text:
            rfc_errors.append(f"{rfc_0006.relative_to(ROOT)} missing term: {term}")
    for state in rfc_0006_required_states:
        if state not in text:
            rfc_errors.append(f"{rfc_0006.relative_to(ROOT)} missing state: {state}")

if rfc_errors:
    print("RFC validation failed:")
    for error in rfc_errors:
        print(f"- {error}")
    sys.exit(1)

print("Repository structure is valid.")
