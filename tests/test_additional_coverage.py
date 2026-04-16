import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.ambiguity.conflict_resolution import resolve_ambiguity_conflicts
from core.composition.role_distribution import apply_role_distribution_composition
from core.ingress.admissibility_pre_u0 import apply_admissibility_pre_u0
from core.ingress.unicode_ingress import apply_unicode_ingress
from core.model import ProofState
from core.proposition.proposition_closure import apply_proposition_closure
from core.singular.closure_contracts import SingularClosureError, enforce_singular_closure
from core.trace.chain_validation import validate_trace_chain
from core.trace.replay_engine import replay_digest
from core.weight.derivational_eligibility import determine_derivational_eligibility
from core.weight.mizan_closure import apply_mizan_closure
from core.weight.weight_legality import verify_weight_legality


class AdditionalCoverageTests(unittest.TestCase):
    def test_admissibility_allows_allowed_control_characters(self) -> None:
        state = ProofState(ingress_text="line1\nline2\tend\r")
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        self.assertTrue(state.admissible)

    def test_enforce_singular_closure_rejects_incomplete_state(self) -> None:
        state = ProofState(ingress_text="text")
        with self.assertRaises(SingularClosureError):
            enforce_singular_closure(state)
        self.assertEqual(state.trace_chain[-1]["event"], "singular_contract_rejected")

    def test_validate_trace_chain_handles_invalid_cases(self) -> None:
        empty = ProofState(ingress_text="x")
        self.assertFalse(validate_trace_chain(empty))

        non_sequential = ProofState(ingress_text="x")
        non_sequential.trace_chain = [
            {"event_id": 1, "event": "unicode_ingress", "payload": {}, "timestamp": "t1"},
            {"event_id": 3, "event": "admissibility_checked", "payload": {}, "timestamp": "t2"},
        ]
        self.assertFalse(validate_trace_chain(non_sequential))

    def test_replay_digest_ignores_prior_replay_events(self) -> None:
        state = ProofState(ingress_text="x")
        state.add_trace("unicode_ingress", {"normalized_length": 1})
        digest_1 = replay_digest(state)
        digest_2 = replay_digest(state)
        self.assertEqual(digest_1, digest_2)
        replay_events = [e for e in state.trace_chain if e["event"] == "replay_generated"]
        self.assertEqual(len(replay_events), 2)

    def test_mizan_label_selection_and_legality_paths(self) -> None:
        for input_text, expected_label in [("one", "fi3l"), ("one two", "maf3ul"), ("one two three", "fa3ala")]:
            state = ProofState(ingress_text=input_text, normalized_text=input_text)
            apply_mizan_closure(state)
            self.assertEqual(state.weight_label, expected_label)
            self.assertTrue(verify_weight_legality(state))

        illegal_weight_state = ProofState(ingress_text="x", normalized_text="x", weight_closed=True, weight_label="unknown")
        self.assertFalse(verify_weight_legality(illegal_weight_state))

    def test_derivational_eligibility_requires_weight_closed(self) -> None:
        state = ProofState(ingress_text="x", weight_closed=False)
        determine_derivational_eligibility(state, weight_legal=True)
        self.assertFalse(state.derivational_eligible)

    def test_role_distribution_sets_implicit_predicate_for_single_token(self) -> None:
        state = ProofState(
            ingress_text="solo",
            normalized_text="solo",
            singular_perceptual_closed=True,
            singular_informational_closed=True,
            singular_conceptual_closed=True,
            weight_closed=True,
        )
        apply_role_distribution_composition(state)
        self.assertEqual(state.composition["subject"], "solo")
        self.assertEqual(state.composition["predicate"], "implicit")

    def test_conflict_resolution_suspends_when_detected_without_candidates(self) -> None:
        state = ProofState(ingress_text="x", ambiguity_detected=True, ambiguity_candidates=[])
        resolve_ambiguity_conflicts(state)
        self.assertEqual(state.ambiguity_outcome, "suspended")
        self.assertEqual(state.ambiguity_reason, "detected_but_unranked")

    def test_proposition_closure_requires_composition_and_communication(self) -> None:
        state = ProofState(ingress_text="x", composition={"subject": "x"}, communicative_closed=False)
        apply_proposition_closure(state)
        self.assertFalse(state.proposition_closed)


if __name__ == "__main__":
    unittest.main()
