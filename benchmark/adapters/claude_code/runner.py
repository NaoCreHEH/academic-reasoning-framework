"""Runner for live Claude Code adapter evaluation."""

from collections.abc import Iterable
from pathlib import Path
import re
import shutil
import subprocess
from typing import Protocol

from benchmark.adapters.claude_code.enums import (
    ClaudeEvaluationStatus,
    ResponseMarkerMatchMode,
)
from benchmark.adapters.claude_code.models import (
    ClaudeAdapterCase,
    ClaudeAdapterCaseResult,
    ClaudeAdapterEvaluationSummary,
    ClaudeInvocationObservation,
    ClaudeInvocationResult,
    ResponseMarker,
)


class ClaudeInvoker(Protocol):
    """Invocation boundary for deterministic tests and local live execution."""

    def invoke(self, prompt: str, plugin_dir: Path) -> ClaudeInvocationObservation:
        """Invoke Claude Code for one prompt and plugin directory."""


class ClaudeCliInvoker:
    """Local Claude Code CLI invoker with conservative availability checks."""

    def __init__(self, timeout_seconds: int = 60) -> None:
        self.timeout_seconds = timeout_seconds

    def invoke(self, prompt: str, plugin_dir: Path) -> ClaudeInvocationObservation:
        claude = shutil.which("claude")
        if claude is None:
            return ClaudeInvocationObservation(
                available=False,
                unavailable_reason="Claude CLI not found",
            )

        help_result = subprocess.run(
            [claude, "--help"],
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        help_text = f"{help_result.stdout}\n{help_result.stderr}"
        if "--plugin-dir" not in help_text:
            return ClaudeInvocationObservation(
                available=False,
                unavailable_reason=(
                    "Claude CLI does not advertise a supported --plugin-dir option"
                ),
            )
        if "--print" not in help_text and "-p" not in help_text:
            return ClaudeInvocationObservation(
                available=False,
                unavailable_reason=(
                    "Claude CLI does not advertise a supported non-interactive "
                    "print mode"
                ),
            )

        print_flag = "--print" if "--print" in help_text else "-p"
        result = subprocess.run(
            [claude, print_flag, "--plugin-dir", str(plugin_dir), prompt],
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        return ClaudeInvocationObservation(
            available=True,
            response_text=result.stdout,
            observed_skill=None,
            process_result=ClaudeInvocationResult(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            ),
            dispatch_observation_reason="skill identity not observable",
        )


def run_claude_adapter_evaluation(
    cases: Iterable[ClaudeAdapterCase],
    invoker: ClaudeInvoker,
    plugin_dir: Path,
) -> ClaudeAdapterEvaluationSummary:
    """Run live adapter cases while preserving skipped dimensions."""

    return ClaudeAdapterEvaluationSummary(
        results=tuple(_run_case(case, invoker, plugin_dir) for case in cases)
    )


def _run_case(
    case: ClaudeAdapterCase,
    invoker: ClaudeInvoker,
    plugin_dir: Path,
) -> ClaudeAdapterCaseResult:
    try:
        observation = invoker.invoke(case.prompt, plugin_dir)
    except Exception as error:  # pragma: no cover - defensive integration boundary
        return ClaudeAdapterCaseResult(
            case_identifier=case.identifier,
            dispatch_status=ClaudeEvaluationStatus.SKIPPED,
            response_contract_status=ClaudeEvaluationStatus.SKIPPED,
            observed_skill=None,
            diagnostic=f"invocation unavailable: {error}",
        )

    if not observation.available:
        return ClaudeAdapterCaseResult(
            case_identifier=case.identifier,
            dispatch_status=ClaudeEvaluationStatus.SKIPPED,
            response_contract_status=ClaudeEvaluationStatus.SKIPPED,
            observed_skill=None,
            diagnostic=f"evaluation unavailable: {observation.unavailable_reason}",
        )

    if (
        observation.process_result is not None
        and observation.process_result.returncode != 0
    ):
        return ClaudeAdapterCaseResult(
            case_identifier=case.identifier,
            dispatch_status=ClaudeEvaluationStatus.FAILED,
            response_contract_status=ClaudeEvaluationStatus.FAILED,
            observed_skill=observation.observed_skill,
            diagnostic=(
                "Claude invocation failed with return code "
                f"{observation.process_result.returncode}"
            ),
        )

    dispatch_status, dispatch_diagnostic = _evaluate_dispatch(case, observation)
    response_status, failed_markers, forbidden_matches = _evaluate_response(
        case,
        observation.response_text or "",
    )
    diagnostic_parts = [dispatch_diagnostic]
    if failed_markers:
        diagnostic_parts.append(f"failed markers: {', '.join(failed_markers)}")
    if forbidden_matches:
        diagnostic_parts.append(
            f"matched forbidden pattern: {', '.join(forbidden_matches)}"
        )
    if response_status is ClaudeEvaluationStatus.PASSED:
        diagnostic_parts.append("response contract passed")
    return ClaudeAdapterCaseResult(
        case_identifier=case.identifier,
        dispatch_status=dispatch_status,
        response_contract_status=response_status,
        observed_skill=observation.observed_skill,
        failed_markers=failed_markers,
        matched_forbidden_patterns=forbidden_matches,
        diagnostic="; ".join(diagnostic_parts),
    )


def _evaluate_dispatch(
    case: ClaudeAdapterCase,
    observation: ClaudeInvocationObservation,
) -> tuple[ClaudeEvaluationStatus, str]:
    if observation.observed_skill is None:
        reason = observation.dispatch_observation_reason or "skill identity not observable"
        return ClaudeEvaluationStatus.SKIPPED, reason
    if observation.observed_skill in case.forbidden_skills:
        return (
            ClaudeEvaluationStatus.FAILED,
            f"observed forbidden skill: {observation.observed_skill}",
        )
    if observation.observed_skill != case.expected_skill:
        return (
            ClaudeEvaluationStatus.FAILED,
            f"expected {case.expected_skill}; observed {observation.observed_skill}",
        )
    return ClaudeEvaluationStatus.PASSED, f"observed {observation.observed_skill}"


def _evaluate_response(
    case: ClaudeAdapterCase,
    response_text: str,
) -> tuple[ClaudeEvaluationStatus, tuple[str, ...], tuple[str, ...]]:
    if (
        not case.response_markers
        and not case.response_forbidden_patterns
        and not case.response_forbidden_regexes
    ):
        return ClaudeEvaluationStatus.SKIPPED, (), ()
    failed_markers = tuple(
        marker.identifier
        for marker in case.response_markers
        if not _marker_matches(marker, response_text)
    )
    forbidden_matches = _matched_forbidden(case, response_text)
    if failed_markers or forbidden_matches:
        return ClaudeEvaluationStatus.FAILED, failed_markers, forbidden_matches
    return ClaudeEvaluationStatus.PASSED, (), ()


def _marker_matches(marker: ResponseMarker, response_text: str) -> bool:
    normalized_response = _normalize(response_text)
    matched = [
        _normalize(pattern) in normalized_response for pattern in marker.patterns
    ]
    if marker.match_mode is ResponseMarkerMatchMode.ANY:
        return any(matched)
    return all(matched)


def _matched_forbidden(
    case: ClaudeAdapterCase,
    response_text: str,
) -> tuple[str, ...]:
    normalized_response = _normalize(response_text)
    literal_matches = tuple(
        pattern
        for pattern in case.response_forbidden_patterns
        if _normalize(pattern) in normalized_response
    )
    regex_matches = tuple(
        pattern
        for pattern in case.response_forbidden_regexes
        if re.search(pattern, response_text, flags=re.IGNORECASE)
    )
    return literal_matches + regex_matches


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())
