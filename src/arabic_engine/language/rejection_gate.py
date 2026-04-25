"""
rejection_gate.py
=================
بوابة الرفض المُنظَّم — لا رفض صامت

تُحوِّل هذه البوابة كل رفض من بوابة العامل/المعمول
إلى سجل رفض مفصَّل مع حكم مدروس.

الأحكام الممكنة:
    مرفوض_قطعي  — جماد بلا خصائص مشتركة (لا مجاز ممكن)
    محتمل_مجازي — حيوان أو كيان بخصائص مشتركة محتملة
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from arabic_engine.language.agent_operator_gate import AgentOperatorResult
from core.model import ProofState

# أنواع الكيانات التي قد تحتمل تأويلًا مجازيًا
_METAPHOR_ELIGIBLE_TYPES: frozenset[str] = frozenset({"حيوان"})

# أنواع الكيانات التي تُرفَض رفضًا قطعيًا
_ABSOLUTE_REJECT_TYPES: frozenset[str] = frozenset({
    "جماد", "مادة", "سائل", "أثاث", "بنية", "أداة", "مصنوع", "ظاهرة", "مكان", "عضو",
})


@dataclass
class RejectionRecord:
    """سجل رفض مُنظَّم — يُوثِّق كل جانب من جوانب الرفض."""
    sentence: str
    violation_type: str
    violating_token: str
    required_property: str
    actual_property: str
    law_triggered: str
    judgment: str           # مرفوض_قطعي | محتمل_مجازي
    explanation: str


def apply_rejection_gate(
    state: ProofState,
    agent_result: AgentOperatorResult,
) -> Optional[RejectionRecord]:
    """
    بوابة الرفض المُنظَّم.

    إن كان الفاعل صالحًا تُعيد None (لا رفض).
    وإلا تبني سجل رفض مفصَّلًا وتُخزِّنه في state.

    المخرجات:
        Optional[RejectionRecord]
        state.symbolic_state["rejection_gate"] — السجل المُسلسَل أو {"valid": True}
        trace event: "rejection_gate"
    """
    if agent_result.valid:
        state.symbolic_state["rejection_gate"] = {"valid": True, "rejection": None}
        state.add_trace("rejection_gate", {"valid": True})
        return None

    # تحديد الحكم: مجازي محتمل أم رفض قطعي؟
    agent_type = agent_result.agent_type
    # جحث عن خصائص مشتركة للكيان في المفاهيم المُثرَاة
    shared = _get_shared_properties(state, agent_result.agent_token)
    if agent_type in _METAPHOR_ELIGIBLE_TYPES or shared:
        judgment = "محتمل_مجازي"
    else:
        judgment = "مرفوض_قطعي"

    explanation = (
        f"{agent_result.agent_token} ({agent_type}) — "
        f"لا يملك خاصية 'قادر' أو 'مريد' لأداء الفعل '{agent_result.verb_token}'"
    )

    record = RejectionRecord(
        sentence=state.effective_text(),
        violation_type=agent_result.violation or "agent_capability_violation",
        violating_token=agent_result.agent_token,
        required_property="إرادة",
        actual_property=agent_type,
        law_triggered=agent_result.law_triggered or "Adam:قابلية",
        judgment=judgment,
        explanation=explanation,
    )

    serialised = asdict(record)
    state.symbolic_state["rejection_gate"] = {"valid": False, "rejection": serialised}
    state.add_trace("rejection_gate", serialised)
    return record


def _get_shared_properties(state: ProofState, token: str) -> tuple[str, ...]:
    """يسترجع الخصائص المشتركة للكيان من المفاهيم المُثرَاة."""
    bare = token[2:] if token.startswith("ال") and len(token) > 2 else token
    for concept in state.enriched_concepts or []:
        t = concept.get("token", "")
        if t == token or t == bare:
            return tuple(concept.get("shared_properties") or [])
    return ()
