from core.model import ProofState


def apply_singular_possibility_closure(state: ProofState) -> ProofState:
    if not state.singular_designation_closed:
        blocker = "prior_level_incomplete:designation"
        state.singular_possibility_closed = False
        state.singular_level_evidence["possibility"] = {}
        state.singular_level_blockers["possibility"] = blocker
        state.singular_rank_states["possibility"] = False
        state.singular_rank_sublayers["possibility"] = {}
        state.singular_rank_blockers["possibility"] = blocker
        state.add_trace("singular_possibility_closure", {"closed": False, "blocker": blocker})
        return state

    text = state.effective_text()
    tokens = [t for t in text.split() if t]
    evidence = {
        "can_be_noun": bool(tokens),
        "can_be_verb": len(tokens) >= 1,
        "can_be_particle": len(tokens) == 1,
        "can_take_time": len(tokens) >= 1,
        "can_take_place": len(tokens) >= 2,
        "can_compose": len(tokens) >= 1,
    }
    closed = evidence["can_compose"] and (evidence["can_be_noun"] or evidence["can_be_verb"] or evidence["can_be_particle"])
    blocker = None if closed else "possibility_threshold_not_met"

    state.singular_possibility_closed = closed
    state.singular_level_evidence["possibility"] = evidence
    state.singular_level_blockers["possibility"] = blocker
    state.singular_rank_states["possibility"] = closed
    state.singular_rank_sublayers["possibility"] = evidence
    state.singular_rank_blockers["possibility"] = blocker
    state.add_trace("singular_possibility_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
