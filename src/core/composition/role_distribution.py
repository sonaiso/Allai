from core.gates.validator import require_for_composition
from core.model import ProofState


def apply_role_distribution_composition(state: ProofState) -> ProofState:
    require_for_composition(state)

    tokens = [t for t in state.normalized_text.split() if t]
    state.composition = {
        "subject": tokens[0] if tokens else None,
        "predicate": " ".join(tokens[1:]) if len(tokens) > 1 else "implicit",
    }
    state.add_trace("composition_applied", {"composition": state.composition})
    return state
