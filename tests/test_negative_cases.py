import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.ambiguity.conflict_resolution import resolve_ambiguity_conflicts
from core.ambiguity.detection import detect_ambiguity
from core.communication.communicative_closure import apply_communicative_closure
from core.model import ProofState
from core.trace.chain_validation import validate_trace_chain


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

    def test_ambiguity_detection_uses_ingress_when_not_normalized(self) -> None:
        state = ProofState(ingress_text="a / b")
        detect_ambiguity(state)
        self.assertTrue(state.ambiguity_detected)
        self.assertGreaterEqual(len(state.ambiguity_candidates), 1)

    def test_trace_validation_rejects_out_of_order_required_events(self) -> None:
        state = ProofState(ingress_text="x")
        required_events_out_of_order = [
            "unicode_ingress",
            "admissibility_checked",
            "singular_informational_closure",
            "singular_perceptual_closure",
            "singular_conceptual_closure",
            "mizan_closure",
            "composition_applied",
            "ambiguity_detected",
            "ambiguity_ranked",
            "ambiguity_outcome",
            "communicative_closure",
            "proposition_closure",
        ]
        state.trace_chain = [
            {"event_id": idx, "event": event, "payload": {}, "timestamp": "2026-01-01T00:00:00+00:00"}
            for idx, event in enumerate(required_events_out_of_order, start=1)
        ]
        self.assertFalse(validate_trace_chain(state))


if __name__ == "__main__":
    unittest.main()
