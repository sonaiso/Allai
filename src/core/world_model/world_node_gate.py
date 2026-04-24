"""
world_node_gate.py
==================
بوابة عقدة العالم

تُحوّل:
    EnrichedConcept + PropertyBundle
    ────────────────────────────────────────────────
    WorldNode (عقدة عالم قابلة للحكم)

القاعدة الدستورية:
    لا يدخل أي مفهوم إلى نموذج العالم حتى يحمل خاصية واحدة على الأقل.

السلسلة:
    أثر → أثر مخزن → اسم → خاصية → عقدة → حكم ممكن
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from core.model import ProofState


# =========================================================
# 1. نموذج عقدة العالم — WorldNode Model
# =========================================================

@dataclass
class WorldNode:
    """
    عقدة عالم — تمثيل مفهوم مُثرَى جاهز للدخول إلى WorldModel.

    يُطبَّق شرط: لا عقدة بلا خاصية (has_properties يجب أن يكون True).
    """
    node_id: str                                      # مُعرَّف فريد = token + index
    label: str                                        # اسم المفهوم
    properties: List[str] = field(default_factory=list)   # الخواص المُجمَّعة من PropertyBundle
    relations: List[str] = field(default_factory=list)    # العلاقات المستخرجة من الإثراء
    possible_judgments: List[str] = field(default_factory=list)  # الأحكام الممكنة
    enrichment_source: str = "none"
    confidence: float = 0.5

    def has_properties(self) -> bool:
        """تحقق: هل تحمل العقدة خاصية واحدة على الأقل؟"""
        return bool(self.properties)


# =========================================================
# 2. دوال المساعدة — Helper Functions
# =========================================================

def _collect_properties_for_token(
    token_index: int,
    property_bundles: list[dict],
) -> list[str]:
    """اجمع جميع الخواص من PropertyBundle المطابق لهذا token_index."""
    props: list[str] = []
    for bundle in property_bundles:
        if bundle.get("anchor_token_index") == token_index:
            for layer_key in (
                "existence_props",
                "identity_props",
                "boundary_props",
                "perception_props",
                "relation_props",
                "action_props",
                "judgment_props",
            ):
                props.extend(bundle.get(layer_key, []))
    return props


def _infer_possible_judgments(
    properties: list[str],
    enriched: dict,
) -> list[str]:
    """استنتج الأحكام الممكنة بناءً على الخواص والإثراء."""
    judgments: list[str] = []

    if "exists" in properties:
        judgments.append("can_be_referenced")
    if "distinguishable" in properties or "distinct" in properties:
        judgments.append("can_be_distinguished")
    if enriched.get("entity_type"):
        judgments.append("is_entity")
    if enriched.get("relation_type"):
        judgments.append("is_relation_marker")
    if enriched.get("root"):
        judgments.append("has_semantic_root")
    if enriched.get("affordances"):
        judgments.append("has_affordance")
    if not judgments:
        judgments.append("requires_further_analysis")

    return judgments


def _extract_relation_labels(enriched: dict) -> list[str]:
    """استخرج تسميات العلاقات من مفهوم مُثرَى."""
    relations: list[str] = []
    if enriched.get("relation_type"):
        relations.append(enriched["relation_type"])
    if enriched.get("roles"):
        relations.extend(enriched["roles"])
    return relations


# =========================================================
# 3. بوابة العقدة — Gate Function
# =========================================================

def apply_world_node_gate(state: ProofState) -> ProofState:
    """
    بوابة عقدة العالم.

    المدخلات:
        state.conceptual_state["enriched_concepts"]   — المفاهيم المُثرَاة
        state.conceptual_state["property_bundles"]    — حزم الخواص الأولى

    المخرجات:
        state.conceptual_state["world_nodes"]         — قائمة WorldNode
        state.conceptual_state["world_nodes_blocked"] — المفاهيم المحجوبة (بلا خواص)
        trace event: "world_node_gate"
    """
    enriched_concepts: list[dict] = state.conceptual_state.get("enriched_concepts", [])
    property_bundles: list[dict] = state.conceptual_state.get("property_bundles", [])

    world_nodes: list[dict] = []
    blocked: list[dict] = []

    seen_tokens: set[str] = set()
    token_index_counter: dict[str, int] = {}

    for enriched in enriched_concepts:
        token = enriched.get("token", "")
        if not token:
            continue

        # عيّن token_index مستقلًا (نستخدم ترتيب الظهور كمقارب)
        if token not in token_index_counter:
            token_index_counter[token] = len(token_index_counter)
        t_idx = token_index_counter[token]

        node_id = f"{token}:{t_idx}"
        if node_id in seen_tokens:
            continue
        seen_tokens.add(node_id)

        # اجمع الخواص من property_bundles
        props = _collect_properties_for_token(t_idx, property_bundles)

        # إن لم تكن هناك خواص من property_bundles (مثلاً عند تخطي property_binding_gate
        # في مسار lexical-only)، أضف خواصًا افتراضية بسيطة بناءً على نوع الإثراء.
        # هذا الاحتياط يضمن أن المفاهيم المُثرَاة بمعلومات معجمية لا تُحجب بشكل خاطئ.
        if not props:
            if enriched.get("entity_type") or enriched.get("root") or enriched.get("relation_type"):
                props = ["exists", "distinguishable"]
            elif enriched.get("enrichment_source") != "none":
                props = ["exists"]

        node = WorldNode(
            node_id=node_id,
            label=token,
            properties=props,
            relations=_extract_relation_labels(enriched),
            possible_judgments=_infer_possible_judgments(props, enriched),
            enrichment_source=enriched.get("enrichment_source", "none"),
            confidence=enriched.get("confidence", 0.5),
        )

        if node.has_properties():
            world_nodes.append(asdict(node))
        else:
            blocked.append(
                {
                    "token": token,
                    "reason": "no_property_assigned",
                    "enrichment_source": node.enrichment_source,
                }
            )

    state.conceptual_state["world_nodes"] = world_nodes
    state.conceptual_state["world_nodes_blocked"] = blocked

    state.add_trace(
        "world_node_gate",
        {
            "world_nodes_count": len(world_nodes),
            "blocked_count": len(blocked),
            "derived_from": "enriched_concepts_v1",
        },
    )
    return state
