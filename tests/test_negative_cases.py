import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.ambiguity.conflict_resolution import resolve_ambiguity_conflicts
from core.ambiguity.detection import detect_ambiguity
from core.communication.communicative_closure import apply_communicative_closure
from core.model import ProofState


class NegativeCaseTests(unittest.TestCase):
    def test_ambiguity_requires_reason_for_closure(self) -> None:
        state = ProofState(ingress_text="a / b")
        detect_ambiguity(state)
        state.ambiguity_reason = None
        state.ambiguity_outcome = None
        apply_communicative_closure(state)
        self.assertFalse(state.communicative_closed)

    def test_conflict_resolution_sets_explicit_outcome(self) -> None:
        state = ProofState(ingress_text="a / b")
        detect_ambiguity(state)
        resolve_ambiguity_conflicts(state)
        self.assertIn(state.ambiguity_outcome, {"resolved", "suspended"})
        self.assertTrue(state.ambiguity_reason)


if __name__ == "__main__":
    unittest.main()
