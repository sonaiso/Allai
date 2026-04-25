"""
rejection_gate.py
==================
محرك الرفض المُعلَّل

يُصدر `RejectionRecord` عند كشف انتهاك دلالي أو عالمي أو منطقي،
ويُبرر الرفض بالخاصية المنتهَكة والقانون المُطبَّق.

الحالات المعالجة:
    - فاعل جماد لفعل يشترط الإرادة (كتب الحجر)
    - أداة غير صالحة للفعل (كتب بالقلم — ولكن أداة أخرى)
    - تعارض فيزيائي (الماء يحترق)

المدخلات:
    state.conceptual_state["agent_operator_result"]
    state.conceptual_state["enriched_concepts"]

المخرجات:
    state.conceptual_state["rejection_records"]
    state.conceptual_state["rejection_gate_passed"]
    trace event: "rejection_gate"
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from core.model import ProofState


# =========================================================
# 1. نموذج الرفض — Rejection Model
# =========================================================

@dataclass(frozen=True)
class RejectionRecord:
    """سجل رفض معلَّل — يحمل كل بيانات الانتهاك."""
    sentence: str
    violation_type: str         # semantic | world | logical
    violating_token: str
    required_property: str
    actual_property: str
    law_triggered: str
    judgment: str               # "مرفوض_معرفيًا" | "محتمل_مجازي"
    explanation: str


# =========================================================
# 2. منطق الكشف — Detection Logic
# =========================================================

def _check_agent_violations(
    agent_result: dict,
    sentence: str,
) -> list[RejectionRecord]:
    """كشف انتهاكات الفاعل من نتيجة محرك العامل."""
    records: list[RejectionRecord] = []

    if agent_result.get("agent_valid", True):
        return records

    agent_token = agent_result.get("agent_token", "غير_محدد")
    reason = agent_result.get("agent_reason", "")

    # حدد نوع الانتهاك
    if "جماد" in reason:
        violation_type = "semantic"
        required_property = "قابلية"
        actual_property = "جماد_بلا_إرادة"
        law = "Adam:قابلية_الفعل_تستلزم_فاعلًا_قادرًا"
        judgment = "محتمل_مجازي"
    elif "إنسان" in reason:
        violation_type = "semantic"
        required_property = "إنسان"
        actual_property = "غير_إنسان"
        law = "Adam:بعض_الأفعال_حكر_على_الإنسان"
        judgment = "مرفوض_معرفيًا"
    elif "حي" in reason:
        violation_type = "semantic"
        required_property = "حي"
        actual_property = "جماد"
        law = "Adam:الفعل_يستلزم_فاعلًا_حيًّا"
        judgment = "مرفوض_معرفيًا"
    else:
        violation_type = "semantic"
        required_property = "قادر"
        actual_property = "غير_مستوفٍ"
        law = "Adam:قابلية"
        judgment = "مرفوض_معرفيًا"

    records.append(
        RejectionRecord(
            sentence=sentence,
            violation_type=violation_type,
            violating_token=agent_token,
            required_property=required_property,
            actual_property=actual_property,
            law_triggered=law,
            judgment=judgment,
            explanation=reason,
        )
    )
    return records


def _check_instrument_violations(
    agent_result: dict,
    sentence: str,
) -> list[RejectionRecord]:
    """كشف انتهاكات الأداة من ربط محرك العامل."""
    records: list[RejectionRecord] = []
    for binding in agent_result.get("instrument_bindings", []):
        if not binding.get("valid", True):
            records.append(
                RejectionRecord(
                    sentence=sentence,
                    violation_type="semantic",
                    violating_token=binding.get("operand", ""),
                    required_property="أداة_صالحة",
                    actual_property="أداة_غير_صالحة",
                    law_triggered=binding.get("law_triggered") or "affordance_violation",
                    judgment="مرفوض_معرفيًا",
                    explanation=binding.get("reason", ""),
                )
            )
    return records


def _check_world_violations(
    enriched: list[dict],
    world_model: dict,
    sentence: str,
) -> list[RejectionRecord]:
    """كشف التعارضات الفيزيائية (مثل: الماء يحترق)."""
    records: list[RejectionRecord] = []

    # قائمة تعارضات فيزيائية معروفة
    PHYSICAL_IMPOSSIBLES: list[tuple[str, str, str]] = [
        ("ماء",  "إحراق", "الماء يطفئ النار ولا يحترق — قانون فيزيائي"),
        ("ثلج",  "إحراق", "الثلج لا يحترق"),
        ("حجر",  "كتابة", "الحجر لا يكتب — بلا إرادة"),
    ]

    entity_tokens = {c.get("token", "").lstrip("ال") for c in enriched if c.get("entity_type")}
    event_actions = {e.get("action", "") for e in world_model.get("events", [])}

    for entity, bad_action, explanation in PHYSICAL_IMPOSSIBLES:
        if entity in entity_tokens and bad_action in event_actions:
            records.append(
                RejectionRecord(
                    sentence=sentence,
                    violation_type="world",
                    violating_token=entity,
                    required_property="قانون_فيزيائي",
                    actual_property=f"{entity}_يقوم_بـ_{bad_action}",
                    law_triggered=f"physical_law_{entity}_{bad_action}",
                    judgment="مرفوض_معرفيًا",
                    explanation=explanation,
                )
            )

    return records


# =========================================================
# 3. البوابة الرئيسية — Main Gate
# =========================================================

def apply_rejection_gate(state: ProofState) -> ProofState:
    """
    محرك الرفض المُعلَّل.

    المدخلات:
        state.conceptual_state["agent_operator_result"]
        state.conceptual_state["enriched_concepts"]
        state.world_model

    المخرجات:
        state.conceptual_state["rejection_records"]
        state.conceptual_state["rejection_gate_passed"]
        trace event: "rejection_gate"
    """
    sentence = state.effective_text()
    agent_result: dict = state.conceptual_state.get("agent_operator_result", {})
    enriched: list[dict] = state.conceptual_state.get("enriched_concepts", [])
    world_model: dict = state.world_model or {}

    all_records: list[RejectionRecord] = []
    all_records.extend(_check_agent_violations(agent_result, sentence))
    all_records.extend(_check_instrument_violations(agent_result, sentence))
    all_records.extend(_check_world_violations(enriched, world_model, sentence))

    passed = len(all_records) == 0
    records_dicts = [asdict(r) for r in all_records]

    state.conceptual_state["rejection_records"] = records_dicts
    state.conceptual_state["rejection_gate_passed"] = passed

    state.add_trace(
        "rejection_gate",
        {
            "passed": passed,
            "rejection_count": len(all_records),
            "violations": [r.get("violation_type") for r in records_dicts],
            "judgments": [r.get("judgment") for r in records_dicts],
        },
    )
    return state
