"""
metaphor_gate.py
================
بوابة المجاز — كشف التعارضات الدلالية وتأويلها

تبحث هذه البوابة عن خاصية مشتركة بين الكيان المتعارِض (مثل: أسد)
والإنسان، فإن وجدتها أصدرت حكم "metaphorical_accepted"، وإلا أبقت الرفض.

مثال:
    أسد يخطب → أسد (حيوان) ∩ إنسان = {شجاعة} → أسد = رجل شجاع
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Optional

from arabic_engine.language.rejection_gate import RejectionRecord
from core.model import ProofState


# =========================================================
# فهرس الخصائص المشتركة — Shared Properties Index
# =========================================================

SHARED_PROPERTIES_INDEX: dict[str, tuple[str, ...]] = {
    "أسد":    ("شجاعة", "قوة"),
    "ثعلب":   ("مكر", "دهاء"),
    "حمار":   ("غباء", "عناد"),
    "نسر":    ("حدة_النظر", "علو"),
    "ذئب":    ("شراسة", "جرأة"),
    "غزال":   ("رشاقة", "جمال"),
    "بحر":    ("كرم", "سعة"),
    "نهر":    ("جريان", "سخاء"),
    "شمس":    ("إشراق", "ظهور"),
    "قمر":    ("نور", "جمال"),
    "إنسان":  ("شجاعة", "عقل", "كلام", "قوة", "كرم"),
    "رجل":    ("شجاعة", "عقل", "كلام", "قوة", "كرم"),
    "طالب":   ("عقل", "كلام"),
}

# الإنسان يشترك في هذه الخصائص مع الحيوانات والطبيعة
_HUMAN_PROPERTIES: frozenset[str] = frozenset({
    "شجاعة", "عقل", "كلام", "قوة", "كرم", "دهاء", "جرأة", "حدة_النظر",
})


@dataclass
class MetaphorResult:
    """نتيجة بوابة المجاز."""
    resolved: bool
    source_token: str
    target_interpretation: str
    shared_property: Optional[str]
    judgment: str           # metaphorical_accepted | unresolved_metaphor | not_applicable


# Arabic diacritics (harakat + tanwin) — U+064B..U+065F and U+0670
_ARABIC_DIACRITICS_RE = re.compile(r'[\u064B-\u065F\u0670]')


def _normalize_arabic(token: str) -> str:
    """
    يُزيل التشكيل والتنوين من الرمز العربي مع الحفاظ على الحروف الأصيلة.

    مثال: أسدًا → أسد  (يحذف تنوين الفتح + الألف، يحفظ الهمزة)
    على خلاف NFKD، هذه الدالة لا تُحلِّل حروف الهمزة.
    """
    # حذف تنوين الفتح المكتوب كـ ـً + ا
    result = token.replace("\u064B\u0627", "")
    # حذف باقي علامات التشكيل
    result = _ARABIC_DIACRITICS_RE.sub("", result)
    # إزالة أداة التعريف
    if result.startswith("ال") and len(result) > 2:
        result = result[2:]
    return result


def apply_metaphor_gate(
    state: ProofState,
    rejection: Optional[RejectionRecord],
) -> MetaphorResult:
    """
    بوابة المجاز.

    إن لم يكن هناك سجل رفض، أو كان الحكم ليس 'محتمل_مجازي'،
    تُعيد نتيجة غير منطبقة.

    وإلا تبحث عن خاصية مشتركة وتُصدر الحكم المناسب.

    المخرجات:
        MetaphorResult
        state.symbolic_state["metaphor_gate"] — النتيجة المُسلسَلة
        trace event: "metaphor_gate"
    """
    if rejection is None or rejection.judgment != "محتمل_مجازي":
        result = MetaphorResult(
            resolved=False,
            source_token="",
            target_interpretation="",
            shared_property=None,
            judgment="not_applicable",
        )
        state.symbolic_state["metaphor_gate"] = asdict(result)
        state.add_trace("metaphor_gate", asdict(result))
        return result

    raw_token = rejection.violating_token
    normalized = _normalize_arabic(raw_token)

    # البحث في فهرس الخصائص المشتركة
    props = SHARED_PROPERTIES_INDEX.get(normalized) or SHARED_PROPERTIES_INDEX.get(raw_token) or ()

    # أيضًا تحقق من المفاهيم المُثرَاة (قد تحمل shared_properties مُعبَّأة)
    if not props:
        props = _lookup_shared_from_enriched(state, raw_token, normalized)

    # البحث عن خاصية تتقاطع مع خصائص الإنسان
    shared_prop: Optional[str] = None
    for prop in props:
        if prop in _HUMAN_PROPERTIES:
            shared_prop = prop
            break

    if shared_prop:
        interpretation = f"{normalized} = رجل {_prop_adjective(shared_prop)}"
        result = MetaphorResult(
            resolved=True,
            source_token=raw_token,
            target_interpretation=interpretation,
            shared_property=shared_prop,
            judgment="metaphorical_accepted",
        )
    else:
        result = MetaphorResult(
            resolved=False,
            source_token=raw_token,
            target_interpretation="",
            shared_property=None,
            judgment="unresolved_metaphor",
        )

    state.symbolic_state["metaphor_gate"] = asdict(result)
    state.add_trace("metaphor_gate", asdict(result))
    return result


def _lookup_shared_from_enriched(
    state: ProofState, raw_token: str, normalized: str
) -> tuple[str, ...]:
    """يسترجع الخصائص المشتركة من المفاهيم المُثرَاة."""
    for concept in state.enriched_concepts or []:
        t = concept.get("token", "")
        t_bare = t[2:] if t.startswith("ال") and len(t) > 2 else t
        if t == raw_token or t == normalized or t_bare == normalized:
            shared = concept.get("shared_properties")
            if shared:
                return tuple(shared)
    return ()


def _prop_adjective(prop: str) -> str:
    """يُحوِّل اسم الخاصية إلى صفة عربية مناسبة."""
    mapping = {
        "شجاعة": "شجاع",
        "قوة": "قوي",
        "كرم": "كريم",
        "دهاء": "داهية",
        "جرأة": "جريء",
        "عقل": "عاقل",
        "كلام": "بليغ",
    }
    return mapping.get(prop, prop)
