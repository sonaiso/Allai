from core.model import ProofState


def apply_singular_relational_closure(state: ProofState) -> ProofState:
    if not state.singular_identity_closed:
        blocker = "prior_level_incomplete:identity"
        state.singular_relational_closed = False
        state.singular_level_evidence["relational"] = {}
        state.singular_level_blockers["relational"] = blocker
        state.singular_rank_states["relational"] = False
        state.singular_rank_sublayers["relational"] = {}
        state.singular_rank_blockers["relational"] = blocker
        state.add_trace("singular_relational_closure", {"closed": False, "blocker": blocker})
        return state

    identity = state.singular_level_evidence.get("identity", {})
    word_class = identity.get("word_class")

    evidence = {
        "can_be_agent": word_class == "noun",
        "can_be_patient": word_class == "noun",
        "can_be_cause": word_class in {"noun", "verb"},
        "can_be_effect": word_class == "verb",
        "can_be_linker": word_class == "particle",
        "can_take_predication": word_class in {"noun", "verb"},
    }
    closed = evidence["can_take_predication"] and (
        evidence["can_be_agent"]
        or evidence["can_be_patient"]
        or evidence["can_be_linker"]
        or evidence["can_be_effect"]
    )
    blocker = None if closed else "relational_capacity_unresolved"

    state.singular_relational_closed = closed
    state.singular_level_evidence["relational"] = evidence
    state.singular_level_blockers["relational"] = blocker
    state.singular_rank_states["relational"] = closed
    state.singular_rank_sublayers["relational"] = evidence
    state.singular_rank_blockers["relational"] = blocker
    state.add_trace("singular_relational_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
