from core.model import ProofState
from core.singular._helpers import _set_rank_blocked


def apply_singular_relational_closure(state: ProofState) -> ProofState:
    if not state.singular_identity_closed:
        _set_rank_blocked(state, "relational", "prior_level_incomplete:identity")
        return state

    identity = state.singular_level_evidence.get("identity", {})
    identity_higher = identity.get("higher_analysis", {})
    word_class = identity_higher.get("word_class")

    minimum_conditions = {
        "accepts_relation": word_class in {"noun", "verb", "particle"},
        "has_primary_relation_type": word_class in {"noun", "verb", "particle"},
    }
    higher_analysis = {
        "can_be_agent": word_class == "noun",
        "can_be_patient": word_class == "noun",
        "can_be_cause": word_class in {"noun", "verb"},
        "can_be_effect": word_class == "verb",
        "can_be_linker": word_class == "particle",
        "can_take_predication": word_class in {"noun", "verb"},
    }
    evidence = {
        "minimum_conditions": minimum_conditions,
        "higher_analysis": higher_analysis,
    }
    closed = all(minimum_conditions.values())
    blocker = None if closed else "relational_capacity_unresolved"

    state.singular_relational_closed = closed
    state.singular_level_evidence["relational"] = evidence
    state.singular_level_blockers["relational"] = blocker
    state.singular_rank_states["relational"] = closed
    state.singular_rank_sublayers["relational"] = evidence
    state.singular_rank_blockers["relational"] = blocker
    state.add_trace("singular_relational_closure", {"closed": closed, "blocker": blocker, "evidence": evidence})
    return state
