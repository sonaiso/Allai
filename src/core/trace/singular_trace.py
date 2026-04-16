from core.model import ProofState


def emit_singular_trace(state: ProofState) -> ProofState:
    state.add_trace(
        "singular_trace_emitted",
        {
            "perceptual": state.singular_perceptual_closed,
            "informational": state.singular_informational_closed,
            "conceptual": state.singular_conceptual_closed,
        },
    )
    return state
