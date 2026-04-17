from core.model import ProofState


class GateViolationError(ValueError):
    """Raised when a constitutional gate is violated."""


def require_for_composition(state: ProofState) -> None:
    record_ready = bool(state.singular_closure_record) and state.ready_for_composition
    if not record_ready:
        state.add_trace(
            "composition_rejected",
            {
                "reason": "missing_or_incomplete_singular_closure_record",
                "closure_record_id": state.closure_record_id,
            },
        )
        raise GateViolationError("No composition without a complete singular closure record.")


def require_for_judgement(state: ProofState, trace_chain_valid: bool) -> None:
    ambiguity_ok = state.ambiguity_outcome in {"resolved", "suspended"} and bool(state.ambiguity_reason)
    proposition_integrity_ok = state.proposition_closed and bool(state.composition)
    if not (proposition_integrity_ok and state.communicative_closed and ambiguity_ok and trace_chain_valid):
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
