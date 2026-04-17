import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.ingress.admissibility_pre_u0 import apply_admissibility_pre_u0
from core.ingress.unicode_ingress import apply_unicode_ingress
from core.model import ProofState
from core.singular.closure_record import assemble_singular_closure_record
from core.singular.designation_closure import apply_singular_designation_closure
from core.singular.existence_closure import apply_singular_existence_closure
from core.singular.identity_closure import apply_singular_identity_closure
from core.singular.possibility_closure import apply_singular_possibility_closure
from core.singular.relational_closure import apply_singular_relational_closure
from core.singular.weight_handoff_closure import apply_singular_weight_handoff_closure
from core.weight.mizan_closure import apply_mizan_closure


class UnitClosureTests(unittest.TestCase):
    def test_admissibility_flags_invalid_text(self) -> None:
        state = ProofState(ingress_text="\x01")
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        self.assertFalse(state.admissible)

    def test_six_level_singular_closure_progression(self) -> None:
        state = ProofState(ingress_text="النص واضح")
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)

        apply_singular_existence_closure(state)
        apply_singular_designation_closure(state)
        apply_singular_possibility_closure(state)
        apply_singular_identity_closure(state)
        apply_singular_relational_closure(state)
        apply_mizan_closure(state)
        apply_singular_weight_handoff_closure(state)
        assemble_singular_closure_record(state)

        self.assertTrue(state.singular_existence_closed)
        self.assertTrue(state.singular_designation_closed)
        self.assertTrue(state.singular_possibility_closed)
        self.assertTrue(state.singular_identity_closed)
        self.assertTrue(state.singular_relational_closed)
        self.assertTrue(state.singular_weight_closed)
        self.assertTrue(state.ready_for_composition)

    def test_no_jump_weight_handoff_rejected_without_relational(self) -> None:
        state = ProofState(ingress_text="النص")
        apply_mizan_closure(state)
        apply_singular_weight_handoff_closure(state)
        self.assertFalse(state.singular_weight_closed)
        self.assertEqual(state.singular_level_blockers.get("weight"), "prior_level_incomplete:relational")

    def test_closure_record_threshold_requires_all_levels(self) -> None:
        state = ProofState(ingress_text="token")
        state.singular_existence_closed = True
        state.singular_designation_closed = True
        state.singular_possibility_closed = True
        state.singular_identity_closed = True
        state.singular_relational_closed = False
        state.singular_weight_closed = True
        state.singular_level_blockers = {"relational": "relational_capacity_unresolved"}
        assemble_singular_closure_record(state)
        self.assertFalse(state.ready_for_composition)
        self.assertIn("relational", state.singular_closure_record["blockers"])


if __name__ == "__main__":
    unittest.main()
