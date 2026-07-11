"""Validation helpers for RFC-0006 interpretation primitives.

Validation uses a hybrid pattern:
- dataclass ``__post_init__`` methods enforce local structural invariants;
- explicit functions enforce conversion or collection invariants that require
  caller context.

The validators do not perform free-form interpretation, artifact detection,
routing, capability lookup, or model calls.
"""

from collections.abc import Iterable
from typing import Any, TypeVar


class InterpretationValidationError(ValueError):
    """Raised when an interpretation object violates a structural invariant."""


class InterpretationConversionError(InterpretationValidationError):
    """Raised when interpretation cannot be converted to a routing request."""

    def __init__(self, signal_kind: object, message: str) -> None:
        self.signal_kind = signal_kind
        super().__init__(message)


T = TypeVar("T")


def require_non_empty(value: str | None, field_name: str) -> None:
    """Reject missing or blank strings."""

    if value is None or not value.strip():
        raise InterpretationValidationError(f"{field_name} cannot be blank")


def validate_unique_items(items: Iterable[T], field_name: str) -> tuple[T, ...]:
    """Return items as a tuple and reject duplicates."""

    values = tuple(items)
    seen: set[T] = set()
    for item in values:
        if item in seen:
            raise InterpretationValidationError(
                f"{field_name} contains duplicate value: {item}"
            )
        seen.add(item)
    return values


def validate_string_tuple(values: tuple[str, ...], field_name: str) -> None:
    """Validate non-empty, unique string tuple entries."""

    validate_unique_items(values, field_name)
    for value in values:
        require_non_empty(value, field_name)


def validate_unique_identifiers(items: Iterable[Any], field_name: str) -> None:
    """Validate uniqueness of objects with an ``identifier`` attribute."""

    seen: set[str] = set()
    for item in items:
        identifier = item.identifier
        if identifier in seen:
            raise InterpretationValidationError(
                f"{field_name} contains duplicate identifier: {identifier}"
            )
        seen.add(identifier)
