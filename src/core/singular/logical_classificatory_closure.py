from core.model import ProofState


def apply_singular_logical_classificatory_closure(state: ProofState) -> ProofState:
    if not state.singular_weight_closed:
        blocker = "prior_rank_incomplete:weight"
        state.singular_logical_classificatory_closed = False
        state.singular_level_evidence["logical_classificatory"] = {}
        state.singular_level_blockers["logical_classificatory"] = blocker
        state.singular_rank_states["logical_classificatory"] = False
        state.singular_rank_sublayers["logical_classificatory"] = {}
        state.singular_rank_blockers["logical_classificatory"] = blocker
        state.add_trace("singular_logical_classificatory_closure", {"closed": False, "blocker": blocker})
        return state

    tokens = [t for t in state.effective_text().split() if t]
    first = tokens[0] if tokens else ""
    identity = state.singular_level_evidence.get("identity", {})
    identity_higher = identity.get("higher_analysis", {})

    minimum_conditions = {
        "independent_meaning": bool(tokens),
        "source_transform_relation": bool(state.weight_label),
    }
    higher_analysis = {
        "independent_meaning": bool(tokens),
        "universality_particularity": bool(tokens),
        "genus_species": bool(identity_higher.get("word_class")),
        "essence": bool(first),
        "literal_figurative": True,
        "linguistic_customary_transferred": True,
        "dalala_type": True,
        "source_transform_relation": bool(state.weight_label),
    }
    evidence = {
        "minimum_conditions": minimum_conditions,
        "higher_analysis": higher_analysis,
    }
    closed = all(minimum_conditions.values())
    blocker = None if closed else "logical_classificatory_incomplete"

    state.singular_logical_classificatory_closed = closed
    state.singular_level_evidence["logical_classificatory"] = evidence
    state.singular_level_blockers["logical_classificatory"] = blocker
    state.singular_rank_states["logical_classificatory"] = closed
    state.singular_rank_sublayers["logical_classificatory"] = evidence
    state.singular_rank_blockers["logical_classificatory"] = blocker
    state.add_trace(
        "singular_logical_classificatory_closure",
        {"closed": closed, "blocker": blocker, "evidence": evidence},
    )
    return state
