from formal.model import Decision, ProofState


def evaluate_case_effects(state: ProofState) -> tuple[Decision, str, dict]:
    if not state.factors:
        return Decision.SUSPEND, "Case effects unresolved: missing factors.", {"case_effects": {}}

    state.case_effects = {
        "traceable_effect": True,
        "effect_source": "role_distribution_and_factors",
    }
    return Decision.PASS, "Case effects interpreted as decision traces.", {"case_effects": state.case_effects}
