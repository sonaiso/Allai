from formal.model import Decision
from programmatic.engine import TransitionEngine


def run_unicode_to_judgement(text: str) -> dict:
    engine = TransitionEngine()
    state, trace = engine.run(text)
    return {
        "state": state,
        "trace": trace,
        "final_decision": trace[-1].decision if trace else Decision.REJECT,
    }
