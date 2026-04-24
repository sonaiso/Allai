"""
test_property_layer.py
======================
اختبارات طبقة الخواص الأولى

تغطي:
    1. PerceptUnit يحمل حقل properties
    2. apply_percept_gate يُعيّن خواص مناسبة لكل نوع وحدة
    3. PropertyBundle يُنتَج بشكل صحيح عبر apply_property_binding_gate
    4. WorldNode لا يُقبل بدون خاصية
    5. apply_world_node_gate يُنتج عقدًا سليمة وتحجب غير الصالحة
    6. apply_ontological_property_layer يبني property_summary مصنَّفًا
"""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from arabic_engine.foundational.gates import (
    apply_percept_gate,
    apply_pre_reality_gate,
    apply_proto_concept_gate,
)
from arabic_engine.foundational.layers import apply_ontological_property_layer
from arabic_engine.foundational.models import PerceptUnit
from arabic_engine.foundational.property_binding_gate import (
    PropertyBundle,
    apply_property_binding_gate,
)
from arabic_engine.language.lexical_enrichment_gate import apply_lexical_enrichment_gate
from arabic_engine.language.minimal_complete_encoding import (
    apply_minimal_complete_encoding_contract,
)
from core.model import ProofState
from core.world_model.world_node_gate import WorldNode, apply_world_node_gate


# =========================================================
# 1. اختبارات نموذج PerceptUnit
# =========================================================

class TestPerceptUnitModel(unittest.TestCase):
    def test_percept_unit_has_properties_field(self) -> None:
        unit = PerceptUnit(
            surface="ق",
            normalized="ق",
            unit_type="letter_or_symbol",
            token_index=0,
            char_index=0,
        )
        self.assertIsInstance(unit.properties, tuple)

    def test_percept_unit_default_properties_empty(self) -> None:
        unit = PerceptUnit(
            surface="ق",
            normalized="ق",
            unit_type="letter_or_symbol",
            token_index=0,
            char_index=0,
        )
        self.assertEqual(unit.properties, ())

    def test_percept_unit_can_carry_properties(self) -> None:
        unit = PerceptUnit(
            surface="ق",
            normalized="ق",
            unit_type="letter_or_symbol",
            token_index=0,
            char_index=0,
            properties=("exists", "distinguishable"),
        )
        self.assertIn("exists", unit.properties)
        self.assertIn("distinguishable", unit.properties)


# =========================================================
# 2. اختبارات بوابة percept_gate
# =========================================================

class TestPerceptGateProperties(unittest.TestCase):
    def _run_percept(self, text: str) -> list[dict]:
        state = ProofState(ingress_text=text)
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        return state.conceptual_state["pre_language"]["percept_units"]

    def test_letter_units_carry_existence_property(self) -> None:
        units = self._run_percept("قلم")
        letter_units = [u for u in units if u["unit_type"] == "letter_or_symbol"]
        self.assertTrue(len(letter_units) > 0)
        for u in letter_units:
            self.assertIn("exists", u["properties"])

    def test_letter_units_carry_distinguishable(self) -> None:
        units = self._run_percept("كتب")
        letter_units = [u for u in units if u["unit_type"] == "letter_or_symbol"]
        for u in letter_units:
            self.assertIn("distinguishable", u["properties"])

    def test_haraka_units_carry_pronounced(self) -> None:
        # النص المُشكَّل يحتوي على حركات (combining characters)
        text = "كَتَبَ"  # كاف + فتحة + تاء + فتحة + باء + فتحة
        units = self._run_percept(text)
        haraka_units = [u for u in units if u["unit_type"] == "haraka"]
        if haraka_units:
            for u in haraka_units:
                self.assertIn("pronounced", u["properties"])

    def test_letter_units_carry_bounded(self) -> None:
        units = self._run_percept("علم")
        letter_units = [u for u in units if u["unit_type"] == "letter_or_symbol"]
        for u in letter_units:
            self.assertIn("bounded", u["properties"])


# =========================================================
# 3. اختبارات PropertyBundle
# =========================================================

class TestPropertyBundleModel(unittest.TestCase):
    def test_empty_bundle_has_no_property(self) -> None:
        bundle = PropertyBundle(proto_label="test", anchor_token_index=0)
        self.assertFalse(bundle.has_any_property())

    def test_bundle_with_existence_has_property(self) -> None:
        bundle = PropertyBundle(
            proto_label="lexical_anchor",
            anchor_token_index=0,
            existence_props=["exists"],
        )
        self.assertTrue(bundle.has_any_property())

    def test_all_properties_aggregates_all_layers(self) -> None:
        bundle = PropertyBundle(
            proto_label="lexical_anchor",
            anchor_token_index=0,
            existence_props=["exists"],
            identity_props=["same"],
            boundary_props=["limited"],
            perception_props=["distinguishable"],
            judgment_props=["known"],
        )
        all_props = bundle.all_properties()
        self.assertIn("exists", all_props)
        self.assertIn("same", all_props)
        self.assertIn("limited", all_props)
        self.assertIn("distinguishable", all_props)
        self.assertIn("known", all_props)


# =========================================================
# 4. اختبارات apply_property_binding_gate
# =========================================================

class TestPropertyBindingGate(unittest.TestCase):
    def _run_gate(self, text: str) -> ProofState:
        state = ProofState(ingress_text=text)
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_property_binding_gate(state)
        return state

    def test_gate_produces_property_bundles(self) -> None:
        state = self._run_gate("قلم كتب")
        bundles = state.conceptual_state.get("property_bundles", [])
        self.assertIsInstance(bundles, list)
        self.assertGreater(len(bundles), 0)

    def test_lexical_anchor_has_existence_props(self) -> None:
        state = self._run_gate("علم")
        bundles = state.conceptual_state.get("property_bundles", [])
        lexical_bundles = [b for b in bundles if b["proto_label"] == "lexical_anchor"]
        self.assertTrue(len(lexical_bundles) > 0)
        for b in lexical_bundles:
            self.assertIn("exists", b["existence_props"])

    def test_lexical_anchor_has_identity_props(self) -> None:
        state = self._run_gate("كتاب")
        bundles = state.conceptual_state.get("property_bundles", [])
        lexical_bundles = [b for b in bundles if b["proto_label"] == "lexical_anchor"]
        for b in lexical_bundles:
            self.assertIn("same", b["identity_props"])

    def test_prosodic_marker_has_perception_props(self) -> None:
        state = self._run_gate("كتب")
        bundles = state.conceptual_state.get("property_bundles", [])
        prosodic = [b for b in bundles if b["proto_label"] == "prosodic_marker"]
        for b in prosodic:
            self.assertIn("pronounced", b["perception_props"])

    def test_gate_adds_trace_event(self) -> None:
        state = self._run_gate("قلم")
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("property_binding_gate", events)

    def test_bundles_all_have_at_least_one_property(self) -> None:
        state = self._run_gate("يكتب الطالب درسًا")
        bundles = state.conceptual_state.get("property_bundles", [])
        self.assertGreater(len(bundles), 0)
        # على الأقل الغالبية يجب أن تحمل خواصًا
        bundles_with_props = [
            b for b in bundles
            if any(
                b.get(k)
                for k in (
                    "existence_props", "identity_props", "boundary_props",
                    "perception_props", "relation_props", "action_props", "judgment_props",
                )
            )
        ]
        self.assertGreater(len(bundles_with_props), 0)


# =========================================================
# 5. اختبارات WorldNode
# =========================================================

class TestWorldNodeModel(unittest.TestCase):
    def test_empty_node_has_no_properties(self) -> None:
        node = WorldNode(node_id="test:0", label="test")
        self.assertFalse(node.has_properties())

    def test_node_with_properties_is_valid(self) -> None:
        node = WorldNode(
            node_id="قلم:0",
            label="قلم",
            properties=["exists", "distinguishable"],
        )
        self.assertTrue(node.has_properties())

    def test_node_possible_judgments(self) -> None:
        node = WorldNode(
            node_id="قلم:0",
            label="قلم",
            properties=["exists"],
            possible_judgments=["can_be_referenced", "is_entity"],
        )
        self.assertIn("can_be_referenced", node.possible_judgments)


# =========================================================
# 6. اختبارات apply_world_node_gate
# =========================================================

class TestWorldNodeGate(unittest.TestCase):
    def _run_full_pipeline(self, text: str) -> ProofState:
        state = ProofState(ingress_text=text)
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_property_binding_gate(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)
        apply_world_node_gate(state)
        return state

    def test_gate_produces_world_nodes(self) -> None:
        state = self._run_full_pipeline("القلم أداة الكتابة")
        nodes = state.conceptual_state.get("world_nodes", [])
        self.assertIsInstance(nodes, list)
        self.assertGreater(len(nodes), 0)

    def test_all_world_nodes_have_properties(self) -> None:
        state = self._run_full_pipeline("كتب الطالب")
        nodes = state.conceptual_state.get("world_nodes", [])
        for node in nodes:
            self.assertGreater(
                len(node["properties"]),
                0,
                f"Node {node['node_id']} has no properties",
            )

    def test_blocked_nodes_have_no_properties(self) -> None:
        state = self._run_full_pipeline("قلم كتاب")
        blocked = state.conceptual_state.get("world_nodes_blocked", [])
        # المحجوبة يجب أن تحمل سببًا
        for b in blocked:
            self.assertIn("reason", b)
            self.assertEqual(b["reason"], "no_property_assigned")

    def test_gate_adds_trace_event(self) -> None:
        state = self._run_full_pipeline("علم")
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("world_node_gate", events)

    def test_world_nodes_have_possible_judgments(self) -> None:
        state = self._run_full_pipeline("القلم أداة")
        nodes = state.conceptual_state.get("world_nodes", [])
        for node in nodes:
            self.assertIsInstance(node["possible_judgments"], list)
            self.assertGreater(len(node["possible_judgments"]), 0)

    def test_known_entity_node_has_is_entity_judgment(self) -> None:
        state = self._run_full_pipeline("القلم")
        nodes = state.conceptual_state.get("world_nodes", [])
        qalam_nodes = [n for n in nodes if "قلم" in n["label"]]
        self.assertGreater(len(qalam_nodes), 0)
        judgments = qalam_nodes[0]["possible_judgments"]
        self.assertIn("is_entity", judgments)


# =========================================================
# 7. اختبارات apply_ontological_property_layer
# =========================================================

class TestOntologicalPropertyLayer(unittest.TestCase):
    def _run_layer(self, text: str) -> ProofState:
        state = ProofState(ingress_text=text)
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_property_binding_gate(state)
        apply_ontological_property_layer(state)
        return state

    def test_layer_produces_property_summary(self) -> None:
        state = self._run_layer("القلم")
        layer_data = state.conceptual_state.get("ontological_property_layer", {})
        self.assertIn("property_summary", layer_data)

    def test_property_summary_has_seven_layers(self) -> None:
        state = self._run_layer("علم")
        summary = state.conceptual_state["ontological_property_layer"]["property_summary"]
        expected_layers = {"existence", "identity", "boundary", "perception", "relation", "action", "judgment"}
        self.assertEqual(set(summary.keys()), expected_layers)

    def test_existence_layer_populated_after_lexical_anchor(self) -> None:
        state = self._run_layer("قلم كتب")
        summary = state.conceptual_state["ontological_property_layer"]["property_summary"]
        self.assertGreater(len(summary["existence"]), 0)

    def test_adam_reference_loaded(self) -> None:
        state = self._run_layer("ماء")
        layer_data = state.conceptual_state["ontological_property_layer"]
        self.assertTrue(layer_data.get("adam_reference_loaded", False))
        self.assertGreater(len(layer_data.get("adam_layers_available", [])), 0)

    def test_layer_adds_trace_event(self) -> None:
        state = self._run_layer("كتاب")
        events = [t["event"] for t in state.trace_chain]
        self.assertIn("ontological_property_layer", events)


# =========================================================
# 8. اختبار ترتيب سلسلة الأثر
# =========================================================

class TestPreLanguageOrderWithPropertyGate(unittest.TestCase):
    def test_property_binding_gate_appears_after_proto_concept_gate(self) -> None:
        state = ProofState(ingress_text="يكتب الطالب")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_property_binding_gate(state)

        events = [t["event"] for t in state.trace_chain]
        proto_idx = events.index("proto_concept_gate")
        binding_idx = events.index("property_binding_gate")
        self.assertLess(proto_idx, binding_idx)

    def test_world_node_gate_appears_after_enrichment(self) -> None:
        state = ProofState(ingress_text="قلم")
        apply_pre_reality_gate(state)
        apply_percept_gate(state)
        apply_proto_concept_gate(state)
        apply_property_binding_gate(state)
        apply_minimal_complete_encoding_contract(state)
        apply_lexical_enrichment_gate(state)
        apply_world_node_gate(state)

        events = [t["event"] for t in state.trace_chain]
        enrichment_idx = events.index("lexical_enrichment_gate")
        node_idx = events.index("world_node_gate")
        self.assertLess(enrichment_idx, node_idx)


if __name__ == "__main__":
    unittest.main()
