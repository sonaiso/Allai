from core.model import ProofState


_ALLOWED = {"fa3ala", "maf3ul", "fi3l"}


def verify_weight_legality(state: ProofState) -> bool:
    legal = state.weight_closed and state.weight_label in _ALLOWED
    state.add_trace("weight_legality_checked", {"legal": legal})
    return legal
