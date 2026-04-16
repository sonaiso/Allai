from core.model import ProofState


_REQUIRED_EVENTS_FOR_JUDGEMENT = [
    "unicode_ingress",
    "admissibility_checked",
    "singular_perceptual_closure",
    "singular_informational_closure",
    "singular_conceptual_closure",
    "mizan_closure",
    "composition_applied",
    "ambiguity_detected",
    "ambiguity_ranked",
    "ambiguity_outcome",
    "communicative_closure",
    "proposition_closure",
]


def validate_trace_chain(state: ProofState) -> bool:
    if not state.trace_chain:
        return False

    ids = [item["event_id"] for item in state.trace_chain]
    if ids != list(range(1, len(ids) + 1)):
        return False

    event_positions = {}
    for index, item in enumerate(state.trace_chain):
        event = item.get("event")
        if event not in event_positions:
            event_positions[event] = index

    if not all(event in event_positions for event in _REQUIRED_EVENTS_FOR_JUDGEMENT):
        return False

    positions = [event_positions[event] for event in _REQUIRED_EVENTS_FOR_JUDGEMENT]
    return positions == sorted(positions)
