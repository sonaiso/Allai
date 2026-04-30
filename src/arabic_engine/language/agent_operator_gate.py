"""
agent_operator_gate.py
======================
بوابة العامل والمعمول — التحقق من قدرة الفاعل على الفعل

تتحقق هذه البوابة من أن الفاعل (عامل) يملك الخصائص الأنطولوجية
اللازمة لأداء الفعل (معمول) المطلوب.

القيد الأساسي:
    جماد + فعل إرادي → رفض فاعل_جماد
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arabic_engine.language.adam_properties import entity_can_act
from arabic_engine.language.verb_frame_lexicon import VerbFrame, get_verb_frame
from core.model import ProofState


@dataclass
class AgentOperatorResult:
    """نتيجة تحقق بوابة العامل والمعمول."""
    valid: bool
    agent_token: str
    agent_type: str
    verb_token: str
    violation: Optional[str] = None
    law_triggered: Optional[str] = None


def _strip_article(token: str) -> str:
    """إزالة أداة التعريف 'ال' من أول الكلمة إن وُجدت."""
    if token.startswith("ال") and len(token) > 2:
        return token[2:]
    return token


def _find_verb_and_frame(enriched: list[dict]) -> tuple[str, Optional[VerbFrame]]:
    """
    يبحث في المفاهيم المُثرَاة عن أول فعل يحمل جذرًا في معجم الإطارات.
    يُعيد (رمز الفعل، إطاره) أو ("", None) إن لم يُعثَر على شيء.
    """
    for concept in enriched:
        token = concept.get("token", "")
        root = concept.get("root")
        if root:
            frame = get_verb_frame(token)
            if frame:
                return token, frame
        # جرّب التطابق المباشر بالرمز
        frame = get_verb_frame(token)
        if frame:
            return token, frame
        bare = _strip_article(token)
        if bare != token:
            frame = get_verb_frame(bare)
            if frame:
                return token, frame
    return "", None


def _find_all_verbs_and_frames(enriched: list[dict]) -> list[tuple[str, VerbFrame]]:
    """
    يبحث في جميع المفاهيم المُثرَاة ويُعيد قائمة بكل أزواج (رمز_الفعل، إطاره).
    """
    results = []
    for concept in enriched:
        token = concept.get("token", "")
        frame = get_verb_frame(token)
        if frame:
            results.append((token, frame))
            continue
        bare = _strip_article(token)
        if bare != token:
            frame = get_verb_frame(bare)
            if frame:
                results.append((token, frame))
    return results


def _find_agent(enriched: list[dict], verb_token: str) -> tuple[str, str]:
    """
    يبحث في المفاهيم المُثرَاة عن الفاعل المحتمل.

    الاستراتيجية:
        1. أي كيان (entity_type موجود) ليس حرف جر ولا الفعل نفسه.
        2. يُرجَّح الكيان الذي لا يحمل relation_type (أي ليس حرف جر).
        3. في حال وجود entity_type: إنسان/حيوان يُقدَّم على غيره.
    """
    candidates = []
    for concept in enriched:
        token = concept.get("token", "")
        if token == verb_token:
            continue
        if concept.get("relation_type"):
            continue
        entity_type = concept.get("entity_type", "")
        root = concept.get("root")
        # تجاهل الكلمات التي هي أفعال فقط (لها جذر لكن لا entity_type)
        if root and not entity_type:
            continue
        if entity_type:
            candidates.append((token, entity_type))

    if not candidates:
        return "", ""

    # إعطاء الأولوية للإنسان/الحيوان
    for token, etype in candidates:
        if etype in ("إنسان", "حيوان"):
            return token, etype

    return candidates[0]


def apply_agent_operator_gate(state: ProofState) -> AgentOperatorResult:
    """
    بوابة العامل والمعمول.

    تُقيِّم جميع أزواج الفعل-الفاعل في الجملة وتُعيد أول انتهاك تجده.
    إن لم تجد انتهاكًا، تُعيد نتيجة صالحة.

    المخرجات:
        AgentOperatorResult — نتيجة التحقق
        state.symbolic_state["agent_operator_gate"] — النتيجة المُسلسَلة
        trace event: "agent_operator_gate"
    """
    enriched: list[dict] = state.enriched_concepts or []

    # نتحقق من جميع الأفعال في الجملة للعثور على أول انتهاك
    all_verbs = _find_all_verbs_and_frames(enriched)

    for verb_token, frame in all_verbs:
        agent_token, agent_type = _find_agent(enriched, verb_token)

        if not agent_token:
            continue

        # التحقق 1: هل الفاعل يملك إرادة إن كان الفعل إراديًا؟
        if frame.volitional and not entity_can_act(agent_type):
            violation = f"فاعل_{agent_type}"
            law_triggered = f"Adam:قابلية_{frame.root.replace(' ', '')}"
            result = AgentOperatorResult(
                valid=False,
                agent_token=agent_token,
                agent_type=agent_type,
                verb_token=verb_token,
                violation=violation,
                law_triggered=law_triggered,
            )
            payload = {
                "valid": False,
                "agent_token": agent_token,
                "agent_type": agent_type,
                "verb_token": verb_token,
                "violation": violation,
                "law_triggered": law_triggered,
            }
            state.symbolic_state["agent_operator_gate"] = payload
            state.add_trace("agent_operator_gate", payload)
            return result

        # التحقق 2: هل نوع الفاعل في قائمة المرفوضين؟
        if agent_type in frame.rejects:
            violation = f"فاعل_{agent_type}"
            law_triggered = f"Adam:قابلية_{frame.root.replace(' ', '')}"
            result = AgentOperatorResult(
                valid=False,
                agent_token=agent_token,
                agent_type=agent_type,
                verb_token=verb_token,
                violation=violation,
                law_triggered=law_triggered,
            )
            payload = {
                "valid": False,
                "agent_token": agent_token,
                "agent_type": agent_type,
                "verb_token": verb_token,
                "violation": violation,
                "law_triggered": law_triggered,
            }
            state.symbolic_state["agent_operator_gate"] = payload
            state.add_trace("agent_operator_gate", payload)
            return result

        # التحقق 3: هل نوع الفاعل في قائمة المتطلبات؟
        if frame.requires_agent_type and agent_type not in frame.requires_agent_type:
            violation = f"فاعل_{agent_type}_غير_مسموح"
            law_triggered = f"Adam:قابلية_{frame.root.replace(' ', '')}"
            result = AgentOperatorResult(
                valid=False,
                agent_token=agent_token,
                agent_type=agent_type,
                verb_token=verb_token,
                violation=violation,
                law_triggered=law_triggered,
            )
            payload = {
                "valid": False,
                "agent_token": agent_token,
                "agent_type": agent_type,
                "verb_token": verb_token,
                "violation": violation,
                "law_triggered": law_triggered,
            }
            state.symbolic_state["agent_operator_gate"] = payload
            state.add_trace("agent_operator_gate", payload)
            return result

    # لا انتهاك في أي فعل — استخرج أول فعل/فاعل للإخزان
    verb_token, frame = _find_verb_and_frame(enriched)
    agent_token, agent_type = _find_agent(enriched, verb_token) if verb_token else ("", "")

    result = AgentOperatorResult(
        valid=True,
        agent_token=agent_token,
        agent_type=agent_type,
        verb_token=verb_token,
    )
    payload = {
        "valid": True,
        "agent_token": agent_token,
        "agent_type": agent_type,
        "verb_token": verb_token,
        "violation": None,
        "law_triggered": None,
    }
    state.symbolic_state["agent_operator_gate"] = payload
    state.add_trace("agent_operator_gate", payload)
    return result
