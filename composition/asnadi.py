from formal.model import Decision, ProofState


def evaluate_asnadi(state: ProofState) -> tuple[Decision, str, dict]:
    asnadi = bool(state.roles.get("fa_iliya") and state.roles.get("maf_uliya"))
    state.relations["asnadi"] = asnadi
    if asnadi:
        return Decision.PASS, "Asnadi relation established.", {"asnadi": True}
    return Decision.SUSPEND, "Asnadi relation unresolved.", {"asnadi": False}
