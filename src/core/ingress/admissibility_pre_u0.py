from core.model import ProofState


_ALLOWED_CONTROLS = {"\n", "\t", "\r"}


def _contains_forbidden_controls(text: str) -> bool:
    for char in text:
        if ord(char) < 32 and char not in _ALLOWED_CONTROLS:
            return True
    return False


def apply_admissibility_pre_u0(state: ProofState) -> ProofState:
    text = state.effective_text()
    state.admissible = bool(text.strip()) and not _contains_forbidden_controls(text)
    state.add_trace("admissibility_checked", {"admissible": state.admissible})
    return state
