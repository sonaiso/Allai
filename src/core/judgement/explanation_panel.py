"""
explanation_panel.py
====================
لوحة التفسير — يجمع الأسباب والقوانين من كل بوابات النظام

يُجيب على:
    - لماذا قُبلت الجملة؟
    - لماذا رُفضت؟
    - ما الخاصية المُنتهَكة؟
    - ما القانون المُطبَّق؟
    - ما الدليل؟
    - ما المانع؟

المدخلات:
    state.trace_chain
    state.conceptual_state

المخرجات:
    ExplanationPanel
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from core.model import ProofState


# =========================================================
# 1. نموذج لوحة التفسير — Explanation Panel Model
# =========================================================

@dataclass
class ExplanationPanel:
    """لوحة التفسير الكاملة لحكم النظام."""
    why_accepted: Optional[str] = None
    why_rejected: Optional[str] = None
    property_triggered: Optional[str] = None
    law_applied: Optional[str] = None
    evidence: list[str] = field(default_factory=list)
    blocker: Optional[str] = None
    prediction_used: Optional[dict] = None
    metaphor_applied: bool = False
    metaphor_interpretation: Optional[str] = None
    judgment: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# =========================================================
# 2. بناء لوحة التفسير — Build Logic
# =========================================================

def _extract_trace_payload(state: ProofState, event_name: str) -> Optional[dict]:
    """استخرج حمولة أول حدث بالاسم المُعطى من سلسلة الأثر."""
    for item in state.trace_chain:
        if item.get("event") == event_name:
            return item.get("payload", {})
    return None


def build_explanation_panel(state: ProofState) -> ExplanationPanel:
    """
    ابنِ لوحة التفسير من حالة الإثبات.

    يجمع من:
        - rejection_gate trace
        - agent_operator_gate trace
        - prediction_gate trace
        - metaphor_gate trace
        - world_knowledge_layer trace
    """
    panel = ExplanationPanel()

    # ── معطيات الرفض ────────────────────────────────────────
    rejection_records: list[dict] = state.conceptual_state.get("rejection_records", [])
    rejection_passed: bool = state.conceptual_state.get("rejection_gate_passed", True)

    if rejection_records and not rejection_passed:
        first = rejection_records[0]
        panel.why_rejected = first.get("explanation", "")
        panel.property_triggered = first.get("required_property")
        panel.law_applied = first.get("law_triggered")
        panel.blocker = first.get("violation_type")
        panel.evidence.extend(
            r.get("explanation", "") for r in rejection_records if r.get("explanation")
        )

    # ── معطيات محرك العامل ──────────────────────────────────
    agent_result: dict = state.conceptual_state.get("agent_operator_result", {})
    if agent_result and not agent_result.get("agent_valid", True):
        reason = agent_result.get("agent_reason", "")
        if reason and reason not in panel.evidence:
            panel.evidence.append(reason)

    # ── معطيات المجاز ────────────────────────────────────────
    metaphor_result: dict = state.conceptual_state.get("metaphor_result", {})
    if metaphor_result.get("metaphor_applied"):
        panel.metaphor_applied = True
        interps = metaphor_result.get("interpretations", [])
        if interps:
            panel.metaphor_interpretation = interps[0].get("interpretation")
            panel.evidence.append(
                f"مجاز: {panel.metaphor_interpretation}"
            )

    # ── التنبؤ المُستخدَم ────────────────────────────────────
    prediction_result = state.conceptual_state.get("prediction_result")
    if prediction_result:
        panel.prediction_used = {
            "syntactic": prediction_result.get("syntactic", {}).get("missing_roles", []),
            "semantic":  prediction_result.get("semantic", {}).get("agent_must_be"),
            "world":     prediction_result.get("world", {}).get("reason"),
        }

    # ── الحكم النهائي ────────────────────────────────────────
    metaphor_overall = metaphor_result.get("overall_judgment", "literal")
    judgement_value = state.judgement or "unknown"

    if panel.metaphor_applied and metaphor_overall == "metaphorical":
        panel.judgment = "metaphorical_accepted"
        if not panel.why_accepted:
            panel.why_accepted = (
                f"مقبول مجازًا — {panel.metaphor_interpretation}"
            )
    elif not rejection_passed and rejection_records:
        # رُفض حرفيًا
        panel.judgment = "rejected"
        if not panel.law_applied:
            panel.law_applied = "rejection_gate_violation"
    elif judgement_value == "accepted":
        panel.judgment = "accepted"
        if not panel.why_accepted:
            panel.why_accepted = _build_acceptance_reason(state, agent_result)
        if not panel.law_applied:
            panel.law_applied = _extract_acceptance_law(state)
    else:
        panel.judgment = judgement_value

    # ── تأكد من وجود قانون دائمًا ───────────────────────────
    if not panel.law_applied:
        panel.law_applied = _fallback_law(state)

    return panel


def _build_acceptance_reason(state: ProofState, agent_result: dict) -> str:
    """بنِ رسالة القبول من بيانات المحركات."""
    verb = agent_result.get("verb")
    agent = agent_result.get("agent_token")
    instruments = agent_result.get("instrument_bindings", [])

    parts: list[str] = []
    if verb:
        parts.append(f"الفعل '{verb}' مقبول دلاليًا")
    if agent and agent_result.get("agent_valid"):
        parts.append(f"الفاعل '{agent}' قادر")
    for b in instruments:
        if b.get("valid"):
            parts.append(f"الأداة '{b.get('operand')}' صالحة")

    if not parts:
        parts.append("الجملة مستوفية للشروط الدلالية والعالمية")

    return " — ".join(parts)


def _extract_acceptance_law(state: ProofState) -> str:
    """استخرج قانون القبول من نتائج المحركات."""
    wm = state.world_model or {}
    laws = wm.get("laws", [])
    if laws:
        return laws[0].get("rule", "قانون_لغوي")

    agent_result = state.conceptual_state.get("agent_operator_result", {})
    verb = agent_result.get("verb")
    if verb:
        return f"VerbFrame:{verb}_accepted"

    return "proposition_and_world_model_closed"


def _fallback_law(state: ProofState) -> str:
    """قانون احتياطي حين لا يُكتشف قانون صريح."""
    if state.world_model_closed:
        return "GL-004:world_model_closed"
    if state.proposition_closed:
        return "GL-002:proposition_closed"
    return "no_law_detected"
