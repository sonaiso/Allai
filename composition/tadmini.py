from formal.model import Decision, ProofState


def evaluate_tadmini(state: ProofState) -> tuple[Decision, str, dict]:
    tadmini = len(state.tokens) >= 2
    state.relations["tadmini"] = tadmini
    if tadmini:
        return Decision.PASS, "Tadmini relation established.", {"tadmini": True}
    return Decision.SUSPEND, "Tadmini relation unresolved.", {"tadmini": False}
