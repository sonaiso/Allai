from core.model import ProofState


def determine_derivational_eligibility(state: ProofState, weight_legal: bool) -> ProofState:
    state.derivational_eligible = bool(weight_legal and state.weight_closed)
    state.add_trace("derivational_eligibility", {"eligible": state.derivational_eligible})
    return state
