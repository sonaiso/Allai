from core.model import ProofState


VERB_PREFIXES = ("ي", "ت")
DEFINITE_ARTICLE = "ال"
FEMININE_MARKER = "ة"


def _determine_word_class(tokens: list[str]) -> str:
    first = tokens[0] if tokens else ""
    if first.startswith(VERB_PREFIXES):
        return "verb"
    return "noun" if first else ""


def apply_singular_identity_closure(state: ProofState) -> ProofState:
    if not state.singular_possibility_closed:
        blocker = "prior_level_incomplete:possibility"
        state.singular_identity_closed = False
        state.singular_level_evidence["identity"] = {}
        state.singular_level_blockers["identity"] = blocker
        state.singular_rank_states["identity"] = False
        state.singular_rank_sublayers["identity"] = {}
        state.singular_rank_blockers["identity"] = blocker
        state.add_trace("singular_identity_closure", {"closed": False, "blocker": blocker})
        return state

    tokens = [t for t in state.effective_text().split() if t]
    first = tokens[0] if tokens else ""
    word_class = _determine_word_class(tokens)

    minimum_conditions = {
        "has_grammatical_class": bool(word_class),
        "has_referential_status": True,
        "has_inflection_mode": True,
        "has_derivation_mode": True,
    }
    higher_analysis = {
        "word_class": word_class,
        "definiteness": "definite" if first.startswith(DEFINITE_ARTICLE) else "indefinite",
        "gender": "feminine" if first.endswith(FEMININE_MARKER) else "masculine",
        "derivation": "derived" if len(first) >= 3 else "primitive",
        "inflection_type": "mu'rab" if len(tokens) >= 2 else "mabni",
        "referential_status": "referential" if first else "non_referential",
    }
    evidence = {
        "minimum_conditions": minimum_conditions,
        "higher_analysis": higher_analysis,
    }
    closed = all(minimum_conditions.values())
    blocker = None if closed else "identity_unresolved"

    state.singular_identity_closed = closed
    state.singular_level_evidence["identity"] = evidence
    state.singular_level_blockers["identity"] = blocker
    state.singular_rank_states["identity"] = closed
    state.singular_rank_sublayers["identity"] = evidence
    state.singular_rank_blockers["identity"] = blocker
    state.add_trace("singular_identity_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
