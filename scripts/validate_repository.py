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
    "E4 - Corroborated evidence",
    "E5 - Derived evidence",
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

if rfc_errors:
    print("RFC validation failed:")
    for error in rfc_errors:
        print(f"- {error}")
    sys.exit(1)

print("Repository structure is valid.")
