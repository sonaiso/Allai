from core.model import ProofState


ARABIC_DIACRITICS = {"\u064e", "\u064f", "\u0650", "\u0652", "\u064b", "\u064c", "\u064d"}


def apply_singular_existence_closure(state: ProofState) -> ProofState:
    text = state.effective_text()
    evidence = {
        "unicode_presence": bool(text),
        "char_presence": any(not ch.isspace() for ch in text),
        "marked_unit_presence": any(ch.isalpha() or ch in ARABIC_DIACRITICS for ch in text),
        "syllabic_presence": bool([t for t in text.split() if t]),
        "lexical_presence": bool(text.strip()),
    }
    closed = evidence["unicode_presence"] and evidence["char_presence"] and evidence["lexical_presence"]
    blocker = None if closed else "missing_observable_unit"

    state.singular_existence_closed = closed
    state.singular_level_evidence["existence"] = evidence
    state.singular_level_blockers["existence"] = blocker
    state.singular_rank_states["existence"] = closed
    state.singular_rank_sublayers["existence"] = evidence
    state.singular_rank_blockers["existence"] = blocker
    state.add_trace("singular_existence_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
