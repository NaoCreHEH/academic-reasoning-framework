from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.adapters.claude_code.analytics import (  # noqa: E402
    CaseSetMismatchError,
    LiveRunLoadError,
    analyze_live_runs,
    load_live_run_report,
    render_json_report,
    render_text_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze multiple Claude adapter live JSON reports."
    )
    parser.add_argument("paths", nargs="+", help="JSON report files or directories.")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the rendered report to an existing local path.",
    )
    parser.add_argument(
        "--allow-case-set-differences",
        action="store_true",
        help="Aggregate the union of case identifiers instead of requiring equality.",
    )
    parser.add_argument(
        "--include-unusable",
        action="store_true",
        help="Include unusable-run infrastructure records in per-case summaries.",
    )
    args = parser.parse_args(argv)

    if args.output is not None and not args.output.parent.exists():
        print(
            f"error: output parent directory does not exist: {args.output.parent}",
            file=sys.stderr,
        )
        return 2

    try:
        input_paths = _resolve_input_paths(args.paths)
        if args.format == "text":
            print(f"Loading {len(input_paths)} live run reports...")
        runs = tuple(load_live_run_report(path) for path in input_paths)
        summary = analyze_live_runs(
            runs,
            include_unusable=args.include_unusable,
            allow_case_set_differences=args.allow_case_set_differences,
        )
    except (LiveRunLoadError, CaseSetMismatchError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    rendered = (
        render_json_report(summary)
        if args.format == "json"
        else render_text_report(summary)
    )
    print(rendered)
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")

    if summary.source_count_inconsistency_runs:
        return 1
    return 0


def _resolve_input_paths(values: list[str]) -> tuple[Path, ...]:
    resolved: list[Path] = []
    for value in values:
        path = Path(value)
        if not path.exists():
            raise ValueError(f"input path does not exist: {path}")
        if path.is_dir():
            resolved.extend(sorted(candidate for candidate in path.glob("*.json")))
        else:
            resolved.append(path)
    unique = tuple(sorted(dict.fromkeys(resolved), key=lambda item: str(item)))
    if not unique:
        raise ValueError("no JSON reports found")
    return unique


if __name__ == "__main__":
    raise SystemExit(main())
