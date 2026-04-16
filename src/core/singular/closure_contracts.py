from core.model import ProofState


class SingularClosureError(ValueError):
    pass


def enforce_singular_closure(state: ProofState) -> None:
    if not (
        state.singular_perceptual_closed
        and state.singular_informational_closed
        and state.singular_conceptual_closed
    ):
        state.add_trace("singular_contract_rejected", {"reason": "incomplete_singular_closure"})
        raise SingularClosureError("Singular closure contracts are not satisfied.")

    state.add_trace("singular_contract_satisfied", {})
