from core.constants import ALLOWED_WEIGHTS
from core.model import ProofState


def verify_weight_legality(state: ProofState) -> bool:
    legal = state.weight_closed and state.weight_label in ALLOWED_WEIGHTS
    state.add_trace("weight_legality_checked", {"legal": legal})
    return legal
