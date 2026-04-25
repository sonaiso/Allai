"""
verb_frame_lexicon.py
=====================
معجم الأفعال كأطر أحداث

كل فعل يُمثَّل كإطار حدث يحدد:
    - requires  : ما يستلزمه الفعل (نوع الفاعل، المتطلبات الوجودية)
    - optional  : ما قد يُصاحبه (أداة، مفعول، مكان، غاية)
    - rejects   : ما يتعارض معه وجوبًا

الاستخدام:
    from arabic_engine.language.verb_frame_lexicon import get_verb_frame, VerbFrame
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# =========================================================
# 1. نموذج إطار الفعل — Verb Frame Model
# =========================================================

@dataclass(frozen=True)
class VerbFrame:
    """إطار حدث الفعل — تعريف قيوده الدلالية والعالمية."""
    verb: str                           # الفعل المضارع / الجذر السطحي
    root: Optional[str]                 # الجذر (إن عُرف)
    event_type: str                     # نوع الحدث الدلالي
    requires: tuple[str, ...]           # ما يستلزمه الفعل
    optional: tuple[str, ...]           # ما قد يُصاحبه
    rejects: tuple[str, ...]            # ما يتعارض معه
    agent_property: str = "قادر"        # الخاصية المطلوبة في الفاعل
    produces: tuple[str, ...] = field(default_factory=tuple)  # ما ينتجه


# =========================================================
# 2. معجم الأفعال المُضمَّن — Embedded Verb Lexicon
# =========================================================

_VERB_FRAMES: tuple[VerbFrame, ...] = (
    VerbFrame(
        verb="كتب",
        root="ك ت ب",
        event_type="إنتاج_رمز_مكتوب",
        requires=("فاعل_قادر",),
        optional=("أداة", "مفعول_مكتوب", "مكان", "غاية"),
        rejects=("فاعل_جماد",),
        agent_property="قادر",
        produces=("نص_مكتوب", "رمز_محفوظ"),
    ),
    VerbFrame(
        verb="قرأ",
        root="ق ر أ",
        event_type="استقبال_رموز_وفهمها",
        requires=("فاعل_مُبصِر", "نص_مكتوب"),
        optional=("مكان", "غاية"),
        rejects=("فاعل_أعمى_بلا_بديل", "فاعل_جماد"),
        agent_property="مُبصِر",
        produces=("فهم_معنى",),
    ),
    VerbFrame(
        verb="خطب",
        root="خ ط ب",
        event_type="إلقاء_كلام_رسمي",
        requires=("فاعل_إنسان",),
        optional=("مكان", "موضوع", "جمهور"),
        rejects=("فاعل_حيوان", "فاعل_جماد"),
        agent_property="إنسان",
        produces=("خطاب_ملقى",),
    ),
    VerbFrame(
        verb="رأى",
        root="ر أ ي",
        event_type="إدراك_بصري",
        requires=("فاعل_مُبصِر",),
        optional=("مفعول",),
        rejects=("فاعل_جماد",),
        agent_property="مُبصِر",
        produces=("إدراك_بصري",),
    ),
    VerbFrame(
        verb="أكل",
        root="أ ك ل",
        event_type="استهلاك_غذاء",
        requires=("فاعل_حي",),
        optional=("مفعول_طعام", "مكان"),
        rejects=("فاعل_جماد",),
        agent_property="حي",
        produces=("شبع", "استهلاك_طعام"),
    ),
    VerbFrame(
        verb="ضرب",
        root="ض ر ب",
        event_type="إحداث_أثر_بقوة",
        requires=("فاعل_قادر",),
        optional=("أداة", "مفعول", "مكان"),
        rejects=("فاعل_جماد",),
        agent_property="قادر",
        produces=("أثر_ضربة", "ألم"),
    ),
    VerbFrame(
        verb="ذهب",
        root="ذ ه ب",
        event_type="انتقال_مكاني",
        requires=("فاعل_حي",),
        optional=("وجهة", "سبب"),
        rejects=("فاعل_جماد",),
        agent_property="حي",
        produces=("تغيير_موقع",),
    ),
    VerbFrame(
        verb="قال",
        root="ق و ل",
        event_type="إصدار_كلام",
        requires=("فاعل_ناطق",),
        optional=("مفعول_قول", "مخاطَب"),
        rejects=("فاعل_جماد",),
        agent_property="ناطق",
        produces=("كلام_مسموع",),
    ),
    VerbFrame(
        verb="علم",
        root="ع ل م",
        event_type="حصول_يقين",
        requires=("فاعل_مدرِك",),
        optional=("مفعول_معلوم",),
        rejects=("فاعل_جماد",),
        agent_property="مدرِك",
        produces=("يقين", "حكم_صادق"),
    ),
    VerbFrame(
        verb="فهم",
        root="ف ه م",
        event_type="إدراك_المعنى",
        requires=("فاعل_عاقل",),
        optional=("مفعول_مفهوم",),
        rejects=("فاعل_جماد",),
        agent_property="عاقل",
        produces=("فهم", "إدراك"),
    ),
    VerbFrame(
        verb="درس",
        root="د ر س",
        event_type="تكرار_قصد_الفهم",
        requires=("فاعل_عاقل",),
        optional=("مفعول_مدروس", "مكان", "غاية"),
        rejects=("فاعل_جماد",),
        agent_property="عاقل",
        produces=("معرفة", "مهارة"),
    ),
    VerbFrame(
        verb="اكتب",
        root="ك ت ب",
        event_type="أمر_بالكتابة",
        requires=("فاعل_قادر",),
        optional=("أداة", "مفعول_مكتوب", "مكان"),
        rejects=("فاعل_جماد",),
        agent_property="قادر",
        produces=("نص_مكتوب",),
    ),
)

# فهرس سريع: الفعل → الإطار
_FRAME_INDEX: dict[str, VerbFrame] = {f.verb: f for f in _VERB_FRAMES}

# تلميحات سطحية: صيغ متعددة ترجع لنفس الإطار
_SURFACE_HINTS: dict[str, str] = {
    # كتب
    "كتب":   "كتب",  "يكتب":  "كتب",  "كتبت": "كتب",
    "اكتب":  "اكتب",
    # قرأ
    "قرأ":   "قرأ",  "يقرأ":  "قرأ",  "قراءة": "قرأ",
    # خطب
    "خطب":   "خطب",  "يخطب":  "خطب",  "خطابة": "خطب",
    # رأى
    "رأى":   "رأى",  "يرى":   "رأى",  "رأيت":  "رأى",
    # أكل
    "أكل":   "أكل",  "يأكل":  "أكل",
    # ضرب
    "ضرب":   "ضرب",  "يضرب":  "ضرب",
    # ذهب
    "ذهب":   "ذهب",  "يذهب":  "ذهب",
    # قال
    "قال":   "قال",  "يقول":  "قال",
    # علم
    "علم":   "علم",  "يعلم":  "علم",
    # فهم
    "فهم":   "فهم",  "يفهم":  "فهم",
    # درس
    "درس":   "درس",  "يدرس":  "درس",  "دراسة": "درس",
}

# خاصية الفاعل → أنواع الكيانات التي تملكها
AGENT_PROPERTY_ENTITY_TYPES: dict[str, tuple[str, ...]] = {
    "قادر":    ("إنسان", "حيوان"),
    "مُبصِر":  ("إنسان", "حيوان"),
    "إنسان":   ("إنسان",),
    "حي":      ("إنسان", "حيوان"),
    "ناطق":    ("إنسان",),
    "مدرِك":   ("إنسان",),
    "عاقل":    ("إنسان",),
}

# ما يُعدّ جمادًا (لا يمكنه أن يكون فاعلًا قادرًا)
INANIMATE_ENTITY_TYPES: frozenset[str] = frozenset({
    "جماد", "أداة", "مادة", "ظاهرة", "مكان", "مصنوع",
})


# =========================================================
# 3. واجهة الاستعلام — Query API
# =========================================================

def get_verb_frame(verb_surface: str) -> Optional[VerbFrame]:
    """
    ابحث عن إطار الفعل بالصيغة السطحية.
    يحاول المطابقة المباشرة أولًا، ثم تلميحات السطح.
    """
    direct = _FRAME_INDEX.get(verb_surface)
    if direct:
        return direct
    canonical = _SURFACE_HINTS.get(verb_surface)
    if canonical:
        return _FRAME_INDEX.get(canonical)
    return None


def entity_satisfies_requirement(entity_type: str, requirement: str) -> bool:
    """
    هل يستوفي نوع الكيان المتطلبَ المُحدَّد؟
    مثال: entity_type="إنسان", requirement="فاعل_قادر" → True
    """
    if requirement in ("فاعل_جماد",):
        return entity_type in INANIMATE_ENTITY_TYPES
    # استخرج الخاصية من "فاعل_خاصية"
    if requirement.startswith("فاعل_"):
        prop = requirement[len("فاعل_"):]
        allowed_types = AGENT_PROPERTY_ENTITY_TYPES.get(prop, ())
        return entity_type in allowed_types
    return False


def is_rejection_applicable(entity_type: str, reject_condition: str) -> bool:
    """
    هل يُطبَّق شرط الرفض على نوع الكيان المُعطى؟
    مثال: entity_type="جماد", reject_condition="فاعل_جماد" → True
    """
    if reject_condition == "فاعل_جماد":
        return entity_type in INANIMATE_ENTITY_TYPES
    if reject_condition == "فاعل_حيوان":
        return entity_type == "حيوان"
    return False


def all_verb_frames() -> tuple[VerbFrame, ...]:
    """أعد كل إطارات الأفعال المُسجَّلة."""
    return _VERB_FRAMES
