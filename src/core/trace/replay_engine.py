import hashlib
import json

from core.model import ProofState


def replay_digest(state: ProofState) -> str:
    stable_trace = [entry for entry in state.trace_chain if entry.get("event") != "replay_generated"]
    serialized = json.dumps(stable_trace, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    state.add_trace("replay_generated", {"digest": digest})
    return digest
