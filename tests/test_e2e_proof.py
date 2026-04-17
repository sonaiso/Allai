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
from core.ingress.admissibility_pre_u0 import apply_admissibility_pre_u0
from core.ingress.unicode_ingress import apply_unicode_ingress
from core.judgement.proposition_to_judgement import transition_proposition_to_judgement
from core.model import ProofState
from core.proposition.proposition_closure import apply_proposition_closure
from core.singular.closure_contracts import enforce_singular_closure
from core.singular.closure_record import assemble_singular_closure_record
from core.singular.conceptual_closure import apply_singular_conceptual_closure
from core.singular.informational_closure import apply_singular_informational_closure
from core.singular.logical_classificatory_closure import apply_singular_logical_classificatory_closure
from core.singular.perceptual_closure import apply_singular_perceptual_closure
from core.singular.unified_closure import apply_singular_unified_closure
from core.singular.weight_handoff_closure import apply_singular_weight_handoff_closure
from core.trace.replay_engine import replay_digest
from core.trace.singular_trace import emit_singular_trace
from core.weight.derivational_eligibility import determine_derivational_eligibility
from core.weight.mizan_closure import apply_mizan_closure
from core.weight.weight_legality import verify_weight_legality


class EndToEndProofTests(unittest.TestCase):
    def test_end_to_end_proof_flow(self) -> None:
        state = ProofState(ingress_text="النص / واضح")

        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)

        apply_singular_perceptual_closure(state)
        apply_singular_informational_closure(state)
        apply_singular_conceptual_closure(state)

        apply_mizan_closure(state)
        legal = verify_weight_legality(state)
        determine_derivational_eligibility(state, legal)
        apply_singular_weight_handoff_closure(state)
        apply_singular_logical_classificatory_closure(state)
        apply_singular_unified_closure(state)
        assemble_singular_closure_record(state)
        enforce_singular_closure(state)
        emit_singular_trace(state)

        apply_role_distribution_composition(state)
        detect_ambiguity(state)
        rank_ambiguity_candidates(state)
        resolve_ambiguity_conflicts(state)
        apply_communicative_closure(state)

        apply_proposition_closure(state)
        transition_proposition_to_judgement(state)

        digest_1 = replay_digest(state)
        digest_2 = replay_digest(state)

        self.assertEqual(state.judgement, "accepted")
        self.assertTrue(state.proposition_closed)
        self.assertTrue(state.communicative_closed)
        self.assertTrue(state.ready_for_composition)
        self.assertIn("minimum_gate_snapshot", state.singular_closure_record)
        self.assertIn("deferred_analysis_snapshot", state.singular_closure_record)
        self.assertIn("unified_closure", state.singular_closure_record["minimum_gate_snapshot"])
        self.assertEqual(digest_1, digest_2)


if __name__ == "__main__":
    unittest.main()
