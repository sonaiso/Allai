import hashlib
import json

from core.model import ProofState


def replay_digest(state: ProofState) -> str:
    serialized = json.dumps(state.trace_chain, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    state.add_trace("replay_generated", {"digest": digest})
    return digest
