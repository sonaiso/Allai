from __future__ import annotations

from core.model import ProofState
from core.world_model.models import (
    CausalLink,
    Entity,
    Event,
    Goal,
    Law,
    Relation,
    WorldModelRecord,
)

_DEFAULT_LINGUISTIC_LAWS: list[dict[str, str]] = [
    {"domain": "arabic_grammar", "rule": "subject_is_nominative", "law_type": "linguistic"},
    {"domain": "arabic_grammar", "rule": "predicate_follows_subject", "law_type": "linguistic"},
]


def _extract_entities(composition: dict) -> list[dict]:
    entities: list[dict] = []
    subject = composition.get("subject")
    if subject:
        entity = Entity(id=subject, entity_type="nominal", attributes={"role": "subject"})
        entities.append(
            {"id": entity.id, "entity_type": entity.entity_type, "attributes": entity.attributes}
        )

    for role_entry in composition.get("role_graph", []):
        token = role_entry.get("token", "")
        role = role_entry.get("governance_role", "")
        if token and token != subject and role == "dependent":
            dep_entity = Entity(
                id=token,
                entity_type="nominal",
                attributes={"role": role, "token_index": role_entry.get("token_index")},
            )
            entities.append(
                {
                    "id": dep_entity.id,
                    "entity_type": dep_entity.entity_type,
                    "attributes": dep_entity.attributes,
                }
            )
    return entities


def _extract_events(composition: dict, sentence_pattern: str, tokens: list[str]) -> list[dict]:
    events: list[dict] = []
    if sentence_pattern == "verbal" and tokens:
        action = tokens[0]
        agent = tokens[1] if len(tokens) > 1 else "unspecified"
        event = Event(action=action, agent=agent, time="unspecified")
        events.append(
            {
                "action": event.action,
                "agent": event.agent,
                "time": event.time,
                "patient": event.patient,
            }
        )
    elif sentence_pattern == "nominal" and len(tokens) >= 2:
        event = Event(action="is", agent=tokens[0], time="present", patient=tokens[1])
        events.append(
            {
                "action": event.action,
                "agent": event.agent,
                "time": event.time,
                "patient": event.patient,
            }
        )
    return events


def _extract_relations(composition: dict) -> list[dict]:
    relations: list[dict] = []
    role_graph = composition.get("role_graph", [])
    if len(role_graph) >= 2:
        governor = next(
            (r for r in role_graph if "governor" in r.get("governance_role", "")), None
        )
        if governor:
            for entry in role_graph:
                if entry is governor:
                    continue
                relation = Relation(
                    source=governor["token"],
                    target=entry["token"],
                    relation_type="governs",
                )
                relations.append(
                    {
                        "source": relation.source,
                        "target": relation.target,
                        "relation_type": relation.relation_type,
                    }
                )
    return relations


def extract_world_model(state: ProofState) -> ProofState:
    composition = state.composition or {}
    minimal_encoding = state.symbolic_state.get("minimal_complete_encoding", {})
    sentence_pattern = minimal_encoding.get("sentence_pattern", "nominal")
    token_units = minimal_encoding.get("token_units", [])
    tokens = [u["token"] for u in token_units if u.get("token")]

    entities = _extract_entities(composition)
    events = _extract_events(composition, sentence_pattern, tokens)
    relations = _extract_relations(composition)
    laws = list(_DEFAULT_LINGUISTIC_LAWS)

    uncertainty: list[str] = []
    causality: list[dict] = []
    goals: list[dict] = []

    if not causality:
        uncertainty.append("causality_not_detected")

    if not goals:
        uncertainty.append("goals_not_detected")

    record = WorldModelRecord(
        entities=entities,
        events=events,
        relations=relations,
        laws=laws,
        causality=causality,
        goals=goals,
        judgments=[],
        uncertainty=uncertainty,
        blockers=[],
        closed=False,
    )

    state.world_model = record.to_dict()
    state.add_trace(
        "world_model_extracted",
        {
            "entity_count": len(entities),
            "event_count": len(events),
            "relation_count": len(relations),
            "law_count": len(laws),
            "causality_count": len(causality),
            "goal_count": len(goals),
            "uncertainty": uncertainty,
        },
    )
    return state
