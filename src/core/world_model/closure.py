from __future__ import annotations

from core.model import ProofState


def apply_world_model_closure(state: ProofState) -> ProofState:
    wm = state.world_model

    language_closed = state.proposition_closed

    world_anchored = bool(wm.get("entities"))

    law_checked = bool(wm.get("laws"))

    causality_list = wm.get("causality")
    causality_mapped = causality_list is not None

    goals_list = wm.get("goals")
    goal_resolved = goals_list is not None

    judgment_ready = bool(wm.get("entities")) and bool(wm.get("events"))

    closed = (
        language_closed
        and world_anchored
        and law_checked
        and causality_mapped
        and goal_resolved
        and judgment_ready
    )

    blockers: list[str] = []
    if not language_closed:
        blockers.append("proposition_not_closed")
    if not world_anchored:
        blockers.append("no_entities_extracted")
    if not law_checked:
        blockers.append("no_laws_available")
    if not causality_mapped:
        blockers.append("causality_list_missing")
    if not goal_resolved:
        blockers.append("goals_list_missing")
    if not judgment_ready:
        blockers.append("insufficient_entities_or_events_for_judgment")

    if isinstance(wm.get("blockers"), list):
        wm["blockers"].extend(blockers)
    else:
        wm["blockers"] = blockers

    wm["closed"] = closed
    state.world_model = wm
    state.world_model_closed = closed

    state.add_trace(
        "world_model_closure",
        {
            "closed": closed,
            "language_closed": language_closed,
            "world_anchored": world_anchored,
            "law_checked": law_checked,
            "causality_mapped": causality_mapped,
            "goal_resolved": goal_resolved,
            "judgment_ready": judgment_ready,
            "blockers": blockers,
        },
    )
    return state
