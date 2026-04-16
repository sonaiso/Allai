from formal.model import ProofState


def can_close_for_judgement(state: ProofState) -> bool:
    return all(
        [
            state.perception_closed,
            state.information_closed,
            state.concept_closed,
            bool(state.roles),
            bool(state.relations.get("asnadi")),
            bool(state.relations.get("tadmini")),
            bool(state.relations.get("taqyidi")),
            bool(state.factors),
            bool(state.case_effects),
            state.communicative_mode is not None,
        ]
    )
