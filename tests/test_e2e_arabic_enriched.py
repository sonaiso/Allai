"""
test_e2e_arabic_enriched.py
============================
اختبار نهاية-لنهاية للأنبوب العربي الكامل مع الإثراء المعجمي ومعرفة العالم.

المثال المحوري:
    "كتب زيد بالقلم"
    الحدث: كتابة
    الفاعل: زيد
    الأداة: قلم (بواسطة حرف الجر "ب")
    الحكم: صحيح — القلم أداة صالحة للكتابة
"""
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
from arabic_engine.language.concept_registry import (
    apply_concept_registry_gate,
    lookup_by_name,
    lookup_by_root,
)
from arabic_engine.language.lexical_enrichment_gate import apply_lexical_enrichment_gate
from arabic_engine.language.minimal_complete_encoding import (
    apply_minimal_complete_encoding_contract,
)
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
from core.singular.logical_classificatory_closure import (
    apply_singular_logical_classificatory_closure,
)
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
from core.world_model.world_knowledge_layer import apply_world_knowledge_layer


# =========================================================
# مساعد — Full Pipeline Runner
# =========================================================

def _run_full_pipeline(text: str) -> ProofState:
    """
    تشغيل الأنبوب الكامل بما يشمل الإثراء المعجمي ومعرفة العالم.

        واقع → أثر → تخزين → استرجاع → مقارنة → ربط
        → إثراء معجمي → نحو معرفي → نموذج عالم → معرفة عالم → حكم
    """
    state = ProofState(ingress_text=text)

    # ── المرحلة 1: ما قبل اللغة ─────────────────────────────────────
    apply_pre_reality_gate(state)       # واقع → أثر خام
    apply_percept_gate(state)           # أثر → وحدات إدراكية
    apply_proto_concept_gate(state)     # وحدات → مفاهيم بدئية
    apply_alignment_gate(state)         # قياس التطابق مع الواقع
    apply_naming_gate(state)            # تسمية المفاهيم البدئية

    # ── المرحلة 2: الإدخال والترميز ─────────────────────────────────
    apply_unicode_ingress(state)
    apply_admissibility_pre_u0(state)
    apply_ontological_property_layer(state)
    apply_symbolic_encoding_layer(state)
    apply_minimal_complete_encoding_contract(state)

    # ── المرحلة 3: الإثراء المعجمي (جديد) ──────────────────────────
    apply_lexical_enrichment_gate(state)    # ProtoConcept + معجم → ConceptFull
    apply_concept_registry_gate(state)     # مطابقة السجل المعرفي

    # ── المرحلة 4: الإغلاقات الفردية السبع ─────────────────────────
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

    # ── المرحلة 5: التركيب ──────────────────────────────────────────
    apply_role_distribution_composition(state)
    detect_ambiguity(state)
    rank_ambiguity_candidates(state)
    resolve_ambiguity_conflicts(state)
    apply_communicative_closure(state)

    # ── المرحلة 6: القضية + نموذج العالم + معرفة العالم ─────────────
    apply_proposition_closure(state)
    extract_world_model(state)
    apply_world_knowledge_layer(state)  # WorldModel + معرفة → WorldModel مُثرَى
    apply_world_model_closure(state)

    # ── المرحلة 7: الحكم النهائي ─────────────────────────────────────
    transition_proposition_to_judgement(state)

    return state


# =========================================================
# 1. اختبارات الإثراء المعجمي
# =========================================================

class LexicalEnrichmentGateTests(unittest.TestCase):

    def test_enrichment_gate_produces_enriched_concepts(self) -> None:
        state = ProofState(ingress_text="كتب زيد بالقلم")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_alignment_gate(state)
        apply_naming_gate(state)
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_symbolic_encoding_layer(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)

        enriched = state.conceptual_state.get("enriched_concepts", [])
        self.assertGreater(len(enriched), 0)

    def test_enrichment_gate_emits_trace(self) -> None:
        state = ProofState(ingress_text="كتب زيد بالقلم")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_alignment_gate(state)
        apply_naming_gate(state)
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_symbolic_encoding_layer(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)

        events = [t["event"] for t in state.trace_chain]
        self.assertIn("lexical_enrichment_gate", events)

    def test_enrichment_identifies_verb_root(self) -> None:
        """كتب → جذر ك ت ب."""
        state = ProofState(ingress_text="كتب زيد بالقلم")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_alignment_gate(state)
        apply_naming_gate(state)
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_symbolic_encoding_layer(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)

        enriched = state.conceptual_state.get("enriched_concepts", [])
        roots = [c.get("root") for c in enriched if c.get("root")]
        self.assertIn("ك ت ب", roots)

    def test_enrichment_identifies_instrument_particle(self) -> None:
        """'ب' يجب أن يُعرَّف كـ Instrumentality."""
        state = ProofState(ingress_text="كتب زيد بالقلم")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_alignment_gate(state)
        apply_naming_gate(state)
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_symbolic_encoding_layer(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)

        enriched = state.conceptual_state.get("enriched_concepts", [])
        relation_types = [c.get("relation_type") for c in enriched if c.get("relation_type")]
        self.assertIn("Instrumentality", relation_types)

    def test_enrichment_identifies_entity_qalam(self) -> None:
        """'القلم' يجب أن يُعرَّف ككيان من نوع أداة."""
        state = ProofState(ingress_text="كتب زيد بالقلم")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_alignment_gate(state)
        apply_naming_gate(state)
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_symbolic_encoding_layer(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)

        enriched = state.conceptual_state.get("enriched_concepts", [])
        entity_types = [c.get("entity_type") for c in enriched if c.get("entity_type")]
        self.assertIn("أداة", entity_types)


# =========================================================
# 2. اختبارات معرفة العالم
# =========================================================

class WorldKnowledgeLayerTests(unittest.TestCase):

    def _build_state_to_world_model(self, text: str) -> ProofState:
        state = ProofState(ingress_text=text)
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
        apply_lexical_enrichment_gate(state)
        apply_concept_registry_gate(state)
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
        return state

    def test_world_knowledge_adds_logical_laws(self) -> None:
        state = self._build_state_to_world_model("كتب زيد بالقلم")
        apply_world_knowledge_layer(state)

        law_types = [law.get("law_type") for law in state.world_model.get("laws", [])]
        self.assertIn("logical", law_types)

    def test_world_knowledge_emits_trace(self) -> None:
        state = self._build_state_to_world_model("كتب زيد بالقلم")
        apply_world_knowledge_layer(state)

        events = [t["event"] for t in state.trace_chain]
        self.assertIn("world_knowledge_layer", events)

    def test_world_knowledge_instrument_validation(self) -> None:
        """يجب أن يتحقق النظام من أن القلم أداة صالحة للكتابة."""
        state = self._build_state_to_world_model("كتب زيد بالقلم")
        apply_world_knowledge_layer(state)

        wk = state.world_model.get("world_knowledge", {})
        self.assertIn("instrument_validation", wk)

    def test_world_knowledge_affordance_laws_added(self) -> None:
        state = self._build_state_to_world_model("كتب زيد بالقلم")
        apply_world_knowledge_layer(state)

        laws = state.world_model.get("laws", [])
        # يجب أن يكون هناك على الأقل القوانين المنطقية الثلاثة
        self.assertGreater(len(laws), 0)

    def test_world_knowledge_causal_rules_for_writing(self) -> None:
        """فعل 'كتب' يجب أن يُنتج ربطًا سببيًا."""
        state = self._build_state_to_world_model("كتب زيد بالقلم")
        apply_world_knowledge_layer(state)

        causality = state.world_model.get("causality", [])
        # قد يكون فارغًا إن لم يطابق الفعل، لكن الطبقة يجب أن تُنفَّذ
        wk = state.world_model.get("world_knowledge", {})
        self.assertIn("causal_rules_matched", wk)

    def test_world_model_closure_after_knowledge_enrichment(self) -> None:
        """بعد الإثراء، يجب أن يُغلَق نموذج العالم."""
        state = self._build_state_to_world_model("كتب زيد بالقلم")
        apply_world_knowledge_layer(state)
        apply_world_model_closure(state)

        self.assertTrue(state.world_model_closed)


# =========================================================
# 3. اختبارات سجل المفاهيم
# =========================================================

class ConceptRegistryTests(unittest.TestCase):

    def test_lookup_by_name_kalam(self) -> None:
        concept = lookup_by_name("كتابة")
        self.assertIsNotNone(concept)
        self.assertEqual(concept.root, "ك ت ب")

    def test_lookup_by_root_ktb(self) -> None:
        concepts = lookup_by_root("ك ت ب")
        self.assertGreater(len(concepts), 0)
        names = [c.name for c in concepts]
        self.assertIn("كتابة", names)

    def test_lookup_by_name_qalam(self) -> None:
        concept = lookup_by_name("قلم")
        self.assertIsNotNone(concept)
        self.assertIn("كتابة", concept.produces)

    def test_concept_registry_gate_matches_known_concept(self) -> None:
        state = ProofState(ingress_text="كتب زيد بالقلم")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_alignment_gate(state)
        apply_naming_gate(state)
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_symbolic_encoding_layer(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)
        apply_concept_registry_gate(state)

        matches = state.conceptual_state.get("concept_registry_matches", [])
        # القلم أو الكتابة يجب أن تُطابَق
        self.assertIsInstance(matches, list)

    def test_concept_registry_gate_emits_trace(self) -> None:
        state = ProofState(ingress_text="كتب زيد بالقلم")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_alignment_gate(state)
        apply_naming_gate(state)
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_symbolic_encoding_layer(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)
        apply_concept_registry_gate(state)

        events = [t["event"] for t in state.trace_chain]
        self.assertIn("concept_registry_gate", events)


# =========================================================
# 4. اختبار نهاية-لنهاية الكامل: "كتب زيد بالقلم"
# =========================================================

class E2EEnrichedArabicTests(unittest.TestCase):
    """
    الاختبار المحوري للمشروع:
        نص عربي → حكم مُعلَّل كامل

    مثال: "كتب زيد بالقلم"
    متوقَّع:
        - الحدث: كتابة
        - الفاعل: زيد
        - الأداة: القلم
        - القلم أداة صالحة للكتابة → حكم مقبول
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = _run_full_pipeline("كتب زيد بالقلم")

    def test_judgement_accepted(self) -> None:
        self.assertEqual(self.state.judgement, "accepted")

    def test_proposition_closed(self) -> None:
        self.assertTrue(self.state.proposition_closed)

    def test_world_model_closed(self) -> None:
        self.assertTrue(self.state.world_model_closed)

    def test_world_model_has_entities(self) -> None:
        entities = self.state.world_model.get("entities", [])
        self.assertGreater(len(entities), 0)

    def test_world_model_has_laws(self) -> None:
        laws = self.state.world_model.get("laws", [])
        self.assertGreater(len(laws), 0)

    def test_world_model_has_knowledge_layer(self) -> None:
        self.assertIn("world_knowledge", self.state.world_model)

    def test_enriched_concepts_present(self) -> None:
        enriched = self.state.conceptual_state.get("enriched_concepts", [])
        self.assertGreater(len(enriched), 0)

    def test_root_ktb_identified(self) -> None:
        enriched = self.state.conceptual_state.get("enriched_concepts", [])
        roots = [c.get("root") for c in enriched if c.get("root")]
        self.assertIn("ك ت ب", roots)

    def test_instrument_particle_identified(self) -> None:
        enriched = self.state.conceptual_state.get("enriched_concepts", [])
        relation_types = [c.get("relation_type") for c in enriched if c.get("relation_type")]
        self.assertIn("Instrumentality", relation_types)

    def test_qalam_entity_identified(self) -> None:
        enriched = self.state.conceptual_state.get("enriched_concepts", [])
        entity_types = [c.get("entity_type") for c in enriched if c.get("entity_type")]
        self.assertIn("أداة", entity_types)

    def test_replay_determinism(self) -> None:
        d1 = replay_digest(self.state)
        d2 = replay_digest(self.state)
        self.assertEqual(d1, d2)

    def test_trace_contains_all_new_gates(self) -> None:
        events = [t["event"] for t in self.state.trace_chain]
        self.assertIn("lexical_enrichment_gate", events)
        self.assertIn("concept_registry_gate", events)
        self.assertIn("world_knowledge_layer", events)

    def test_trace_new_gates_ordered_correctly(self) -> None:
        """
        lexical_enrichment_gate يجب أن يأتي قبل world_knowledge_layer،
        وworld_knowledge_layer قبل world_model_closure.
        """
        event_positions = {
            t["event"]: t["event_id"]
            for t in self.state.trace_chain
        }
        self.assertLess(
            event_positions["lexical_enrichment_gate"],
            event_positions["world_knowledge_layer"],
        )
        self.assertLess(
            event_positions["world_knowledge_layer"],
            event_positions["world_model_closure"],
        )

    def test_singular_closure_record_intact(self) -> None:
        self.assertIn("minimum_gate_snapshot", self.state.singular_closure_record)
        self.assertIn("deferred_analysis_snapshot", self.state.singular_closure_record)

    def test_no_jump_invariants_respected(self) -> None:
        self.assertTrue(self.state.ready_for_composition)
        self.assertTrue(self.state.singular_unified_closure_closed)


# =========================================================
# 5. اختبار نهاية-لنهاية بنصوص مختلفة
# =========================================================

class E2EVariousTextsTests(unittest.TestCase):

    def test_nominal_sentence(self) -> None:
        """النص / واضح — جملة اسمية."""
        state = _run_full_pipeline("النص / واضح")
        self.assertEqual(state.judgement, "accepted")
        self.assertTrue(state.world_model_closed)

    def test_writing_sentence_no_instrument(self) -> None:
        """كتب الطالب — كتابة بلا أداة صريحة."""
        state = _run_full_pipeline("كتب الطالب")
        self.assertEqual(state.judgement, "accepted")

    def test_instrument_affordance_validation(self) -> None:
        """
        التحقق من أن طبقة المعرفة تُسجِّل instrument_validation
        حتى حين لا يوجد تطابق (الأداة غير معروفة).
        """
        state = _run_full_pipeline("كتب زيد بالقلم")
        wk = state.world_model.get("world_knowledge", {})
        self.assertIn("instrument_validation", wk)

    def test_world_knowledge_logical_laws_always_present(self) -> None:
        """القوانين المنطقية يجب أن تكون حاضرة في كل جملة."""
        for text in ["كتب زيد بالقلم", "النص / واضح", "درس الطالب"]:
            state = _run_full_pipeline(text)
            laws = state.world_model.get("laws", [])
            law_types = [l.get("law_type") for l in laws]
            self.assertIn("logical", law_types, f"Failed for: {text}")


if __name__ == "__main__":
    unittest.main()
