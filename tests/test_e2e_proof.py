import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from arabic_engine.foundational.gates import (
    apply_alignment_gate,
    apply_naming_gate,
    apply_percept_gate,
    apply_pre_reality_gate,
    apply_proto_concept_gate,
)
from arabic_engine.foundational.layers import apply_ontological_property_layer
from arabic_engine.language.minimal_complete_encoding import apply_minimal_complete_encoding_contract
from arabic_engine.symbolic.encoding import apply_symbolic_encoding_layer
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
from core.world_model.closure import apply_world_model_closure
from core.world_model.extractor import extract_world_model


class EndToEndProofTests(unittest.TestCase):
    def test_end_to_end_proof_flow(self) -> None:
        state = ProofState(ingress_text="النص / واضح")

        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_alignment_gate(state)
        apply_naming_gate(state)

        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_ontological_property_layer(state)
        apply_symbolic_encoding_layer(state)
        apply_minimal_complete_encoding_contract(state)

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
        extract_world_model(state)
        apply_world_model_closure(state)
        transition_proposition_to_judgement(state)

        digest_1 = replay_digest(state)
        digest_2 = replay_digest(state)

        self.assertEqual(state.judgement, "accepted")
        self.assertTrue(state.proposition_closed)
        self.assertTrue(state.communicative_closed)
        self.assertTrue(state.world_model_closed)
        self.assertTrue(state.ready_for_composition)
        self.assertIn("minimum_gate_snapshot", state.singular_closure_record)
        self.assertIn("deferred_analysis_snapshot", state.singular_closure_record)
        self.assertIn("unified_closure", state.singular_closure_record["minimum_gate_snapshot"])
        self.assertIn("pre_language", state.conceptual_state)
        self.assertIn("symbolic_encoding_layer", state.symbolic_state)
        self.assertEqual(digest_1, digest_2)
        self.assertIn("entities", state.world_model)
        self.assertIn("laws", state.world_model)
        self.assertTrue(state.world_model.get("closed"))


if __name__ == "__main__":
    unittest.main()
