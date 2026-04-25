"""
prediction_gate.py
==================
محرك التنبؤ الرمزي — أربع طبقات

الطبقات:
    1. صرفية   — توقع الوزن والحركة الإعرابية
    2. نحوية   — توقع الأدوار المفقودة والاختيارية
    3. دلالية  — توقع أنواع الكيانات المقبولة لكل دور
    4. عالمية  — توقع ما هو ممكن وما هو ممتنع من القوانين

المدخلات:
    state.symbolic_state["minimal_complete_encoding"]
    state.conceptual_state["enriched_concepts"]
    state.conceptual_state["agent_operator_result"]
    state.world_model

المخرجات:
    state.conceptual_state["prediction_result"]
    trace event: "prediction_gate"
"""
from __future__ import annotations

from typing import Any

from arabic_engine.language.verb_frame_lexicon import (
    AGENT_PROPERTY_ENTITY_TYPES,
    get_verb_frame,
)
from core.model import ProofState


# =========================================================
# 1. طبقة التنبؤ الصرفي — Morphological Prediction
# =========================================================

_PATTERN_CASE_MAP: dict[str, str] = {
    "فَاعِل":   "رفع",
    "مَفْعُول": "نصب",
    "مِفْعَال": "جر",
    "فَعَلَ":   "رفع",
    "فَعَّلَ":  "رفع",
}

_SENTENCE_PATTERN_CASE: dict[str, dict[str, str]] = {
    "verbal": {
        "verb":    "رفع (فاعل)",
        "subject": "رفع",
        "object":  "نصب",
    },
    "nominal": {
        "subject": "رفع",
        "predicate": "رفع",
    },
}


def _predict_morphological(
    minimal_encoding: dict,
    enriched: list[dict],
) -> dict[str, Any]:
    """تنبؤ صرفي: الوزن والحركة الإعرابية المتوقعة."""
    sentence_pattern = minimal_encoding.get("sentence_pattern", "nominal")
    token_units = minimal_encoding.get("token_units", [])

    predictions: list[dict] = []
    for unit in token_units:
        token = unit.get("token", "")
        # ابحث عن المفهوم المُثرَى المقابل
        concept = next((c for c in enriched if c.get("token") == token), {})
        pattern = concept.get("pattern")
        predicted_case = _PATTERN_CASE_MAP.get(pattern, "غير_محدد")
        predictions.append({
            "token": token,
            "expected_pattern": pattern or "غير_معروف",
            "expected_case": predicted_case,
        })

    return {
        "sentence_pattern": sentence_pattern,
        "token_predictions": predictions,
        "case_map": _SENTENCE_PATTERN_CASE.get(sentence_pattern, {}),
    }


# =========================================================
# 2. طبقة التنبؤ النحوي — Syntactic Prediction
# =========================================================

def _predict_syntactic(
    verb_token: str | None,
    enriched: list[dict],
    agent_result: dict,
) -> dict[str, Any]:
    """تنبؤ نحوي: الأدوار المفقودة والمتوقعة."""
    if not verb_token:
        return {"missing_roles": [], "optional_roles": [], "present_roles": []}

    frame = get_verb_frame(verb_token)
    if not frame:
        return {"missing_roles": [], "optional_roles": [], "present_roles": []}

    present_roles: list[str] = []

    # الفاعل
    if agent_result.get("agent_token"):
        present_roles.append("فاعل")

    # الأدوات
    has_instrument = any(
        c.get("relation_type") == "Instrumentality"
        or "instrument" in c.get("roles", [])
        for c in enriched
    )
    if has_instrument:
        present_roles.append("أداة")

    # تحديد ما ينقص
    required_not_present = [
        r for r in frame.requires
        if r not in present_roles
        and r not in (
            "فاعل_قادر", "فاعل_إنسان", "فاعل_حي", "فاعل_مُبصِر",
            "فاعل_ناطق", "فاعل_مدرِك", "فاعل_عاقل", "فاعل_جماد"
        )
    ]
    missing = required_not_present if present_roles else list(frame.requires)

    return {
        "verb": verb_token,
        "requires": list(frame.requires),
        "missing_roles": missing,
        "optional_roles": list(frame.optional),
        "present_roles": present_roles,
        "rejects": list(frame.rejects),
    }


# =========================================================
# 3. طبقة التنبؤ الدلالي — Semantic Prediction
# =========================================================

def _predict_semantic(
    verb_token: str | None,
    enriched: list[dict],
) -> dict[str, Any]:
    """تنبؤ دلالي: أنواع الكيانات المقبولة لكل دور."""
    if not verb_token:
        return {}

    frame = get_verb_frame(verb_token)
    if not frame:
        return {}

    agent_prop = frame.agent_property
    allowed_agent_types = list(AGENT_PROPERTY_ENTITY_TYPES.get(agent_prop, ()))

    instrument_requirements: list[str] = []
    if "أداة" in frame.optional or "أداة" in frame.requires:
        instrument_requirements.append(f"قابلية_{verb_token}")

    return {
        "verb": verb_token,
        "agent_must_be": agent_prop,
        "allowed_agent_entity_types": allowed_agent_types,
        "instrument_must_have": instrument_requirements,
        "event_type": frame.event_type,
        "produces": list(frame.produces),
    }


# =========================================================
# 4. طبقة التنبؤ العالمي — World Prediction
# =========================================================

def _predict_world(
    world_model: dict,
    agent_result: dict,
) -> dict[str, Any]:
    """تنبؤ عالمي: الممكن والممتنع من القوانين العالمية."""
    laws = world_model.get("laws", [])
    causality = world_model.get("causality", [])

    possible: list[str] = []
    impossible: list[str] = []

    for law in laws:
        rule = law.get("rule", "")
        if law.get("law_type") == "affordance":
            possible.append(rule)

    violations = agent_result.get("violations", [])
    impossible.extend(violations)

    inferred_effects: list[str] = []
    for causal in causality:
        effect = causal.get("effect", "")
        if effect:
            inferred_effects.append(effect)

    return {
        "possible": possible,
        "impossible": impossible,
        "inferred_effects": inferred_effects,
        "world_laws_count": len(laws),
        "causality_count": len(causality),
        "reason": (
            "القوانين العالمية تُرجِّح الإمكان" if not impossible
            else f"تعارض: {'; '.join(impossible[:2])}"
        ),
    }


# =========================================================
# 5. البوابة الرئيسية — Main Gate
# =========================================================

def apply_prediction_gate(state: ProofState) -> ProofState:
    """
    محرك التنبؤ الرمزي (أربع طبقات).

    المدخلات:
        state.symbolic_state["minimal_complete_encoding"]
        state.conceptual_state["enriched_concepts"]
        state.conceptual_state["agent_operator_result"]
        state.world_model

    المخرجات:
        state.conceptual_state["prediction_result"]
        trace event: "prediction_gate"
    """
    enriched: list[dict] = state.conceptual_state.get("enriched_concepts", [])
    minimal_encoding: dict = state.symbolic_state.get("minimal_complete_encoding", {})
    agent_result: dict = state.conceptual_state.get("agent_operator_result", {})
    world_model: dict = state.world_model or {}

    verb_token: str | None = agent_result.get("verb")

    morphological = _predict_morphological(minimal_encoding, enriched)
    syntactic = _predict_syntactic(verb_token, enriched, agent_result)
    semantic = _predict_semantic(verb_token, enriched)
    world = _predict_world(world_model, agent_result)

    prediction_result: dict[str, Any] = {
        "morphological": morphological,
        "syntactic": syntactic,
        "semantic": semantic,
        "world": world,
    }

    state.conceptual_state["prediction_result"] = prediction_result

    state.add_trace(
        "prediction_gate",
        {
            "verb": verb_token,
            "missing_roles": syntactic.get("missing_roles", []),
            "possible_count": len(world.get("possible", [])),
            "impossible_count": len(world.get("impossible", [])),
        },
    )
    return state
