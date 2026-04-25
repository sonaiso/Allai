"""
agent_operator_gate.py
=======================
محرك العامل — قانون: عامل + معمول → أثر + علاقة

يُطبِّق القانون الدلالي:
    الفعل + الكيان/الأداة → نوع العلاقة + صحتها

المدخلات:
    state.conceptual_state["enriched_concepts"]
    state.conceptual_state.get("verb_frame")   — (اختياري، يُحسَب داخليًا)

المخرجات:
    state.conceptual_state["agent_operator_result"]
    trace event: "agent_operator_gate"
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from arabic_engine.language.verb_frame_lexicon import (
    INANIMATE_ENTITY_TYPES,
    VerbFrame,
    get_verb_frame,
    is_rejection_applicable,
)
from core.model import ProofState


# =========================================================
# 1. نماذج النتائج — Result Models
# =========================================================

@dataclass
class OperatorBinding:
    """نتيجة ربط عامل بمعمول واحد."""
    operator: str                       # الفعل
    operand: str                        # المعمول (الأداة / المفعول / الفاعل)
    relation: str                       # نوع العلاقة (آلة / فاعل / مفعول / ظرف)
    valid: bool                         # هل الربط صحيح؟
    reason: str                         # التبرير
    law_triggered: Optional[str] = None  # القانون الذي تُطبَّق بموجبه


@dataclass
class AgentOperatorResult:
    """نتيجة محرك العامل الكاملة لجملة."""
    verb: Optional[str]
    verb_frame: Optional[dict]
    agent_token: Optional[str]
    agent_valid: bool
    agent_reason: str
    instrument_bindings: list[OperatorBinding] = field(default_factory=list)
    object_bindings: list[OperatorBinding] = field(default_factory=list)
    overall_valid: bool = True
    violations: list[str] = field(default_factory=list)


# =========================================================
# 1b. تعيين الفعل → مصدره — Verb to Masdar Map
# =========================================================

# تعيين من صيغة الفعل السطحية إلى المصدر المقابل في قوائم القدرات
_VERB_TO_MASDAR: dict[str, str] = {
    "كتب":   "كتابة",
    "يكتب":  "كتابة",
    "اكتب":  "كتابة",
    "قرأ":   "قراءة",
    "يقرأ":  "قراءة",
    "أكل":   "أكل",
    "يأكل":  "أكل",
    "ضرب":   "ضرب",
    "يضرب":  "ضرب",
    "فتح":   "فتح",
    "يفتح":  "فتح",
    "ذهب":   "ذهب",
    "يذهب":  "ذهب",
    "قال":   "تواصل",
    "يقول":  "تواصل",
    "خطب":   "خطب",
    "يخطب":  "خطب",
    "رأى":   "رأى",
    "يرى":   "رأى",
}


def _verb_matches_affordance(verb: str, affordances: list) -> bool:
    """
    هل الفعل (أو مصدره) يتطابق مع إحدى القدرات؟
    يتحقق من الفعل مباشرة، ثم من المصدر المقابل.
    """
    if verb in affordances:
        return True
    masdar = _VERB_TO_MASDAR.get(verb)
    if masdar and masdar in affordances:
        return True
    return False


# =========================================================
# 2. منطق الربط — Binding Logic
# =========================================================

def _find_verb(enriched_concepts: list[dict]) -> Optional[str]:
    """استخرج الفعل من المفاهيم المُثرَاة (بحث في الجذور والنوع الصرفي)."""
    from arabic_engine.language.lexical_enrichment_gate import _ROOT_SURFACE_HINTS  # type: ignore[attr-defined]
    for concept in enriched_concepts:
        token = concept.get("token", "")
        if _ROOT_SURFACE_HINTS.get(token):
            frame = get_verb_frame(token)
            if frame:
                return token
    return None


def _find_agent(enriched_concepts: list[dict]) -> Optional[dict]:
    """
    ابحث عن أول مفهوم كيان يمكن أن يكون فاعلًا.
    يُستبعَد: الحروف (relation_type موجود)، والأدوات التي تحمل دور instrument.
    """
    for concept in enriched_concepts:
        # يجب أن يكون كيانًا حقيقيًا (entity_type) وليس حرفًا (relation_type)
        if concept.get("entity_type") and concept.get("relation_type") is None:
            # يُستبعَد ما يحمل دور "instrument"
            if "instrument" not in concept.get("roles", []):
                return concept
    return None


def _validate_agent(agent_concept: dict, frame: VerbFrame) -> tuple[bool, str, Optional[str]]:
    """
    تحقق: هل الفاعل يستوفي متطلبات الفعل؟
    يُعيد: (valid, reason, law_triggered)
    """
    entity_type = agent_concept.get("entity_type", "")
    token = agent_concept.get("token", "")

    # فحص: هل نوع الكيان في قائمة الرفض؟
    for reject in frame.rejects:
        if is_rejection_applicable(entity_type, reject):
            law = f"{frame.verb}_rejects_{reject}"
            return (
                False,
                f"{token} ({entity_type}) لا يُقبل فاعلًا للفعل '{frame.verb}' — شرط الرفض: {reject}",
                law,
            )

    # فحص: هل يملك خاصية الفاعل المطلوبة؟
    agent_prop = frame.agent_property
    if agent_prop == "قادر" and entity_type in INANIMATE_ENTITY_TYPES:
        return (
            False,
            f"{token} ({entity_type}) جماد — لا يملك خاصية 'قادر' المطلوبة للفعل '{frame.verb}'",
            f"Adam:قابلية_{frame.verb}",
        )

    if agent_prop == "إنسان" and entity_type not in ("إنسان",):
        return (
            False,
            f"{token} ({entity_type}) ليس إنسانًا — الفعل '{frame.verb}' يشترط فاعلًا إنسانًا",
            f"Adam:فعل_{frame.verb}_يشترط_إنسان",
        )

    if agent_prop == "حي" and entity_type in INANIMATE_ENTITY_TYPES:
        return (
            False,
            f"{token} ({entity_type}) غير حي — الفعل '{frame.verb}' يشترط فاعلًا حيًّا",
            f"Adam:فعل_{frame.verb}_يشترط_حي",
        )

    return True, f"{token} ({entity_type}) فاعل مقبول للفعل '{frame.verb}'", None


def _validate_instrument(
    instrument_concept: dict,
    frame: VerbFrame,
) -> OperatorBinding:
    """تحقق: هل الأداة صالحة لهذا الفعل؟"""
    token = instrument_concept.get("token", "")
    bare = token.lstrip("ال")
    entity_type = instrument_concept.get("entity_type", "")
    affordances = instrument_concept.get("affordances", [])
    impossible = instrument_concept.get("impossible_actions", [])

    # هل الفعل في قائمة الأفعال الممتنعة على هذه الأداة؟
    if frame.verb in impossible:
        return OperatorBinding(
            operator=frame.verb,
            operand=bare,
            relation="آلة",
            valid=False,
            reason=f"{bare} لا يُستخدم في '{frame.verb}' — مدرج في impossible_actions",
            law_triggered=f"affordance_violation_{bare}_{frame.verb}",
        )

    # هل الأداة مُدرجة في القدرات (تطابق مباشر أو عبر المصدر)؟
    if _verb_matches_affordance(frame.verb, affordances):
        return OperatorBinding(
            operator=frame.verb,
            operand=bare,
            relation="آلة",
            valid=True,
            reason=f"{bare} أداة صالحة لـ '{frame.verb}'",
        )

    # لا توجد قدرة موثَّقة
    return OperatorBinding(
        operator=frame.verb,
        operand=bare,
        relation="آلة",
        valid=False,
        reason=f"{bare} ({entity_type}) — لا توجد قدرة مؤكدة على '{frame.verb}'",
        law_triggered=f"affordance_unknown_{bare}",
    )


# =========================================================
# 3. البوابة الرئيسية — Main Gate
# =========================================================

def apply_agent_operator_gate(state: ProofState) -> ProofState:
    """
    محرك العامل.

    المدخلات:
        state.conceptual_state["enriched_concepts"]

    المخرجات:
        state.conceptual_state["agent_operator_result"]
        trace event: "agent_operator_gate"
    """
    enriched: list[dict] = state.conceptual_state.get("enriched_concepts", [])

    # ── استخراج الفعل ──────────────────────────────────────
    verb_token = _find_verb(enriched)
    # محاولة من الـ minimal_complete_encoding
    if not verb_token:
        token_units = (
            state.symbolic_state.get("minimal_complete_encoding", {}).get("token_units", [])
        )
        for unit in token_units:
            t = unit.get("token", "")
            if get_verb_frame(t):
                verb_token = t
                break

    frame: Optional[VerbFrame] = get_verb_frame(verb_token) if verb_token else None

    result = AgentOperatorResult(
        verb=verb_token,
        verb_frame=asdict(frame) if frame else None,
        agent_token=None,
        agent_valid=True,
        agent_reason="no_verb_detected",
    )

    if not frame:
        state.conceptual_state["agent_operator_result"] = asdict(result)
        state.add_trace("agent_operator_gate", {"verb": verb_token, "frame_found": False})
        return state

    # ── التحقق من الفاعل ────────────────────────────────────
    agent_concept = _find_agent(enriched)
    if agent_concept:
        result.agent_token = agent_concept.get("token")
        valid, reason, law = _validate_agent(agent_concept, frame)
        result.agent_valid = valid
        result.agent_reason = reason
        if not valid:
            result.overall_valid = False
            result.violations.append(reason)

    # ── التحقق من الأدوات ────────────────────────────────────
    # استبعاد الحروف (relation_type موجود) والاحتفاظ بالكيانات الحقيقية التي لها دور أداة
    instrument_concepts = [
        c for c in enriched
        if "instrument" in c.get("roles", [])
        and c.get("entity_type") is not None
    ]
    for inst_concept in instrument_concepts:
        binding = _validate_instrument(inst_concept, frame)
        result.instrument_bindings.append(binding)
        if not binding.valid:
            result.overall_valid = False
            result.violations.append(binding.reason)

    # ── تخزين القاموس في الحالة ─────────────────────────────
    result_dict: dict[str, Any] = {
        "verb": result.verb,
        "verb_frame": result.verb_frame,
        "agent_token": result.agent_token,
        "agent_valid": result.agent_valid,
        "agent_reason": result.agent_reason,
        "instrument_bindings": [asdict(b) for b in result.instrument_bindings],
        "object_bindings": [asdict(b) for b in result.object_bindings],
        "overall_valid": result.overall_valid,
        "violations": result.violations,
    }
    state.conceptual_state["agent_operator_result"] = result_dict

    state.add_trace(
        "agent_operator_gate",
        {
            "verb": verb_token,
            "frame_found": True,
            "agent_valid": result.agent_valid,
            "instruments": len(result.instrument_bindings),
            "overall_valid": result.overall_valid,
            "violation_count": len(result.violations),
        },
    )
    return state
