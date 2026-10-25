"""
explanation_panel.py
====================
لوحة التفسير — تجميع كل آثار البوابات في تفسير موحَّد

تجمع هذه الوحدة نتائج جميع البوابات الرمزية في كيان واحد
يشرح سبب قبول أو رفض الجملة باللغة العربية.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.model import ProofState


@dataclass
class ExplanationPanel:
    """لوحة التفسير الموحَّدة — ملخَّص قابل للقراءة البشرية."""
    why_accepted: Optional[str] = None
    why_rejected: Optional[str] = None
    law_applied: Optional[str] = None
    property_triggered: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    blocker: Optional[str] = None


def build_explanation_panel(state: ProofState) -> ExplanationPanel:
    """
    يبني لوحة التفسير من نتائج البوابات الرمزية المُخزَّنة
    في state.symbolic_state.

    يُخزِّن اللوحة في state.explanation_panel.
    """
    agent_gate: Dict[str, Any] = state.symbolic_state.get("agent_operator_gate", {})
    rejection_gate: Dict[str, Any] = state.symbolic_state.get("rejection_gate", {})
    metaphor_gate: Dict[str, Any] = state.symbolic_state.get("metaphor_gate", {})
    prediction_gate: Dict[str, Any] = state.symbolic_state.get("prediction_gate", {})

    panel = ExplanationPanel()
    evidence: list[str] = []

    # ── البوابة الدلالية ────────────────────────────────────────────────
    rejection_rec = rejection_gate.get("rejection")
    agent_valid = agent_gate.get("valid", True)

    if not agent_valid:
        agent_token = agent_gate.get("agent_token", "")
        agent_type = agent_gate.get("agent_type", "")
        verb_token = agent_gate.get("verb_token", "")
        law = agent_gate.get("law_triggered", "Adam:قابلية")
        panel.blocker = (
            f"{agent_token} ({agent_type}) — لا يملك خاصية 'إرادة' لأداء الفعل '{verb_token}'"
        )
        panel.law_applied = law
        panel.property_triggered = "إرادة"
        evidence.append(f"بوابة_العامل: {panel.blocker}")

    # ── بوابة المجاز ────────────────────────────────────────────────────
    metaphor_resolved = metaphor_gate.get("resolved", False)
    metaphor_judgment = metaphor_gate.get("judgment", "")
    shared_prop = metaphor_gate.get("shared_property")

    if metaphor_resolved and metaphor_judgment == "metaphorical_accepted":
        interpretation = metaphor_gate.get("target_interpretation", "")
        panel.why_accepted = f"قُبِل مجازيًا: {interpretation}"
        if shared_prop:
            panel.property_triggered = shared_prop
            evidence.append(f"خاصية_مشتركة: {shared_prop} → {interpretation}")
    elif rejection_rec:
        judgment = rejection_rec.get("judgment", "")
        violating = rejection_rec.get("violating_token", "")
        explanation = rejection_rec.get("explanation", "")
        panel.why_rejected = explanation or f"{violating} — {judgment}"
        evidence.append(f"بوابة_الرفض: {judgment} — {explanation}")

    # ── بوابة التنبؤ ────────────────────────────────────────────────────
    pred_results = prediction_gate.get("results", [])
    for pred in pred_results:
        layer = pred.get("layer", "")
        passed = pred.get("passed", True)
        reason = pred.get("reason", "")
        if not passed:
            evidence.append(f"تنبؤ_{layer}: {reason}")
            if not panel.blocker:
                panel.blocker = reason

    # ── الحكم النهائي ───────────────────────────────────────────────────
    final_judgment = state.judgement
    if final_judgment == "metaphorical_accepted":
        if not panel.why_accepted:
            panel.why_accepted = "قُبِل مجازيًا"
    elif final_judgment == "accepted":
        if not panel.why_accepted:
            panel.why_accepted = "الجملة مقبولة — جميع البوابات اجتازت التحقق"
        evidence.append("حكم: مقبول")
    elif final_judgment == "rejected":
        if not panel.why_rejected:
            panel.why_rejected = "الجملة مرفوضة — انتهاك قواعد أنطولوجية أو دلالية"
        evidence.append("حكم: مرفوض")

    panel.evidence = evidence

    serialised = asdict(panel)
    state.explanation_panel = serialised
    return panel
