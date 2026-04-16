from formal.model import Decision, ProofState


def evaluate_factors(state: ProofState) -> tuple[Decision, str, dict]:
    if not state.relations.get("asnadi"):
        return Decision.SUSPEND, "Factors unresolved: asnadi relation not closed.", {"factors": {}}

    state.factors = {
        "role_distributor": "active",
        "effect_generator": "active",
        "legality_model": "active",
    }
    return Decision.PASS, "Factors modeled as rationality generators.", {"factors": state.factors}
