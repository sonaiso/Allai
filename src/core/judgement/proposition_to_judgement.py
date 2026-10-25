from arabic_engine.language.agent_operator_gate import apply_agent_operator_gate
from arabic_engine.language.explanation_panel import build_explanation_panel
from arabic_engine.language.metaphor_gate import apply_metaphor_gate
from arabic_engine.language.prediction_gate import apply_prediction_gate
from arabic_engine.language.rejection_gate import apply_rejection_gate
from core.gates.validator import require_for_judgement
from core.model import ProofState
from core.trace.chain_validation import validate_trace_chain


def transition_proposition_to_judgement(state: ProofState) -> ProofState:
    trace_chain_valid = validate_trace_chain(state)
    require_for_judgement(state, trace_chain_valid=trace_chain_valid)

    # ── الطبقة الرمزية ───────────────────────────────────────────────
    agent_result = apply_agent_operator_gate(state)
    rejection = apply_rejection_gate(state, agent_result)
    metaphor = apply_metaphor_gate(state, rejection)
    apply_prediction_gate(state)

    # ── تحديد الحكم ─────────────────────────────────────────────────
    if metaphor.resolved and metaphor.judgment == "metaphorical_accepted":
        state.judgement = "metaphorical_accepted"
    elif rejection is not None and not metaphor.resolved:
        # الرفض الرمزي يتغلب على الإغلاق البنيوي للقضية
        state.judgement = "rejected"
    else:
        state.judgement = "accepted" if state.proposition_closed else "rejected"

    state.add_trace("judgement_issued", {"judgement": state.judgement})

    # ── لوحة التفسير ────────────────────────────────────────────────
    build_explanation_panel(state)

    return state
