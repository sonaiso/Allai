"""
adam_properties.py
==================
خواص آدم — بذور المعرفة الأولى

يُعرِّف الخواص الوجودية الثلاثة عشر التي تُشكّل لبنة أساس كل معرفة:
    وجود، هوية، تمايز، حد، زمان، مكان، علاقة، فعل، أثر، قابلية، سبب، نتيجة، حكم

لكل خاصية:
    - name        : الاسم العربي
    - definition  : تعريف موجز
    - property_type: ontological | temporal | relational | causal | evaluative
    - implies     : قائمة بالخواص التي تستلزمها هذه الخاصية
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# =========================================================
# 1. نموذج الخاصية — Property Model
# =========================================================

@dataclass(frozen=True)
class AdamProperty:
    """خاصية وجودية أولى — بذرة من بذور المعرفة."""
    name: str
    definition: str
    property_type: str          # ontological | temporal | spatial | relational | causal | evaluative
    implies: tuple[str, ...] = field(default_factory=tuple)


# =========================================================
# 2. قائمة الخواص المُضمَّنة — Embedded Properties
# =========================================================

_ADAM_PROPERTIES: tuple[AdamProperty, ...] = (
    AdamProperty(
        name="وجود",
        definition="كون الشيء موجودًا في الواقع أو الذهن",
        property_type="ontological",
        implies=(),
    ),
    AdamProperty(
        name="هوية",
        definition="كون الشيء هو هو ولا يختلط بغيره",
        property_type="ontological",
        implies=("وجود", "تمايز"),
    ),
    AdamProperty(
        name="تمايز",
        definition="انفراد الشيء بخصائص تُميّزه عن سواه",
        property_type="ontological",
        implies=("وجود", "هوية"),
    ),
    AdamProperty(
        name="حد",
        definition="الحدود التي يقف عندها الشيء وتفصله عن غيره",
        property_type="ontological",
        implies=("وجود", "تمايز"),
    ),
    AdamProperty(
        name="زمان",
        definition="موقع الشيء أو الحدث في التسلسل الزمني",
        property_type="temporal",
        implies=("وجود",),
    ),
    AdamProperty(
        name="مكان",
        definition="موقع الشيء في الفضاء المادي أو المجازي",
        property_type="spatial",
        implies=("وجود", "حد"),
    ),
    AdamProperty(
        name="علاقة",
        definition="ارتباط بين شيئين أو أكثر بنسبة ما",
        property_type="relational",
        implies=("وجود", "تمايز"),
    ),
    AdamProperty(
        name="فعل",
        definition="صدور حركة أو تغيير من فاعل قادر",
        property_type="causal",
        implies=("وجود", "قابلية"),
    ),
    AdamProperty(
        name="أثر",
        definition="ما ينتج عن الفعل من تغيير في الواقع",
        property_type="causal",
        implies=("فعل", "سبب", "نتيجة"),
    ),
    AdamProperty(
        name="قابلية",
        definition="استعداد الشيء لاستقبال فعل بعينه أو إحداثه",
        property_type="ontological",
        implies=("وجود",),
    ),
    AdamProperty(
        name="سبب",
        definition="الشرط الكافي الذي يُوجب وقوع النتيجة",
        property_type="causal",
        implies=("فعل", "علاقة"),
    ),
    AdamProperty(
        name="نتيجة",
        definition="ما يترتب ضرورةً أو ترجيحًا على السبب",
        property_type="causal",
        implies=("سبب", "أثر"),
    ),
    AdamProperty(
        name="حكم",
        definition="إصدار تقييم على الشيء: صدق/كذب، جواز/امتناع، وجوب",
        property_type="evaluative",
        implies=("وجود", "علاقة"),
    ),
)


# فهرس سريع: الاسم → الخاصية
_PROPERTY_INDEX: dict[str, AdamProperty] = {p.name: p for p in _ADAM_PROPERTIES}

# تصنيف حسب النوع
_BY_TYPE: dict[str, list[AdamProperty]] = {}
for _p in _ADAM_PROPERTIES:
    _BY_TYPE.setdefault(_p.property_type, []).append(_p)

# تعيين الخواص المناسبة لكل نوع كيان
_ENTITY_TYPE_PROPERTIES: dict[str, tuple[str, ...]] = {
    "إنسان":   ("وجود", "هوية", "تمايز", "حد", "زمان", "مكان", "علاقة", "فعل", "قابلية"),
    "حيوان":   ("وجود", "هوية", "تمايز", "حد", "زمان", "مكان", "فعل", "قابلية"),
    "جماد":    ("وجود", "هوية", "تمايز", "حد", "مكان"),
    "أداة":    ("وجود", "هوية", "حد", "مكان", "قابلية"),
    "مادة":    ("وجود", "حد", "مكان", "قابلية"),
    "ظاهرة":   ("وجود", "زمان", "مكان", "فعل", "أثر", "سبب", "نتيجة"),
    "مكان":    ("وجود", "حد", "مكان", "علاقة"),
    "مصنوع":   ("وجود", "هوية", "حد", "مكان", "قابلية"),
    "مصدر":    ("وجود", "فعل", "أثر", "سبب", "نتيجة"),
    "اسم":     ("وجود", "هوية", "تمايز"),
}


# =========================================================
# 3. واجهة الاستعلام — Query API
# =========================================================

def get_property(name: str) -> Optional[AdamProperty]:
    """ابحث عن خاصية بالاسم."""
    return _PROPERTY_INDEX.get(name)


def get_properties_by_type(property_type: str) -> list[AdamProperty]:
    """أعد كل الخواص من نوع معين."""
    return list(_BY_TYPE.get(property_type, []))


def applicable_properties(entity_type: str) -> tuple[str, ...]:
    """
    أعد أسماء الخواص المناسبة لنوع كيان معين.
    إن لم يُعرَّف نوع الكيان، تُعاد الخواص الأساسية فقط.
    """
    return _ENTITY_TYPE_PROPERTIES.get(entity_type, ("وجود", "هوية", "تمايز", "حد"))


def all_properties() -> tuple[AdamProperty, ...]:
    """أعد جميع الخواص الأولى."""
    return _ADAM_PROPERTIES


def property_implies(name: str) -> tuple[str, ...]:
    """أعد الخواص التي تستلزمها الخاصية المُعطاة."""
    prop = _PROPERTY_INDEX.get(name)
    return prop.implies if prop else ()


def entity_can_act(entity_type: str) -> bool:
    """هل يملك هذا النوع من الكيانات خاصية 'فعل'؟"""
    return "فعل" in applicable_properties(entity_type)
