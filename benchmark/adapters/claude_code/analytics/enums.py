"""Enums for offline Claude adapter multi-run analytics."""

from enum import Enum


class RunUsabilityStatus(Enum):
    """Run-level usability for behavioral conclusions."""

    USABLE = "usable"
    DEGRADED = "degraded"
    UNUSABLE = "unusable"


class CaseOutcomeCategory(Enum):
    """Observable categories attached to one case result."""

    DISPATCH_PASSED = "dispatch_passed"
    DISPATCH_SKIPPED = "dispatch_skipped"
    DISPATCH_WRONG = "dispatch_wrong"
    RESPONSE_PASSED = "response_passed"
    RESPONSE_FAILED = "response_failed"
    RESPONSE_SKIPPED = "response_skipped"
    INVOCATION_TIMEOUT = "invocation_timeout"
    INVOCATION_PROCESS_FAILURE = "invocation_process_failure"
    INVOCATION_ENCODING_FAILURE = "invocation_encoding_failure"
    INVOCATION_STREAM_PARSE_FAILURE = "invocation_stream_parse_failure"
    PLUGIN_LOAD_FAILURE = "plugin_load_failure"
    EVALUATION_UNAVAILABLE = "evaluation_unavailable"
    OTHER_INVOCATION_FAILURE = "other_invocation_failure"


class BehavioralEligibility(Enum):
    """Whether a case result may inform behavioral stability."""

    ELIGIBLE = "eligible"
    INELIGIBLE_INFRASTRUCTURE = "ineligible_infrastructure"
    INELIGIBLE_UNAVAILABLE = "ineligible_unavailable"
