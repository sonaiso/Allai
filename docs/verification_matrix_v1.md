# Verification Matrix v1

| Constitutional Clause | Module | Invariant | Test | Trace Evidence |
|---|---|---|---|---|
| No composition without complete singular closure record | `src/core/gates/validator.py` | Reject composition when closure record missing/incomplete | `tests/test_contract_invariants.py::test_composition_rejected_without_required_closures` | `composition_rejected` event |
| Six-level singular closure thresholding | `src/core/singular/*.py` | Each level depends on prior level and sets blocker on failure | `tests/test_unit_closures.py::test_six_level_singular_closure_progression` | `singular_*_closure` events |
| No-jump weight handoff | `src/core/singular/weight_handoff_closure.py` | Reject weight handoff before relational closure | `tests/test_unit_closures.py::test_no_jump_weight_handoff_rejected_without_relational` | `singular_weight_handoff_closure` event |
| Closure record completeness threshold | `src/core/singular/closure_record.py` | `ready_for_composition` false when any level is incomplete | `tests/test_unit_closures.py::test_closure_record_threshold_requires_all_levels` | `singular_closure_record_assembled` event |
| Admissibility enforced pre-U0 | `src/core/ingress/admissibility_pre_u0.py` | Reject empty/control-heavy ingress | `tests/test_unit_closures.py::test_admissibility_flags_invalid_text` | `admissibility_checked` event |
| Ordered trace-chain validation with six-level events | `src/core/trace/chain_validation.py` | Reject out-of-order required constitutional events | `tests/test_negative_cases.py::test_trace_validation_rejects_out_of_order_required_events` | `trace_chain_rejected` event |
| Replay determinism | `src/core/trace/replay_engine.py` | Same trace yields same digest | `tests/test_e2e_proof.py::test_end_to_end_proof_flow` | `replay_generated` event |
| No judgement without proposition + communicative + ambiguity + valid trace | `src/core/judgement/proposition_to_judgement.py` | Reject judgement when constitutional preconditions fail | `tests/test_contract_invariants.py::test_judgement_requires_constitutional_preconditions` | `judgement_rejected` event |
