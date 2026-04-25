from core.gates.validator import require_for_judgement
from core.judgement.explanation_panel import build_explanation_panel
from core.model import ProofState
from core.trace.chain_validation import validate_trace_chain


def transition_proposition_to_judgement(state: ProofState) -> ProofState:
    trace_chain_valid = validate_trace_chain(state)
    require_for_judgement(state, trace_chain_valid=trace_chain_valid)

    # تحديد الحكم مع مراعاة المجاز
    metaphor_result = state.conceptual_state.get("metaphor_result", {})
    rejection_passed = state.conceptual_state.get("rejection_gate_passed", True)

    if state.proposition_closed:
        if metaphor_result.get("metaphor_applied") and not rejection_passed:
            state.judgement = "metaphorical_accepted"
        else:
            state.judgement = "accepted"
    else:
        state.judgement = "rejected"

    # بناء لوحة التفسير
    panel = build_explanation_panel(state)
    state.explanation_panel = panel.to_dict()

    state.add_trace(
        "judgement_issued",
        {
            "judgement": state.judgement,
            "explanation_panel_built": True,
        },
    )
    return state

