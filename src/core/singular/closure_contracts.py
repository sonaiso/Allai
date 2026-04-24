from core.exceptions import SingularClosureError
from core.model import ProofState

__all__ = ["SingularClosureError"]


def enforce_singular_closure(state: ProofState) -> None:
    if not state.ready_for_composition:
        state.add_trace(
            "singular_contract_rejected",
            {
                "reason": "incomplete_singular_closure_record",
                "closure_record_id": state.closure_record_id,
            },
        )
        raise SingularClosureError("Singular closure record is not complete.")

    state.add_trace(
        "singular_contract_satisfied",
        {
            "closure_record_id": state.closure_record_id,
            "ready_for_composition": state.ready_for_composition,
        },
    )
