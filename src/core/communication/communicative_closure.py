from core.model import ProofState


def apply_communicative_closure(state: ProofState) -> ProofState:
    state.communicative_closed = state.ambiguity_outcome in {"resolved", "suspended"} and bool(state.ambiguity_reason)
    state.add_trace("communicative_closure", {"closed": state.communicative_closed})
    return state
