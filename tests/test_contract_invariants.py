import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.composition.role_distribution import apply_role_distribution_composition
from core.gates.validator import GateViolationError
from core.judgement.proposition_to_judgement import transition_proposition_to_judgement
from core.model import ProofState


class ContractInvariantTests(unittest.TestCase):
    def test_composition_rejected_without_required_closures(self) -> None:
        state = ProofState(ingress_text="x")
        with self.assertRaises(GateViolationError):
            apply_role_distribution_composition(state)

    def test_judgement_requires_constitutional_preconditions(self) -> None:
        state = ProofState(ingress_text="x")
        with self.assertRaises(GateViolationError):
            transition_proposition_to_judgement(state)


if __name__ == "__main__":
    unittest.main()
