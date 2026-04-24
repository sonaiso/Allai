"""
constants.py
============
Shared linguistic and weight constants used across core modules.

Centralising these prevents silent divergence between files that
must stay in sync (e.g. allowed weight labels, verb-prefix sets).
"""

# ---------------------------------------------------------------------------
# Weight / Mizan
# ---------------------------------------------------------------------------

#: The three canonical Arabic morphological weight labels recognised by the system.
ALLOWED_WEIGHTS: frozenset[str] = frozenset({"fa3ala", "maf3ul", "fi3l"})

# ---------------------------------------------------------------------------
# Arabic morphology markers
# ---------------------------------------------------------------------------

#: Present-tense verb prefixes (ي / ت). Used for word-class detection.
VERB_PREFIXES: tuple[str, ...] = ("ي", "ت")

#: The definite article "ال".
DEFINITE_ARTICLE: str = "ال"

#: Feminine marker (tā' marbūṭa).
FEMININE_MARKER: str = "ة"

#: Common Arabic prepositions / particles used to detect *particle* word class.
PREPOSITIONS: frozenset[str] = frozenset({"في", "من", "إلى", "على", "عن", "ب", "ل", "ك", "مع", "و", "ف", "ثم"})
