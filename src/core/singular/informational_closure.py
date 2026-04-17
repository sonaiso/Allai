from core.model import ProofState
from core.singular.designation_closure import apply_singular_designation_closure
from core.singular.possibility_closure import apply_singular_possibility_closure


def apply_singular_informational_closure(state: ProofState) -> ProofState:
    apply_singular_designation_closure(state)
    apply_singular_possibility_closure(state)
    state.singular_informational_closed = state.singular_designation_closed and state.singular_possibility_closed
    state.add_trace(
        "singular_informational_closure",
        {
            "closed": state.singular_informational_closed,
            "mapped_to": ["designation", "possibility"],
        },
    )
    return state
