from core.model import ProofState


def apply_proposition_closure(state: ProofState) -> ProofState:
    state.proposition_closed = bool(state.composition) and state.communicative_closed
    state.add_trace("proposition_closure", {"closed": state.proposition_closed})
    return state
