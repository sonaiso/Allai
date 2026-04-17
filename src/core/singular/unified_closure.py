from core.model import ProofState


_DECISION_PASS = "PASS"
_DECISION_SUSPEND = "SUSPEND"
_DECISION_REJECT = "REJECT"


def _required_rank_states(state: ProofState) -> dict[str, bool]:
    return {
        "existence": state.singular_existence_closed,
        "designation": state.singular_designation_closed,
        "possibility": state.singular_possibility_closed,
        "identity": state.singular_identity_closed,
        "relational": state.singular_relational_closed,
        "weight": state.singular_weight_closed,
        "logical_classificatory": state.singular_logical_classificatory_closed,
    }


def apply_singular_unified_closure(state: ProofState) -> ProofState:
    rank_states = _required_rank_states(state)
    blockers = {
        rank: state.singular_level_blockers.get(rank)
        for rank in rank_states
        if state.singular_level_blockers.get(rank)
    }

    closed = all(rank_states.values()) and len(blockers) == 0
    if closed:
        decision = _DECISION_PASS
        reason = "all_required_ranks_closed"
    elif any(rank_states.values()):
        decision = _DECISION_SUSPEND
        reason = "partial_rank_closure"
    else:
        decision = _DECISION_REJECT
        reason = "no_rank_closed"

    state.singular_unified_closure_closed = closed
    state.ready_for_composition = closed
    state.singular_final_decision = decision
    state.singular_final_decision_reason = reason

    state.singular_rank_states.update(rank_states)
    state.singular_rank_sublayers["unified_closure"] = {
        "minimum_conditions": {
            "all_required_ranks_closed": all(rank_states.values()),
            "no_rank_blockers": len(blockers) == 0,
        },
        "higher_analysis": {
            "rank_states": rank_states,
            "blockers": blockers,
            "decision": decision,
            "reason": reason,
            "ready_for_composition": closed,
        },
    }
    state.singular_rank_blockers["unified_closure"] = None if closed else "unified_closure_incomplete"

    state.add_trace(
        "singular_unified_closure",
        {
            "closed": closed,
            "decision": decision,
            "reason": reason,
            "blockers": blockers,
        },
    )
    return state
