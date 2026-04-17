from core.model import ProofState


_REQUIRED_EVENTS_FOR_JUDGEMENT = [
    "unicode_ingress",
    "admissibility_checked",
    "singular_existence_closure",
    "singular_designation_closure",
    "singular_possibility_closure",
    "singular_identity_closure",
    "singular_relational_closure",
    "mizan_closure",
    "singular_weight_handoff_closure",
    "singular_logical_classificatory_closure",
    "singular_unified_closure",
    "singular_closure_record_assembled",
    "composition_applied",
    "ambiguity_detected",
    "ambiguity_ranked",
    "ambiguity_outcome",
    "communicative_closure",
    "proposition_closure",
]


def _reject(state: ProofState, reason: str) -> bool:
    state.add_trace("trace_chain_rejected", {"reason": reason})
    return False


def validate_trace_chain(state: ProofState) -> bool:
    if not state.trace_chain:
        return _reject(state, "empty_trace_chain")

    ids = [item["event_id"] for item in state.trace_chain]
    if ids != list(range(1, len(ids) + 1)):
        return _reject(state, "non_sequential_event_ids")

    event_positions = {}
    for index, item in enumerate(state.trace_chain):
        event = item.get("event")
        if event not in event_positions:
            event_positions[event] = index

    missing = [event for event in _REQUIRED_EVENTS_FOR_JUDGEMENT if event not in event_positions]
    if missing:
        return _reject(state, f"missing_required_events:{','.join(missing)}")

    positions = [event_positions[event] for event in _REQUIRED_EVENTS_FOR_JUDGEMENT]
    if positions != sorted(positions):
        return _reject(state, "required_events_out_of_order")

    state.add_trace("trace_chain_validated", {})
    return True
