from core.gates.validator import GateViolationError, require_for_composition
from core.model import ProofState

MIN_ROLE_TOKENS = 2


def apply_role_distribution_composition(state: ProofState) -> ProofState:
    require_for_composition(state)

    tokens = [t for t in state.effective_text().split() if t]
    if len(tokens) < MIN_ROLE_TOKENS:
        state.add_trace("composition_rejected", {"reason": "insufficient_tokens_for_role_distribution"})
        raise GateViolationError("Composition requires at least two tokens for role distribution.")

    state.composition = {
        "subject": tokens[0],
        "predicate": " ".join(tokens[1:]),
    }
    state.add_trace("composition_applied", {"composition": state.composition})
    return state
