"""
lexicon_layer.py
================
طبقة المعجم: نماذج البيانات ومحرك القواعد (rule engine)

الهيكل:
    RawLexicon → BuiltInventory + InflectedInventory
                      ↓
                Operators (حركات + زوائد + موقع + وزن + سياق)
                      ↓
                ExceptionClasses
                      ↓
                FinalAnalysis

يتوافق هذا الملف مع مخطط قاعدة البيانات:
    db/schema/sql/002_lexicon_layer_schema.sql
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from core.model import ProofState


# =========================================================
# 1. ENUMERATIONS — تعدادات الطبقة المعجمية
# =========================================================

class EntryType(str, Enum):
    TOOL                  = "tool"
    PRONOUN               = "pronoun"
    DEMONSTRATIVE         = "demonstrative"
    RELATIVE              = "relative"
    CONDITIONAL           = "conditional"
    INTERROGATIVE         = "interrogative"
    VERBAL_NOUN           = "verbal_noun"
    PAST_VERB_BARE        = "past_verb_bare"
    PAST_VERB_AUGMENTED   = "past_verb_augmented"
    IMPERATIVE_VERB       = "imperative_verb"
    FROZEN_NOUN           = "frozen_noun"
    TRILATERAL_ROOT       = "trilateral_root"
    QUADRILATERAL_ROOT    = "quadrilateral_root"
    PRESENT_VERB          = "present_verb"
    DERIVED_NOUN          = "derived_noun"


class InflectionClass(str, Enum):
    MABNI         = "mabni"           # مبني
    MURAB_FULL    = "murab_full"      # معرب كامل
    MURAB_PARTIAL = "murab_partial"   # معرب ناقص (ممنوع من الصرف)


class GrammaticalGender(str, Enum):
    MASCULINE = "masculine"
    FEMININE  = "feminine"
    COMMON    = "common"


class GrammaticalNumber(str, Enum):
    SINGULAR             = "singular"
    DUAL                 = "dual"
    SOUND_MASC_PLURAL    = "sound_masculine_plural"
    SOUND_FEM_PLURAL     = "sound_feminine_plural"
    BROKEN_PLURAL        = "broken_plural"


class CaseRole(str, Enum):
    RAF  = "raf"
    NASB = "nasb"
    JARR = "jarr"
    JAZM = "jazm"
    BINA = "bina"
    NONE = "none"


class CaseMarkerKind(str, Enum):
    HARAKA            = "haraka"
    LETTER_WAW        = "letter_waw"
    LETTER_ALIF       = "letter_alif"
    LETTER_YA         = "letter_ya"
    LETTER_NUN_THABUT = "letter_nun_thabut"
    LETTER_NUN_HADHF  = "letter_nun_hadhf"
    NONE              = "none"


class Tense(str, Enum):
    PAST      = "past"
    PRESENT   = "present"
    IMPERATIVE = "imperative"
    NONE      = "none"


class Transitivity(str, Enum):
    TRANSITIVE   = "transitive"
    INTRANSITIVE = "intransitive"
    BOTH         = "both"
    NONE         = "none"


class Definiteness(str, Enum):
    DEFINITE    = "definite"
    INDEFINITE  = "indefinite"
    PROPER_NOUN = "proper_noun"
    NONE        = "none"


class ExceptionClass(str, Enum):
    PRONOUN                = "pronoun"
    DEMONSTRATIVE_RELATIVE = "demonstrative_relative"
    DIPTOTE                = "diptote"
    FIVE_NOUNS             = "five_nouns"
    DUAL                   = "dual"
    SOUND_MASC_PLURAL      = "sound_masc_plural"
    FIVE_VERBS             = "five_verbs"
    DEFECTIVE_HAMZA_DOUBLED = "defective_hamza_doubled"
    DIMINUTIVE_NISBA       = "diminutive_nisba"
    BROKEN_PLURAL          = "broken_plural"
    MASDAR                 = "masdar"
    PAUSE_SCRIPT           = "pause_script"


class OperatorType(str, Enum):
    HARAKA   = "haraka"
    ZAWAID   = "zawaid"
    POSITION = "position"
    PATTERN  = "pattern"
    CONTEXT  = "context"


# =========================================================
# 2. DATA MODELS — نماذج البيانات
# =========================================================

@dataclass(frozen=True)
class LexiconEntry:
    """مدخل معجمي خام — طبقة الاستيراد الأولى."""
    code: str
    arabic_form: str
    entry_type: EntryType
    inflection_class: InflectionClass
    gender_default: GrammaticalGender = GrammaticalGender.COMMON
    semantic_class: Optional[str] = None
    transliteration: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class BuiltEntry:
    """مبنيّ — أدوات / ضمائر / أسماء إشارة / موصولات / شرط / استفهام ..."""
    entry_code: str
    sub_type: EntryType
    fixed_form: str
    attachment_type: str = "free"       # free | attached | both
    reference_function: Optional[str] = None
    syntactic_slot: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class InflectedEntry:
    """معرب خام — أسماء جامدة / جذور / مضارع / مشتقات."""
    entry_code: str
    bare_form: str
    root_code: Optional[str] = None
    pattern_code: Optional[str] = None
    radical_count: Optional[int] = None
    gender_default: GrammaticalGender = GrammaticalGender.MASCULINE
    accepts_tanween: bool = True
    notes: Optional[str] = None


@dataclass(frozen=True)
class ExceptionClassRecord:
    """وحدة خاصة — صنف استثناء إعرابي / صرفي."""
    code: str
    name_ar: str
    exception_type: ExceptionClass
    behavior_desc: str
    rule_tag: Optional[str] = None
    complexity_score: float = 0.5


@dataclass(frozen=True)
class Operator:
    """مشغّل — حركة / زيادة / موقع / وزن / سياق."""
    code: str
    name_ar: str
    operator_type: OperatorType
    applies_to: tuple[EntryType, ...]
    generates: tuple[str, ...]
    rule_formula: Optional[str] = None
    priority: int = 10
    haraka_code: Optional[str] = None
    augmentation_code: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class OperatorResult:
    """نتيجة تطبيق مشغّل على مدخل معجمي."""
    entry_code: str
    operator_code: str
    definiteness: Definiteness
    gender: GrammaticalGender
    number: GrammaticalNumber
    case_role: CaseRole
    case_marker_kind: CaseMarkerKind
    tense: Tense
    transitivity: Transitivity
    surface_form: str
    confidence: float = 1.0


@dataclass(frozen=True)
class FinalAnalysisRecord:
    """التحليل النهائي الموحّد لمدخل معجمي."""
    entry_code: str
    entry_type: EntryType
    final_surface_form: str
    case_marker_kind: CaseMarkerKind
    bina_or_irab: str                   # "bina" | "irab"
    definiteness: Definiteness
    gender: GrammaticalGender
    number: GrammaticalNumber
    case_role: CaseRole
    tense: Tense
    transitivity: Transitivity
    exception_types: tuple[ExceptionClass, ...] = field(default_factory=tuple)
    pause_form: Optional[str] = None
    pattern_code: Optional[str] = None
    augmentation_code: Optional[str] = None
    haraka_code: Optional[str] = None
    confidence: float = 1.0
    analysis_trace: dict = field(default_factory=dict)


# =========================================================
# 3. EXCEPTION CLASS REGISTRY — سجلّ الوحدات الخاصة
#    (الاثنا عشر صنفًا الواردة في المواصفة)
# =========================================================

EXCEPTION_CLASS_REGISTRY: tuple[ExceptionClassRecord, ...] = (
    ExceptionClassRecord(
        code="EXC_PRONOUN",
        name_ar="الضمائر",
        exception_type=ExceptionClass.PRONOUN,
        behavior_desc="مبنية، متصلة أو منفصلة، لا تُعرب بالحركات",
        rule_tag="is_pronoun AND inflection_class=mabni",
        complexity_score=0.3,
    ),
    ExceptionClassRecord(
        code="EXC_DEMO_REL",
        name_ar="أسماء الإشارة والموصول والشرط والاستفهام",
        exception_type=ExceptionClass.DEMONSTRATIVE_RELATIVE,
        behavior_desc="أسماء مبنية ذات وظيفة ربط أو إحالة",
        rule_tag="entry_type IN (demonstrative, relative, conditional, interrogative)",
        complexity_score=0.35,
    ),
    ExceptionClassRecord(
        code="EXC_DIPTOTE",
        name_ar="الممنوع من الصرف",
        exception_type=ExceptionClass.DIPTOTE,
        behavior_desc="معرب ناقص العلامات: لا يُنوَّن، يُجرّ بالفتحة",
        rule_tag="inflection_class=murab_partial",
        complexity_score=0.55,
    ),
    ExceptionClassRecord(
        code="EXC_FIVE_NOUNS",
        name_ar="الأسماء الخمسة",
        exception_type=ExceptionClass.FIVE_NOUNS,
        behavior_desc="إعراب بالحروف: أب أخ حم فو ذو",
        rule_tag="arabic_form IN (أب, أخ, حم, فو, ذو) AND case_marker_kind=letter",
        complexity_score=0.7,
    ),
    ExceptionClassRecord(
        code="EXC_DUAL",
        name_ar="المثنى",
        exception_type=ExceptionClass.DUAL,
        behavior_desc="إعراب بالألف رفعًا وبالياء نصبًا وجرًا",
        rule_tag="number=dual AND case_marker_kind IN (letter_alif, letter_ya)",
        complexity_score=0.5,
    ),
    ExceptionClassRecord(
        code="EXC_SMP",
        name_ar="جمع المذكر السالم",
        exception_type=ExceptionClass.SOUND_MASC_PLURAL,
        behavior_desc="إعراب بالواو رفعًا وبالياء نصبًا وجرًا",
        rule_tag="number=sound_masculine_plural AND case_marker_kind IN (letter_waw, letter_ya)",
        complexity_score=0.5,
    ),
    ExceptionClassRecord(
        code="EXC_FIVE_VERBS",
        name_ar="الأفعال الخمسة",
        exception_type=ExceptionClass.FIVE_VERBS,
        behavior_desc="إعرابها بثبوت النون أو حذفها",
        rule_tag="entry_type=present_verb AND person IN (2m_sg, 2f_sg, 2m_pl, 3f_pl, 3m_dual)",
        complexity_score=0.65,
    ),
    ExceptionClassRecord(
        code="EXC_DEFECTIVE",
        name_ar="المعتل والمهموز والمضعف",
        exception_type=ExceptionClass.DEFECTIVE_HAMZA_DOUBLED,
        behavior_desc="تغيّر سطحي بالإعلال أو الإبدال أو الإدغام",
        rule_tag="root_has_weak_letter OR root_has_hamza OR root_has_gemination",
        complexity_score=0.8,
    ),
    ExceptionClassRecord(
        code="EXC_DIM_NISBA",
        name_ar="التصغير والنسب",
        exception_type=ExceptionClass.DIMINUTIVE_NISBA,
        behavior_desc="تحويل وزني خاص: فُعَيْل للتصغير، فَعِيّ للنسب",
        rule_tag="derivation_type IN (diminutive, nisba)",
        complexity_score=0.6,
    ),
    ExceptionClassRecord(
        code="EXC_BROKEN_PL",
        name_ar="جمع التكسير",
        exception_type=ExceptionClass.BROKEN_PLURAL,
        behavior_desc="تغيير داخلي في البنية الصوتية، لا مجرد لاحقة",
        rule_tag="number=broken_plural AND internal_structural_change=true",
        complexity_score=0.75,
    ),
    ExceptionClassRecord(
        code="EXC_MASDAR",
        name_ar="المصادر",
        exception_type=ExceptionClass.MASDAR,
        behavior_desc="منها السماعي ومنها القياسي؛ لا ينطبق عليها وزن واحد",
        rule_tag="pattern_family=masdar",
        complexity_score=0.6,
    ),
    ExceptionClassRecord(
        code="EXC_PAUSE_SCRIPT",
        name_ar="الوقف والابتداء والرسم",
        exception_type=ExceptionClass.PAUSE_SCRIPT,
        behavior_desc="تعديلات الطبقة السطحية النهائية عند الوقف أو الابتداء",
        rule_tag="surface_layer=pause OR surface_layer=script",
        complexity_score=0.4,
    ),
)

# فهرس سريع: exception_type → ExceptionClassRecord
EXCEPTION_CLASS_INDEX: dict[ExceptionClass, ExceptionClassRecord] = {
    rec.exception_type: rec for rec in EXCEPTION_CLASS_REGISTRY
}


# =========================================================
# 4. BUILT INVENTORY DEFAULTS — مخزون المبنيات الافتراضي
# =========================================================

#: المبنيات الثابتة الأكثر شيوعًا (عيّنة للاختبار والبذر)
BUILT_INVENTORY_DEFAULTS: tuple[LexiconEntry, ...] = (
    # ---- أدوات ----
    LexiconEntry("TOOL_FI",    "في",   EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف جر"),
    LexiconEntry("TOOL_MIN",   "من",   EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف جر"),
    LexiconEntry("TOOL_ILA",   "إلى",  EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف جر"),
    LexiconEntry("TOOL_ALA",   "على",  EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف جر"),
    LexiconEntry("TOOL_AN",    "عن",   EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف جر"),
    LexiconEntry("TOOL_BI",    "ب",    EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف جر"),
    LexiconEntry("TOOL_LI",    "ل",    EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف جر"),
    LexiconEntry("TOOL_KA",    "ك",    EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف جر"),
    LexiconEntry("TOOL_WA",    "و",    EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف عطف"),
    LexiconEntry("TOOL_FA",    "ف",    EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف عطف/سببية"),
    LexiconEntry("TOOL_THUM",  "ثم",   EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف عطف"),
    LexiconEntry("TOOL_AW",    "أو",   EntryType.TOOL,   InflectionClass.MABNI,  notes="حرف عطف"),
    LexiconEntry("TOOL_LA",    "لا",   EntryType.TOOL,   InflectionClass.MABNI,  notes="نفي/نهي"),
    LexiconEntry("TOOL_MAA",   "ما",   EntryType.TOOL,   InflectionClass.MABNI,  notes="نفي/موصول"),
    LexiconEntry("TOOL_INNA",  "إن",   EntryType.TOOL,   InflectionClass.MABNI,  notes="شرطية/مخففة"),
    # ---- ضمائر ----
    LexiconEntry("PRON_ANA",   "أنا",  EntryType.PRONOUN, InflectionClass.MABNI, GrammaticalGender.COMMON,  notes="ضمير منفصل مرفوع"),
    LexiconEntry("PRON_ANTA",  "أنت",  EntryType.PRONOUN, InflectionClass.MABNI, GrammaticalGender.MASCULINE, notes="ضمير منفصل مرفوع"),
    LexiconEntry("PRON_ANTI",  "أنتِ", EntryType.PRONOUN, InflectionClass.MABNI, GrammaticalGender.FEMININE,  notes="ضمير منفصل مرفوع"),
    LexiconEntry("PRON_HUW",   "هو",   EntryType.PRONOUN, InflectionClass.MABNI, GrammaticalGender.MASCULINE, notes="ضمير منفصل مرفوع"),
    LexiconEntry("PRON_HIY",   "هي",   EntryType.PRONOUN, InflectionClass.MABNI, GrammaticalGender.FEMININE,  notes="ضمير منفصل مرفوع"),
    LexiconEntry("PRON_NAHNU", "نحن",  EntryType.PRONOUN, InflectionClass.MABNI, GrammaticalGender.COMMON,   notes="ضمير منفصل مرفوع"),
    # ---- أسماء إشارة ----
    LexiconEntry("DEM_HATHA",  "هذا",  EntryType.DEMONSTRATIVE, InflectionClass.MABNI, GrammaticalGender.MASCULINE, notes="قريب مفرد مذكر"),
    LexiconEntry("DEM_HATHIH", "هذه",  EntryType.DEMONSTRATIVE, InflectionClass.MABNI, GrammaticalGender.FEMININE,  notes="قريب مفرد مؤنث"),
    LexiconEntry("DEM_THALIK", "ذلك",  EntryType.DEMONSTRATIVE, InflectionClass.MABNI, GrammaticalGender.MASCULINE, notes="بعيد مفرد مذكر"),
    LexiconEntry("DEM_TILK",   "تلك",  EntryType.DEMONSTRATIVE, InflectionClass.MABNI, GrammaticalGender.FEMININE,  notes="بعيد مفرد مؤنث"),
    # ---- موصولات ----
    LexiconEntry("REL_ALLATHIY",  "الذي",  EntryType.RELATIVE, InflectionClass.MABNI, GrammaticalGender.MASCULINE, notes="موصول مفرد مذكر"),
    LexiconEntry("REL_ALLATIY",   "التي",  EntryType.RELATIVE, InflectionClass.MABNI, GrammaticalGender.FEMININE,  notes="موصول مفرد مؤنث"),
    # ---- أسماء استفهام ----
    LexiconEntry("INTG_MAN",   "من",   EntryType.INTERROGATIVE, InflectionClass.MABNI, notes="استفهام عن عاقل"),
    LexiconEntry("INTG_MA",    "ما",   EntryType.INTERROGATIVE, InflectionClass.MABNI, notes="استفهام عن غير عاقل"),
    LexiconEntry("INTG_KAYF",  "كيف", EntryType.INTERROGATIVE, InflectionClass.MABNI, notes="استفهام عن الحال"),
    LexiconEntry("INTG_AYNA",  "أين", EntryType.INTERROGATIVE, InflectionClass.MABNI, notes="استفهام عن المكان"),
    LexiconEntry("INTG_MATA",  "متى", EntryType.INTERROGATIVE, InflectionClass.MABNI, notes="استفهام عن الزمان"),
)


# =========================================================
# 5. RULE ENGINE — محرك القواعد
# =========================================================

def _resolve_exception_types(
    entry: LexiconEntry,
    exception_map: dict[str, tuple[ExceptionClass, ...]],
) -> tuple[ExceptionClass, ...]:
    """تحديد أصناف الاستثناء لمدخل معجمي."""
    from_map = exception_map.get(entry.code, ())
    inferred: list[ExceptionClass] = list(from_map)

    # استنتاج تلقائي بناءً على نوع المدخل
    if entry.entry_type == EntryType.PRONOUN:
        if ExceptionClass.PRONOUN not in inferred:
            inferred.append(ExceptionClass.PRONOUN)
    if entry.entry_type in (
        EntryType.DEMONSTRATIVE,
        EntryType.RELATIVE,
        EntryType.CONDITIONAL,
        EntryType.INTERROGATIVE,
    ):
        if ExceptionClass.DEMONSTRATIVE_RELATIVE not in inferred:
            inferred.append(ExceptionClass.DEMONSTRATIVE_RELATIVE)
    if entry.inflection_class == InflectionClass.MURAB_PARTIAL:
        if ExceptionClass.DIPTOTE not in inferred:
            inferred.append(ExceptionClass.DIPTOTE)

    return tuple(inferred)


def _resolve_case_marker_kind(
    case_role: CaseRole,
    number: GrammaticalNumber,
    exception_types: tuple[ExceptionClass, ...],
) -> CaseMarkerKind:
    """تحديد نوع علامة الإعراب بناءً على العدد والصنف وحالة الإعراب."""
    if ExceptionClass.FIVE_NOUNS in exception_types:
        if case_role == CaseRole.RAF:
            return CaseMarkerKind.LETTER_WAW
        if case_role in (CaseRole.NASB, CaseRole.JARR):
            return CaseMarkerKind.LETTER_ALIF

    if number == GrammaticalNumber.DUAL or ExceptionClass.DUAL in exception_types:
        if case_role == CaseRole.RAF:
            return CaseMarkerKind.LETTER_ALIF
        if case_role in (CaseRole.NASB, CaseRole.JARR):
            return CaseMarkerKind.LETTER_YA

    if (
        number == GrammaticalNumber.SOUND_MASC_PLURAL
        or ExceptionClass.SOUND_MASC_PLURAL in exception_types
    ):
        if case_role == CaseRole.RAF:
            return CaseMarkerKind.LETTER_WAW
        if case_role in (CaseRole.NASB, CaseRole.JARR):
            return CaseMarkerKind.LETTER_YA

    if ExceptionClass.FIVE_VERBS in exception_types:
        if case_role == CaseRole.RAF:
            return CaseMarkerKind.LETTER_NUN_THABUT
        if case_role in (CaseRole.NASB, CaseRole.JAZM):
            return CaseMarkerKind.LETTER_NUN_HADHF

    # الأصل: حركة
    if case_role == CaseRole.BINA:
        return CaseMarkerKind.NONE
    return CaseMarkerKind.HARAKA


def _resolve_bina_or_irab(inflection_class: InflectionClass) -> str:
    """تحديد ما إذا كان المدخل مبنيًا أو معربًا."""
    return "bina" if inflection_class == InflectionClass.MABNI else "irab"


def apply_lexicon_layer(
    state: ProofState,
    entries: tuple[LexiconEntry, ...],
    exception_map: Optional[dict[str, tuple[ExceptionClass, ...]]] = None,
) -> ProofState:
    """
    تطبيق طبقة المعجم على ProofState.

    المعاملات:
        state         — الحالة الحالية للبرهان
        entries       — المدخلات المعجمية (من المبنيات والمعربات)
        exception_map — قاموس {entry_code: tuple[ExceptionClass, ...]}
                        للأصناف الاستثنائية المُسبقة الإسناد

    الناتج:
        ProofState مُحدَّثة تحتوي على:
            conceptual_state["lexicon_layer"]["entries"]
            conceptual_state["lexicon_layer"]["exception_registry"]
            trace_chain["lexicon_layer"]
    """
    if exception_map is None:
        exception_map = {}

    analysed: list[dict] = []

    for entry in entries:
        exc_types = _resolve_exception_types(entry, exception_map)

        # لكل مدخل نُصدر تحليلًا نموذجيًا (حالة الرفع، مفرد، نكرة)
        case_role = CaseRole.BINA if entry.inflection_class == InflectionClass.MABNI else CaseRole.RAF
        number    = GrammaticalNumber.SINGULAR
        definiteness = Definiteness.INDEFINITE if entry.inflection_class != InflectionClass.MABNI else Definiteness.NONE

        case_marker = _resolve_case_marker_kind(case_role, number, exc_types)
        bina_irab   = _resolve_bina_or_irab(entry.inflection_class)

        record = FinalAnalysisRecord(
            entry_code         = entry.code,
            entry_type         = entry.entry_type,
            final_surface_form = entry.arabic_form,
            case_marker_kind   = case_marker,
            bina_or_irab       = bina_irab,
            definiteness       = definiteness,
            gender             = entry.gender_default,
            number             = number,
            case_role          = case_role,
            tense              = Tense.NONE,
            transitivity       = Transitivity.NONE,
            exception_types    = exc_types,
            confidence         = 1.0,
            analysis_trace     = {
                "source": "lexicon_layer_v1",
                "exception_types": [e.value for e in exc_types],
                "inflection_class": entry.inflection_class.value,
            },
        )
        analysed.append({
            "entry_code":          record.entry_code,
            "entry_type":          record.entry_type.value,
            "final_surface_form":  record.final_surface_form,
            "case_marker_kind":    record.case_marker_kind.value,
            "bina_or_irab":        record.bina_or_irab,
            "definiteness":        record.definiteness.value,
            "gender":              record.gender.value,
            "number":              record.number.value,
            "case_role":           record.case_role.value,
            "tense":               record.tense.value,
            "transitivity":        record.transitivity.value,
            "exception_types":     [e.value for e in record.exception_types],
            "confidence":          record.confidence,
            "analysis_trace":      record.analysis_trace,
        })

    exception_registry = [
        {
            "code":             rec.code,
            "name_ar":          rec.name_ar,
            "exception_type":   rec.exception_type.value,
            "behavior_desc":    rec.behavior_desc,
            "rule_tag":         rec.rule_tag,
            "complexity_score": rec.complexity_score,
        }
        for rec in EXCEPTION_CLASS_REGISTRY
    ]

    state.conceptual_state["lexicon_layer"] = {
        "entries":            analysed,
        "entry_count":        len(analysed),
        "exception_registry": exception_registry,
    }
    state.add_trace(
        "lexicon_layer",
        {
            "entry_count":            len(analysed),
            "exception_class_count":  len(EXCEPTION_CLASS_REGISTRY),
        },
    )
    return state
