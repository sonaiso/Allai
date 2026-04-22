from __future__ import annotations

from dataclasses import asdict
import unicodedata

from arabic_engine.foundational.models import PerceptUnit, ProtoConcept, RealityAlignment
from core.model import ProofState

_PRE_LANGUAGE_ORDER = [
    "pre_reality_gate",
    "percept_gate",
    "proto_concept_gate",
    "alignment_gate",
    "naming_gate",
    "unicode_ingress",
]


def apply_pre_reality_gate(state: ProofState) -> ProofState:
    text = state.effective_text()
    raw_tokens = [token for token in text.split() if token]
    state.conceptual_state.setdefault("pre_language", {})
    state.conceptual_state["pre_language"]["pre_reality"] = {
        "token_count": len(raw_tokens),
        "char_count": len(text),
        "derived_from": "text_ingress_v1",
    }
    state.add_trace(
        "pre_reality_gate",
        {
            "token_count": len(raw_tokens),
            "char_count": len(text),
            "derived_from": "text_ingress_v1",
        },
    )
    return state


def apply_percept_gate(state: ProofState) -> ProofState:
    text = state.effective_text()
    percept_units: list[PerceptUnit] = []
    token_index = -1
    for char_index, char in enumerate(text):
        if char.isspace():
            continue
        if char_index == 0 or text[char_index - 1].isspace():
            token_index += 1
        unit_type = "haraka" if unicodedata.combining(char) > 0 else "letter_or_symbol"
        percept_units.append(
            PerceptUnit(
                surface=char,
                normalized=unicodedata.normalize("NFKC", char),
                unit_type=unit_type,
                token_index=max(token_index, 0),
                char_index=char_index,
            )
        )

    state.conceptual_state.setdefault("pre_language", {})
    state.conceptual_state["pre_language"]["percept_units"] = [asdict(unit) for unit in percept_units]
    state.add_trace("percept_gate", {"unit_count": len(percept_units), "derived_from": "normalized_text_v1"})
    return state


def apply_proto_concept_gate(state: ProofState) -> ProofState:
    percept_dicts = state.conceptual_state.get("pre_language", {}).get("percept_units", [])
    proto_concepts: list[ProtoConcept] = []
    for unit in percept_dicts:
        unit_type = unit.get("unit_type", "letter_or_symbol")
        if unit_type == "haraka":
            label = "prosodic_marker"
            confidence = 0.6
        else:
            label = "lexical_anchor"
            confidence = 0.7
        proto_concepts.append(
            ProtoConcept(
                label=label,
                source_unit_type=unit_type,
                confidence=confidence,
                anchor_token_index=unit.get("token_index", 0),
            )
        )

    state.conceptual_state.setdefault("pre_language", {})
    state.conceptual_state["pre_language"]["proto_concepts"] = [asdict(item) for item in proto_concepts]
    state.add_trace("proto_concept_gate", {"concept_count": len(proto_concepts)})
    return state


def apply_alignment_gate(state: ProofState) -> ProofState:
    concepts = state.conceptual_state.get("pre_language", {}).get("proto_concepts", [])
    confidence_values = [item.get("confidence", 0.0) for item in concepts]
    score = (sum(confidence_values) / len(confidence_values)) if confidence_values else 0.0
    aligned = bool(concepts)
    alignment = RealityAlignment(
        aligned=aligned,
        score=round(score, 4),
        reason=None if aligned else "no_proto_concepts_available",
    )

    state.conceptual_state.setdefault("pre_language", {})
    state.conceptual_state["pre_language"]["reality_alignment"] = asdict(alignment)
    state.add_trace(
        "alignment_gate",
        {
            "aligned": alignment.aligned,
            "score": alignment.score,
            "policy": alignment.policy,
            "blocking": False,
        },
    )
    return state


def apply_naming_gate(state: ProofState) -> ProofState:
    proto_concepts = state.conceptual_state.get("pre_language", {}).get("proto_concepts", [])
    names = [f"{item.get('label')}:{index}" for index, item in enumerate(proto_concepts, start=1)]

    state.conceptual_state.setdefault("pre_language", {})
    state.conceptual_state["pre_language"]["concept_names"] = names
    state.add_trace("naming_gate", {"name_count": len(names)})
    return state


def validate_pre_language_trace(state: ProofState) -> tuple[bool, str]:
    event_positions: dict[str, int] = {}
    for index, item in enumerate(state.trace_chain):
        event = item.get("event")
        if event not in event_positions:
            event_positions[event] = index

    present = [event for event in _PRE_LANGUAGE_ORDER if event in event_positions]
    if not present:
        return True, "not_present_in_trace"

    positions = [event_positions[event] for event in present]
    if positions != sorted(positions):
        return False, "pre_language_events_out_of_order"

    if state.processing_mode == "concept_first":
        missing = [event for event in _PRE_LANGUAGE_ORDER if event not in event_positions]
        if missing:
            return False, f"concept_first_missing_pre_language_events:{','.join(missing)}"

    return True, "validated"
