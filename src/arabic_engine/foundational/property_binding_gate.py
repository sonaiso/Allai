"""
property_binding_gate.py
========================
بوابة ربط الخواص

تُحوّل:
    ProtoConcept (أثر مُسمَّى)
    ────────────────────────────────────────────────
    PropertyBundle (حزمة الخواص الأولى المُصنَّفة)

القاعدة:
    haraka → خواص الإدراك (pronunciation + auditory)
    lexical_anchor → خواص الوجود + الهوية + الحدود + الإدراك

المرجع:
    specs/adam_properties.yaml — الطبقات السبع
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List

from core.model import ProofState


# =========================================================
# 1. نموذج حزمة الخواص — PropertyBundle Model
# =========================================================

@dataclass
class PropertyBundle:
    """حزمة الخواص الأولى المرتبطة بمفهوم بدئي."""
    proto_label: str
    anchor_token_index: int
    # الطبقات السبع
    existence_props: List[str] = field(default_factory=list)
    identity_props: List[str] = field(default_factory=list)
    boundary_props: List[str] = field(default_factory=list)
    perception_props: List[str] = field(default_factory=list)
    relation_props: List[str] = field(default_factory=list)
    action_props: List[str] = field(default_factory=list)
    judgment_props: List[str] = field(default_factory=list)

    def all_properties(self) -> List[str]:
        """أعد قائمة بجميع الخواص مهما كانت طبقتها."""
        return (
            self.existence_props
            + self.identity_props
            + self.boundary_props
            + self.perception_props
            + self.relation_props
            + self.action_props
            + self.judgment_props
        )

    def has_any_property(self) -> bool:
        """تحقق: هل تحمل هذه الحزمة خاصية واحدة على الأقل؟"""
        return bool(self.all_properties())


# =========================================================
# 2. قواعد التعيين — Assignment Rules
# =========================================================

_HARAKA_BUNDLE: dict[str, list[str]] = {
    "existence_props": [],
    "identity_props": [],
    "boundary_props": [],
    "perception_props": ["pronounced", "audible"],
    "relation_props": [],
    "action_props": [],
    "judgment_props": ["possible"],
}

_LEXICAL_ANCHOR_BUNDLE: dict[str, list[str]] = {
    "existence_props": ["exists"],
    "identity_props": ["same", "stable"],
    "boundary_props": ["limited", "separable", "distinct"],
    "perception_props": ["distinguishable", "pronounceable", "bounded_percept"],
    "relation_props": [],
    "action_props": [],
    "judgment_props": ["known"],
}

_PROSODIC_MARKER_BUNDLE: dict[str, list[str]] = {
    "existence_props": [],
    "identity_props": [],
    "boundary_props": [],
    "perception_props": ["pronounced", "audible"],
    "relation_props": [],
    "action_props": [],
    "judgment_props": ["possible"],
}

_DEFAULT_BUNDLE: dict[str, list[str]] = {
    "existence_props": ["exists"],
    "identity_props": ["same"],
    "boundary_props": ["limited"],
    "perception_props": ["distinguishable"],
    "relation_props": [],
    "action_props": [],
    "judgment_props": ["possible"],
}


def _select_bundle(proto_label: str, source_unit_type: str) -> dict[str, list[str]]:
    """اختر قاموس الخواص المناسب بناءً على نوع الوحدة أو النموذج البدئي."""
    if source_unit_type == "haraka" or proto_label == "prosodic_marker":
        return _HARAKA_BUNDLE
    if proto_label == "lexical_anchor":
        return _LEXICAL_ANCHOR_BUNDLE
    if proto_label == "prosodic_marker":
        return _PROSODIC_MARKER_BUNDLE
    return _DEFAULT_BUNDLE


# =========================================================
# 3. بوابة الربط — Gate Function
# =========================================================

def apply_property_binding_gate(state: ProofState) -> ProofState:
    """
    بوابة ربط الخواص الأولى.

    المدخلات:
        state.conceptual_state["pre_language"]["proto_concepts"]

    المخرجات:
        state.conceptual_state["property_bundles"]   — قائمة PropertyBundle
        trace event: "property_binding_gate"
    """
    proto_concepts: list[dict] = (
        state.conceptual_state.get("pre_language", {}).get("proto_concepts", [])
    )

    bundles: list[dict] = []

    for proto in proto_concepts:
        label = proto.get("label", "lexical_anchor")
        unit_type = proto.get("source_unit_type", "letter_or_symbol")
        anchor = proto.get("anchor_token_index", 0)

        rule = _select_bundle(label, unit_type)

        bundle = PropertyBundle(
            proto_label=label,
            anchor_token_index=anchor,
            existence_props=list(rule["existence_props"]),
            identity_props=list(rule["identity_props"]),
            boundary_props=list(rule["boundary_props"]),
            perception_props=list(rule["perception_props"]),
            relation_props=list(rule["relation_props"]),
            action_props=list(rule["action_props"]),
            judgment_props=list(rule["judgment_props"]),
        )
        bundles.append(asdict(bundle))

    state.conceptual_state.setdefault("pre_language", {})
    state.conceptual_state["property_bundles"] = bundles

    has_property_count = sum(
        1 for b in bundles
        if any(b.get(k) for k in (
            "existence_props", "identity_props", "boundary_props",
            "perception_props", "relation_props", "action_props", "judgment_props",
        ))
    )

    state.add_trace(
        "property_binding_gate",
        {
            "bundle_count": len(bundles),
            "bundles_with_properties": has_property_count,
            "derived_from": "proto_concepts_v1",
        },
    )
    return state
