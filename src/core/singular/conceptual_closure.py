from core.model import ProofState
from core.singular.identity_closure import apply_singular_identity_closure
from core.singular.relational_closure import apply_singular_relational_closure


def apply_singular_conceptual_closure(state: ProofState) -> ProofState:
    apply_singular_identity_closure(state)
    apply_singular_relational_closure(state)
    state.singular_conceptual_closed = state.singular_identity_closed and state.singular_relational_closed
    state.add_trace(
        "singular_conceptual_closure",
        {
            "closed": state.singular_conceptual_closed,
            "mapped_to": ["identity", "relational"],
        },
    )
    return state
