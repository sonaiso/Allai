from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import unicodedata


@dataclass
class ProofState:
    ingress_text: str
    normalized_text: str = ""
    admissible: bool = False

    singular_perceptual_closed: bool = False
    singular_informational_closed: bool = False
    singular_conceptual_closed: bool = False

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
    judgement: Optional[str] = None

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
