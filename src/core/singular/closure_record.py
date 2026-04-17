import hashlib
import json

from core.model import ProofState


CLOSURE_RECORD_ID_PREFIX_CHARS = 16


def _rank_states(state: ProofState) -> dict[str, bool]:
    return {
        "existence": state.singular_existence_closed,
        "designation": state.singular_designation_closed,
        "possibility": state.singular_possibility_closed,
        "identity": state.singular_identity_closed,
        "relational": state.singular_relational_closed,
        "weight": state.singular_weight_closed,
        "logical_classificatory": state.singular_logical_classificatory_closed,
    }


def _resolve_rank_blocker(state: ProofState, rank: str) -> str | None:
    rank_blocker = state.singular_rank_blockers.get(rank)
    if rank_blocker is not None:
        return rank_blocker
    return state.singular_level_blockers.get(rank)


def assemble_singular_closure_record(state: ProofState) -> ProofState:
    rank_states = _rank_states(state)
    blockers = {
        rank: state.singular_level_blockers.get(rank)
        for rank in rank_states
        if state.singular_level_blockers.get(rank)
    }

    if state.singular_final_decision:
        decision = state.singular_final_decision
        decision_reason = state.singular_final_decision_reason or "provided_by_unified_closure"
    elif state.singular_unified_closure_closed:
        decision = "PASS"
        decision_reason = "all_required_ranks_closed"
    else:
        decision = "SUSPEND"
        decision_reason = "unified_closure_stage_missing_or_incomplete"
    if state.ready_for_composition and state.composition != {}:
        decision = "COMPLETE"
        decision_reason = "unified_closure_complete_and_composed"

    seed_payload = {
        "text": state.effective_text(),
        "rank_states": rank_states,
        "weight_label": state.weight_label,
        "decision": decision,
        "ready": state.ready_for_composition,
    }
    closure_record_id = hashlib.sha256(
        json.dumps(seed_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:CLOSURE_RECORD_ID_PREFIX_CHARS]

    state.closure_record_id = closure_record_id
    state.existence_closed = rank_states["existence"]
    state.designation_closed = rank_states["designation"]
    state.possibility_closed = rank_states["possibility"]
    state.identity_closed = rank_states["identity"]
    state.relational_closed = rank_states["relational"]
    state.weight_handoff_closed = rank_states["weight"]

    hierarchical_trace = []
    for event in state.trace_chain:
        event_name = str(event.get("event", ""))
        if event_name.startswith("singular_") and event_name.endswith("closure"):
            hierarchical_trace.append(event)

    state.singular_closure_record = {
        "closure_record_id": closure_record_id,
        "existence_closed": rank_states["existence"],
        "designation_closed": rank_states["designation"],
        "possibility_closed": rank_states["possibility"],
        "identity_closed": rank_states["identity"],
        "relational_closed": rank_states["relational"],
        "weight_closed": rank_states["weight"],
        "logical_classificatory_closed": rank_states["logical_classificatory"],
        "unified_closure_closed": state.singular_unified_closure_closed,
        "ready_for_composition": state.ready_for_composition,
        "blockers": blockers,
        "rank_states": rank_states,
        "sublayer_records": state.singular_rank_sublayers,
        "hierarchical_evidence": state.singular_level_evidence,
        "hierarchical_blockers": {
            rank: _resolve_rank_blocker(state, rank) for rank in (*rank_states.keys(), "unified_closure")
        },
        "hierarchical_trace": hierarchical_trace,
        "final_decision": decision,
        "final_decision_reason": decision_reason,
    }
    state.add_trace(
        "singular_closure_record_assembled",
        {
            "closure_record_id": closure_record_id,
            "ready_for_composition": state.ready_for_composition,
            "final_decision": decision,
            "blockers": blockers,
        },
    )
    return state
