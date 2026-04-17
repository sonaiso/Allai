import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.composition.role_distribution import apply_role_distribution_composition
from core.gates.validator import GateViolationError
from core.judgement.proposition_to_judgement import transition_proposition_to_judgement
from core.model import ProofState
from core.singular.closure_record import assemble_singular_closure_record
from core.singular.unified_closure import apply_singular_unified_closure


class ContractInvariantTests(unittest.TestCase):
    def test_composition_rejected_without_required_closures(self) -> None:
        state = ProofState(ingress_text="x")
        with self.assertRaises(GateViolationError):
            apply_role_distribution_composition(state)

    def test_judgement_requires_constitutional_preconditions(self) -> None:
        state = ProofState(ingress_text="x")
        with self.assertRaises(GateViolationError):
            transition_proposition_to_judgement(state)

    def test_composition_rejected_when_role_tokens_insufficient(self) -> None:
        state = ProofState(ingress_text="x")
        state.normalized_text = "token"
        state.singular_existence_closed = True
        state.singular_designation_closed = True
        state.singular_possibility_closed = True
        state.singular_identity_closed = True
        state.singular_relational_closed = True
        state.singular_weight_closed = True
        state.singular_logical_classificatory_closed = True
        apply_singular_unified_closure(state)
        assemble_singular_closure_record(state)
        with self.assertRaises(GateViolationError):
            apply_role_distribution_composition(state)

    def test_gate_laws_policy_declares_minimum_first(self) -> None:
        content = (ROOT / "specs" / "gate_laws.yaml").read_text(encoding="utf-8")
        self.assertIn("mandatory_gates: minimum_transition_conditions_only", content)
        self.assertIn("deferred_layers_default: non_blocking", content)


if __name__ == "__main__":
    unittest.main()
