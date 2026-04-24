"""
exceptions.py
=============
Centralised exception hierarchy for the Allai core engine.

All engine-level errors inherit from :class:`AllaiBaseError` so that
callers can catch the whole family with a single ``except AllaiBaseError``
while still distinguishing specific failure modes when needed.
"""


class AllaiBaseError(Exception):
    """Base class for all Allai engine errors."""


class GateViolationError(AllaiBaseError):
    """Raised when a constitutional gate law is violated.

    Examples: attempting composition before singular closure is complete,
    or attempting judgement before proposition/world-model closure.
    """


class SingularClosureError(AllaiBaseError):
    """Raised when a singular closure contract is not satisfied.

    Typically used by :func:`enforce_singular_closure` when the
    closure record is incomplete at the contract-enforcement stage.
    """
