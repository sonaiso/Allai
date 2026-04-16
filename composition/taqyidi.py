from formal.model import Decision, ProofState


def evaluate_taqyidi(state: ProofState) -> tuple[Decision, str, dict]:
    taqyidi = len(state.tokens) >= 3
    state.relations["taqyidi"] = taqyidi
    if taqyidi:
        return Decision.PASS, "Taqyidi relation established.", {"taqyidi": True}
    return Decision.SUSPEND, "Taqyidi relation unresolved.", {"taqyidi": False}
