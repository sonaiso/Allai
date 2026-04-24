"""
concept_registry.py
====================
سجل المفاهيم — دعم وضع Concept-First

يُخزِّن المفاهيم المُعرَّفة مسبقًا ويُتيح:
    1. البحث بالاسم  (lookup_by_name)
    2. البحث بالجذر  (lookup_by_root)
    3. البحث بالمجال (lookup_by_domain)
    4. تسجيل مفهوم جديد في وقت التشغيل (register)

في وضع concept_first يُستخدم لتوليد حكم ابتدائي قبل تحليل النص،
ثم تُقارَن نتيجة التحليل اللغوي بهذا الحكم الابتدائي.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.model import ProofState


# =========================================================
# 1. نموذج المفهوم — Concept Model
# =========================================================

@dataclass
class ConceptRecord:
    """مفهوم كامل مُعرَّف مسبقًا."""
    name: str                               # اسم المفهوم بالعربية
    concept_type: str                       # فعل | اسم | حرف | صفة | مصدر
    semantic_core: str                      # اللبّ الدلالي
    root: Optional[str] = None              # الجذر الثلاثي
    domain: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)   # ما يستلزمه
    produces: List[str] = field(default_factory=list)        # ما ينتجه
    world_laws: List[str] = field(default_factory=list)      # قوانين مرتبطة
    confidence: float = 1.0


# =========================================================
# 2. السجل المُضمَّن — Embedded Registry
# =========================================================

_CONCEPT_REGISTRY: list[ConceptRecord] = [
    ConceptRecord(
        name="كتابة",
        concept_type="مصدر",
        semantic_core="إحداث نقش/ترميز على سطح",
        root="ك ت ب",
        domain=["معرفة", "تواصل"],
        roles=["كاتب", "مكتوب", "أداة_كتابة", "سطح"],
        prerequisites=["أداة_كتابة", "سطح_قابل_للكتابة"],
        produces=["نقش_رموز", "تسجيل_معلومة"],
        world_laws=["الكتابة تحتاج أداة", "الكتابة تنتج نصًا"],
        confidence=1.0,
    ),
    ConceptRecord(
        name="قراءة",
        concept_type="مصدر",
        semantic_core="استقبال رموز مكتوبة وتحويلها إلى معنى",
        root="ق ر أ",
        domain=["معرفة", "تواصل"],
        roles=["قارئ", "مقروء"],
        prerequisites=["نص_مكتوب", "معرفة_بالرموز"],
        produces=["فهم_معنى"],
        world_laws=["القراءة تحتاج نصًا"],
        confidence=1.0,
    ),
    ConceptRecord(
        name="علم",
        concept_type="اسم",
        semantic_core="حصول اليقين بالشيء",
        root="ع ل م",
        domain=["معرفة", "إدراك"],
        roles=["عالم", "معلوم"],
        prerequisites=["دليل", "إدراك"],
        produces=["يقين", "حكم_صادق"],
        world_laws=["العلم يستلزم دليلًا"],
        confidence=1.0,
    ),
    ConceptRecord(
        name="قلم",
        concept_type="اسم",
        semantic_core="أداة إحداث نقش/ترميز",
        root="ق ل م",
        domain=["تعليم", "تواصل"],
        roles=["أداة"],
        prerequisites=[],
        produces=["كتابة"],
        world_laws=["القلم أداة للكتابة"],
        confidence=1.0,
    ),
    ConceptRecord(
        name="دراسة",
        concept_type="مصدر",
        semantic_core="تكرار فهم وحفظ قصد اكتساب العلم",
        root="د ر س",
        domain=["معرفة"],
        roles=["دارس", "مدروس"],
        prerequisites=["وقت", "جهد"],
        produces=["معرفة", "مهارة"],
        world_laws=["الدراسة تفضي إلى العلم"],
        confidence=0.95,
    ),
    ConceptRecord(
        name="نار",
        concept_type="اسم",
        semantic_core="ظاهرة فيزيائية — أكسدة سريعة مع توليد حرارة وضوء",
        root=None,
        domain=["طبيعة", "فيزياء"],
        roles=["فاعل_إحراق"],
        prerequisites=["وقود", "أكسجين", "حرارة_اشتعال"],
        produces=["حرارة", "ضوء", "رماد"],
        world_laws=["النار تحرق المواد العضوية"],
        confidence=1.0,
    ),
    ConceptRecord(
        name="ماء",
        concept_type="اسم",
        semantic_core="سائل ضروري للحياة",
        root=None,
        domain=["طبيعة", "حياة"],
        roles=["وسيط", "مطفئ"],
        prerequisites=[],
        produces=["ري", "طفاء_نار"],
        world_laws=["الماء يسيل", "الماء يطفئ النار"],
        confidence=1.0,
    ),
    ConceptRecord(
        name="إسناد",
        concept_type="مصدر",
        semantic_core="إنتاج نسبة بين مسنَد ومسنَد إليه",
        root="س ن د",
        domain=["نحو_معرفي", "منطق"],
        roles=["مسنَد_إليه", "مسنَد"],
        prerequisites=["طرفان_قابلان_للنسبة"],
        produces=["حكم_أولي"],
        world_laws=["الإسناد يتطلب طرفين"],
        confidence=1.0,
    ),
]

# فهارس سريعة
_BY_NAME:   dict[str, ConceptRecord] = {c.name: c for c in _CONCEPT_REGISTRY}
_BY_ROOT:   dict[str, list[ConceptRecord]] = {}
_BY_DOMAIN: dict[str, list[ConceptRecord]] = {}

for _c in _CONCEPT_REGISTRY:
    if _c.root:
        _BY_ROOT.setdefault(_c.root, []).append(_c)
    for _d in _c.domain:
        _BY_DOMAIN.setdefault(_d, []).append(_c)


# =========================================================
# 3. واجهة السجل — Registry API
# =========================================================

def lookup_by_name(name: str) -> Optional[ConceptRecord]:
    """ابحث عن مفهوم باسمه."""
    return _BY_NAME.get(name)


def lookup_by_root(root: str) -> list[ConceptRecord]:
    """ابحث عن المفاهيم التي تشترك في جذر."""
    return list(_BY_ROOT.get(root, []))


def lookup_by_domain(domain: str) -> list[ConceptRecord]:
    """ابحث عن المفاهيم المنتمية إلى مجال."""
    return list(_BY_DOMAIN.get(domain, []))


def register(concept: ConceptRecord) -> None:
    """سجّل مفهومًا جديدًا في وقت التشغيل."""
    _CONCEPT_REGISTRY.append(concept)
    _BY_NAME[concept.name] = concept
    if concept.root:
        _BY_ROOT.setdefault(concept.root, []).append(concept)
    for domain in concept.domain:
        _BY_DOMAIN.setdefault(domain, []).append(concept)


def all_concepts() -> list[ConceptRecord]:
    """أعد قائمة بكل المفاهيم المُسجَّلة."""
    return list(_CONCEPT_REGISTRY)


# =========================================================
# 4. بوابة التشغيل — Gate Function
# =========================================================

def apply_concept_registry_gate(state: ProofState) -> ProofState:
    """
    بوابة سجل المفاهيم (مسار concept_first).

    تُطابق المفاهيم المُثرَاة بالسجل لتوليد حكم ابتدائي قبل التحقق اللغوي.

    المدخلات:
        state.conceptual_state["enriched_concepts"]

    المخرجات:
        state.conceptual_state["concept_registry_matches"]
        trace event: "concept_registry_gate"
    """
    enriched: list[dict] = state.conceptual_state.get("enriched_concepts", [])
    matches: list[dict[str, Any]] = []

    for concept_dict in enriched:
        token = concept_dict.get("token", "")
        root = concept_dict.get("root")

        # مطابقة بالاسم المباشر
        record = lookup_by_name(token) or lookup_by_name(token.lstrip("ال"))
        if record:
            matches.append(
                {"token": token, "match_type": "name", "concept": asdict(record)}
            )
            continue

        # مطابقة بالجذر
        if root:
            root_matches = lookup_by_root(root)
            if root_matches:
                matches.append(
                    {
                        "token": token,
                        "match_type": "root",
                        "concept": asdict(root_matches[0]),
                    }
                )

    state.conceptual_state["concept_registry_matches"] = matches

    # في وضع concept_first، إن وُجدت مطابقات، نولّد حكمًا ابتدائيًا
    preliminary_judgment: Optional[str] = None
    if state.processing_mode == "concept_first" and matches:
        known_concepts = [m["concept"]["name"] for m in matches]
        preliminary_judgment = f"concepts_identified:{','.join(known_concepts)}"

    state.conceptual_state["preliminary_judgment"] = preliminary_judgment

    state.add_trace(
        "concept_registry_gate",
        {
            "match_count": len(matches),
            "mode": state.processing_mode,
            "preliminary_judgment": preliminary_judgment,
        },
    )
    return state
