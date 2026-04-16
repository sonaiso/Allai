import unicodedata

from core.model import ProofState


def apply_unicode_ingress(state: ProofState) -> ProofState:
    state.normalized_text = unicodedata.normalize("NFKC", state.ingress_text or "")
    state.add_trace("unicode_ingress", {"normalized_length": len(state.normalized_text)})
    return state
