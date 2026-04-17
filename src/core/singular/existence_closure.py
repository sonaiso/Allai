from core.model import ProofState


ARABIC_DIACRITICS = {"\u064e", "\u064f", "\u0650", "\u0652", "\u064b", "\u064c", "\u064d"}


def apply_singular_existence_closure(state: ProofState) -> ProofState:
    text = state.effective_text()
    minimum_conditions = {
        "presence": bool(text),
        "distinguishability": any(not ch.isspace() for ch in text),
        "non_annihilation": bool(text.strip()),
    }
    higher_analysis = {
        "unicode_presence": bool(text),
        "char_presence": any(not ch.isspace() for ch in text),
        "marked_unit_presence": any(ch.isalpha() or ch in ARABIC_DIACRITICS for ch in text),
        "syllabic_presence": bool([t for t in text.split() if t]),
        "lexical_presence": bool(text.strip()),
    }
    evidence = {
        "minimum_conditions": minimum_conditions,
        "higher_analysis": higher_analysis,
    }
    closed = all(minimum_conditions.values())
    blocker = None if closed else "missing_observable_unit"

    state.singular_existence_closed = closed
    state.singular_level_evidence["existence"] = evidence
    state.singular_level_blockers["existence"] = blocker
    state.singular_rank_states["existence"] = closed
    state.singular_rank_sublayers["existence"] = evidence
    state.singular_rank_blockers["existence"] = blocker
    state.add_trace("singular_existence_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
