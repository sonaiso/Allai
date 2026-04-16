from core.model import ProofState


def apply_singular_perceptual_closure(state: ProofState) -> ProofState:
    state.singular_perceptual_closed = bool(state.normalized_text.strip())
    state.add_trace("singular_perceptual_closure", {"closed": state.singular_perceptual_closed})
    return state
