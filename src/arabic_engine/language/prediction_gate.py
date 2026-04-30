"""
prediction_gate.py
==================
بوابة التنبؤ الرباعية — التحقق الرمزي متعدد الطبقات

تُشغِّل هذه البوابة أربع طبقات تحقق مستقلة على الجملة:
    1. صرفية    — اتساق الحالة الإعرابية والوزن
    2. نحوية    — وجود الأدوار المطلوبة
    3. دلالية   — توافق نوع الفاعل مع إطار الفعل
    4. عالم     — إمكانية الفعل في العالم الواقعي
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

from arabic_engine.language.verb_frame_lexicon import VerbFrame, get_verb_frame
from arabic_engine.language.adam_properties import entity_can_act
from core.model import ProofState


@dataclass
class PredictionResult:
    """نتيجة طبقة تنبؤ واحدة."""
    layer: str      # morphological | syntactic | semantic | world
    passed: bool
    reason: str


def _strip_article(token: str) -> str:
    if token.startswith("ال") and len(token) > 2:
        return token[2:]
    return token


def _find_frame(enriched: list[dict]) -> tuple[str, VerbFrame | None]:
    """يبحث عن أول فعل وإطاره في المفاهيم المُثرَاة."""
    for concept in enriched:
        token = concept.get("token", "")
        frame = get_verb_frame(token)
        if frame:
            return token, frame
        bare = _strip_article(token)
        frame = get_verb_frame(bare)
        if frame:
            return token, frame
    return "", None


def _morphological_check(enriched: list[dict]) -> PredictionResult:
    """
    الطبقة الصرفية: يتحقق من وجود مفاهيم مُثرَاة بصورة كافية.
    معيار الاجتياز: وجود مفهوم واحد على الأقل له جذر أو entity_type.
    """
    has_rooted = any(c.get("root") for c in enriched)
    has_entity = any(c.get("entity_type") for c in enriched)
    passed = has_rooted or has_entity
    reason = (
        "اتساق صرفي مقبول — تم تحديد جذور أو كيانات" if passed
        else "لا جذر ولا كيان مُعرَّف — تحليل صرفي ناقص"
    )
    return PredictionResult(layer="morphological", passed=passed, reason=reason)


def _syntactic_check(enriched: list[dict], verb_token: str, frame: VerbFrame | None) -> PredictionResult:
    """
    الطبقة النحوية: يتحقق من وجود الأدوار المطلوبة.
    معيار الاجتياز: وجود مفهوم يصلح فاعلًا إن كان الإطار يشترط فاعلًا.
    """
    if frame is None:
        return PredictionResult(
            layer="syntactic",
            passed=True,
            reason="لا إطار فعل — تحقق نحوي غير مطلوب",
        )

    # التحقق من وجود فاعل محتمل (كيان ليس حرف جر وليس الفعل نفسه)
    has_agent = any(
        c.get("entity_type") and not c.get("relation_type") and c.get("token") != verb_token
        for c in enriched
    )

    if "فاعل" in frame.requires and not has_agent:
        return PredictionResult(
            layer="syntactic",
            passed=False,
            reason=f"الإطار '{frame.root}' يستلزم فاعلًا ولم يُعثَر على كيان صالح",
        )

    return PredictionResult(
        layer="syntactic",
        passed=True,
        reason="الأدوار النحوية المطلوبة موجودة",
    )


def _semantic_check(enriched: list[dict], verb_token: str, frame: VerbFrame | None) -> PredictionResult:
    """
    الطبقة الدلالية: يتحقق من توافق نوع الفاعل مع قيود إطار الفعل.
    """
    if frame is None:
        return PredictionResult(
            layer="semantic",
            passed=True,
            reason="لا إطار فعل — تحقق دلالي غير مطلوب",
        )

    # العثور على الفاعل المحتمل
    agent_type = ""
    agent_token = ""
    for concept in enriched:
        token = concept.get("token", "")
        if token == verb_token:
            continue
        if concept.get("relation_type"):
            continue
        etype = concept.get("entity_type", "")
        if etype:
            agent_token = token
            agent_type = etype
            if etype in ("إنسان", "حيوان"):
                break

    if not agent_type:
        return PredictionResult(
            layer="semantic",
            passed=True,
            reason="لم يُعثَر على فاعل — تحقق دلالي غير قاطع",
        )

    # التحقق من أن الفاعل يملك إرادة إن كان الفعل إراديًا
    if frame.volitional and not entity_can_act(agent_type):
        return PredictionResult(
            layer="semantic",
            passed=False,
            reason=f"الفاعل '{agent_token}' ({agent_type}) لا يملك إرادة لأداء '{verb_token}'",
        )

    # التحقق من قائمة المرفوضين
    if agent_type in frame.rejects:
        return PredictionResult(
            layer="semantic",
            passed=False,
            reason=f"نوع الفاعل '{agent_type}' مرفوض صراحةً في إطار '{frame.root}'",
        )

    return PredictionResult(
        layer="semantic",
        passed=True,
        reason=f"الفاعل '{agent_token}' ({agent_type}) متوافق مع إطار '{frame.root}'",
    )


def _normalize_token(token: str) -> str:
    """يُزيل التشكيل وأداة التعريف من الرمز لأغراض المقارنة."""
    # إزالة تنوين الفتح (ـًا)
    result = token.replace("\u064B\u0627", "")
    # إزالة باقي علامات التشكيل (U+064B..U+065F, U+0670)
    result = "".join(
        ch for ch in result if not ("\u064B" <= ch <= "\u065F" or ch == "\u0670")
    )
    # إزالة أداة التعريف
    if result.startswith("ال") and len(result) > 2:
        result = result[2:]
    return result


def _world_check(enriched: list[dict], verb_token: str) -> PredictionResult:
    """
    طبقة العالم: يتحقق من وجود أفعال مستحيلة مُسجَّلة في الكيانات.
    """
    verb_bare = _normalize_token(verb_token)

    for concept in enriched:
        if concept.get("token") in (verb_token, verb_bare):
            continue
        impossible = concept.get("impossible_actions") or []
        entity_type = concept.get("entity_type", "")
        if not entity_type:
            continue
        # تحقق من تطابق دقيق بين الفعل والأفعال المستحيلة (بعد التطبيع)
        if any(_normalize_token(imp) == verb_bare or imp == verb_token for imp in impossible):
            return PredictionResult(
                layer="world",
                passed=False,
                reason=(
                    f"الفعل '{verb_token}' مستحيل للكيان '{concept.get('token')}' "
                    f"({entity_type}) وفق قوانين العالم"
                ),
            )

    return PredictionResult(
        layer="world",
        passed=True,
        reason="لا تعارض مع قوانين العالم المُسجَّلة",
    )


def apply_prediction_gate(state: ProofState) -> list[PredictionResult]:
    """
    بوابة التنبؤ الرباعية.

    تُشغِّل الطبقات الأربع بالترتيب وتُخزِّن نتائجها.

    المخرجات:
        list[PredictionResult] — نتائج الطبقات الأربع
        state.symbolic_state["prediction_gate"] — النتائج المُسلسَلة
        trace event: "prediction_gate"
    """
    enriched: list[dict] = state.enriched_concepts or []
    verb_token, frame = _find_frame(enriched)

    results = [
        _morphological_check(enriched),
        _syntactic_check(enriched, verb_token, frame),
        _semantic_check(enriched, verb_token, frame),
        _world_check(enriched, verb_token),
    ]

    serialised = [asdict(r) for r in results]
    all_passed = all(r.passed for r in results)
    state.symbolic_state["prediction_gate"] = {
        "results": serialised,
        "all_passed": all_passed,
        "verb_token": verb_token,
    }
    state.add_trace(
        "prediction_gate",
        {"results": serialised, "all_passed": all_passed, "verb_token": verb_token},
    )
    return results
