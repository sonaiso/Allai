from __future__ import annotations

from dataclasses import asdict
import unicodedata

from arabic_engine.symbolic.models import HarakaSymbol, LetterSymbol
from core.model import ProofState

_ARABIC_HARAKAT = {
    "\u064e",
    "\u064f",
    "\u0650",
    "\u0652",
    "\u064b",
    "\u064c",
    "\u064d",
}


def _letter_role(char: str) -> str:
    if char.isalpha():
        return "lexical_carrier"
    if char.isdigit():
        return "numeric_carrier"
    if char.isspace():
        return "separator"
    return "symbolic_marker"


def apply_symbolic_encoding_layer(state: ProofState) -> ProofState:
    text = state.effective_text()
    letters: list[LetterSymbol] = []
    harakat: list[HarakaSymbol] = []

    for char in text:
        if char.isspace():
            continue

        normalized = unicodedata.normalize("NFKC", char)
        is_haraka = (char in _ARABIC_HARAKAT) or (unicodedata.combining(char) > 0)
        if is_haraka:
            harakat.append(
                HarakaSymbol(
                    mark=char,
                    normalized=normalized,
                    role="phonetic_modifier",
                    structural_constraint="requires_adjacent_letter",
                )
            )
            continue

        letters.append(
            LetterSymbol(
                char=char,
                normalized=normalized,
                role=_letter_role(char),
                can_compose=bool(normalized),
            )
        )

    state.symbolic_state["symbolic_encoding_layer"] = {
        "letters": [asdict(letter) for letter in letters],
        "harakat": [asdict(haraka) for haraka in harakat],
        "normalization": "NFKC",
        "constitutional_functional_only": True,
    }
    state.add_trace(
        "symbolic_encoding_layer",
        {
            "letter_count": len(letters),
            "haraka_count": len(harakat),
            "constitutional_functional_only": True,
        },
    )
    return state
