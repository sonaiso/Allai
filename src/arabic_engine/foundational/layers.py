from __future__ import annotations

from core.model import ProofState


def apply_ontological_property_layer(state: ProofState) -> ProofState:
    pre_language = state.conceptual_state.get("pre_language", {})
    percept_units = pre_language.get("percept_units", [])
    proto_concepts = pre_language.get("proto_concepts", [])
    alignment = pre_language.get("reality_alignment", {})

    state.conceptual_state["ontological_property_layer"] = {
        "percept_units": len(percept_units),
        "proto_concepts": len(proto_concepts),
        "alignment_score": alignment.get("score", 0.0),
        "alignment_non_blocking": True,
    }
    state.add_trace(
        "ontological_property_layer",
        {
            "percept_units": len(percept_units),
            "proto_concepts": len(proto_concepts),
            "alignment_non_blocking": True,
        },
    )
    return state
