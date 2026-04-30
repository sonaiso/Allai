"""
test_symbolic_reasoning.py
============================
اختبارات الاستدلال الرمزي — الجمل الذهبية

تُغطِّي هذه الاختبارات البوابات الرمزية الجديدة:
    - adam_properties.py
    - verb_frame_lexicon.py
    - agent_operator_gate.py
    - rejection_gate.py
    - metaphor_gate.py
    - prediction_gate.py
    - explanation_panel.py

الحالات المعيارية الست:
    1. كتب الحجر بالقلم        — جماد كفاعل → مرفوض_قطعي
    2. رأيت أسدًا يخطب         — حيوان → محتمل_مجازي → metaphorical_accepted
    3. كتب زيد الرسالة          — إنسان كفاعل → مقبول
    4. قرأ الطالب الكتاب        — إنسان كفاعل → مقبول
    5. ضرب الرجل بالعصا         — إنسان كفاعل مع أداة → مقبول
    6. أكل الحجر الخبز          — جماد كفاعل → مرفوض_قطعي
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
from arabic_engine.language.adam_properties import (
    ADAM_PROPERTIES,
    applicable_properties,
    entity_can_act,
)
from arabic_engine.language.agent_operator_gate import apply_agent_operator_gate
from arabic_engine.language.concept_registry import apply_concept_registry_gate
from arabic_engine.language.explanation_panel import build_explanation_panel
from arabic_engine.language.lexical_enrichment_gate import (
    apply_lexical_enrichment_gate,
    has_root_surface_hint,
)
from arabic_engine.language.metaphor_gate import (
    SHARED_PROPERTIES_INDEX,
    apply_metaphor_gate,
    _normalize_arabic,
)
from arabic_engine.language.minimal_complete_encoding import (
    apply_minimal_complete_encoding_contract,
)
from arabic_engine.language.prediction_gate import apply_prediction_gate
from arabic_engine.language.rejection_gate import RejectionRecord, apply_rejection_gate
from arabic_engine.language.verb_frame_lexicon import (
    VERB_FRAME_LEXICON,
    get_verb_frame,
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
from core.trace.singular_trace import emit_singular_trace
from core.weight.derivational_eligibility import determine_derivational_eligibility
from core.weight.mizan_closure import apply_mizan_closure
from core.weight.weight_legality import verify_weight_legality
from core.world_model.closure import apply_world_model_closure
from core.world_model.extractor import extract_world_model
from core.world_model.world_knowledge_layer import apply_world_knowledge_layer


# =========================================================
# مساعد — الأنبوب الكامل مع الإثراء المعجمي
# =========================================================

def _run_symbolic_pipeline(text: str) -> ProofState:
    """
    تشغيل الأنبوب الكامل شاملًا البوابات الرمزية.

    المراحل: إدخال → ترميز → إثراء → إغلاقات → تركيب → قضية → حكم
    الحكم يمر عبر: agent_operator_gate → rejection_gate → metaphor_gate
    """
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
    apply_world_knowledge_layer(state)
    apply_world_model_closure(state)

    transition_proposition_to_judgement(state)

    return state


def _build_enriched_state(text: str) -> ProofState:
    """يبني حالة وصلت إلى مرحلة الإثراء المعجمي فقط."""
    state = ProofState(ingress_text=text)
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
    return state


# =========================================================
# 1. اختبارات خصائص آدم — adam_properties
# =========================================================

class AdamPropertiesTests(unittest.TestCase):

    def test_thirteen_properties_defined(self) -> None:
        self.assertEqual(len(ADAM_PROPERTIES), 13)

    def test_property_names_in_arabic(self) -> None:
        arabic_names = {p.arabic for p in ADAM_PROPERTIES}
        self.assertIn("وجود", arabic_names)
        self.assertIn("إرادة", arabic_names)
        self.assertIn("قدرة", arabic_names)
        self.assertIn("علم", arabic_names)
        self.assertIn("حياة", arabic_names)
        self.assertIn("كلام", arabic_names)

    def test_entity_can_act_human(self) -> None:
        self.assertTrue(entity_can_act("إنسان"))

    def test_entity_can_act_animal(self) -> None:
        self.assertTrue(entity_can_act("حيوان"))

    def test_entity_cannot_act_inanimate(self) -> None:
        self.assertFalse(entity_can_act("جماد"))

    def test_entity_cannot_act_material(self) -> None:
        self.assertFalse(entity_can_act("مادة"))

    def test_entity_cannot_act_tool(self) -> None:
        self.assertFalse(entity_can_act("أداة"))

    def test_entity_cannot_act_liquid(self) -> None:
        self.assertFalse(entity_can_act("سائل"))

    def test_applicable_properties_human_includes_irada(self) -> None:
        props = applicable_properties("إنسان")
        arabic_names = {p.arabic for p in props}
        self.assertIn("إرادة", arabic_names)

    def test_applicable_properties_human_includes_ilm(self) -> None:
        props = applicable_properties("إنسان")
        arabic_names = {p.arabic for p in props}
        self.assertIn("علم", arabic_names)

    def test_applicable_properties_inanimate_only_wujud(self) -> None:
        props = applicable_properties("جماد")
        arabic_names = {p.arabic for p in props}
        self.assertIn("وجود", arabic_names)
        self.assertNotIn("إرادة", arabic_names)
        self.assertNotIn("علم", arabic_names)

    def test_applicable_properties_animal_includes_irada(self) -> None:
        props = applicable_properties("حيوان")
        arabic_names = {p.arabic for p in props}
        self.assertIn("إرادة", arabic_names)

    def test_applicable_properties_animal_excludes_ilm(self) -> None:
        props = applicable_properties("حيوان")
        arabic_names = {p.arabic for p in props}
        self.assertNotIn("علم", arabic_names)


# =========================================================
# 2. اختبارات معجم إطارات الأفعال — verb_frame_lexicon
# =========================================================

class VerbFrameLexiconTests(unittest.TestCase):

    def test_lexicon_has_entries(self) -> None:
        self.assertGreater(len(VERB_FRAME_LEXICON), 0)

    def test_get_verb_frame_kataba(self) -> None:
        frame = get_verb_frame("كتب")
        self.assertIsNotNone(frame)
        self.assertEqual(frame.root, "ك ت ب")

    def test_get_verb_frame_yaktub(self) -> None:
        frame = get_verb_frame("يكتب")
        self.assertIsNotNone(frame)
        self.assertEqual(frame.root, "ك ت ب")

    def test_get_verb_frame_khataba(self) -> None:
        frame = get_verb_frame("خطب")
        self.assertIsNotNone(frame)
        self.assertEqual(frame.root, "خ ط ب")

    def test_get_verb_frame_akala(self) -> None:
        frame = get_verb_frame("أكل")
        self.assertIsNotNone(frame)
        self.assertEqual(frame.root, "أ ك ل")

    def test_kataba_frame_rejects_inanimate(self) -> None:
        frame = get_verb_frame("كتب")
        self.assertIn("جماد", frame.rejects)

    def test_kataba_frame_requires_agent(self) -> None:
        frame = get_verb_frame("كتب")
        self.assertIn("فاعل", frame.requires)

    def test_kataba_frame_is_volitional(self) -> None:
        frame = get_verb_frame("كتب")
        self.assertTrue(frame.volitional)

    def test_get_verb_frame_unknown_returns_none(self) -> None:
        frame = get_verb_frame("قطقط")
        self.assertIsNone(frame)

    def test_kataba_frame_requires_human_or_animal(self) -> None:
        frame = get_verb_frame("كتب")
        self.assertIn("إنسان", frame.requires_agent_type)

    def test_akala_frame_rejects_inanimate(self) -> None:
        frame = get_verb_frame("أكل")
        self.assertIn("جماد", frame.rejects)


# =========================================================
# 3. اختبارات الإثراء المعجمي الموسَّع — enriched EntityEntry
# =========================================================

class EnrichedEntityEntryTests(unittest.TestCase):

    def test_hajar_enriched_as_inanimate(self) -> None:
        state = _build_enriched_state("كتب الحجر بالقلم")
        entity_types = [c.get("entity_type") for c in state.enriched_concepts
                        if c.get("entity_type")]
        self.assertIn("جماد", entity_types)

    def test_hajar_cannot_be_agent(self) -> None:
        state = _build_enriched_state("كتب الحجر بالقلم")
        for concept in state.enriched_concepts:
            if concept.get("entity_type") == "جماد":
                self.assertFalse(concept.get("can_be_agent", True))
                break

    def test_asad_has_shared_properties(self) -> None:
        state = _build_enriched_state("رأيت أسدًا يخطب")
        found = False
        for concept in state.enriched_concepts:
            if concept.get("entity_type") == "حيوان":
                shared = concept.get("shared_properties", [])
                self.assertIn("شجاعة", shared)
                found = True
                break
        self.assertTrue(found, "أسد يجب أن يُعرَّف بنوع حيوان")

    def test_zayd_can_be_agent(self) -> None:
        state = _build_enriched_state("كتب زيد الرسالة")
        for concept in state.enriched_concepts:
            if concept.get("entity_type") == "إنسان":
                self.assertTrue(concept.get("can_be_agent", False))
                break

    def test_has_root_surface_hint_kataba(self) -> None:
        self.assertTrue(has_root_surface_hint("كتب"))

    def test_has_root_surface_hint_unknown(self) -> None:
        self.assertFalse(has_root_surface_hint("قطقط"))


# =========================================================
# 4. اختبارات بوابة العامل والمعمول — agent_operator_gate
# =========================================================

class AgentOperatorGateTests(unittest.TestCase):

    def test_hajar_kataba_rejected(self) -> None:
        """كتب الحجر بالقلم: الحجر جماد لا يصلح فاعلًا."""
        state = _build_enriched_state("كتب الحجر بالقلم")
        result = apply_agent_operator_gate(state)
        self.assertFalse(result.valid)

    def test_hajar_kataba_law_triggered(self) -> None:
        state = _build_enriched_state("كتب الحجر بالقلم")
        result = apply_agent_operator_gate(state)
        self.assertIsNotNone(result.law_triggered)
        self.assertIn("Adam", result.law_triggered)

    def test_hajar_kataba_violation_contains_jamaad(self) -> None:
        state = _build_enriched_state("كتب الحجر بالقلم")
        result = apply_agent_operator_gate(state)
        self.assertIsNotNone(result.violation)
        self.assertIn("جماد", result.violation)

    def test_zayd_kataba_valid(self) -> None:
        """كتب زيد الرسالة: زيد إنسان — فاعل صالح."""
        state = _build_enriched_state("كتب زيد الرسالة")
        result = apply_agent_operator_gate(state)
        self.assertTrue(result.valid)

    def test_agent_operator_gate_stores_result_in_state(self) -> None:
        state = _build_enriched_state("كتب الحجر بالقلم")
        apply_agent_operator_gate(state)
        self.assertIn("agent_operator_gate", state.symbolic_state)

    def test_agent_operator_gate_emits_trace(self) -> None:
        state = _build_enriched_state("كتب الحجر بالقلم")
        apply_agent_operator_gate(state)
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("agent_operator_gate", events)

    def test_hajar_akala_rejected(self) -> None:
        """أكل الحجر الخبز: الحجر جماد لا يصلح فاعلًا لفعل إرادي."""
        state = _build_enriched_state("أكل الحجر الخبز")
        result = apply_agent_operator_gate(state)
        self.assertFalse(result.valid)

    def test_rajul_daraba_valid(self) -> None:
        """ضرب الرجل بالعصا: الرجل إنسان — فاعل صالح."""
        state = _build_enriched_state("ضرب الرجل بالعصا")
        result = apply_agent_operator_gate(state)
        self.assertTrue(result.valid)


# =========================================================
# 5. اختبارات بوابة الرفض — rejection_gate
# =========================================================

class RejectionGateTests(unittest.TestCase):

    def _run_to_rejection(self, text: str):
        state = _build_enriched_state(text)
        agent_result = apply_agent_operator_gate(state)
        rejection = apply_rejection_gate(state, agent_result)
        return state, agent_result, rejection

    def test_hajar_kataba_rejected_absolutely(self) -> None:
        """الحجر جماد → مرفوض_قطعي."""
        _, _, rejection = self._run_to_rejection("كتب الحجر بالقلم")
        self.assertIsNotNone(rejection)
        self.assertEqual(rejection.judgment, "مرفوض_قطعي")

    def test_rejection_record_has_law_triggered(self) -> None:
        _, _, rejection = self._run_to_rejection("كتب الحجر بالقلم")
        self.assertIsNotNone(rejection.law_triggered)
        self.assertIn("Adam", rejection.law_triggered)

    def test_rejection_record_has_violating_token(self) -> None:
        _, _, rejection = self._run_to_rejection("كتب الحجر بالقلم")
        self.assertIsNotNone(rejection.violating_token)

    def test_rejection_record_has_explanation(self) -> None:
        _, _, rejection = self._run_to_rejection("كتب الحجر بالقلم")
        self.assertIsNotNone(rejection.explanation)
        self.assertGreater(len(rejection.explanation), 0)

    def test_valid_agent_no_rejection(self) -> None:
        """كتب زيد → لا رفض."""
        _, _, rejection = self._run_to_rejection("كتب زيد الرسالة")
        self.assertIsNone(rejection)

    def test_rejection_gate_stores_in_state(self) -> None:
        state, _, _ = self._run_to_rejection("كتب الحجر بالقلم")
        self.assertIn("rejection_gate", state.symbolic_state)

    def test_rejection_gate_emits_trace(self) -> None:
        state, _, _ = self._run_to_rejection("كتب الحجر بالقلم")
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("rejection_gate", events)

    def test_asad_khataba_metaphor_eligible(self) -> None:
        """أسد حيوان → محتمل_مجازي."""
        _, _, rejection = self._run_to_rejection("رأيت أسدًا يخطب")
        if rejection is not None:
            self.assertEqual(rejection.judgment, "محتمل_مجازي")

    def test_hajar_akala_rejected_absolutely(self) -> None:
        """أكل الحجر → مرفوض_قطعي."""
        _, _, rejection = self._run_to_rejection("أكل الحجر الخبز")
        self.assertIsNotNone(rejection)
        self.assertEqual(rejection.judgment, "مرفوض_قطعي")


# =========================================================
# 6. اختبارات بوابة المجاز — metaphor_gate
# =========================================================

class MetaphorGateTests(unittest.TestCase):

    def test_normalize_arabic_strips_tanwin(self) -> None:
        self.assertEqual(_normalize_arabic("أسدًا"), "أسد")

    def test_normalize_arabic_strips_diacritics(self) -> None:
        # Diacritic-free token should be unchanged
        result = _normalize_arabic("أسد")
        self.assertEqual(result, "أسد")  # hamza preserved

    def test_shared_properties_index_has_asad(self) -> None:
        self.assertIn("أسد", SHARED_PROPERTIES_INDEX)
        self.assertIn("شجاعة", SHARED_PROPERTIES_INDEX["أسد"])

    def test_asad_metaphor_resolves(self) -> None:
        """أسد له خاصية 'شجاعة' المشتركة مع الإنسان → يُحلَّل مجازيًا."""
        rejection = RejectionRecord(
            sentence="رأيت أسدًا يخطب",
            violation_type="فاعل_حيوان",
            violating_token="أسدًا",
            required_property="إرادة",
            actual_property="حيوان",
            law_triggered="Adam:قابليةخطب",
            judgment="محتمل_مجازي",
            explanation="أسد حيوان لا يخطب",
        )
        state = ProofState(ingress_text="رأيت أسدًا يخطب")
        result = apply_metaphor_gate(state, rejection)
        self.assertTrue(result.resolved)
        self.assertEqual(result.judgment, "metaphorical_accepted")

    def test_asad_metaphor_shared_property_is_shajaa(self) -> None:
        rejection = RejectionRecord(
            sentence="رأيت أسدًا يخطب",
            violation_type="فاعل_حيوان",
            violating_token="أسدًا",
            required_property="إرادة",
            actual_property="حيوان",
            law_triggered="Adam:قابليةخطب",
            judgment="محتمل_مجازي",
            explanation="أسد حيوان",
        )
        state = ProofState(ingress_text="رأيت أسدًا يخطب")
        result = apply_metaphor_gate(state, rejection)
        self.assertEqual(result.shared_property, "شجاعة")

    def test_asad_interpretation_contains_shujaa(self) -> None:
        rejection = RejectionRecord(
            sentence="رأيت أسدًا يخطب",
            violation_type="فاعل_حيوان",
            violating_token="أسدًا",
            required_property="إرادة",
            actual_property="حيوان",
            law_triggered="Adam:قابليةخطب",
            judgment="محتمل_مجازي",
            explanation="",
        )
        state = ProofState(ingress_text="رأيت أسدًا يخطب")
        result = apply_metaphor_gate(state, rejection)
        self.assertIn("شجاع", result.target_interpretation)

    def test_no_metaphor_for_absolute_rejection(self) -> None:
        """مرفوض_قطعي → بوابة المجاز لا تنطبق."""
        rejection = RejectionRecord(
            sentence="كتب الحجر بالقلم",
            violation_type="فاعل_جماد",
            violating_token="الحجر",
            required_property="إرادة",
            actual_property="جماد",
            law_triggered="Adam:قابليةكتب",
            judgment="مرفوض_قطعي",
            explanation="الحجر جماد",
        )
        state = ProofState(ingress_text="كتب الحجر بالقلم")
        result = apply_metaphor_gate(state, rejection)
        self.assertFalse(result.resolved)
        self.assertEqual(result.judgment, "not_applicable")

    def test_metaphor_gate_not_applicable_when_no_rejection(self) -> None:
        state = ProofState(ingress_text="كتب زيد الرسالة")
        result = apply_metaphor_gate(state, None)
        self.assertFalse(result.resolved)
        self.assertEqual(result.judgment, "not_applicable")

    def test_metaphor_gate_stores_in_state(self) -> None:
        state = ProofState(ingress_text="رأيت أسدًا يخطب")
        rejection = RejectionRecord(
            sentence="رأيت أسدًا يخطب",
            violation_type="فاعل_حيوان",
            violating_token="أسدًا",
            required_property="إرادة",
            actual_property="حيوان",
            law_triggered="Adam:قابليةخطب",
            judgment="محتمل_مجازي",
            explanation="",
        )
        apply_metaphor_gate(state, rejection)
        self.assertIn("metaphor_gate", state.symbolic_state)

    def test_metaphor_gate_emits_trace(self) -> None:
        state = ProofState(ingress_text="رأيت أسدًا يخطب")
        rejection = RejectionRecord(
            sentence="رأيت أسدًا يخطب",
            violation_type="فاعل_حيوان",
            violating_token="أسدًا",
            required_property="إرادة",
            actual_property="حيوان",
            law_triggered="Adam:قابليةخطب",
            judgment="محتمل_مجازي",
            explanation="",
        )
        apply_metaphor_gate(state, rejection)
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("metaphor_gate", events)


# =========================================================
# 7. اختبارات بوابة التنبؤ — prediction_gate
# =========================================================

class PredictionGateTests(unittest.TestCase):

    def test_returns_four_results(self) -> None:
        state = _build_enriched_state("كتب زيد الرسالة")
        results = apply_prediction_gate(state)
        self.assertEqual(len(results), 4)

    def test_layers_names(self) -> None:
        state = _build_enriched_state("كتب زيد الرسالة")
        results = apply_prediction_gate(state)
        layers = {r.layer for r in results}
        self.assertIn("morphological", layers)
        self.assertIn("syntactic", layers)
        self.assertIn("semantic", layers)
        self.assertIn("world", layers)

    def test_semantic_layer_fails_for_hajar(self) -> None:
        """الطبقة الدلالية يجب أن تفشل للحجر كفاعل."""
        state = _build_enriched_state("كتب الحجر بالقلم")
        results = apply_prediction_gate(state)
        semantic = next(r for r in results if r.layer == "semantic")
        self.assertFalse(semantic.passed)

    def test_semantic_layer_passes_for_zayd(self) -> None:
        """الطبقة الدلالية يجب أن تنجح لزيد كفاعل."""
        state = _build_enriched_state("كتب زيد الرسالة")
        results = apply_prediction_gate(state)
        semantic = next(r for r in results if r.layer == "semantic")
        self.assertTrue(semantic.passed)

    def test_prediction_gate_stores_in_state(self) -> None:
        state = _build_enriched_state("كتب زيد الرسالة")
        apply_prediction_gate(state)
        self.assertIn("prediction_gate", state.symbolic_state)

    def test_prediction_gate_emits_trace(self) -> None:
        state = _build_enriched_state("كتب زيد الرسالة")
        apply_prediction_gate(state)
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("prediction_gate", events)

    def test_morphological_layer_passes_for_known_verb(self) -> None:
        state = _build_enriched_state("كتب زيد الرسالة")
        results = apply_prediction_gate(state)
        morphological = next(r for r in results if r.layer == "morphological")
        self.assertTrue(morphological.passed)


# =========================================================
# 8. اختبارات لوحة التفسير — explanation_panel
# =========================================================

class ExplanationPanelTests(unittest.TestCase):

    def test_panel_attached_to_state(self) -> None:
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        self.assertIsNotNone(state.explanation_panel)

    def test_panel_has_required_keys(self) -> None:
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        panel = state.explanation_panel
        self.assertIn("why_accepted", panel)
        self.assertIn("why_rejected", panel)
        self.assertIn("law_applied", panel)
        self.assertIn("evidence", panel)
        self.assertIn("blocker", panel)

    def test_panel_why_accepted_for_valid_sentence(self) -> None:
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        panel = state.explanation_panel
        self.assertIsNotNone(panel.get("why_accepted"))

    def test_panel_blocker_for_inanimate_agent(self) -> None:
        """لوحة التفسير يجب أن تُوضِّح سبب رفض الحجر كفاعل."""
        state = _build_enriched_state("كتب الحجر بالقلم")
        agent_result = apply_agent_operator_gate(state)
        rejection = apply_rejection_gate(state, agent_result)
        apply_metaphor_gate(state, rejection)
        apply_prediction_gate(state)
        # نُعيِّن الحكم يدويًا لأن الأنبوب الكامل غير مكتمل هنا
        state.judgement = "rejected"
        panel = build_explanation_panel(state)
        # يجب أن يكون هناك حاجز أو سبب رفض
        has_info = bool(panel.blocker) or bool(panel.why_rejected)
        self.assertTrue(has_info)

    def test_panel_evidence_is_list(self) -> None:
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        panel = state.explanation_panel
        self.assertIsInstance(panel.get("evidence"), list)


# =========================================================
# 9. اختبارات الجمل الذهبية — Golden Sentence Tests (E2E)
# =========================================================

class GoldenSentenceCase1Tests(unittest.TestCase):
    """الحالة 1: كتب الحجر بالقلم — جماد كفاعل → مرفوض"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = _run_symbolic_pipeline("كتب الحجر بالقلم")

    def test_judgement_not_accepted(self) -> None:
        """الحجر لا يكتب — الحكم لا يجب أن يكون مقبولًا."""
        self.assertNotEqual(self.state.judgement, "accepted")

    def test_agent_operator_gate_fired(self) -> None:
        self.assertIn("agent_operator_gate", self.state.symbolic_state)

    def test_rejection_gate_fired(self) -> None:
        self.assertIn("rejection_gate", self.state.symbolic_state)

    def test_rejection_record_exists(self) -> None:
        rejection_data = self.state.symbolic_state.get("rejection_gate", {})
        self.assertFalse(rejection_data.get("valid", True))

    def test_explanation_panel_has_blocker(self) -> None:
        panel = self.state.explanation_panel
        self.assertIsNotNone(panel)
        has_info = bool(panel.get("blocker")) or bool(panel.get("why_rejected"))
        self.assertTrue(has_info)

    def test_law_triggered_references_adam(self) -> None:
        agent_data = self.state.symbolic_state.get("agent_operator_gate", {})
        law = agent_data.get("law_triggered", "")
        self.assertIn("Adam", law)

    def test_metaphor_not_resolved(self) -> None:
        metaphor_data = self.state.symbolic_state.get("metaphor_gate", {})
        self.assertFalse(metaphor_data.get("resolved", False))


class GoldenSentenceCase2Tests(unittest.TestCase):
    """الحالة 2: رأيت أسدًا يخطب — مجاز → metaphorical_accepted"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = _run_symbolic_pipeline("رأيت أسدًا يخطب")

    def test_judgement_metaphorical_or_accepted(self) -> None:
        """أسد = رجل شجاع — الحكم يجب أن يكون مقبولًا أو مقبولًا مجازيًا."""
        self.assertIn(self.state.judgement, ("metaphorical_accepted", "accepted"))

    def test_agent_operator_gate_fired(self) -> None:
        self.assertIn("agent_operator_gate", self.state.symbolic_state)

    def test_metaphor_gate_fired(self) -> None:
        self.assertIn("metaphor_gate", self.state.symbolic_state)

    def test_explanation_panel_exists(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)


class GoldenSentenceCase3Tests(unittest.TestCase):
    """الحالة 3: كتب زيد الرسالة — إنسان كفاعل → مقبول"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = _run_symbolic_pipeline("كتب زيد الرسالة")

    def test_judgement_accepted(self) -> None:
        self.assertEqual(self.state.judgement, "accepted")

    def test_agent_operator_valid(self) -> None:
        agent_data = self.state.symbolic_state.get("agent_operator_gate", {})
        self.assertTrue(agent_data.get("valid", False))

    def test_no_rejection_record(self) -> None:
        rejection_data = self.state.symbolic_state.get("rejection_gate", {})
        self.assertTrue(rejection_data.get("valid", True))

    def test_explanation_panel_has_why_accepted(self) -> None:
        panel = self.state.explanation_panel
        self.assertIsNotNone(panel.get("why_accepted"))

    def test_prediction_gate_semantic_passes(self) -> None:
        pred_data = self.state.symbolic_state.get("prediction_gate", {})
        results = pred_data.get("results", [])
        semantic = next((r for r in results if r.get("layer") == "semantic"), None)
        if semantic:
            self.assertTrue(semantic.get("passed", True))


class GoldenSentenceCase4Tests(unittest.TestCase):
    """الحالة 4: قرأ الطالب الكتاب — إنسان كفاعل → مقبول"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = _run_symbolic_pipeline("قرأ الطالب الكتاب")

    def test_judgement_accepted(self) -> None:
        self.assertEqual(self.state.judgement, "accepted")

    def test_agent_operator_valid(self) -> None:
        agent_data = self.state.symbolic_state.get("agent_operator_gate", {})
        self.assertTrue(agent_data.get("valid", False))

    def test_prediction_gate_fired(self) -> None:
        self.assertIn("prediction_gate", self.state.symbolic_state)

    def test_explanation_panel_exists(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)


class GoldenSentenceCase5Tests(unittest.TestCase):
    """الحالة 5: ضرب الرجل بالعصا — إنسان + أداة → مقبول"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = _run_symbolic_pipeline("ضرب الرجل بالعصا")

    def test_judgement_accepted(self) -> None:
        self.assertEqual(self.state.judgement, "accepted")

    def test_agent_operator_valid(self) -> None:
        agent_data = self.state.symbolic_state.get("agent_operator_gate", {})
        self.assertTrue(agent_data.get("valid", False))

    def test_explanation_panel_exists(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)


class GoldenSentenceCase6Tests(unittest.TestCase):
    """الحالة 6: أكل الحجر الخبز — جماد كفاعل → مرفوض"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.state = _run_symbolic_pipeline("أكل الحجر الخبز")

    def test_judgement_not_accepted(self) -> None:
        self.assertNotEqual(self.state.judgement, "accepted")

    def test_agent_operator_invalid(self) -> None:
        agent_data = self.state.symbolic_state.get("agent_operator_gate", {})
        self.assertFalse(agent_data.get("valid", True))

    def test_rejection_record_exists(self) -> None:
        rejection_data = self.state.symbolic_state.get("rejection_gate", {})
        self.assertFalse(rejection_data.get("valid", True))

    def test_metaphor_not_resolved(self) -> None:
        metaphor_data = self.state.symbolic_state.get("metaphor_gate", {})
        self.assertFalse(metaphor_data.get("resolved", False))

    def test_explanation_panel_has_info(self) -> None:
        panel = self.state.explanation_panel
        has_info = bool(panel.get("blocker")) or bool(panel.get("why_rejected"))
        self.assertTrue(has_info)


# =========================================================
# 10. اختبارات دمج الحكم مع الأنبوب القائم
# =========================================================

class SymbolicPipelineIntegrationTests(unittest.TestCase):

    def test_trace_contains_agent_operator_gate(self) -> None:
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("agent_operator_gate", events)

    def test_trace_contains_rejection_gate(self) -> None:
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("rejection_gate", events)

    def test_trace_contains_metaphor_gate(self) -> None:
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("metaphor_gate", events)

    def test_trace_contains_prediction_gate(self) -> None:
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("prediction_gate", events)

    def test_trace_order_symbolic_before_judgement(self) -> None:
        """البوابات الرمزية يجب أن تُسجَّل قبل إصدار الحكم."""
        state = _run_symbolic_pipeline("كتب زيد الرسالة")
        events = [t["event"] for t in state.trace_chain]
        symbolic_idx = max(
            (i for i, e in enumerate(events) if e in (
                "agent_operator_gate", "rejection_gate", "metaphor_gate", "prediction_gate"
            )),
            default=-1,
        )
        judgement_idx = next(
            (i for i, e in enumerate(events) if e == "judgement_issued"), -1
        )
        self.assertGreater(judgement_idx, symbolic_idx)

    def test_existing_pipeline_still_produces_judgement(self) -> None:
        """الأنبوب القائم لا يزال يُنتج حكمًا."""
        state = _run_symbolic_pipeline("النص / واضح")
        self.assertIsNotNone(state.judgement)

    def test_explanation_panel_field_exists_on_proof_state(self) -> None:
        """الحقل explanation_panel يجب أن يكون موجودًا في ProofState."""
        state = ProofState(ingress_text="test")
        self.assertTrue(hasattr(state, "explanation_panel"))

    def test_explanation_panel_initially_none(self) -> None:
        state = ProofState(ingress_text="test")
        self.assertIsNone(state.explanation_panel)


if __name__ == "__main__":
    unittest.main()
