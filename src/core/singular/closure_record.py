import hashlib
import json

from core.model import ProofState


CLOSURE_RECORD_ID_PREFIX_CHARS = 16


def assemble_singular_closure_record(state: ProofState) -> ProofState:
    level_states = {
        "existence_closed": state.singular_existence_closed,
        "designation_closed": state.singular_designation_closed,
        "possibility_closed": state.singular_possibility_closed,
        "identity_closed": state.singular_identity_closed,
        "relational_closed": state.singular_relational_closed,
        "weight_closed": state.singular_weight_closed,
    }
    blockers = {
        level: blocker
        for level, blocker in state.singular_level_blockers.items()
        if blocker
    }
    ready_for_composition = all(level_states.values()) and not blockers

    seed_payload = {
        "text": state.effective_text(),
        "level_states": level_states,
        "weight_label": state.weight_label,
        "ready": ready_for_composition,
    }
    closure_record_id = hashlib.sha256(
        json.dumps(seed_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:CLOSURE_RECORD_ID_PREFIX_CHARS]

    state.closure_record_id = closure_record_id
    state.existence_closed = level_states["existence_closed"]
    state.designation_closed = level_states["designation_closed"]
    state.possibility_closed = level_states["possibility_closed"]
    state.identity_closed = level_states["identity_closed"]
    state.relational_closed = level_states["relational_closed"]
    state.weight_handoff_closed = level_states["weight_closed"]
    state.ready_for_composition = ready_for_composition
    state.singular_closure_record = {
        "closure_record_id": closure_record_id,
        **level_states,
        "ready_for_composition": ready_for_composition,
        "blockers": blockers,
        "level_evidence": state.singular_level_evidence,
    }
    state.add_trace(
        "singular_closure_record_assembled",
        {
            "closure_record_id": closure_record_id,
            "ready_for_composition": ready_for_composition,
            "blockers": blockers,
        },
    )
    return state
