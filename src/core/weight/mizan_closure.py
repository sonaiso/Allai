from core.constants import ALLOWED_WEIGHTS
from core.model import ProofState


def apply_mizan_closure(state: ProofState) -> ProofState:
    token_count = len([t for t in state.effective_text().split() if t])
    if token_count == 0:
        state.weight_label = None
    elif token_count >= 3:
        state.weight_label = "fa3ala"
    elif token_count == 2:
        state.weight_label = "maf3ul"
    else:
        state.weight_label = "fi3l"

    state.weight_closed = state.weight_label in ALLOWED_WEIGHTS
    state.add_trace(
        "mizan_closure",
        {"weight_label": state.weight_label, "closed": state.weight_closed, "token_count": token_count},
    )
    return state
