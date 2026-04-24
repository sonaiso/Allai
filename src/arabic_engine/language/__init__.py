"""Language-facing namespace."""

from arabic_engine.language.minimal_complete_encoding import (
    VALID_SENTENCE_PATTERNS,
    apply_minimal_complete_encoding_contract,
)
from arabic_engine.language.lexical_enrichment_gate import apply_lexical_enrichment_gate
from arabic_engine.language.concept_registry import apply_concept_registry_gate

__all__ = [
    "apply_minimal_complete_encoding_contract",
    "VALID_SENTENCE_PATTERNS",
    "apply_lexical_enrichment_gate",
    "apply_concept_registry_gate",
]
