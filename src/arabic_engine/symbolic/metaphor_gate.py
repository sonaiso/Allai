"""
metaphor_gate.py
================
محرك المجاز — كشف التعارض والبحث عن الخاصية المشتركة

الخطوات:
    1. كشف التعارض الدلالي (entity_type ≠ required_type)
    2. البحث عن خاصية مشتركة في `shared_properties_index`
    3. توليد تفسير مجازي موثَّق
    4. تحديث world_model.judgments بـ judgment_type="metaphorical"

المدخلات:
    state.conceptual_state["rejection_records"]
    state.conceptual_state["enriched_concepts"]
    state.world_model

المخرجات:
    state.conceptual_state["metaphor_result"]
    state.world_model["judgments"] (مُحدَّث)
    trace event: "metaphor_gate"
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from core.model import ProofState


# =========================================================
# 1. فهرس الخواص المشتركة — Shared Properties Index
# =========================================================

# يُعرِّف للمجاز: الكيان المجازي + الكيان الحقيقي + الخاصية الجامعة + التفسير
_SHARED_PROPERTIES_INDEX: dict[str, dict[str, Any]] = {
    "أسد": {
        "actual_type":    "حيوان",
        "metaphoric_for": "إنسان",
        "shared_property": "شجاعة",
        "interpretation": "أسد = رجل شجاع",
        "confidence":     0.90,
    },
    "ثعلب": {
        "actual_type":    "حيوان",
        "metaphoric_for": "إنسان",
        "shared_property": "مكر",
        "interpretation": "ثعلب = شخص ماكر",
        "confidence":     0.85,
    },
    "نسر": {
        "actual_type":    "حيوان",
        "metaphoric_for": "إنسان",
        "shared_property": "قوة",
        "interpretation": "نسر = إنسان قوي طليق",
        "confidence":     0.80,
    },
    "بحر": {
        "actual_type":    "مكان",
        "metaphoric_for": "إنسان",
        "shared_property": "كرم",
        "interpretation": "بحر = إنسان كريم لا يُحصى عطاؤه",
        "confidence":     0.85,
    },
    "شمس": {
        "actual_type":    "ظاهرة",
        "metaphoric_for": "إنسان",
        "shared_property": "نور",
        "interpretation": "شمس = إنسان مشرق مضيء",
        "confidence":     0.85,
    },
}


# =========================================================
# 2. نموذج نتيجة المجاز — Metaphor Result Model
# =========================================================

@dataclass
class MetaphorInterpretation:
    """تفسير مجازي موثَّق لكيان في سياق متعارض."""
    metaphoric_token: str               # الكيان المجازي (مثل: أسد)
    actual_type: str                    # نوعه الحقيقي (مثل: حيوان)
    metaphoric_for: str                 # ما يُمثّله (مثل: إنسان)
    shared_property: str               # الخاصية المشتركة (مثل: شجاعة)
    interpretation: str                # التفسير الكامل
    confidence: float
    law_source: str = "shared_property_index"


@dataclass
class MetaphorResult:
    """نتيجة محرك المجاز الكاملة."""
    conflict_detected: bool = False
    interpretations: list[MetaphorInterpretation] = field(default_factory=list)
    unresolved_conflicts: list[str] = field(default_factory=list)
    metaphor_applied: bool = False
    overall_judgment: str = "literal"   # literal | metaphorical | unresolved


# =========================================================
# 3. منطق الاستدلال المجازي — Metaphor Inference Logic
# =========================================================

def _normalize_token(token: str) -> str:
    """
    تطبيع الرمز: إزالة أداة التعريف، التنوين، والتشكيل.
    أمثلة: "الأسدِ" → "أسد" ، "أسدًا" → "أسد"
    """
    # إزالة أداة التعريف
    bare = token.lstrip("ال") if token.startswith("ال") and len(token) > 2 else token
    # إزالة التنوين وعلامات الإعراب
    diacritics = "ًٌٍَُِّْ"
    has_tanwin_nasb = "\u064b" in bare
    result = bare.translate(str.maketrans("", "", diacritics))
    if has_tanwin_nasb and result.endswith("\u0627"):
        result = result[:-1]
    return result


def _find_metaphor(token: str) -> Optional[dict[str, Any]]:
    """ابحث عن تفسير مجازي للرمز في الفهرس."""
    normalized = _normalize_token(token)
    return (
        _SHARED_PROPERTIES_INDEX.get(normalized)
        or _SHARED_PROPERTIES_INDEX.get(token)
        or _SHARED_PROPERTIES_INDEX.get(token.lstrip("ال"))
    )


def _is_conflict_possibly_metaphorical(rejection_record: dict) -> bool:
    """
    هل انتهاك الفاعل ذو طابع دلالي (لا منطقي/فيزيائي) مما قد يُفسَّر مجازًا؟
    """
    violation_type = rejection_record.get("violation_type", "")
    judgment = rejection_record.get("judgment", "")
    return violation_type == "semantic" and judgment == "محتمل_مجازي"


def _interpret_metaphorically(
    rejection_records: list[dict],
    enriched: list[dict],
) -> MetaphorResult:
    """حاول تفسير التعارضات الدلالية مجازًا."""
    result = MetaphorResult()

    for record in rejection_records:
        if not _is_conflict_possibly_metaphorical(record):
            continue

        result.conflict_detected = True
        violating_token = record.get("violating_token", "")

        meta_info = _find_metaphor(violating_token)
        if meta_info:
            interpretation = MetaphorInterpretation(
                metaphoric_token=violating_token,
                actual_type=meta_info["actual_type"],
                metaphoric_for=meta_info["metaphoric_for"],
                shared_property=meta_info["shared_property"],
                interpretation=meta_info["interpretation"],
                confidence=meta_info["confidence"],
            )
            result.interpretations.append(interpretation)
            result.metaphor_applied = True
        else:
            result.unresolved_conflicts.append(
                f"{violating_token}: لا توجد خاصية مشتركة موثَّقة في الفهرس"
            )

    if result.metaphor_applied and not result.unresolved_conflicts:
        result.overall_judgment = "metaphorical"
    elif result.conflict_detected and result.unresolved_conflicts:
        result.overall_judgment = "unresolved"
    else:
        result.overall_judgment = "literal"

    return result


# =========================================================
# 4. البوابة الرئيسية — Main Gate
# =========================================================

def apply_metaphor_gate(state: ProofState) -> ProofState:
    """
    محرك المجاز.

    المدخلات:
        state.conceptual_state["rejection_records"]
        state.conceptual_state["enriched_concepts"]
        state.world_model

    المخرجات:
        state.conceptual_state["metaphor_result"]
        state.world_model["judgments"] (مُحدَّث)
        trace event: "metaphor_gate"
    """
    rejection_records: list[dict] = state.conceptual_state.get("rejection_records", [])
    enriched: list[dict] = state.conceptual_state.get("enriched_concepts", [])

    result = _interpret_metaphorically(rejection_records, enriched)

    # تحديث world_model.judgments
    wm = state.world_model or {}
    judgments: list[dict] = list(wm.get("judgments", []))

    for interp in result.interpretations:
        judgments.append({
            "judgment_type": "metaphorical",
            "value": interp.interpretation,
            "justification": (
                f"خاصية_مشتركة:{interp.shared_property} — "
                f"{interp.metaphoric_token} ({interp.actual_type}) "
                f"تُستعمل مجازًا عن {interp.metaphoric_for}"
            ),
            "confidence": interp.confidence,
            "token": interp.metaphoric_token,
        })

    if result.overall_judgment == "literal" and not rejection_records:
        judgments.append({
            "judgment_type": "validity",
            "value": "literal_accepted",
            "justification": "لا تعارض — الجملة حرفية صحيحة",
            "confidence": 1.0,
        })

    wm["judgments"] = judgments
    state.world_model = wm

    result_dict: dict[str, Any] = {
        "conflict_detected": result.conflict_detected,
        "interpretations": [asdict(i) for i in result.interpretations],
        "unresolved_conflicts": result.unresolved_conflicts,
        "metaphor_applied": result.metaphor_applied,
        "overall_judgment": result.overall_judgment,
    }
    state.conceptual_state["metaphor_result"] = result_dict

    state.add_trace(
        "metaphor_gate",
        {
            "conflict_detected": result.conflict_detected,
            "metaphor_applied": result.metaphor_applied,
            "interpretation_count": len(result.interpretations),
            "unresolved_count": len(result.unresolved_conflicts),
            "overall_judgment": result.overall_judgment,
        },
    )
    return state
