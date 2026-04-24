from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import unicodedata


@dataclass
class ProofState:
    ingress_text: str
    processing_mode: str = "legacy_text_first"
    normalized_text: str = ""
    admissible: bool = False

    singular_perceptual_closed: bool = False
    singular_informational_closed: bool = False
    singular_conceptual_closed: bool = False
    singular_existence_closed: bool = False
    singular_designation_closed: bool = False
    singular_possibility_closed: bool = False
    singular_identity_closed: bool = False
    singular_relational_closed: bool = False
    singular_weight_closed: bool = False
    singular_logical_classificatory_closed: bool = False
    singular_unified_closure_closed: bool = False

    singular_level_evidence: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    singular_level_blockers: Dict[str, Optional[str]] = field(default_factory=dict)

    singular_rank_states: Dict[str, bool] = field(default_factory=dict)
    singular_rank_sublayers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    singular_rank_blockers: Dict[str, Optional[str]] = field(default_factory=dict)
    singular_final_decision: Optional[str] = None
    singular_final_decision_reason: Optional[str] = None

    closure_record_id: Optional[str] = None
    existence_closed: bool = False
    designation_closed: bool = False
    possibility_closed: bool = False
    identity_closed: bool = False
    relational_closed: bool = False
    weight_handoff_closed: bool = False
    ready_for_composition: bool = False
    singular_closure_record: Dict[str, Any] = field(default_factory=dict)

    weight_closed: bool = False
    weight_label: Optional[str] = None
    derivational_eligible: bool = False

    composition: Dict[str, Any] = field(default_factory=dict)

    ambiguity_detected: bool = False
    ambiguity_candidates: List[Dict[str, Any]] = field(default_factory=list)
    ambiguity_outcome: Optional[str] = None  # resolved | suspended
    ambiguity_reason: Optional[str] = None

    communicative_closed: bool = False
    proposition_closed: bool = False
    world_model: Dict[str, Any] = field(default_factory=dict)
    world_model_closed: bool = False
    judgement: Optional[str] = None

    conceptual_state: Dict[str, Any] = field(default_factory=dict)
    symbolic_state: Dict[str, Any] = field(default_factory=dict)

    trace_chain: List[Dict[str, Any]] = field(default_factory=list)

    def effective_text(self) -> str:
        if self.normalized_text:
            return self.normalized_text
        return unicodedata.normalize("NFKC", self.ingress_text or "")

    def add_trace(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        payload = payload or {}
        self.trace_chain.append(
            {
                "event_id": len(self.trace_chain) + 1,
                "event": event,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
