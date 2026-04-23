"""Language-facing namespace."""

from arabic_engine.language.minimal_complete_encoding import (
    VALID_SENTENCE_PATTERNS,
    apply_minimal_complete_encoding_contract,
)

__all__ = ["apply_minimal_complete_encoding_contract", "VALID_SENTENCE_PATTERNS"]
