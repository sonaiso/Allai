import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.ambiguity.conflict_resolution import resolve_ambiguity_conflicts
from core.ambiguity.detection import detect_ambiguity
from core.ambiguity.ranking import rank_ambiguity_candidates
from core.communication.communicative_closure import apply_communicative_closure
from core.composition.role_distribution import apply_role_distribution_composition
from core.gates.validator import GateViolationError
from core.ingress.admissibility_pre_u0 import apply_admissibility_pre_u0
from core.ingress.unicode_ingress import apply_unicode_ingress
from core.model import ProofState
from core.proposition.proposition_closure import apply_proposition_closure
from core.singular.closure_contracts import SingularClosureError, enforce_singular_closure
from core.singular.closure_record import assemble_singular_closure_record
from core.singular.conceptual_closure import apply_singular_conceptual_closure
from core.singular.designation_closure import apply_singular_designation_closure
from core.singular.identity_closure import apply_singular_identity_closure
from core.singular.logical_classificatory_closure import apply_singular_logical_classificatory_closure
from core.singular.possibility_closure import apply_singular_possibility_closure
from core.singular.unified_closure import apply_singular_unified_closure
from core.trace.chain_validation import validate_trace_chain
from core.trace.replay_engine import replay_digest
from core.trace.singular_trace import emit_singular_trace
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

    def test_role_distribution_rejects_single_token(self) -> None:
        state = ProofState(
            ingress_text="solo",
            normalized_text="solo",
            singular_perceptual_closed=True,
            singular_informational_closed=True,
            singular_conceptual_closed=True,
            weight_closed=True,
        )
        with self.assertRaises(GateViolationError):
            apply_role_distribution_composition(state)
        self.assertEqual(state.trace_chain[-1]["event"], "composition_rejected")

    def test_conflict_resolution_suspends_when_detected_without_candidates(self) -> None:
        state = ProofState(ingress_text="x", ambiguity_detected=True, ambiguity_candidates=[])
        resolve_ambiguity_conflicts(state)
        self.assertEqual(state.ambiguity_outcome, "suspended")
        self.assertEqual(state.ambiguity_reason, "detected_but_unranked")

    def test_conflict_resolution_resolves_when_not_detected(self) -> None:
        state = ProofState(ingress_text="x", ambiguity_detected=False)
        resolve_ambiguity_conflicts(state)
        self.assertEqual(state.ambiguity_outcome, "resolved")
        self.assertEqual(state.ambiguity_reason, "no_ambiguity_detected")

    def test_ambiguity_detection_and_ranking_assigns_stable_order(self) -> None:
        state = ProofState(ingress_text="A OR B / C ?")
        detect_ambiguity(state)
        self.assertTrue(state.ambiguity_detected)
        self.assertEqual({c["marker"] for c in state.ambiguity_candidates}, {"/", "?", "or"})

        rank_ambiguity_candidates(state)
        ranked_markers = [c["marker"] for c in state.ambiguity_candidates]
        self.assertEqual(ranked_markers, ["/", "?", "or"])
        self.assertEqual([c["rank"] for c in state.ambiguity_candidates], [1, 2, 3])

    def test_communicative_closure_requires_reason(self) -> None:
        state = ProofState(ingress_text="x", ambiguity_outcome="resolved", ambiguity_reason="")
        apply_communicative_closure(state)
        self.assertFalse(state.communicative_closed)

    def test_singular_conceptual_closure_requires_non_empty_tokens(self) -> None:
        state = ProofState(
            ingress_text="   ",
            normalized_text="   ",
            singular_informational_closed=True,
        )
        apply_singular_conceptual_closure(state)
        self.assertFalse(state.singular_conceptual_closed)

    def test_emit_singular_trace_captures_current_closure_flags(self) -> None:
        state = ProofState(
            ingress_text="x",
            singular_perceptual_closed=True,
            singular_informational_closed=False,
            singular_conceptual_closed=True,
        )
        emit_singular_trace(state)
        self.assertEqual(state.trace_chain[-1]["event"], "singular_trace_emitted")
        self.assertEqual(
            state.trace_chain[-1]["payload"],
            {"perceptual": True, "informational": False, "conceptual": True},
        )

    def test_verify_weight_legality_requires_closed_weight(self) -> None:
        state = ProofState(ingress_text="x", weight_closed=False, weight_label="fa3ala")
        self.assertFalse(verify_weight_legality(state))

    def test_proposition_closure_requires_composition_and_communication(self) -> None:
        state = ProofState(ingress_text="x", composition={"subject": "x"}, communicative_closed=False)
        apply_proposition_closure(state)
        self.assertFalse(state.proposition_closed)

    def test_designation_rejects_when_existence_not_closed(self) -> None:
        state = ProofState(ingress_text="x", singular_existence_closed=False)
        apply_singular_designation_closure(state)
        self.assertFalse(state.singular_designation_closed)
        self.assertEqual(state.singular_level_blockers["designation"], "prior_level_incomplete:existence")

    def test_possibility_rejects_when_designation_not_closed(self) -> None:
        state = ProofState(ingress_text="x", singular_designation_closed=False)
        apply_singular_possibility_closure(state)
        self.assertFalse(state.singular_possibility_closed)
        self.assertEqual(state.singular_level_blockers["possibility"], "prior_level_incomplete:designation")

    def test_logical_classificatory_rejects_when_weight_rank_incomplete(self) -> None:
        state = ProofState(ingress_text="x", singular_weight_closed=False)
        apply_singular_logical_classificatory_closure(state)
        self.assertFalse(state.singular_logical_classificatory_closed)
        self.assertEqual(state.singular_level_blockers["logical_classificatory"], "prior_rank_incomplete:weight")

    def test_identity_detects_verb_word_class_from_prefix(self) -> None:
        state = ProofState(
            ingress_text="يكتب بسرعة",
            normalized_text="يكتب بسرعة",
            singular_possibility_closed=True,
        )
        apply_singular_identity_closure(state)
        self.assertEqual(state.singular_level_evidence["identity"]["higher_analysis"]["word_class"], "verb")

    def test_mizan_marks_empty_input_as_not_closed(self) -> None:
        state = ProofState(ingress_text="   ", normalized_text="   ")
        apply_mizan_closure(state)
        self.assertIsNone(state.weight_label)
        self.assertFalse(state.weight_closed)

    def test_unified_closure_rejects_when_no_required_ranks_are_closed(self) -> None:
        state = ProofState(ingress_text="x")
        apply_singular_unified_closure(state)
        self.assertEqual(state.singular_final_decision, "REJECT")
        self.assertFalse(state.ready_for_composition)

    def test_closure_record_derives_pass_and_suspend_without_precomputed_decision(self) -> None:
        pass_state = ProofState(ingress_text="x", singular_unified_closure_closed=True)
        assemble_singular_closure_record(pass_state)
        self.assertEqual(pass_state.singular_closure_record["final_decision"], "PASS")

        suspend_state = ProofState(ingress_text="x", singular_unified_closure_closed=False)
        assemble_singular_closure_record(suspend_state)
        self.assertEqual(suspend_state.singular_closure_record["final_decision"], "SUSPEND")

    def test_closure_record_marks_complete_when_composition_exists(self) -> None:
        state = ProofState(
            ingress_text="x",
            singular_final_decision="PASS",
            singular_final_decision_reason="all_required_ranks_closed",
            ready_for_composition=True,
            composition={"subject": "x"},
        )
        assemble_singular_closure_record(state)
        self.assertEqual(state.singular_closure_record["final_decision"], "COMPLETE")
        self.assertEqual(state.singular_closure_record["final_decision_reason"], "unified_closure_complete_and_composed")

    def test_closure_record_prefers_rank_blocker_when_present(self) -> None:
        state = ProofState(
            ingress_text="x",
            singular_final_decision="SUSPEND",
            singular_level_blockers={"identity": "identity_unresolved"},
            singular_rank_blockers={"identity": "rank_specific_identity_blocker"},
        )
        assemble_singular_closure_record(state)
        self.assertEqual(
            state.singular_closure_record["hierarchical_blockers"]["identity"],
            "rank_specific_identity_blocker",
        )


if __name__ == "__main__":
    unittest.main()
