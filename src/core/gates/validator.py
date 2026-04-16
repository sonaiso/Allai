from core.model import ProofState


class GateViolationError(ValueError):
    """Raised when a constitutional gate is violated."""


def require_for_composition(state: ProofState) -> None:
    if not (
        state.singular_perceptual_closed
        and state.singular_informational_closed
        and state.singular_conceptual_closed
        and state.weight_closed
    ):
        state.add_trace("composition_rejected", {"reason": "missing_singular_or_weight_closure"})
        raise GateViolationError("No composition without singular closure + weight closure.")


def require_for_judgement(state: ProofState, trace_chain_valid: bool) -> None:
    ambiguity_ok = state.ambiguity_outcome in {"resolved", "suspended"} and bool(state.ambiguity_reason)
    if not (state.proposition_closed and state.communicative_closed and ambiguity_ok and trace_chain_valid):
        state.add_trace(
            "judgement_rejected",
            {
                "reason": "missing_proposition_or_communication_or_ambiguity_or_trace_validity",
                "trace_chain_valid": trace_chain_valid,
            },
        )
        raise GateViolationError(
            "No judgement without proposition closure + communicative closure + ambiguity resolution/suspend + valid trace chain."
        )
