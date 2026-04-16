# Contributing

## Adding a new rank or transition safely
1. Add the new rank to `formal/model.py` and preserve strict `RANK_ORDER` sequence.
2. Add preconditions in `rank_preconditions` so illegal transitions cannot run.
3. Implement a deterministic handler that returns `(decision, reason, evidence)`.
4. Register handler order in `programmatic/engine.py` without bypassing prior gates.
5. Ensure the transition appends a mandatory trace entry.
6. Add tests for pass/suspend/reject behavior and replay stability.
