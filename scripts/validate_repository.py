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
    "rfcs/RFC-0001-reasoning-model.md",
    "rfcs/RFC-0002-evidence-model.md",
    "rfcs/RFC-0003-feedback-contract.md",
    "rfcs/RFC-0004-confidence-model.md",
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

if rfc_errors:
    print("RFC validation failed:")
    for error in rfc_errors:
        print(f"- {error}")
    sys.exit(1)

print("Repository structure is valid.")
