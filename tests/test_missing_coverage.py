"""Tests that cover the 11 previously-uncovered lines in the source.

Lines targeted (11 of the original 12 uncovered statements)
------------------------------------------------------------
src/core/world_model/closure.py     : 40, 42, 49
src/core/world_model/extractor.py   : 51-54
src/core/world_model/models.py      : 14, 17-19

Note: chain_validation.py:61 is unreachable dead code — "composition_applied"
is always present in event_positions by the time execution reaches that line
because it is a member of _REQUIRED_EVENTS_FOR_JUDGEMENT and is checked on
the earlier "missing required events" guard (lines 48-50).
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.model import ProofState
from core.world_model.closure import apply_world_model_closure
from core.world_model.extractor import extract_world_model
from core.world_model.models import Entity


# ---------------------------------------------------------------------------
# world_model/models.py — Entity.__hash__ and Entity.__eq__
# ---------------------------------------------------------------------------

class EntityModelTests(unittest.TestCase):
    def test_entity_hash_is_based_on_id_and_type(self) -> None:
        """Covers models.py:14 — Entity.__hash__ return statement."""
        e = Entity(id="word", entity_type="nominal")
        expected = hash(("word", "nominal"))
        self.assertEqual(hash(e), expected)

    def test_entity_hash_can_be_used_in_set(self) -> None:
        """Entity must be usable as a set/dict key (exercises __hash__)."""
        e1 = Entity(id="a", entity_type="nominal")
        e2 = Entity(id="a", entity_type="nominal")
        s = {e1, e2}
        self.assertEqual(len(s), 1)

    def test_entity_eq_with_same_values(self) -> None:
        """Covers models.py:19 — __eq__ equality path."""
        e1 = Entity(id="x", entity_type="verbal")
        e2 = Entity(id="x", entity_type="verbal")
        self.assertEqual(e1, e2)

    def test_entity_eq_with_different_values(self) -> None:
        """Covers models.py:19 — __eq__ inequality path."""
        e1 = Entity(id="x", entity_type="nominal")
        e2 = Entity(id="y", entity_type="nominal")
        self.assertNotEqual(e1, e2)

    def test_entity_eq_with_non_entity_returns_not_implemented(self) -> None:
        """Covers models.py:17-18 — isinstance guard returning NotImplemented."""
        e = Entity(id="x", entity_type="nominal")
        result = e.__eq__("not_an_entity")
        self.assertIs(result, NotImplemented)


# ---------------------------------------------------------------------------
# world_model/closure.py — causality/goals None, blockers not-a-list
# ---------------------------------------------------------------------------

class WorldModelClosureBlockerTests(unittest.TestCase):
    def _state_with_wm(self, world_model: dict, proposition_closed: bool = True) -> ProofState:
        state = ProofState(ingress_text="x")
        state.proposition_closed = proposition_closed
        state.world_model = world_model
        return state

    def test_causality_none_adds_causality_list_missing_blocker(self) -> None:
        """Covers closure.py:40 — causality key absent (None) triggers blocker."""
        state = self._state_with_wm(
            {
                "entities": [{"id": "a", "entity_type": "nominal", "attributes": {}}],
                "events": [{"action": "is", "agent": "a", "time": "present", "patient": None}],
                "relations": [],
                "laws": [{"domain": "test", "rule": "r", "law_type": "linguistic"}],
                # causality key intentionally absent → wm.get("causality") is None
                "goals": [],
                "judgments": [],
                "uncertainty": [],
                "blockers": [],
                "closed": False,
            }
        )
        apply_world_model_closure(state)
        self.assertFalse(state.world_model_closed)
        self.assertIn("causality_list_missing", state.world_model["blockers"])

    def test_goals_none_adds_goals_list_missing_blocker(self) -> None:
        """Covers closure.py:42 — goals key absent (None) triggers blocker."""
        state = self._state_with_wm(
            {
                "entities": [{"id": "a", "entity_type": "nominal", "attributes": {}}],
                "events": [{"action": "is", "agent": "a", "time": "present", "patient": None}],
                "relations": [],
                "laws": [{"domain": "test", "rule": "r", "law_type": "linguistic"}],
                "causality": [],
                # goals key intentionally absent → wm.get("goals") is None
                "judgments": [],
                "uncertainty": [],
                "blockers": [],
                "closed": False,
            }
        )
        apply_world_model_closure(state)
        self.assertFalse(state.world_model_closed)
        self.assertIn("goals_list_missing", state.world_model["blockers"])

    def test_blockers_not_a_list_is_replaced(self) -> None:
        """Covers closure.py:49 — else-branch when wm['blockers'] is not a list."""
        state = self._state_with_wm(
            {
                "entities": [{"id": "a", "entity_type": "nominal", "attributes": {}}],
                "events": [{"action": "is", "agent": "a", "time": "present", "patient": None}],
                "relations": [],
                "laws": [{"domain": "test", "rule": "r", "law_type": "linguistic"}],
                "causality": [],
                "goals": [],
                "judgments": [],
                "uncertainty": [],
                # Not a list → triggers the else branch at closure.py:49
                "blockers": None,
                "closed": False,
            }
        )
        apply_world_model_closure(state)
        # blockers should now be a list (assigned, not extended)
        self.assertIsInstance(state.world_model["blockers"], list)


# ---------------------------------------------------------------------------
# world_model/extractor.py — verbal sentence pattern (lines 51-54)
# ---------------------------------------------------------------------------

class WorldModelExtractorVerbalPatternTests(unittest.TestCase):
    def _state_with_verbal_encoding(self, tokens: list[str]) -> ProofState:
        """Build a minimal ProofState with a verbal sentence_pattern encoding."""
        state = ProofState(ingress_text=" ".join(tokens))
        state.proposition_closed = True
        state.composition = {
            "subject": tokens[0] if tokens else "",
            "role_graph": [],
        }
        state.symbolic_state["minimal_complete_encoding"] = {
            "sentence_pattern": "verbal",
            "token_units": [{"token": t} for t in tokens],
        }
        return state

    def test_verbal_pattern_single_token_creates_event_with_unspecified_agent(self) -> None:
        """Covers extractor.py:51-54 — verbal pattern, agent falls back to 'unspecified'."""
        state = self._state_with_verbal_encoding(["ذهب"])
        extract_world_model(state)

        events = state.world_model.get("events", [])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["action"], "ذهب")
        self.assertEqual(events[0]["agent"], "unspecified")
        self.assertEqual(events[0]["time"], "unspecified")

    def test_verbal_pattern_two_tokens_creates_event_with_agent(self) -> None:
        """Covers extractor.py:51-54 — verbal pattern with explicit agent token."""
        state = self._state_with_verbal_encoding(["ذهب", "زيد"])
        extract_world_model(state)

        events = state.world_model.get("events", [])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["action"], "ذهب")
        self.assertEqual(events[0]["agent"], "زيد")
        self.assertIsNone(events[0]["patient"])

    def test_verbal_pattern_trace_event_emitted(self) -> None:
        """Verbal extraction emits the world_model_extracted trace event."""
        state = self._state_with_verbal_encoding(["كتب", "محمد"])
        extract_world_model(state)

        trace_events = [t["event"] for t in state.trace_chain]
        self.assertIn("world_model_extracted", trace_events)

    def test_verbal_pattern_event_count_in_trace(self) -> None:
        """Trace payload correctly reports event_count for verbal extraction."""
        state = self._state_with_verbal_encoding(["قرأ", "علي"])
        extract_world_model(state)

        trace = next(t for t in state.trace_chain if t["event"] == "world_model_extracted")
        self.assertEqual(trace["payload"]["event_count"], 1)


if __name__ == "__main__":
    unittest.main()
