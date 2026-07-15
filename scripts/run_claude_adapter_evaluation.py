from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmark.adapters.claude_code import (  # noqa: E402
    CLAUDE_ADAPTER_CASES,
    ClaudeAdapterCase,
    ClaudeAdapterEvaluationSummary,
    ClaudeCliInvoker,
    evaluation_summary_to_dict,
    run_claude_adapter_evaluation,
)


PLUGIN_DIR = ROOT / "implementations" / "claude-code" / "arf-academic"


def main(argv: list[str] | None = None) -> int:
    _configure_utf8_diagnostics()
    parser = argparse.ArgumentParser(
        description="Run live Claude Code adapter evaluation cases."
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--show-responses",
        action="store_true",
        help="Print public model responses in text output for local diagnostics.",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_int,
        default=180,
        help="Per-case Claude invocation timeout in seconds.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the rendered report to an existing local path.",
    )
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--case", help="Run one built-in case identifier.")
    selection.add_argument("--tag", help="Run built-in cases containing a tag.")
    args = parser.parse_args(argv)
    if args.show_responses and args.format == "json":
        parser.error("--show-responses is only supported with --format text")
    if args.output is not None and not args.output.parent.exists():
        parser.error(f"output parent directory does not exist: {args.output.parent}")

    try:
        cases = _select_cases(args.case, args.tag)
    except ValueError as error:
        parser.error(str(error))

    response_texts: dict[str, str] = {}

    def remember_response(case, observation) -> None:
        if observation.raw_response_available and observation.response_text is not None:
            response_texts[case.identifier] = observation.response_text

    summary = run_claude_adapter_evaluation(
        cases=cases,
        invoker=ClaudeCliInvoker(timeout_seconds=args.timeout),
        plugin_dir=PLUGIN_DIR,
        on_observation=remember_response if args.show_responses else None,
    )

    rendered = _render_report(
        summary,
        args.format,
        response_texts if args.show_responses else None,
    )
    print(rendered)
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")

    if summary.any_failed:
        return 1
    if summary.all_skipped:
        return 3
    return 0


def _render_report(
    summary: ClaudeAdapterEvaluationSummary,
    output_format: str,
    response_texts: dict[str, str] | None = None,
) -> str:
    if output_format == "json":
        return _to_json(summary)
    return _to_text(summary, response_texts)


def _configure_utf8_diagnostics() -> None:
    # Claude stream data and local diagnostic output are expected to be UTF-8.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def _select_cases(
    case_identifier: str | None,
    tag: str | None,
) -> tuple[ClaudeAdapterCase, ...]:
    if case_identifier is not None:
        matches = tuple(
            case for case in CLAUDE_ADAPTER_CASES if case.identifier == case_identifier
        )
        if not matches:
            raise ValueError(f"unknown case: {case_identifier}")
        return matches
    if tag is not None:
        matches = tuple(case for case in CLAUDE_ADAPTER_CASES if tag in case.tags)
        if not matches:
            raise ValueError(f"unknown tag: {tag}")
        return matches
    return CLAUDE_ADAPTER_CASES


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be a positive integer") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive integer")
    return parsed


def _to_text(
    summary: ClaudeAdapterEvaluationSummary,
    response_texts: dict[str, str] | None = None,
) -> str:
    lines: list[str] = []
    for result in summary.results:
        lines.append(result.case_identifier)
        if result.observed_skill is not None:
            dispatch_detail = f" - {result.observed_skill}"
        elif result.dispatch_status.name == "SKIPPED":
            dispatch_detail = f" - {result.diagnostic}"
        else:
            dispatch_detail = ""
        lines.append(
            f"  dispatch: {result.dispatch_status.name}{dispatch_detail}"
        )
        lines.append(
            f"  response_contract: {result.response_contract_status.name}"
        )
        lines.append(f"  diagnostic: {result.diagnostic}")
        if response_texts is not None and result.case_identifier in response_texts:
            lines.append("  response:")
            lines.extend(
                f"    {line}" for line in response_texts[result.case_identifier].splitlines()
            )
    lines.append(
        "Totals: "
        f"cases={summary.total_cases}; "
        f"dispatch passed/failed/skipped="
        f"{summary.dispatch_passed}/{summary.dispatch_failed}/"
        f"{summary.dispatch_skipped}; "
        f"response passed/failed/skipped="
        f"{summary.response_passed}/{summary.response_failed}/"
        f"{summary.response_skipped}; "
        f"fully successful cases={summary.fully_successful_cases}"
    )
    return "\n".join(lines)


def _to_json(summary: ClaudeAdapterEvaluationSummary) -> str:
    return json.dumps(evaluation_summary_to_dict(summary), indent=2)


if __name__ == "__main__":
    raise SystemExit(main())
