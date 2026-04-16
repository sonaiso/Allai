from formal.model import Decision, ProofState


def classify_mode(state: ProofState) -> tuple[Decision, str, dict]:
    if state.normalized_unicode is None:
        return Decision.SUSPEND, "Communicative mode unresolved: no normalized text.", {"mode": None}

    mode = "insha" if "؟" in state.normalized_unicode or "?" in state.normalized_unicode else "khabar"
    state.communicative_mode = mode
    return Decision.PASS, "Communicative mode classified.", {"mode": mode}
