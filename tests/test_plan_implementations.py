"""
test_plan_implementations.py
=============================
Tests that validate the implementation plan changes:
  1. Shared constants are used (no duplicate definitions).
  2. word_class == "particle" is detected for preposition-led text.
  3. weight_handoff without mizan emits an explicit "mizan_not_applied" blocker.
  4. AllaiBaseError exception hierarchy is correct.
  5. _set_rank_blocked helper populates all required state fields.
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.constants import ALLOWED_WEIGHTS, PREPOSITIONS, VERB_PREFIXES
from core.exceptions import AllaiBaseError, GateViolationError, SingularClosureError
from core.model import ProofState
from core.singular._helpers import _set_rank_blocked
from core.singular.designation_closure import apply_singular_designation_closure
from core.singular.existence_closure import apply_singular_existence_closure
from core.singular.identity_closure import _determine_word_class, apply_singular_identity_closure
from core.singular.possibility_closure import apply_singular_possibility_closure
from core.singular.relational_closure import apply_singular_relational_closure
from core.singular.weight_handoff_closure import apply_singular_weight_handoff_closure
from core.weight.mizan_closure import apply_mizan_closure
from core.weight.weight_legality import verify_weight_legality


# ---------------------------------------------------------------------------
# 1. Shared constants
# ---------------------------------------------------------------------------
class SharedConstantsTests(unittest.TestCase):
    def test_allowed_weights_is_frozenset(self) -> None:
        self.assertIsInstance(ALLOWED_WEIGHTS, frozenset)

    def test_allowed_weights_values(self) -> None:
        self.assertEqual(ALLOWED_WEIGHTS, frozenset({"fa3ala", "maf3ul", "fi3l"}))

    def test_verb_prefixes_contains_ya_and_ta(self) -> None:
        self.assertIn("ي", VERB_PREFIXES)
        self.assertIn("ت", VERB_PREFIXES)

    def test_prepositions_contains_core_set(self) -> None:
        for prep in ("في", "من", "إلى", "على", "عن"):
            self.assertIn(prep, PREPOSITIONS)

    def test_mizan_uses_shared_constant(self) -> None:
        """mizan_closure and weight_legality must agree on allowed weights."""
        state = ProofState(ingress_text="كتب الولد")
        apply_mizan_closure(state)
        self.assertIn(state.weight_label, ALLOWED_WEIGHTS)
        self.assertTrue(verify_weight_legality(state))


# ---------------------------------------------------------------------------
# 2. word_class particle detection
# ---------------------------------------------------------------------------
class WordClassParticleTests(unittest.TestCase):
    def test_preposition_first_token_gives_particle(self) -> None:
        self.assertEqual(_determine_word_class(["في", "البيت"]), "particle")

    def test_verb_prefix_gives_verb(self) -> None:
        self.assertEqual(_determine_word_class(["يكتب", "الولد"]), "verb")

    def test_regular_noun_gives_noun(self) -> None:
        self.assertEqual(_determine_word_class(["الولد", "يكتب"]), "noun")

    def test_empty_tokens_gives_empty_string(self) -> None:
        self.assertEqual(_determine_word_class([]), "")

    def test_particle_text_passes_full_singular_pipeline(self) -> None:
        """Text starting with a preposition should reach relational_closed=True."""
        state = ProofState(ingress_text="في البيت")
        apply_existence_to_relational(state)
        self.assertTrue(state.singular_identity_closed)
        self.assertEqual(
            state.singular_level_evidence["identity"]["higher_analysis"]["word_class"],
            "particle",
        )
        self.assertTrue(state.singular_relational_closed)

    def test_particle_relational_can_be_linker(self) -> None:
        state = ProofState(ingress_text="في البيت")
        apply_existence_to_relational(state)
        higher = state.singular_level_evidence["relational"]["higher_analysis"]
        self.assertTrue(higher["can_be_linker"])

    def test_particle_relational_not_agent(self) -> None:
        state = ProofState(ingress_text="في البيت")
        apply_existence_to_relational(state)
        higher = state.singular_level_evidence["relational"]["higher_analysis"]
        self.assertFalse(higher["can_be_agent"])


def apply_existence_to_relational(state: ProofState) -> None:
    apply_singular_existence_closure(state)
    apply_singular_designation_closure(state)
    apply_singular_possibility_closure(state)
    apply_singular_identity_closure(state)
    apply_singular_relational_closure(state)


# ---------------------------------------------------------------------------
# 3. mizan_not_applied detection in weight_handoff
# ---------------------------------------------------------------------------
class MizanNotAppliedTests(unittest.TestCase):
    def _state_with_relational_closed(self) -> ProofState:
        state = ProofState(ingress_text="في البيت")
        apply_existence_to_relational(state)
        return state

    def test_weight_handoff_without_mizan_emits_mizan_not_applied(self) -> None:
        state = self._state_with_relational_closed()
        # Do NOT call apply_mizan_closure — weight_label stays None
        apply_singular_weight_handoff_closure(state)
        self.assertFalse(state.singular_weight_closed)
        self.assertEqual(state.singular_level_blockers.get("weight"), "mizan_not_applied")

    def test_weight_handoff_without_mizan_trace_has_correct_blocker(self) -> None:
        state = self._state_with_relational_closed()
        apply_singular_weight_handoff_closure(state)
        trace_events = [e["event"] for e in state.trace_chain]
        self.assertIn("singular_weight_handoff_closure", trace_events)
        last = next(
            e for e in reversed(state.trace_chain)
            if e["event"] == "singular_weight_handoff_closure"
        )
        self.assertEqual(last["payload"]["blocker"], "mizan_not_applied")

    def test_weight_handoff_with_mizan_succeeds(self) -> None:
        state = self._state_with_relational_closed()
        apply_mizan_closure(state)
        apply_singular_weight_handoff_closure(state)
        self.assertTrue(state.singular_weight_closed)
        self.assertIsNone(state.singular_level_blockers.get("weight"))


# ---------------------------------------------------------------------------
# 4. Exception hierarchy
# ---------------------------------------------------------------------------
class ExceptionHierarchyTests(unittest.TestCase):
    def test_gate_violation_is_allai_base(self) -> None:
        err = GateViolationError("test")
        self.assertIsInstance(err, AllaiBaseError)

    def test_singular_closure_error_is_allai_base(self) -> None:
        err = SingularClosureError("test")
        self.assertIsInstance(err, AllaiBaseError)

    def test_allai_base_is_exception(self) -> None:
        err = AllaiBaseError("test")
        self.assertIsInstance(err, Exception)

    def test_gate_violation_and_singular_closure_are_distinct(self) -> None:
        self.assertFalse(issubclass(GateViolationError, SingularClosureError))
        self.assertFalse(issubclass(SingularClosureError, GateViolationError))

    def test_can_catch_both_with_base_class(self) -> None:
        for exc_class in (GateViolationError, SingularClosureError):
            with self.assertRaises(AllaiBaseError):
                raise exc_class("caught by base")

    def test_gate_violation_imported_from_validator(self) -> None:
        from core.gates.validator import GateViolationError as GVE
        self.assertIs(GVE, GateViolationError)

    def test_singular_closure_error_imported_from_contracts(self) -> None:
        from core.singular.closure_contracts import SingularClosureError as SCE
        self.assertIs(SCE, SingularClosureError)


# ---------------------------------------------------------------------------
# 5. _set_rank_blocked helper
# ---------------------------------------------------------------------------
class SetRankBlockedHelperTests(unittest.TestCase):
    def test_sets_all_state_fields(self) -> None:
        state = ProofState(ingress_text="test")
        _set_rank_blocked(state, "possibility", "test_blocker")
        self.assertFalse(state.singular_possibility_closed)
        self.assertEqual(state.singular_level_evidence["possibility"], {})
        self.assertEqual(state.singular_level_blockers["possibility"], "test_blocker")
        self.assertFalse(state.singular_rank_states["possibility"])
        self.assertEqual(state.singular_rank_sublayers["possibility"], {})
        self.assertEqual(state.singular_rank_blockers["possibility"], "test_blocker")

    def test_emits_trace(self) -> None:
        state = ProofState(ingress_text="test")
        _set_rank_blocked(state, "designation", "blocker_x")
        events = [e["event"] for e in state.trace_chain]
        self.assertIn("singular_designation_closure", events)

    def test_custom_trace_event(self) -> None:
        state = ProofState(ingress_text="test")
        _set_rank_blocked(state, "weight", "b", trace_event="singular_weight_handoff_closure")
        events = [e["event"] for e in state.trace_chain]
        self.assertIn("singular_weight_handoff_closure", events)

    def test_custom_evidence_stored(self) -> None:
        state = ProofState(ingress_text="test")
        ev = {"minimum_conditions": {"x": False}}
        _set_rank_blocked(state, "designation", "b", evidence=ev)
        self.assertEqual(state.singular_level_evidence["designation"], ev)
        self.assertEqual(state.singular_rank_sublayers["designation"], ev)

    def test_custom_closed_attr(self) -> None:
        state = ProofState(ingress_text="test")
        state.singular_existence_closed = True
        _set_rank_blocked(state, "existence", "force_block", closed_attr="singular_existence_closed")
        self.assertFalse(state.singular_existence_closed)


if __name__ == "__main__":
    unittest.main()
