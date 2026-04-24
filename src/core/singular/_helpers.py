"""
_helpers.py
===========
Internal helpers shared across singular-closure modules.

These utilities eliminate the repeated 6-line boilerplate that each
closure function needs when it must block early because a prior rank
has not been completed.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.model import ProofState


def _set_rank_blocked(
    state: ProofState,
    rank: str,
    blocker: str,
    evidence: Optional[Dict[str, Any]] = None,
    trace_event: Optional[str] = None,
    *,
    closed_attr: Optional[str] = None,
) -> None:
    """Mark *rank* as blocked and populate all related state fields.

    Parameters
    ----------
    state:
        The mutable :class:`~core.model.ProofState` being updated.
    rank:
        The rank name (e.g. ``"designation"``, ``"weight"``).
    blocker:
        Human-readable blocker string stored in all blocker dicts.
    evidence:
        Optional evidence dict to store (defaults to ``{}``).
    trace_event:
        Trace-event name to emit.  Defaults to
        ``"singular_{rank}_closure"``.
    closed_attr:
        Name of the ``singular_*_closed`` boolean attribute on *state*
        to set to ``False``.  Defaults to ``"singular_{rank}_closed"``.
    """
    ev: Dict[str, Any] = evidence if evidence is not None else {}
    attr = closed_attr if closed_attr is not None else f"singular_{rank}_closed"
    event = trace_event if trace_event is not None else f"singular_{rank}_closure"

    setattr(state, attr, False)
    state.singular_level_evidence[rank] = ev
    state.singular_level_blockers[rank] = blocker
    state.singular_rank_states[rank] = False
    state.singular_rank_sublayers[rank] = ev
    state.singular_rank_blockers[rank] = blocker
    state.add_trace(event, {"closed": False, "blocker": blocker})
