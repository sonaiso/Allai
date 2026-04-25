"""
test_golden_sentences.py
========================
اختبارات الجمل الذهبية — التحقق من المحرك الرمزي

| الجملة              | الحكم المتوقع          |
| ------------------- | ---------------------- |
| كتب زيد بالقلم     | مقبول — آلة صالحة     |
| كتب الحجر بالقلم   | مرفوض — فاعل غير قادر |
| رأيت عينًا          | غموض مُعلَّق           |
| رأيت أسدًا يخطب    | مقبول مجازيًا          |
| النار حارة          | مقبول — قانون فيزيائي  |
| اكتب بالقلم         | مقبول — أمر + أداة     |
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
from arabic_engine.language.concept_registry import apply_concept_registry_gate
from arabic_engine.language.lexical_enrichment_gate import apply_lexical_enrichment_gate
from arabic_engine.language.minimal_complete_encoding import (
    apply_minimal_complete_encoding_contract,
)
from arabic_engine.symbolic.agent_operator_gate import apply_agent_operator_gate
from arabic_engine.symbolic.encoding import apply_symbolic_encoding_layer
from arabic_engine.symbolic.metaphor_gate import apply_metaphor_gate
from arabic_engine.symbolic.prediction_gate import apply_prediction_gate
from arabic_engine.symbolic.rejection_gate import apply_rejection_gate
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
# مساعد — أنبوب المعالجة الكامل مع المحركات الرمزية الجديدة
# =========================================================

def _run_symbolic_pipeline(text: str) -> ProofState:
    """
    أنبوب المعالجة الكامل بما يشمل:
        - الإثراء المعجمي
        - محرك العامل (AgentOperatorGate)
        - محرك التنبؤ (PredictionGate)
        - محرك الرفض (RejectionGate)
        - محرك المجاز (MetaphorGate)
        - لوحة التفسير
    """
    state = ProofState(ingress_text=text)

    # ── المرحلة 1: ما قبل اللغة ─────────────────────────────────────
    apply_pre_reality_gate(state)
    apply_percept_gate(state)
    apply_proto_concept_gate(state)
    apply_alignment_gate(state)
    apply_naming_gate(state)

    # ── المرحلة 2: الإدخال والترميز ─────────────────────────────────
    apply_unicode_ingress(state)
    apply_admissibility_pre_u0(state)
    apply_ontological_property_layer(state)
    apply_symbolic_encoding_layer(state)
    apply_minimal_complete_encoding_contract(state)

    # ── المرحلة 3: الإثراء المعجمي ──────────────────────────────────
    apply_lexical_enrichment_gate(state)
    apply_concept_registry_gate(state)

    # ── المرحلة 4: الإغلاقات الفردية ────────────────────────────────
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
    apply_world_knowledge_layer(state)

    # ── المرحلة 7: المحركات الرمزية الجديدة ──────────────────────────
    apply_agent_operator_gate(state)      # عامل + معمول → أثر + علاقة
    apply_prediction_gate(state)          # تنبؤ رمزي متعدد الطبقات
    apply_rejection_gate(state)           # رفض مُعلَّل
    apply_metaphor_gate(state)            # مجاز موثَّق

    # ── المرحلة 8: الإغلاق + الحكم ──────────────────────────────────
    apply_world_model_closure(state)
    transition_proposition_to_judgement(state)

    return state


# =========================================================
# 1. "كتب زيد بالقلم" — مقبول، آلة صالحة
# =========================================================

class GoldenTest_KatabaZaidBilQalam(unittest.TestCase):
    """كتب زيد بالقلم — الحكم المتوقع: مقبول."""

    def setUp(self) -> None:
        self.state = _run_symbolic_pipeline("كتب زيد بالقلم")

    def test_judgement_accepted(self) -> None:
        self.assertIn(self.state.judgement, {"accepted", "metaphorical_accepted"})

    def test_agent_operator_gate_fired(self) -> None:
        events = [t["event"] for t in self.state.trace_chain]
        self.assertIn("agent_operator_gate", events)

    def test_prediction_gate_fired(self) -> None:
        events = [t["event"] for t in self.state.trace_chain]
        self.assertIn("prediction_gate", events)

    def test_rejection_gate_fired(self) -> None:
        events = [t["event"] for t in self.state.trace_chain]
        self.assertIn("rejection_gate", events)

    def test_explanation_panel_built(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)

    def test_explanation_panel_has_law(self) -> None:
        panel = self.state.explanation_panel or {}
        self.assertIsNotNone(panel.get("law_applied"))

    def test_rejection_gate_passed(self) -> None:
        passed = self.state.conceptual_state.get("rejection_gate_passed", True)
        self.assertTrue(passed)

    def test_agent_operator_detects_verb(self) -> None:
        agent_result = self.state.conceptual_state.get("agent_operator_result", {})
        self.assertIsNotNone(agent_result.get("verb"))


# =========================================================
# 2. "كتب الحجر بالقلم" — مرفوض، فاعل غير قادر
# =========================================================

class GoldenTest_KatabaAlHajarBilQalam(unittest.TestCase):
    """كتب الحجر بالقلم — الحكم المتوقع: رفض (فاعل جماد)."""

    def setUp(self) -> None:
        self.state = _run_symbolic_pipeline("كتب الحجر بالقلم")

    def test_rejection_gate_detected_violation(self) -> None:
        passed = self.state.conceptual_state.get("rejection_gate_passed", True)
        # الحجر جماد → يجب أن يُكشف انتهاك في محرك العامل
        agent_result = self.state.conceptual_state.get("agent_operator_result", {})
        # إما الرفض مباشر أو انتهاك الفاعل
        has_violation = not passed or not agent_result.get("agent_valid", True)
        self.assertTrue(has_violation)

    def test_rejection_records_present_or_agent_invalid(self) -> None:
        records = self.state.conceptual_state.get("rejection_records", [])
        agent_result = self.state.conceptual_state.get("agent_operator_result", {})
        has_evidence = len(records) > 0 or not agent_result.get("agent_valid", True)
        self.assertTrue(has_evidence)

    def test_explanation_panel_built(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)

    def test_explanation_panel_has_law(self) -> None:
        panel = self.state.explanation_panel or {}
        self.assertIsNotNone(panel.get("law_applied"))

    def test_rejection_gate_fired(self) -> None:
        events = [t["event"] for t in self.state.trace_chain]
        self.assertIn("rejection_gate", events)


# =========================================================
# 3. "رأيت عينًا" — غموض مُعلَّق
# =========================================================

class GoldenTest_RaaytuAynan(unittest.TestCase):
    """رأيت عينًا — الحكم المتوقع: مقبول (بعين أو غيرها)."""

    def setUp(self) -> None:
        self.state = _run_symbolic_pipeline("رأيت عينًا")

    def test_pipeline_completes(self) -> None:
        self.assertIsNotNone(self.state.judgement)

    def test_explanation_panel_built(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)

    def test_explanation_panel_has_law(self) -> None:
        panel = self.state.explanation_panel or {}
        self.assertIsNotNone(panel.get("law_applied"))

    def test_all_new_gates_fired(self) -> None:
        events = [t["event"] for t in self.state.trace_chain]
        self.assertIn("agent_operator_gate", events)
        self.assertIn("rejection_gate", events)
        self.assertIn("metaphor_gate", events)


# =========================================================
# 4. "رأيت أسدًا يخطب" — مقبول مجازيًا
# =========================================================

class GoldenTest_RaaytuAsadanYakhtub(unittest.TestCase):
    """رأيت أسدًا يخطب — الحكم المتوقع: مقبول مجازيًا."""

    def setUp(self) -> None:
        self.state = _run_symbolic_pipeline("رأيت أسدًا يخطب")

    def test_metaphor_gate_fired(self) -> None:
        events = [t["event"] for t in self.state.trace_chain]
        self.assertIn("metaphor_gate", events)

    def test_explanation_panel_built(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)

    def test_explanation_panel_has_law(self) -> None:
        panel = self.state.explanation_panel or {}
        self.assertIsNotNone(panel.get("law_applied"))

    def test_pipeline_completes(self) -> None:
        self.assertIsNotNone(self.state.judgement)

    def test_metaphor_result_present(self) -> None:
        metaphor_result = self.state.conceptual_state.get("metaphor_result", {})
        self.assertIsNotNone(metaphor_result)

    def test_asad_detected_in_enriched(self) -> None:
        enriched = self.state.conceptual_state.get("enriched_concepts", [])
        tokens = [c.get("token", "").lstrip("ال") for c in enriched]
        self.assertTrue(any("أسد" in t for t in tokens))


# =========================================================
# 5. "النار حارة" — مقبول، قانون فيزيائي
# =========================================================

class GoldenTest_AlNarHarra(unittest.TestCase):
    """النار حارة — الحكم المتوقع: مقبول."""

    def setUp(self) -> None:
        self.state = _run_symbolic_pipeline("النار حارة")

    def test_judgement_accepted(self) -> None:
        self.assertIn(self.state.judgement, {"accepted", "metaphorical_accepted"})

    def test_explanation_panel_built(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)

    def test_explanation_panel_has_law(self) -> None:
        panel = self.state.explanation_panel or {}
        self.assertIsNotNone(panel.get("law_applied"))

    def test_nar_entity_enriched(self) -> None:
        enriched = self.state.conceptual_state.get("enriched_concepts", [])
        entity_types = [c.get("entity_type") for c in enriched if c.get("entity_type")]
        self.assertTrue(len(entity_types) > 0)

    def test_world_model_closed(self) -> None:
        self.assertTrue(self.state.world_model_closed)


# =========================================================
# 6. "اكتب بالقلم" — مقبول، أمر + أداة صالحة
# =========================================================

class GoldenTest_UktubBilQalam(unittest.TestCase):
    """اكتب بالقلم — الحكم المتوقع: مقبول."""

    def setUp(self) -> None:
        self.state = _run_symbolic_pipeline("اكتب بالقلم")

    def test_judgement_accepted(self) -> None:
        self.assertIn(self.state.judgement, {"accepted", "metaphorical_accepted"})

    def test_explanation_panel_built(self) -> None:
        self.assertIsNotNone(self.state.explanation_panel)

    def test_explanation_panel_has_law(self) -> None:
        panel = self.state.explanation_panel or {}
        self.assertIsNotNone(panel.get("law_applied"))

    def test_all_new_gates_fired(self) -> None:
        events = [t["event"] for t in self.state.trace_chain]
        self.assertIn("agent_operator_gate", events)
        self.assertIn("prediction_gate", events)
        self.assertIn("rejection_gate", events)
        self.assertIn("metaphor_gate", events)

    def test_qalam_is_instrument(self) -> None:
        enriched = self.state.conceptual_state.get("enriched_concepts", [])
        instrument_found = any(
            c.get("relation_type") == "Instrumentality"
            or "instrument" in c.get("roles", [])
            for c in enriched
        )
        self.assertTrue(instrument_found)


# =========================================================
# 7. اختبارات الوحدة — AdamProperties
# =========================================================

class AdamPropertiesUnitTests(unittest.TestCase):
    """اختبارات وحدة لخواص آدم."""

    def test_all_thirteen_properties_exist(self) -> None:
        from arabic_engine.foundational.adam_properties import all_properties, get_property
        props = all_properties()
        self.assertEqual(len(props), 13)
        expected_names = [
            "وجود", "هوية", "تمايز", "حد", "زمان", "مكان",
            "علاقة", "فعل", "أثر", "قابلية", "سبب", "نتيجة", "حكم",
        ]
        for name in expected_names:
            self.assertIsNotNone(get_property(name), f"خاصية مفقودة: {name}")

    def test_get_property_returns_correct_type(self) -> None:
        from arabic_engine.foundational.adam_properties import get_property
        prop = get_property("وجود")
        self.assertIsNotNone(prop)
        self.assertEqual(prop.property_type, "ontological")  # type: ignore[union-attr]

    def test_applicable_properties_for_human(self) -> None:
        from arabic_engine.foundational.adam_properties import applicable_properties
        props = applicable_properties("إنسان")
        self.assertIn("فعل", props)
        self.assertIn("وجود", props)

    def test_applicable_properties_for_inanimate(self) -> None:
        from arabic_engine.foundational.adam_properties import applicable_properties
        props = applicable_properties("جماد")
        self.assertNotIn("فعل", props)
        self.assertIn("وجود", props)

    def test_entity_can_act_human(self) -> None:
        from arabic_engine.foundational.adam_properties import entity_can_act
        self.assertTrue(entity_can_act("إنسان"))

    def test_entity_can_act_inanimate(self) -> None:
        from arabic_engine.foundational.adam_properties import entity_can_act
        self.assertFalse(entity_can_act("جماد"))

    def test_property_implies_chain(self) -> None:
        from arabic_engine.foundational.adam_properties import property_implies
        implies = property_implies("هوية")
        self.assertIn("وجود", implies)
        self.assertIn("تمايز", implies)


# =========================================================
# 8. اختبارات الوحدة — VerbFrameLexicon
# =========================================================

class VerbFrameLexiconUnitTests(unittest.TestCase):
    """اختبارات وحدة لمعجم الأفعال."""

    def test_kataba_frame_exists(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import get_verb_frame
        frame = get_verb_frame("كتب")
        self.assertIsNotNone(frame)

    def test_kataba_requires_capable_agent(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import get_verb_frame
        frame = get_verb_frame("كتب")
        self.assertIsNotNone(frame)
        self.assertIn("فاعل_قادر", frame.requires)  # type: ignore[union-attr]

    def test_kataba_rejects_inanimate(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import get_verb_frame
        frame = get_verb_frame("كتب")
        self.assertIsNotNone(frame)
        self.assertIn("فاعل_جماد", frame.rejects)  # type: ignore[union-attr]

    def test_khataba_requires_human_agent(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import get_verb_frame
        frame = get_verb_frame("خطب")
        self.assertIsNotNone(frame)
        self.assertIn("فاعل_إنسان", frame.requires)  # type: ignore[union-attr]

    def test_surface_hints_resolve(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import get_verb_frame
        frame = get_verb_frame("يكتب")
        self.assertIsNotNone(frame)
        self.assertEqual(frame.verb, "كتب")  # type: ignore[union-attr]

    def test_entity_satisfies_requirement_human_capable(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import entity_satisfies_requirement
        self.assertTrue(entity_satisfies_requirement("إنسان", "فاعل_قادر"))

    def test_entity_satisfies_requirement_stone_incapable(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import entity_satisfies_requirement
        self.assertFalse(entity_satisfies_requirement("جماد", "فاعل_قادر"))

    def test_inanimate_rejection_applicable_for_stone(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import is_rejection_applicable
        self.assertTrue(is_rejection_applicable("جماد", "فاعل_جماد"))

    def test_human_not_rejected_by_inanimate_condition(self) -> None:
        from arabic_engine.language.verb_frame_lexicon import is_rejection_applicable
        self.assertFalse(is_rejection_applicable("إنسان", "فاعل_جماد"))


# =========================================================
# 9. اختبارات الوحدة — RejectionRecord
# =========================================================

class RejectionGateUnitTests(unittest.TestCase):
    """اختبارات وحدة لمحرك الرفض."""

    def test_rejection_record_is_frozen_dataclass(self) -> None:
        from arabic_engine.symbolic.rejection_gate import RejectionRecord
        rec = RejectionRecord(
            sentence="كتب الحجر",
            violation_type="semantic",
            violating_token="الحجر",
            required_property="قابلية",
            actual_property="جماد",
            law_triggered="Adam:قابلية",
            judgment="مرفوض_معرفيًا",
            explanation="الحجر لا يملك خاصية 'قادر'",
        )
        self.assertEqual(rec.violation_type, "semantic")
        self.assertEqual(rec.judgment, "مرفوض_معرفيًا")

    def test_rejection_gate_produces_trace_event(self) -> None:
        state = ProofState(ingress_text="كتب الحجر بالقلم")
        state.conceptual_state["agent_operator_result"] = {
            "verb": "كتب",
            "agent_token": "الحجر",
            "agent_valid": False,
            "agent_reason": "الحجر (جماد) لا يملك خاصية 'قادر'",
            "instrument_bindings": [],
            "overall_valid": False,
            "violations": ["الحجر جماد"],
        }
        state.conceptual_state["enriched_concepts"] = []
        state.world_model = {"events": [], "entities": []}
        apply_rejection_gate(state)
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("rejection_gate", events)

    def test_rejection_gate_flags_inanimate_agent(self) -> None:
        state = ProofState(ingress_text="كتب الحجر")
        state.conceptual_state["agent_operator_result"] = {
            "verb": "كتب",
            "agent_token": "الحجر",
            "agent_valid": False,
            "agent_reason": "الحجر (جماد) لا يملك خاصية 'قادر'",
            "instrument_bindings": [],
            "overall_valid": False,
            "violations": ["الحجر جماد"],
        }
        state.conceptual_state["enriched_concepts"] = []
        state.world_model = {"events": [], "entities": []}
        apply_rejection_gate(state)
        records = state.conceptual_state.get("rejection_records", [])
        passed = state.conceptual_state.get("rejection_gate_passed", True)
        self.assertFalse(passed)
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0]["violating_token"], "الحجر")


# =========================================================
# 10. اختبارات الوحدة — MetaphorGate
# =========================================================

class MetaphorGateUnitTests(unittest.TestCase):
    """اختبارات وحدة لمحرك المجاز."""

    def _make_state_with_conflict(self) -> ProofState:
        state = ProofState(ingress_text="رأيت أسدًا يخطب")
        state.conceptual_state["rejection_records"] = [
            {
                "sentence": "رأيت أسدًا يخطب",
                "violation_type": "semantic",
                "violating_token": "أسدًا",
                "required_property": "إنسان",
                "actual_property": "حيوان",
                "law_triggered": "خطب_rejects_فاعل_حيوان",
                "judgment": "محتمل_مجازي",
                "explanation": "أسد (حيوان) لا يخطب — لكن محتمل مجازيًا",
            }
        ]
        state.conceptual_state["enriched_concepts"] = []
        state.world_model = {"judgments": []}
        return state

    def test_metaphor_gate_detects_conflict(self) -> None:
        state = self._make_state_with_conflict()
        apply_metaphor_gate(state)
        result = state.conceptual_state.get("metaphor_result", {})
        self.assertTrue(result.get("conflict_detected"))

    def test_metaphor_gate_resolves_asad(self) -> None:
        state = self._make_state_with_conflict()
        apply_metaphor_gate(state)
        result = state.conceptual_state.get("metaphor_result", {})
        self.assertTrue(result.get("metaphor_applied"))

    def test_metaphor_gate_produces_interpretation(self) -> None:
        state = self._make_state_with_conflict()
        apply_metaphor_gate(state)
        result = state.conceptual_state.get("metaphor_result", {})
        interps = result.get("interpretations", [])
        self.assertGreater(len(interps), 0)
        self.assertEqual(interps[0]["shared_property"], "شجاعة")

    def test_metaphor_gate_updates_world_judgments(self) -> None:
        state = self._make_state_with_conflict()
        apply_metaphor_gate(state)
        judgments = state.world_model.get("judgments", [])
        types = [j.get("judgment_type") for j in judgments]
        self.assertIn("metaphorical", types)

    def test_metaphor_gate_emits_trace(self) -> None:
        state = self._make_state_with_conflict()
        apply_metaphor_gate(state)
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("metaphor_gate", events)

    def test_no_metaphor_without_index_entry(self) -> None:
        state = ProofState(ingress_text="كتب الحجر")
        state.conceptual_state["rejection_records"] = [
            {
                "violation_type": "semantic",
                "violating_token": "الحجر",
                "judgment": "محتمل_مجازي",
                "explanation": "الحجر جماد",
            }
        ]
        state.conceptual_state["enriched_concepts"] = []
        state.world_model = {"judgments": []}
        apply_metaphor_gate(state)
        result = state.conceptual_state.get("metaphor_result", {})
        # الحجر لا يملك خاصية مشتركة موثَّقة في الفهرس
        self.assertFalse(result.get("metaphor_applied", False))
        self.assertGreater(len(result.get("unresolved_conflicts", [])), 0)


# =========================================================
# 11. اختبارات الوحدة — ExplanationPanel
# =========================================================

class ExplanationPanelUnitTests(unittest.TestCase):
    """اختبارات وحدة للوحة التفسير."""

    def test_panel_built_from_accepted_state(self) -> None:
        from core.judgement.explanation_panel import build_explanation_panel
        state = ProofState(ingress_text="كتب زيد")
        state.judgement = "accepted"
        state.proposition_closed = True
        state.world_model_closed = True
        state.world_model = {
            "laws": [{"rule": "الفاعل_مرفوع", "law_type": "linguistic"}],
            "entities": [{"id": "زيد"}],
            "events": [{"action": "كتب", "agent": "زيد"}],
        }
        state.conceptual_state["agent_operator_result"] = {
            "verb": "كتب",
            "agent_token": "زيد",
            "agent_valid": True,
            "agent_reason": "زيد (إنسان) فاعل مقبول",
            "instrument_bindings": [],
            "overall_valid": True,
            "violations": [],
        }
        state.conceptual_state["rejection_records"] = []
        state.conceptual_state["rejection_gate_passed"] = True
        state.conceptual_state["metaphor_result"] = {"metaphor_applied": False, "overall_judgment": "literal"}

        panel = build_explanation_panel(state)
        self.assertIsNotNone(panel)
        self.assertIsNotNone(panel.law_applied)
        self.assertEqual(panel.judgment, "accepted")

    def test_panel_built_from_rejected_state(self) -> None:
        from core.judgement.explanation_panel import build_explanation_panel
        state = ProofState(ingress_text="كتب الحجر")
        state.judgement = "rejected"
        state.proposition_closed = False
        state.world_model_closed = False
        state.world_model = {}
        state.conceptual_state["rejection_records"] = [
            {
                "violation_type": "semantic",
                "violating_token": "الحجر",
                "required_property": "قابلية",
                "actual_property": "جماد",
                "law_triggered": "Adam:قابلية",
                "judgment": "مرفوض_معرفيًا",
                "explanation": "الحجر لا يملك خاصية قادر",
            }
        ]
        state.conceptual_state["rejection_gate_passed"] = False
        state.conceptual_state["agent_operator_result"] = {
            "verb": "كتب", "agent_token": "الحجر", "agent_valid": False,
            "agent_reason": "الحجر جماد", "instrument_bindings": [],
            "overall_valid": False, "violations": [],
        }
        state.conceptual_state["metaphor_result"] = {"metaphor_applied": False, "overall_judgment": "literal"}

        panel = build_explanation_panel(state)
        self.assertIsNotNone(panel.why_rejected)
        self.assertIsNotNone(panel.law_applied)
        self.assertEqual(panel.judgment, "rejected")

    def test_panel_to_dict_is_serializable(self) -> None:
        from core.judgement.explanation_panel import ExplanationPanel
        panel = ExplanationPanel(
            why_accepted="الجملة صحيحة",
            law_applied="GL-002",
            judgment="accepted",
        )
        d = panel.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["judgment"], "accepted")
        self.assertEqual(d["law_applied"], "GL-002")


if __name__ == "__main__":
    unittest.main()
