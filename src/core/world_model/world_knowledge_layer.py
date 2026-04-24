"""
world_knowledge_layer.py
========================
طبقة معرفة العالم

تُحوّل:
    WorldModel (مستخرَج من النص فقط)
    ──────────────────────────────────
    WorldModel (مُتحقَّق + مُثرَى بمعرفة عالم حقيقية)

أنواع المعرفة:
    1. فيزيائية  — النار تحرق، الماء يسيل، القلم يكتب
    2. سببية     — الكتابة تحتاج أداة، الدراسة تفضي إلى العلم
    3. منطقية    — لا يجتمع النقيضان، الكلّ أكبر من الجزء
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.model import ProofState


# =========================================================
# 1. نماذج قواعد المعرفة — Knowledge Rule Models
# =========================================================

@dataclass(frozen=True)
class PhysicalRule:
    """قاعدة فيزيائية — علاقة بين كيان وفعل أو أثر."""
    subject: str                 # e.g. "نار"
    predicate: str               # e.g. "تحرق"
    object_type: str             # e.g. "مادة_قابلة_للاشتعال"
    confidence: float = 1.0
    law_tag: str = "physical"


@dataclass(frozen=True)
class CausalRule:
    """قاعدة سببية — cause → effect."""
    cause_action: str            # e.g. "كتابة"
    requires: str                # e.g. "أداة_كتابة"
    effect: str                  # e.g. "نقش_على_سطح"
    confidence: float = 0.95
    law_tag: str = "causal"


@dataclass(frozen=True)
class LogicalRule:
    """قاعدة منطقية — ثابت تشغيلي غير مشروط."""
    name: str                    # e.g. "law_of_non_contradiction"
    statement: str               # e.g. "لا يجتمع النقيضان"
    law_tag: str = "logical"


@dataclass(frozen=True)
class AffordanceRule:
    """قاعدة قدرة — ما يستطيع هذا الكيان أن يُنجز."""
    entity: str                  # e.g. "قلم"
    action: str                  # e.g. "كتابة"
    instrument_of: str           # e.g. "كتابة"
    confidence: float = 0.9
    law_tag: str = "affordance"


# =========================================================
# 2. قواعد المعرفة المُضمَّنة — Embedded Knowledge Rules
# =========================================================

PHYSICAL_RULES: tuple[PhysicalRule, ...] = (
    PhysicalRule("نار",    "تحرق",    "مادة_عضوية",         1.0),
    PhysicalRule("ماء",    "يسيل",    "وعاء_أو_سطح",        1.0),
    PhysicalRule("ماء",    "يطفئ",    "نار",                0.95),
    PhysicalRule("ضوء",    "يضيء",    "فضاء_مظلم",          1.0),
    PhysicalRule("ثقل",    "يسقط",    "أرض",                0.95),
    PhysicalRule("برودة",  "تُجمّد",  "سائل",               0.9),
)

CAUSAL_RULES: tuple[CausalRule, ...] = (
    CausalRule("كتابة",  "أداة_كتابة",   "نقش_رموز_على_سطح",  0.95),
    CausalRule("قراءة",  "نص_مكتوب",     "فهم_معنى",           0.90),
    CausalRule("دراسة",  "وقت_وجهد",     "اكتساب_علم",         0.90),
    CausalRule("أكل",    "طعام",          "شبع",               0.95),
    CausalRule("ضرب",    "قوة",           "ألم_أو_أثر",         0.90),
    CausalRule("فتح",    "مفتاح_أو_يد",  "إزالة_إغلاق",        0.85),
    CausalRule("بناء",   "مواد_بناء",    "مبنى",               0.90),
    CausalRule("تعلّم",  "تكرار_وفهم",   "مهارة_أو_معرفة",     0.85),
)

LOGICAL_RULES: tuple[LogicalRule, ...] = (
    LogicalRule("law_of_non_contradiction", "لا يجتمع النقيضان في آنٍ واحد"),
    LogicalRule("law_of_excluded_middle",   "الشيء إما موجود أو غير موجود"),
    LogicalRule("law_of_identity",          "كل شيء يساوي نفسه"),
    LogicalRule("transitivity_of_causality","إن كان أ يؤدي إلى ب وب يؤدي إلى ج فأ يؤدي إلى ج"),
    LogicalRule("whole_greater_than_part",  "الكل أكبر من الجزء"),
)

AFFORDANCE_RULES: tuple[AffordanceRule, ...] = (
    AffordanceRule("قلم",    "كتابة",  "كتابة",   0.95),
    AffordanceRule("قلم",    "رسم",    "رسم",     0.85),
    AffordanceRule("كتاب",   "قراءة",  "قراءة",   0.95),
    AffordanceRule("سكين",   "قطع",    "قطع",     0.95),
    AffordanceRule("هاتف",   "تواصل",  "تواصل",   0.95),
    AffordanceRule("حاسوب",  "كتابة",  "كتابة",   0.90),
    AffordanceRule("حاسوب",  "حساب",   "حساب",    0.90),
    AffordanceRule("باب",    "فتح",    "فتح",     0.90),
    AffordanceRule("باب",    "غلق",    "غلق",     0.90),
    AffordanceRule("ماء",    "شرب",    "شرب",     0.90),
    AffordanceRule("طعام",   "أكل",    "أكل",     0.95),
    AffordanceRule("مفتاح",  "فتح",    "فتح",     0.95),
)

_AFFORDANCE_INDEX: dict[str, list[AffordanceRule]] = {}
for _rule in AFFORDANCE_RULES:
    _AFFORDANCE_INDEX.setdefault(_rule.entity, []).append(_rule)

_CAUSAL_INDEX: dict[str, CausalRule] = {r.cause_action: r for r in CAUSAL_RULES}
_PHYSICAL_INDEX: dict[str, PhysicalRule] = {r.subject: r for r in PHYSICAL_RULES}


# =========================================================
# 3. منطق الإثراء — Enrichment Logic
# =========================================================

def _match_affordance_laws(entities: list[dict], events: list[dict]) -> list[dict]:
    """طابق الكيانات المُستخرَجة بالقدرات لتوليد قوانين ضمنية."""
    new_laws: list[dict] = []
    entity_ids = {e.get("id", "") for e in entities}
    event_actions = {ev.get("action", "") for ev in events}

    for entity_id in entity_ids:
        for bare in [entity_id, entity_id.lstrip("ال")]:
            affordances = _AFFORDANCE_INDEX.get(bare, [])
            for aff in affordances:
                if aff.action in event_actions or not event_actions:
                    new_laws.append(
                        {
                            "domain": "world_affordance",
                            "rule": f"{aff.entity} أداة صالحة لـ {aff.instrument_of}",
                            "law_type": aff.law_tag,
                            "confidence": aff.confidence,
                            "entity": aff.entity,
                            "action": aff.action,
                        }
                    )
    return new_laws


def _match_causal_rules(events: list[dict]) -> tuple[list[dict], list[dict]]:
    """استنتاج روابط السببية والأهداف من الأحداث."""
    new_causality: list[dict] = []
    new_goals: list[dict] = []
    for event in events:
        action = event.get("action", "")
        causal = _CAUSAL_INDEX.get(action)
        if causal:
            new_causality.append(
                {
                    "cause": causal.cause_action,
                    "requires": causal.requires,
                    "effect": causal.effect,
                    "confidence": causal.confidence,
                    "law_tag": causal.law_tag,
                }
            )
            new_goals.append(
                {
                    "action": causal.cause_action,
                    "purpose": causal.effect,
                    "inferred": True,
                }
            )
    return new_causality, new_goals


def _validate_instrument_use(
    events: list[dict],
    entities: list[dict],
    enriched_concepts: list[dict],
) -> dict[str, Any]:
    """
    تحقق: هل الأداة المذكورة في الجملة صالحة للفعل؟
    تفحص مفاهيم مُثرَاة بـ relation_type=Instrumentality.
    """
    instrument_tokens: list[str] = []
    for concept in enriched_concepts:
        if concept.get("relation_type") == "Instrumentality":
            # الرمز التالي بعد حرف الجر هو الأداة الفعلية
            token = concept.get("token", "")
            if token:
                instrument_tokens.append(token)

    if not instrument_tokens or not events:
        return {"validated": False, "reason": "no_instrument_or_event"}

    event_actions = [ev.get("action", "") for ev in events]
    validations: list[dict] = []

    for instrument_raw in instrument_tokens:
        bare = instrument_raw.lstrip("ال")
        for action in event_actions:
            affordances = _AFFORDANCE_INDEX.get(bare, [])
            valid = any(a.action == action or a.instrument_of == action for a in affordances)
            validations.append(
                {
                    "instrument": bare,
                    "action": action,
                    "valid": valid,
                    "explanation": (
                        f"{bare} أداة صالحة لـ {action}"
                        if valid
                        else f"{bare} لا يُعرف استخدامه في {action}"
                    ),
                }
            )

    overall_valid = any(v["valid"] for v in validations) if validations else False
    return {"validated": overall_valid, "checks": validations}


# =========================================================
# 4. البوابة الرئيسية — Main Gate
# =========================================================

def apply_world_knowledge_layer(state: ProofState) -> ProofState:
    """
    طبقة معرفة العالم.

    المدخلات:
        state.world_model        — WorldModel المُستخرَج
        state.conceptual_state["enriched_concepts"]  — المفاهيم المُثرَاة (اختياري)

    المخرجات:
        state.world_model   — مُثرَى بـ: قوانين جديدة + سببية + أهداف + تحقق الأداة
        trace event: "world_knowledge_layer"
    """
    wm = state.world_model
    entities = wm.get("entities", [])
    events = wm.get("events", [])
    enriched_concepts: list[dict] = state.conceptual_state.get("enriched_concepts", [])

    # ── القوانين المنطقية الثابتة دائمًا ──────────────────────────────
    _core_logical_rule_names = {
        "law_of_non_contradiction",
        "law_of_excluded_middle",
        "law_of_identity",
    }
    logical_laws = [
        {"domain": "logic", "rule": r.statement, "law_type": r.law_tag, "name": r.name}
        for r in LOGICAL_RULES
        if r.name in _core_logical_rule_names
    ]

    # ── قوانين القدرات (affordance) ─────────────────────────────────
    affordance_laws = _match_affordance_laws(entities, events)

    # ── السببية والأهداف ─────────────────────────────────────────────
    new_causality, new_goals = _match_causal_rules(events)

    # ── تحقق الأداة ─────────────────────────────────────────────────
    instrument_validation = _validate_instrument_use(events, entities, enriched_concepts)

    # ── دمج في WorldModel ──────────────────────────────────────────
    existing_laws: list[dict] = list(wm.get("laws", []))
    existing_causality: list[dict] = list(wm.get("causality", []))
    existing_goals: list[dict] = list(wm.get("goals", []))
    uncertainty: list[str] = list(wm.get("uncertainty", []))

    all_laws = existing_laws + logical_laws + affordance_laws
    all_causality = existing_causality + new_causality
    all_goals = existing_goals + new_goals

    # إزالة "causality_not_detected" / "goals_not_detected" إن أُضيف محتوى
    if new_causality and "causality_not_detected" in uncertainty:
        uncertainty.remove("causality_not_detected")
    if new_goals and "goals_not_detected" in uncertainty:
        uncertainty.remove("goals_not_detected")

    wm["laws"] = all_laws
    wm["causality"] = all_causality
    wm["goals"] = all_goals
    wm["uncertainty"] = uncertainty
    wm["world_knowledge"] = {
        "logical_laws_added": len(logical_laws),
        "affordance_laws_added": len(affordance_laws),
        "causal_rules_matched": len(new_causality),
        "goals_inferred": len(new_goals),
        "instrument_validation": instrument_validation,
    }

    state.world_model = wm

    state.add_trace(
        "world_knowledge_layer",
        {
            "laws_total": len(all_laws),
            "causality_total": len(all_causality),
            "goals_total": len(all_goals),
            "instrument_valid": instrument_validation.get("validated", False),
        },
    )
    return state
