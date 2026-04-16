from core.model import ProofState


def apply_singular_informational_closure(state: ProofState) -> ProofState:
    state.singular_informational_closed = state.singular_perceptual_closed and state.admissible
    state.add_trace("singular_informational_closure", {"closed": state.singular_informational_closed})
    return state
