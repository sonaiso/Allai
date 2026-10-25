"""
adam_properties.py
==================
خصائص آدم الأنطولوجية — الصفات الوجودية الثلاثة عشر

تُعرِّف هذا الوحدةُ الصفاتِ الأنطولوجية المؤسِّسة المستخدَمة
لتقييم قدرة الكيانات على الفعل في البوابات الرمزية.

الصفات الثلاث عشرة (بترتيبها المنطقي):
    وجود، قِدَم، بقاء، مخالفة للحوادث، قيام بالنفس، وحدانية،
    قدرة، إرادة، علم، حياة، سمع، بصر، كلام
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdamProperty:
    """صفة أنطولوجية — وحدة من وحدات تصنيف الكيانات وقدراتها."""
    name: str                       # الاسم الإنجليزي e.g. "wujud"
    arabic: str                     # الاسم العربي e.g. "وجود"
    description: str                # وصف مختصر
    required_by: tuple[str, ...]    # أنواع الكيانات التي تمتلك هذه الصفة


# =========================================================
# الصفات الثلاث عشرة — الثوابت المُسمَّاة
# =========================================================

WUJUD = AdamProperty(
    name="wujud",
    arabic="وجود",
    description="الكيان موجود في الواقع",
    required_by=("إنسان", "حيوان", "جماد", "ظاهرة", "مكان", "مادة", "سائل", "أداة",
                 "مصنوع", "أثاث", "بنية", "عضو"),
)

QIDAM = AdamProperty(
    name="qidam",
    arabic="قِدَم",
    description="الكيان سابق لا يُسبَق بعدم",
    required_by=(),
)

BAQA = AdamProperty(
    name="baqa",
    arabic="بقاء",
    description="الكيان يستمر في الوجود",
    required_by=(),
)

MUKHALAFA = AdamProperty(
    name="mukhalafa",
    arabic="مخالفة للحوادث",
    description="الكيان لا يشبه الكائنات الحادثة",
    required_by=(),
)

QIYAM = AdamProperty(
    name="qiyam",
    arabic="قيام بالنفس",
    description="الكيان قائم بذاته لا يحتاج إلى غيره",
    required_by=("إنسان", "حيوان"),
)

WAHDANIYA = AdamProperty(
    name="wahdaniya",
    arabic="وحدانية",
    description="الكيان فريد من نوعه",
    required_by=(),
)

QUDRA = AdamProperty(
    name="qudra",
    arabic="قدرة",
    description="الكيان قادر على إحداث أثر",
    required_by=("إنسان", "حيوان"),
)

IRADA = AdamProperty(
    name="irada",
    arabic="إرادة",
    description="الكيان يملك إرادة وقصدًا — الشرط الأساسي للفاعلية الاختيارية",
    required_by=("إنسان", "حيوان"),
)

ILM = AdamProperty(
    name="ilm",
    arabic="علم",
    description="الكيان يملك معرفة أو إدراكًا",
    required_by=("إنسان",),
)

HAYAT = AdamProperty(
    name="hayat",
    arabic="حياة",
    description="الكيان حي",
    required_by=("إنسان", "حيوان"),
)

SAMA = AdamProperty(
    name="sama",
    arabic="سمع",
    description="الكيان يملك قدرة السمع",
    required_by=("إنسان", "حيوان"),
)

BASAR = AdamProperty(
    name="basar",
    arabic="بصر",
    description="الكيان يملك قدرة الإبصار",
    required_by=("إنسان", "حيوان"),
)

KALAM = AdamProperty(
    name="kalam",
    arabic="كلام",
    description="الكيان يملك قدرة الكلام والتعبير",
    required_by=("إنسان",),
)


# =========================================================
# الفهرس الكامل — جميع الصفات بترتيبها
# =========================================================

ADAM_PROPERTIES: tuple[AdamProperty, ...] = (
    WUJUD, QIDAM, BAQA, MUKHALAFA, QIYAM, WAHDANIYA,
    QUDRA, IRADA, ILM, HAYAT, SAMA, BASAR, KALAM,
)

# أنواع الكيانات التي تملك صفة الإرادة (الفاعلية الاختيارية)
_VOLITIONAL_ENTITY_TYPES: frozenset[str] = frozenset({"إنسان", "حيوان"})


def applicable_properties(entity_type: str) -> tuple[AdamProperty, ...]:
    """
    يُعيد الصفات الأنطولوجية المنطبِقة على نوع الكيان المحدَّد.

    مثال:
        applicable_properties("إنسان") → جميع الصفات ذات required_by تشمل "إنسان"
        applicable_properties("جماد") → WUJUD فقط
    """
    return tuple(p for p in ADAM_PROPERTIES if entity_type in p.required_by)


def entity_can_act(entity_type: str) -> bool:
    """
    يُحدِّد إن كان الكيان يملك صفة الإرادة (القدرة على الفعل الاختياري).

    الكيانات الجامدة (جماد، مادة، سائل، أداة، أثاث، بنية، ظاهرة، مكان، مصنوع، عضو)
    لا تملك إرادة وبالتالي لا تصلح فاعلًا لأفعال إرادية.

    الإنسان والحيوان يملكان إرادة.
    """
    return entity_type in _VOLITIONAL_ENTITY_TYPES
