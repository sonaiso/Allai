from __future__ import annotations

import unicodedata
from communicative.closure import can_close_for_judgement
from communicative.khabar_insha import classify_mode
from composition.asnadi import evaluate_asnadi
from composition.case_effects import evaluate_case_effects
from composition.concept import close_concept
from composition.factors import evaluate_factors
from composition.information import close_information
from composition.perception import close_perception
from composition.roles import assign_roles
from composition.tadmini import evaluate_tadmini
from composition.taqyidi import evaluate_taqyidi
from formal.model import Decision, ProofState, Rank, TraceEntry, rank_preconditions, validate_no_jump


class TransitionError(RuntimeError):
    pass


class TransitionEngine:
    def __init__(self) -> None:
        self.trace: list[TraceEntry] = []
        self.state = ProofState()
        self._previous_rank: Rank | None = None

    def _append_trace(self, rank: Rank, decision: Decision, reason: str, evidence: dict) -> None:
        anti_jump = validate_no_jump(self._previous_rank, rank)
        if not anti_jump:
            raise TransitionError(f"No-jump invariant violated: {self._previous_rank} -> {rank}")

        legal = rank_preconditions(self.state, rank)
        if not legal:
            raise TransitionError(f"Illegal transition for rank {rank}: preconditions failed")

        self.trace.append(
            TraceEntry(
                rank=rank,
                decision=decision,
                reason=reason,
                evidence=evidence,
                legality_check=True,
                anti_jump_enforced=True,
            )
        )
        self._previous_rank = rank

    def _unicode_ingress(self, text: str) -> tuple[Decision, str, dict]:
        normalized = unicodedata.normalize("NFKC", text).strip()
        self.state.original_unicode = text
        self.state.normalized_unicode = normalized
        self.state.tokens = [t for t in normalized.split() if t]
        return Decision.PASS, "Unicode ingress complete.", {"normalization": "NFKC+strip", "tokens": self.state.tokens}

    def _admissibility(self) -> tuple[Decision, str, dict]:
        text = self.state.normalized_unicode or ""
        if not text:
            self.state.admissibility = "incomplete"
            return Decision.SUSPEND, "Input incomplete.", {"admissibility": "incomplete"}

        has_arabic = any("\u0600" <= ch <= "\u06FF" for ch in text)
        if not has_arabic:
            self.state.admissibility = "invalid"
            return Decision.REJECT, "Input invalid for Arabic-focused v1.", {"admissibility": "invalid"}

        if "؟" in text or "?" in text:
            self.state.admissibility = "ambiguous"
            return Decision.SUSPEND, "Input ambiguous and needs disambiguation.", {"admissibility": "ambiguous"}

        self.state.admissibility = "accepted"
        self.state.closed_sing = True
        self.state.closed_weight = True
        return Decision.PASS, "Input admissible for composition pipeline.", {"admissibility": "accepted"}

    def run(self, text: str) -> tuple[ProofState, list[TraceEntry]]:
        self._append_trace(Rank.UNICODE, *self._unicode_ingress(text))
        admissibility = self._admissibility()
        self._append_trace(Rank.ADMISSIBILITY, *admissibility)

        if admissibility[0] in (Decision.REJECT, Decision.SUSPEND):
            return self.state, self.trace

        transitions = [
            (Rank.PERCEPTION, close_perception),
            (Rank.INFORMATION, close_information),
            (Rank.CONCEPT, close_concept),
            (Rank.ROLES, assign_roles),
            (Rank.ASNADI, evaluate_asnadi),
            (Rank.TADMINI, evaluate_tadmini),
            (Rank.TAQYIDI, evaluate_taqyidi),
            (Rank.FACTORS, evaluate_factors),
            (Rank.CASE_EFFECTS, evaluate_case_effects),
            (Rank.KHABAR_INSHA, classify_mode),
        ]

        for rank, handler in transitions:
            decision, reason, evidence = handler(self.state)
            self._append_trace(rank, decision, reason, evidence)
            if decision in (Decision.REJECT, Decision.SUSPEND):
                return self.state, self.trace

        if not can_close_for_judgement(self.state):
            self._append_trace(Rank.JUDGEMENT, Decision.SUSPEND, "Judgement suspended: closure conditions failed.", {"closure": False})
            return self.state, self.trace

        self.state.judgement = {
            "label": "composition_rational",
            "confidence": 1.0,
            "explanation": "All required compositional and communicative closures passed.",
        }
        self._append_trace(Rank.JUDGEMENT, Decision.COMPLETE, "Judgement completed.", {"judgement": self.state.judgement})
        return self.state, self.trace
