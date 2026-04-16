from core.model import ProofState


def apply_singular_conceptual_closure(state: ProofState) -> ProofState:
    token_count = len([t for t in state.effective_text().split() if t])
    state.singular_conceptual_closed = state.singular_informational_closed and token_count >= 1
    state.add_trace(
        "singular_conceptual_closure",
        {"closed": state.singular_conceptual_closed, "token_count": token_count},
    )
    return state
