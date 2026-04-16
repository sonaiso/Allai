from formal.model import TraceEntry
from programmatic.engine import TransitionEngine


def replay_from_unicode(original_unicode: str, expected_trace: list[TraceEntry]) -> tuple[bool, str]:
    engine = TransitionEngine()
    _, replay_trace = engine.run(original_unicode)

    if len(replay_trace) != len(expected_trace):
        return False, "Trace length mismatch"

    for a, b in zip(expected_trace, replay_trace):
        if a.rank != b.rank or a.decision != b.decision or a.reason != b.reason:
            return False, f"Trace mismatch at rank {a.rank}: expected {a.decision}/{a.reason}, got {b.decision}/{b.reason}"

    return True, "Replay successful and deterministic"
