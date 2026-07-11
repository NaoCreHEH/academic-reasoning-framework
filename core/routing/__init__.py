"""Capability registry primitives for ARF routing boundaries."""

from core.routing.engine import (
    RoutingDecision,
    RoutingRequest,
    StructuredRoutingEngine,
)
from core.routing.registry import (
    CapabilityDefinition,
    CapabilityRegistry,
    CapabilityRegistryError,
    CapabilityYieldRule,
    UnknownCapabilityError,
    build_default_academic_registry,
    validate_registry_references,
)

__all__ = [
    "CapabilityDefinition",
    "CapabilityRegistry",
    "CapabilityRegistryError",
    "CapabilityYieldRule",
    "RoutingDecision",
    "RoutingRequest",
    "StructuredRoutingEngine",
    "UnknownCapabilityError",
    "build_default_academic_registry",
    "validate_registry_references",
]
