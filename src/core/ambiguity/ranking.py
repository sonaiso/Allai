from core.model import ProofState


def rank_ambiguity_candidates(state: ProofState) -> ProofState:
    ranked = sorted(state.ambiguity_candidates, key=lambda c: c["marker"])
    for idx, item in enumerate(ranked, start=1):
        item["rank"] = idx
        item["ranking_reason"] = "lexicographic_stability"

    state.ambiguity_candidates = ranked
    state.add_trace("ambiguity_ranked", {"ranked": ranked})
    return state
