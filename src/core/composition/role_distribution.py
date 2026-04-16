from core.gates.validator import GateViolationError, require_for_composition
from core.model import ProofState


def apply_role_distribution_composition(state: ProofState) -> ProofState:
    require_for_composition(state)

    tokens = [t for t in state.effective_text().split() if t]
    if len(tokens) < 2:
        state.add_trace("composition_rejected", {"reason": "insufficient_tokens_for_role_distribution"})
        raise GateViolationError("Composition requires at least two tokens for role distribution.")

    state.composition = {
        "subject": tokens[0] if tokens else None,
        "predicate": " ".join(tokens[1:]),
    }
    state.add_trace("composition_applied", {"composition": state.composition})
    return state
