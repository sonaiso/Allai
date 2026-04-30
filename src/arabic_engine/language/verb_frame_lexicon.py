"""
verb_frame_lexicon.py
=====================
معجم إطارات الأفعال الدلالية

يُعرِّف هذا المعجمُ قيود الأفعال الدلالية (event frames) التي تُحدِّد:
    - الأدوار المطلوبة والاختيارية
    - أنواع الفاعل المسموح بها والمرفوضة
    - الأنماط السطحية التي تُشير إلى إطار معيَّن
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import unicodedata


@dataclass(frozen=True)
class VerbFrame:
    """إطار حدث فعل — يُحدِّد القيود الدلالية للفعل."""
    root: str                               # e.g. "ك ت ب"
    requires: tuple[str, ...]               # الأدوار المطلوبة  e.g. ("فاعل",)
    optional: tuple[str, ...]               # الأدوار الاختيارية e.g. ("مفعول", "أداة")
    rejects: tuple[str, ...]                # أنواع الفاعل المرفوضة e.g. ("جماد",)
    requires_agent_type: tuple[str, ...]    # أنواع الفاعل المسموح بها e.g. ("إنسان",)
    volitional: bool = True                 # هل يستلزم الفعل إرادة؟


# =========================================================
# معجم إطارات الأفعال — Verb Frame Lexicon
# =========================================================

VERB_FRAME_LEXICON: tuple[VerbFrame, ...] = (
    VerbFrame(
        root="ك ت ب",
        requires=("فاعل",),
        optional=("مفعول", "أداة"),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="ق ر أ",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان",),
        volitional=True,
    ),
    VerbFrame(
        root="خ ط ب",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان",),
        volitional=True,
    ),
    VerbFrame(
        root="ض ر ب",
        requires=("فاعل",),
        optional=("مفعول", "أداة"),
        rejects=("جماد", "مادة", "سائل", "ظاهرة"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="أ ك ل",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="ق و ل",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان",),
        volitional=True,
    ),
    VerbFrame(
        root="ذ ه ب",
        requires=("فاعل",),
        optional=("وجهة",),
        rejects=("جماد", "مادة", "سائل"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="ج ل س",
        requires=("فاعل",),
        optional=("مكان",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="ع ل م",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان",),
        volitional=True,
    ),
    VerbFrame(
        root="ف ه م",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان",),
        volitional=True,
    ),
    VerbFrame(
        root="ف ت ح",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="ن ص ر",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="د ر س",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان",),
        volitional=True,
    ),
    VerbFrame(
        root="ح م ل",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="و ج د",
        requires=("فاعل",),
        optional=(),
        rejects=(),
        requires_agent_type=(),
        volitional=False,
    ),
    VerbFrame(
        root="ب ن ي",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
    VerbFrame(
        root="ر أ ي",
        requires=("فاعل",),
        optional=("مفعول",),
        rejects=("جماد", "مادة", "سائل", "ظاهرة", "أثاث", "بنية", "أداة", "مصنوع"),
        requires_agent_type=("إنسان", "حيوان"),
        volitional=True,
    ),
)

_VERB_FRAME_INDEX: dict[str, VerbFrame] = {f.root: f for f in VERB_FRAME_LEXICON}

# =========================================================
# تلميحات السطح → الجذر — Surface Hints
# =========================================================

_VERB_FRAME_SURFACE_HINTS: dict[str, str] = {
    # ك ت ب
    "كتب": "ك ت ب",   "يكتب": "ك ت ب",  "كاتب": "ك ت ب",  "كتابة": "ك ت ب",
    "كتاب": "ك ت ب",  "مكتوب": "ك ت ب",
    # ق ر أ
    "قرأ": "ق ر أ",   "يقرأ": "ق ر أ",  "قارئ": "ق ر أ",  "قراءة": "ق ر أ",
    # خ ط ب
    "خطب": "خ ط ب",   "يخطب": "خ ط ب",  "خاطب": "خ ط ب",  "خطبة": "خ ط ب",
    "يخطبون": "خ ط ب",
    # ض ر ب
    "ضرب": "ض ر ب",   "يضرب": "ض ر ب",  "ضارب": "ض ر ب",
    # أ ك ل
    "أكل": "أ ك ل",   "يأكل": "أ ك ل",
    # ق و ل
    "قال": "ق و ل",   "يقول": "ق و ل",  "قول": "ق و ل",
    # ذ ه ب
    "ذهب": "ذ ه ب",   "يذهب": "ذ ه ب",
    # ج ل س
    "جلس": "ج ل س",   "يجلس": "ج ل س",
    # ع ل م
    "علم": "ع ل م",   "يعلم": "ع ل م",  "عالم": "ع ل م",
    # ف ه م
    "فهم": "ف ه م",   "يفهم": "ف ه م",
    # ف ت ح
    "فتح": "ف ت ح",   "يفتح": "ف ت ح",
    # ن ص ر
    "نصر": "ن ص ر",   "ينصر": "ن ص ر",
    # د ر س
    "درس": "د ر س",   "يدرس": "د ر س",  "دراسة": "د ر س",
    # ح م ل
    "حمل": "ح م ل",   "يحمل": "ح م ل",
    # و ج د
    "وجد": "و ج د",   "يوجد": "و ج د",
    # ب ن ي
    "بنى": "ب ن ي",   "يبني": "ب ن ي",
    # ر أ ي
    "رأى": "ر أ ي",   "رأيت": "ر أ ي",  "يرى": "ر أ ي",
}


def _normalize_surface(token: str) -> str:
    """إزالة التشكيل والتنوين من الرمز لتسهيل المطابقة."""
    # إزالة علامات التشكيل Unicode (category Mn = Mark, Nonspacing)
    normalized = unicodedata.normalize("NFKD", token)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def get_verb_frame(surface: str) -> Optional[VerbFrame]:
    """
    يُعيد إطار الفعل المقابل للصيغة السطحية المعطاة.

    يُزيل التشكيل والتنوين، ثم يبحث في جدول التلميحات السطحية.
    يُعيد None إن لم يُعثَر على إطار مطابق.
    """
    normalized = _normalize_surface(surface)
    root = _VERB_FRAME_SURFACE_HINTS.get(normalized) or _VERB_FRAME_SURFACE_HINTS.get(surface)
    if root:
        return _VERB_FRAME_INDEX.get(root)
    return None
