"""
lexical_enrichment_gate.py
==========================
بوابة الإثراء المعجمي

تحوّل:
    ProtoConcept (أثر مُسمَّى) + المعجم المُضمَّن
    ──────────────────────────────────────────────
    ConceptFull (عقدة معرفية مُثرَاة)

الطبقات:
    1. معجم الجذور  (ROOT_LEXICON)     — جذر + لب دلالي + مجال + أدوار
    2. معجم الأوزان (PATTERN_LEXICON)  — وزن + قانون دلالي + قيود
    3. معجم المشتقات (DERIVED_LEXICON) — صيغة + نوع + دور + الجذر الأصلي
    4. معجم العلاقات (RELATION_LEXICON) — أداة + نوع + مجال + قيد
    5. معجم الكيانات (ENTITY_LEXICON)   — كيان + نوع + قدرات + مجال
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.model import ProofState


# =========================================================
# 1. نماذج البيانات — Data Models
# =========================================================

@dataclass(frozen=True)
class RootEntry:
    """مدخل جذر — أصل الكلمة ولبّها الدلالي."""
    root: str                               # e.g. "ك ت ب"
    semantic_core: str                      # e.g. "إحداث نقش/ترميز"
    domain: tuple[str, ...]                 # e.g. ("معرفة", "تواصل")
    roles: tuple[str, ...]                  # e.g. ("فاعل", "مفعول", "أداة")


@dataclass(frozen=True)
class PatternEntry:
    """مدخل وزن — قانون توليد الصيغ الصرفية."""
    pattern: str                            # e.g. "فعّل"
    law: str                                # e.g. "تكثير / تعدية / تقوية"
    constraints: tuple[str, ...]            # e.g. ("يتطلب فاعلًا",)


@dataclass(frozen=True)
class DerivedEntry:
    """مدخل مشتق — صيغة مشتقة من جذر."""
    form: str                               # e.g. "كاتب"
    derived_type: str                       # e.g. "اسم_فاعل"
    role: str                               # e.g. "Initiator"
    root: str                               # e.g. "ك ت ب"
    semantic_hint: Optional[str] = None


@dataclass(frozen=True)
class RelationEntry:
    """مدخل أداة/علاقة — معنى حرف الجر أو الرابط."""
    particle: str                           # e.g. "في"
    relation_type: str                      # e.g. "Containment"
    domain: tuple[str, ...]                 # e.g. ("مكان", "مجال")
    constraint: str                         # e.g. "X داخل Y"


@dataclass(frozen=True)
class EntityEntry:
    """مدخل كيان — معرفة العالم لكيان بعينه."""
    entity: str                                         # e.g. "قلم"
    entity_type: str                                    # e.g. "أداة"
    affordances: tuple[str, ...]                        # e.g. ("كتابة",)
    domain: tuple[str, ...]                             # e.g. ("تعليم",)
    can_be_agent: bool = False                          # هل يمكنه أن يكون فاعلًا قادرًا؟
    possible_actions: tuple[str, ...] = ()              # الأفعال التي يمكنه القيام بها
    impossible_actions: tuple[str, ...] = ()            # الأفعال الممتنعة عليه
    entity_properties: tuple[str, ...] = ()             # خواص آدم المرتبطة بهذا الكيان
    shared_properties: tuple[str, ...] = ()             # خواص مشتركة (للمجاز)


@dataclass
class EnrichedConcept:
    """مفهوم مُثرَى — ناتج الإثراء المعجمي."""
    token: str
    proto_label: str
    root: Optional[str] = None
    semantic_core: Optional[str] = None
    domain: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    pattern: Optional[str] = None
    pattern_law: Optional[str] = None
    derived_type: Optional[str] = None
    relation_type: Optional[str] = None
    relation_constraint: Optional[str] = None
    entity_type: Optional[str] = None
    affordances: List[str] = field(default_factory=list)
    can_be_agent: bool = False
    possible_actions: List[str] = field(default_factory=list)
    impossible_actions: List[str] = field(default_factory=list)
    entity_properties: List[str] = field(default_factory=list)
    shared_properties: List[str] = field(default_factory=list)
    confidence: float = 0.5
    enrichment_source: str = "none"


# =========================================================
# 2. المعجمات المُضمَّنة — Embedded Lexicons
# =========================================================

ROOT_LEXICON: tuple[RootEntry, ...] = (
    RootEntry("ك ت ب",  "إحداث نقش/ترميز",       ("معرفة", "تواصل"),          ("فاعل", "مفعول", "أداة")),
    RootEntry("ق ر أ",  "استقبال رموز/معنى",      ("معرفة", "تواصل"),          ("فاعل", "مفعول")),
    RootEntry("ع ل م",  "حصول اليقين بالشيء",     ("معرفة", "إدراك"),          ("فاعل", "مفعول")),
    RootEntry("ف ه م",  "إدراك المعنى الداخلي",   ("إدراك",),                  ("فاعل", "مفعول")),
    RootEntry("ق و ل",  "إصدار كلام",              ("تواصل",),                  ("فاعل", "مفعول")),
    RootEntry("ذ ه ب",  "انتقال في المكان",        ("حركة",),                   ("فاعل", "وجهة")),
    RootEntry("ج ل س",  "استقرار بوضع معين",       ("حركة", "حال"),             ("فاعل", "مكان")),
    RootEntry("أ ك ل",  "إدخال غذاء وتحليله",     ("فيزياء", "حياة"),          ("فاعل", "مفعول")),
    RootEntry("ض ر ب",  "إحداث أثر بقوة",          ("فيزياء",),                 ("فاعل", "مفعول", "أداة")),
    RootEntry("ف ت ح",  "إزالة حاجز/إغلاق",       ("فيزياء", "فعل"),           ("فاعل", "مفعول")),
    RootEntry("ن ص ر",  "تقديم عون",               ("اجتماع",),                 ("فاعل", "مفعول")),
    RootEntry("د ر س",  "تكرار قصد الفهم والحفظ", ("معرفة",),                  ("فاعل", "مفعول")),
    RootEntry("ح م ل",  "رفع شيء ونقله",           ("فيزياء",),                 ("فاعل", "مفعول")),
    RootEntry("و ج د",  "كون الشيء موجودًا",       ("وجود",),                   ("فاعل",)),
    RootEntry("ب ن ي",  "تشييد/تأسيس",             ("فيزياء", "مجتمع"),         ("فاعل", "مفعول")),
)

# فهرس سريع: تطابق جزئي للسطح مع الجذر
_ROOT_SURFACE_HINTS: dict[str, str] = {
    "كتب":   "ك ت ب",  "كاتب":  "ك ت ب",  "مكتوب": "ك ت ب",  "يكتب": "ك ت ب",
    "كتابة": "ك ت ب",  "كتاب":  "ك ت ب",
    "قرأ":   "ق ر أ",  "يقرأ":  "ق ر أ",  "قراءة": "ق ر أ",
    "علم":   "ع ل م",  "عالم":  "ع ل م",  "معلوم": "ع ل م",  "يعلم": "ع ل م",
    "فهم":   "ف ه م",  "يفهم":  "ف ه م",
    "قال":   "ق و ل",  "يقول":  "ق و ل",  "قول":   "ق و ل",
    "ذهب":   "ذ ه ب",  "يذهب":  "ذ ه ب",
    "جلس":   "ج ل س",  "يجلس":  "ج ل س",
    "أكل":   "أ ك ل",  "يأكل":  "أ ك ل",
    "ضرب":   "ض ر ب",  "يضرب":  "ض ر ب",
    "فتح":   "ف ت ح",  "يفتح":  "ف ت ح",
    "نصر":   "ن ص ر",  "ينصر":  "ن ص ر",
    "درس":   "د ر س",  "يدرس":  "د ر س",  "دراسة": "د ر س",
    "حمل":   "ح م ل",  "يحمل":  "ح م ل",
    "وجد":   "و ج د",  "يوجد":  "و ج د",
    "بنى":   "ب ن ي",  "يبني":  "ب ن ي",
}

_ROOT_INDEX: dict[str, RootEntry] = {r.root: r for r in ROOT_LEXICON}


PATTERN_LEXICON: tuple[PatternEntry, ...] = (
    PatternEntry("فَعَلَ",  "فعل ثلاثي ماضي لازم/متعدٍّ",        ("قد يتعدى",)),
    PatternEntry("فَعَّلَ", "تكثير / تعدية / تقوية",              ("يتطلب فاعلًا", "قد يطلب مفعولًا")),
    PatternEntry("أَفْعَلَ", "تعدية / دخول في الشيء",             ("يتطلب فاعلًا", "قد يطلب مفعولًا")),
    PatternEntry("تَفَعَّلَ", "مطاوعة / تكلّف",                   ("يتطلب فاعلًا",)),
    PatternEntry("فَاعَلَ",  "مشاركة",                             ("يتطلب طرفين",)),
    PatternEntry("فَعِيل",   "صفة مشبهة / مبالغة",                ()),
    PatternEntry("فَاعِل",   "اسم فاعل — صاحب الفعل",             ("فاعل متصرف",)),
    PatternEntry("مَفْعُول", "اسم مفعول — محل الفعل",             ("مفعول متأثر",)),
    PatternEntry("فِعَال",   "مصدر / جمع تكسير",                  ()),
    PatternEntry("مِفْعَال", "اسم آلة",                            ("يدل على أداة",)),
    PatternEntry("فَعَّال",  "صيغة مبالغة — كثير الفعل",          ()),
    PatternEntry("فُعُول",   "جمع تكسير / مصدر",                  ()),
)

_PATTERN_INDEX: dict[str, PatternEntry] = {p.pattern: p for p in PATTERN_LEXICON}
_PATTERN_SURFACE_HINTS: dict[str, str] = {
    "كاتب": "فَاعِل", "قارئ": "فَاعِل", "عالم": "فَاعِل", "ضارب": "فَاعِل",
    "مكتوب": "مَفْعُول", "مضروب": "مَفْعُول", "مفهوم": "مَفْعُول",
    "كتابة": "فِعَال", "قراءة": "فِعَال",
    "قلم": "فَعَل",
}


DERIVED_LEXICON: tuple[DerivedEntry, ...] = (
    DerivedEntry("كاتب",   "اسم_فاعل",   "Initiator",      "ك ت ب",  "من يكتب"),
    DerivedEntry("مكتوب",  "اسم_مفعول",  "Patient",         "ك ت ب",  "ما كُتب"),
    DerivedEntry("كتابة",  "مصدر",        "AbstractProcess", "ك ت ب",  "فعل الكتابة"),
    DerivedEntry("كتاب",   "اسم",         "Artifact",        "ك ت ب",  "نتاج الكتابة"),
    DerivedEntry("مكتبة",  "اسم_مكان",   "Location",        "ك ت ب",  "مكان الكتب"),
    DerivedEntry("قارئ",   "اسم_فاعل",   "Initiator",       "ق ر أ",  "من يقرأ"),
    DerivedEntry("قراءة",  "مصدر",        "AbstractProcess", "ق ر أ",  "فعل القراءة"),
    DerivedEntry("عالم",   "اسم_فاعل",   "KnowledgeHolder", "ع ل م",  "حامل العلم"),
    DerivedEntry("دراسة",  "مصدر",        "AbstractProcess", "د ر س",  "فعل الدراسة"),
)

_DERIVED_INDEX: dict[str, DerivedEntry] = {d.form: d for d in DERIVED_LEXICON}


RELATION_LEXICON: tuple[RelationEntry, ...] = (
    RelationEntry("في",  "Containment",  ("مكان", "مجال", "زمان"), "X داخل Y"),
    RelationEntry("من",  "Origin",       ("مكان", "مصدر"),         "X صادر من Y"),
    RelationEntry("إلى", "Direction",    ("مكان", "وجهة"),         "X متجه نحو Y"),
    RelationEntry("على", "Surface",      ("مكان", "استعلاء"),      "X فوق Y"),
    RelationEntry("عن",  "Separation",   ("مكان", "سبب"),          "X بعيد/صادر عن Y"),
    RelationEntry("ب",   "Instrumentality", ("أداة", "مصاحبة"),   "X بواسطة Y"),
    RelationEntry("ل",   "Beneficiary",  ("مستفيد", "غرض"),        "X لأجل Y أو ملك Y"),
    RelationEntry("ك",   "Similitude",   ("تشبيه",),               "X مثل Y"),
    RelationEntry("مع",  "Accompaniment",("مصاحبة",),              "X بصحبة Y"),
    RelationEntry("و",   "Conjunction",  ("ربط",),                 "X وY معًا"),
    RelationEntry("ف",   "Consequence",  ("سببية",),               "X ثم حدث Y"),
    RelationEntry("ثم",  "Sequence",     ("تتابع",),               "X ثم Y بترتيب"),
)

_RELATION_INDEX: dict[str, RelationEntry] = {r.particle: r for r in RELATION_LEXICON}


ENTITY_LEXICON: tuple[EntityEntry, ...] = (
    EntityEntry(
        "قلم", "أداة", ("كتابة",), ("تعليم", "تواصل"),
        can_be_agent=False,
        possible_actions=("كتابة",),
        impossible_actions=("أكل", "مشي", "خطب", "قراءة"),
        entity_properties=("وجود", "هوية", "حد", "مكان", "قابلية"),
    ),
    EntityEntry(
        "كتاب", "مصنوع", ("قراءة", "تخزين_معلومة"), ("تعليم", "معرفة"),
        can_be_agent=False,
        possible_actions=(),
        impossible_actions=("أكل", "خطب"),
        entity_properties=("وجود", "هوية", "حد", "مكان"),
    ),
    EntityEntry(
        "ورقة", "مادة", ("كتابة", "طباعة"), ("تعليم",),
        can_be_agent=False,
        entity_properties=("وجود", "حد", "مكان", "قابلية"),
    ),
    EntityEntry(
        "طاولة", "أثاث", ("وضع_أشياء",), ("بيت", "مكتب"),
        can_be_agent=False,
        entity_properties=("وجود", "حد", "مكان"),
    ),
    EntityEntry(
        "كرسي", "أثاث", ("جلوس",), ("بيت", "مكتب"),
        can_be_agent=False,
        entity_properties=("وجود", "حد", "مكان"),
    ),
    EntityEntry(
        "باب", "بنية", ("فتح", "غلق", "عبور"), ("بيت", "مبنى"),
        can_be_agent=False,
        entity_properties=("وجود", "حد", "مكان", "قابلية"),
    ),
    EntityEntry(
        "ماء", "سائل", ("شرب", "غسل", "سقي"), ("طبيعة", "حياة"),
        can_be_agent=False,
        impossible_actions=("كتابة", "خطب"),
        entity_properties=("وجود", "حد", "مكان", "قابلية"),
    ),
    EntityEntry(
        "نار", "ظاهرة", ("إحراق", "إضاءة"), ("طبيعة", "خطر"),
        can_be_agent=False,
        impossible_actions=("كتابة", "خطب"),
        entity_properties=("وجود", "مكان", "فعل", "أثر", "سبب", "نتيجة"),
    ),
    EntityEntry(
        "بيت", "مكان", ("سكن", "إيواء"), ("مجتمع",),
        can_be_agent=False,
        entity_properties=("وجود", "حد", "مكان"),
    ),
    EntityEntry(
        "مدرسة", "مكان", ("تعليم", "دراسة"), ("تعليم",),
        can_be_agent=False,
        entity_properties=("وجود", "حد", "مكان"),
    ),
    EntityEntry(
        "يد", "عضو", ("حمل", "كتابة", "لمس"), ("جسد",),
        can_be_agent=False,
        entity_properties=("وجود", "حد", "مكان", "قابلية"),
    ),
    EntityEntry(
        "رجل", "إنسان", ("قيام", "مشي"), ("مجتمع",),
        can_be_agent=True,
        possible_actions=("كتابة", "قراءة", "خطب", "أكل", "ذهب"),
        impossible_actions=(),
        entity_properties=("وجود", "هوية", "تمايز", "حد", "زمان", "مكان", "علاقة", "فعل", "قابلية"),
    ),
    EntityEntry(
        "طعام", "مادة", ("أكل",), ("حياة",),
        can_be_agent=False,
        entity_properties=("وجود", "حد", "مكان", "قابلية"),
    ),
    EntityEntry(
        "هاتف", "أداة", ("تواصل", "اتصال"), ("تواصل", "تقنية"),
        can_be_agent=False,
        possible_actions=(),
        impossible_actions=("أكل", "خطب"),
        entity_properties=("وجود", "هوية", "حد", "مكان", "قابلية"),
    ),
    EntityEntry(
        "حاسوب", "أداة", ("كتابة", "حساب", "تواصل"), ("تقنية",),
        can_be_agent=False,
        impossible_actions=("أكل", "خطب"),
        entity_properties=("وجود", "هوية", "حد", "مكان", "قابلية"),
    ),
    # كيانات جديدة — مطلوبة للاختبارات الذهبية
    EntityEntry(
        "حجر", "جماد", (), ("طبيعة",),
        can_be_agent=False,
        possible_actions=(),
        impossible_actions=("كتابة", "خطب", "قراءة", "أكل", "قال"),
        entity_properties=("وجود", "هوية", "تمايز", "حد", "مكان"),
    ),
    EntityEntry(
        "زيد", "إنسان", ("كتابة", "قراءة", "خطب"), ("مجتمع",),
        can_be_agent=True,
        possible_actions=("كتابة", "قراءة", "خطب", "أكل", "ذهب", "قال"),
        impossible_actions=(),
        entity_properties=("وجود", "هوية", "تمايز", "حد", "زمان", "مكان", "علاقة", "فعل", "قابلية"),
    ),
    EntityEntry(
        "إنسان", "إنسان", ("كتابة", "قراءة", "خطب"), ("مجتمع",),
        can_be_agent=True,
        possible_actions=("كتابة", "قراءة", "خطب", "أكل", "ذهب", "قال"),
        impossible_actions=(),
        entity_properties=("وجود", "هوية", "تمايز", "حد", "زمان", "مكان", "علاقة", "فعل", "قابلية"),
    ),
    EntityEntry(
        "أسد", "حيوان", ("هجوم", "صيد"), ("طبيعة",),
        can_be_agent=True,
        possible_actions=("هجوم", "صيد", "مشي"),
        impossible_actions=("كتابة", "خطب"),
        entity_properties=("وجود", "هوية", "حد", "زمان", "مكان", "فعل", "قابلية"),
        shared_properties=("شجاعة", "قوة"),
    ),
    EntityEntry(
        "عين", "اسم_مشترك", (), (),
        can_be_agent=False,
        entity_properties=("وجود", "هوية", "تمايز"),
    ),
)

_ENTITY_INDEX: dict[str, EntityEntry] = {e.entity: e for e in ENTITY_LEXICON}


# =========================================================
# 3. منطق الإثراء — Enrichment Logic
# =========================================================

def _strip_article(token: str) -> str:
    """إزالة أداة التعريف 'ال' من أول الكلمة إن وُجدت."""
    if token.startswith("ال") and len(token) > 2:
        return token[2:]
    return token


# الحروف الواحدة التي تُكتَب ملتصقة بالكلمة التالية (حروف جر/عطف بادئة)
_SINGLE_CHAR_PARTICLES = {"ب", "ل", "ك", "و", "ف", "س"}


def _split_fused_token(token: str) -> tuple[str, str] | None:
    """
    إذا بدأت الكلمة بحرف جر/عطف ملتصق بأداة التعريف، تُعيد (الحرف، ما بعده).
    مثال: "بالقلم" → ("ب", "القلم")  ،  "للطالب" → ("ل", "الطالب")
    نشترط أن يكون ما بعد الحرف مبدوءًا بـ "ال" لتجنب تفكيك جذور حقيقية
    مثل: "كتب" (لا نُفككها رغم أن "ك" حرف جر).
    """
    if len(token) >= 3 and token[0] in _SINGLE_CHAR_PARTICLES:
        particle = token[0]
        rest = token[1:]
        if rest.startswith("ال"):
            return particle, rest
    return None


def _enrich_token(token: str, proto_label: str) -> list[EnrichedConcept]:
    """
    إثراء رمز واحد باستخدام المعجمات المُضمَّنة.

    يُعيد قائمة بمفهوم واحد أو اثنين في حالة الرمز المُدمَج (مثل: بالقلم).
    """
    # تحقق من الرمز المُدمَج أولًا (مثل: بالقلم → ب + القلم)
    fused = _split_fused_token(token)
    if fused:
        particle, rest = fused
        particle_concept = _enrich_single(particle, "particle", is_fused_particle=True)
        rest_concept = _enrich_single(rest, proto_label)
        # إن كانت العلاقة أداتية، أضف الأداة إلى المفهوم الثاني
        if particle_concept.relation_type == "Instrumentality":
            rest_concept.roles = list(rest_concept.roles) + ["instrument"]
        return [particle_concept, rest_concept]

    return [_enrich_single(token, proto_label)]


def _enrich_single(token: str, proto_label: str, is_fused_particle: bool = False) -> EnrichedConcept:
    """إثراء رمز واحد بسيط."""
    bare = _strip_article(token)

    concept = EnrichedConcept(token=token, proto_label=proto_label, confidence=0.5)

    # 1. البحث في معجم العلاقات (الأدوات) — مهم أن يكون أولًا للحروف
    rel_entry = _RELATION_INDEX.get(bare) or _RELATION_INDEX.get(token)
    if rel_entry:
        concept.relation_type = rel_entry.relation_type
        concept.relation_constraint = rel_entry.constraint
        concept.domain = list(rel_entry.domain)
        concept.enrichment_source = "relation_lexicon"
        concept.confidence = 0.95
        return concept

    # 2. البحث في معجم الكيانات
    entity = _ENTITY_INDEX.get(bare) or _ENTITY_INDEX.get(token)
    if entity:
        concept.entity_type = entity.entity_type
        concept.affordances = list(entity.affordances)
        concept.domain = list(entity.domain)
        concept.can_be_agent = entity.can_be_agent
        concept.possible_actions = list(entity.possible_actions)
        concept.impossible_actions = list(entity.impossible_actions)
        concept.entity_properties = list(entity.entity_properties)
        concept.shared_properties = list(entity.shared_properties)
        concept.enrichment_source = "entity_lexicon"
        concept.confidence = 0.85
        return concept

    # 3. البحث في معجم المشتقات
    derived = _DERIVED_INDEX.get(bare) or _DERIVED_INDEX.get(token)
    if derived:
        concept.derived_type = derived.derived_type
        concept.roles = [derived.role]
        concept.root = derived.root
        root_entry = _ROOT_INDEX.get(derived.root)
        if root_entry:
            concept.semantic_core = root_entry.semantic_core
            concept.domain = list(root_entry.domain)
        concept.enrichment_source = "derived_lexicon"
        concept.confidence = 0.9
        return concept

    # 4. البحث في معجم الجذور (بواسطة التلميحات السطحية)
    root_key = _ROOT_SURFACE_HINTS.get(bare) or _ROOT_SURFACE_HINTS.get(token)
    if root_key:
        root_entry = _ROOT_INDEX.get(root_key)
        if root_entry:
            concept.root = root_entry.root
            concept.semantic_core = root_entry.semantic_core
            concept.domain = list(root_entry.domain)
            concept.roles = list(root_entry.roles)
            concept.enrichment_source = "root_lexicon"
            concept.confidence = 0.85

    # 5. البحث في معجم الأوزان
    pattern_key = _PATTERN_SURFACE_HINTS.get(bare) or _PATTERN_SURFACE_HINTS.get(token)
    if pattern_key:
        pattern_entry = _PATTERN_INDEX.get(pattern_key)
        if pattern_entry:
            concept.pattern = pattern_entry.pattern
            concept.pattern_law = pattern_entry.law
            concept.enrichment_source = concept.enrichment_source or "pattern_lexicon"
            concept.confidence = max(concept.confidence, 0.75)

    return concept


# =========================================================
# 4. البوابة الرئيسية — Main Gate
# =========================================================

def apply_lexical_enrichment_gate(state: ProofState) -> ProofState:
    """
    بوابة الإثراء المعجمي.

    المدخلات:
        state.conceptual_state["pre_language"]["proto_concepts"]
        state.symbolic_state["minimal_complete_encoding"]["token_units"]  (إن وُجد)

    المخرجات:
        state.conceptual_state["enriched_concepts"]
        trace event: "lexical_enrichment_gate"
    """
    proto_concepts: list[dict] = (
        state.conceptual_state.get("pre_language", {}).get("proto_concepts", [])
    )

    # نجمع الرموز الفريدة من التحليل الأدنى إن وُجد، وإلا من الإدخال
    token_units: list[dict] = (
        state.symbolic_state
        .get("minimal_complete_encoding", {})
        .get("token_units", [])
    )

    # نبني خريطة token_index → token للوصول السريع
    token_map: dict[int, str] = {}
    for unit in token_units:
        idx = unit.get("token_index", -1)
        if idx >= 0 and idx not in token_map:
            token_map[idx] = unit.get("token", "")

    # إن لم تكن هناك وحدات رمزية، نستخدم الكلمات من النص الفعّال
    if not token_map:
        words = [w for w in state.effective_text().split() if w]
        token_map = {i: w for i, w in enumerate(words)}

    enriched: list[dict[str, Any]] = []
    seen_tokens: set[str] = set()

    for proto in proto_concepts:
        anchor = proto.get("anchor_token_index", 0)
        token = token_map.get(anchor, "")
        if not token or token in seen_tokens:
            continue
        seen_tokens.add(token)

        concepts = _enrich_token(token, proto.get("label", "unknown"))
        enriched.extend(asdict(c) for c in concepts)

    # أضف الرموز التي لم تُغطَّ بالمفاهيم البدئية (من token_map مباشرة)
    for token in token_map.values():
        if token and token not in seen_tokens:
            seen_tokens.add(token)
            concepts = _enrich_token(token, "lexical_anchor")
            enriched.extend(asdict(c) for c in concepts)

    enriched_count = len(enriched)
    rooted_count   = sum(1 for c in enriched if c.get("root"))
    related_count  = sum(1 for c in enriched if c.get("relation_type"))

    state.conceptual_state["enriched_concepts"] = enriched
    state.enriched_concepts = enriched

    state.add_trace(
        "lexical_enrichment_gate",
        {
            "enriched_count": enriched_count,
            "rooted_count": rooted_count,
            "related_count": related_count,
        },
    )
    return state


def has_root_surface_hint(token: str) -> bool:
    """
    واجهة عامة: هل الرمز مُدرج كتلميح سطحي لجذر معروف؟
    تُستخدم بدلًا من استيراد المتغير الخاص `_ROOT_SURFACE_HINTS`.
    """
    return token in _ROOT_SURFACE_HINTS
