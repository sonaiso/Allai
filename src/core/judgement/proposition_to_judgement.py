from core.gates.validator import require_for_judgement
from core.model import ProofState
from core.trace.chain_validation import validate_trace_chain


def transition_proposition_to_judgement(state: ProofState) -> ProofState:
    trace_chain_valid = validate_trace_chain(state)
    require_for_judgement(state, trace_chain_valid=trace_chain_valid)

    state.judgement = "accepted" if state.proposition_closed else "rejected"
    state.add_trace("judgement_issued", {"judgement": state.judgement})
    return state
