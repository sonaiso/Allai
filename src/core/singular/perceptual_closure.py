from core.model import ProofState
from core.singular.existence_closure import apply_singular_existence_closure


def apply_singular_perceptual_closure(state: ProofState) -> ProofState:
    apply_singular_existence_closure(state)
    state.singular_perceptual_closed = state.singular_existence_closed
    state.add_trace(
        "singular_perceptual_closure",
        {
            "closed": state.singular_perceptual_closed,
            "mapped_to": "existence",
        },
    )
    return state
