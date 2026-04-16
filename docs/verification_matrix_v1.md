# Verification Matrix v1

| Constitutional Clause | Module | Invariant | Test | Trace Evidence |
|---|---|---|---|---|
| No composition without singular + weight closure | `src/core/composition/role_distribution.py` | Reject composition when closures missing | `tests/test_contract_invariants.py::test_composition_rejected_without_required_closures` | `composition_rejected` event |
| Role distribution requires minimum tokens | `src/core/composition/role_distribution.py` | Reject composition when role tokens are insufficient | `tests/test_contract_invariants.py::test_composition_rejected_when_role_tokens_insufficient` | `composition_rejected` event |
| No judgement without proposition + communicative + ambiguity + valid trace | `src/core/judgement/proposition_to_judgement.py` | Reject judgement when constitutional preconditions fail | `tests/test_contract_invariants.py::test_judgement_requires_constitutional_preconditions` | `judgement_rejected` event |
| Admissibility enforced pre-U0 | `src/core/ingress/admissibility_pre_u0.py` | Reject empty/control-heavy ingress | `tests/test_unit_closures.py::test_admissibility_flags_invalid_text` | `admissibility_checked` event |
| Replay determinism | `src/core/trace/replay_engine.py` | Same trace yields same digest | `tests/test_e2e_proof.py::test_end_to_end_proof_flow` | `replay_generated` event |
| Ordered trace-chain validation | `src/core/trace/chain_validation.py` | Reject out-of-order required constitutional events | `tests/test_negative_cases.py::test_trace_validation_rejects_out_of_order_required_events` | `judgement_rejected` event |
