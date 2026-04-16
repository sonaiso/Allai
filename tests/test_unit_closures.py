import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.ingress.admissibility_pre_u0 import apply_admissibility_pre_u0
from core.ingress.unicode_ingress import apply_unicode_ingress
from core.model import ProofState
from core.singular.conceptual_closure import apply_singular_conceptual_closure
from core.singular.informational_closure import apply_singular_informational_closure
from core.singular.perceptual_closure import apply_singular_perceptual_closure
from core.weight.mizan_closure import apply_mizan_closure


class UnitClosureTests(unittest.TestCase):
    def test_admissibility_flags_invalid_text(self) -> None:
        state = ProofState(ingress_text="\x01")
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        self.assertFalse(state.admissible)

    def test_singular_closure_progression(self) -> None:
        state = ProofState(ingress_text="النص واضح")
        apply_unicode_ingress(state)
        apply_admissibility_pre_u0(state)
        apply_singular_perceptual_closure(state)
        apply_singular_informational_closure(state)
        apply_singular_conceptual_closure(state)

        self.assertTrue(state.singular_perceptual_closed)
        self.assertTrue(state.singular_informational_closed)
        self.assertTrue(state.singular_conceptual_closed)

    def test_singular_perceptual_uses_ingress_when_not_normalized(self) -> None:
        state = ProofState(ingress_text="النص")
        apply_singular_perceptual_closure(state)
        self.assertTrue(state.singular_perceptual_closed)

    def test_mizan_empty_text_not_closed(self) -> None:
        state = ProofState(ingress_text="")
        apply_mizan_closure(state)
        self.assertFalse(state.weight_closed)
        self.assertIsNone(state.weight_label)


if __name__ == "__main__":
    unittest.main()
