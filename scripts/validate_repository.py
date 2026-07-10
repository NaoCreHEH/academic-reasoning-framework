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

print("Repository structure is valid.")
