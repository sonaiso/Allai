"""Foundational pre-language entities and gates."""

from arabic_engine.foundational.gates import (
    apply_alignment_gate,
    apply_naming_gate,
    apply_percept_gate,
    apply_pre_reality_gate,
    apply_proto_concept_gate,
    validate_pre_language_trace,
)
from arabic_engine.foundational.layers import apply_ontological_property_layer
from arabic_engine.foundational.models import PerceptUnit, ProtoConcept, RealityAlignment

__all__ = [
    "PerceptUnit",
    "ProtoConcept",
    "RealityAlignment",
    "apply_pre_reality_gate",
    "apply_percept_gate",
    "apply_proto_concept_gate",
    "apply_alignment_gate",
    "apply_naming_gate",
    "validate_pre_language_trace",
    "apply_ontological_property_layer",
]
