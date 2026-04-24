# Contributing to Allai

Thank you for your interest in contributing. This document describes the development workflow,
coding standards, and the constitutional rules that govern how the pipeline may be extended.

---

## Table of Contents

- [Development Setup](#development-setup)
- [Running Tests and Checks](#running-tests-and-checks)
- [Code Style](#code-style)
- [Constitutional Constraints](#constitutional-constraints)
- [Adding a New Closure Rank](#adding-a-new-closure-rank)
- [Adding a New Gate Law](#adding-a-new-gate-law)
- [Commit Messages](#commit-messages)

---

## Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"
```

Runtime dependencies: **none** (Python 3.11+ standard library only).

---

## Running Tests and Checks

```bash
# Full test suite
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py' -v

# Coverage (must stay ≥ 85 %)
PYTHONPATH=src python -m coverage run -m unittest discover -s tests -p 'test_*.py'
python -m coverage report

# Linter
flake8 src tests

# Type checker
mypy src
```

All checks must pass before a pull request can be merged.

---

## Code Style

- Follow PEP 8. `flake8` configuration is in `.flake8`.
- Use `from __future__ import annotations` for forward-reference compatibility.
- Prefer explicit `Optional[T]` / `T | None` over bare `None` returns.
- Keep modules small and single-purpose. Each closure rank lives in its own file.
- Every public function and class must have a docstring when the intent is not self-evident
  from its name and type annotations.
- Do not add comments unless they explain *why*, not *what*.

---

## Constitutional Constraints

The following rules are non-negotiable (see `docs/constitutional_invariants.md`):

1. **No composition without complete unified singular closure record.**
2. **No judgement without proposition + communicative + ambiguity + trace chain + world model closure.**
3. **No-jump progression:** `L_n → L_(n+1)` only; skipping is constitutionally forbidden.
4. **Minimum-first doctrine:** Only minimum transition conditions are mandatory gates. Higher
   analytical fields are non-gating by default.
5. **Gate-law-first:** A new foundational clause becomes an executable blocker only after it is
   explicitly promoted into a machine-checkable gate law in `specs/gate_laws.yaml` and
   implemented in `src/core/gates/validator.py`.

Any contribution that would allow bypassing a gate without satisfying the constitutional
requirements will be rejected.

---

## Adding a New Closure Rank

1. Create a new module under `src/core/singular/` (e.g. `my_new_rank_closure.py`).
2. Implement an `apply_my_new_rank_closure(state: ProofState) -> ProofState` function that:
   - Reads from `state`.
   - Sets the corresponding boolean flag on `state` (e.g. `state.singular_my_new_rank_closed`).
   - Adds a trace event via `state.add_trace(...)`.
   - Returns the mutated `state`.
3. Add the new flag to `ProofState` in `src/core/model.py`.
4. Update `apply_singular_unified_closure` in `src/core/singular/unified_closure.py` to include
   the new rank in `_required_rank_states` **only if it is a mandatory gate**; otherwise leave
   it as a non-gating deferred field.
5. Add a no-jump invariant in `specs/no_jump_invariants.yaml` if the rank introduces a new
   required event.
6. Write tests in `tests/` covering both the happy path and the blocker path.

---

## Adding a New Gate Law

1. Add the law to `specs/gate_laws.yaml` with a unique `GL-NNN` id, a human-readable `name`,
   the `when` trigger (`composition` or `judgement`), and the list of `requires` conditions.
2. Implement enforcement in `src/core/gates/validator.py` by adding a new `require_for_*`
   function or extending an existing one.
3. Update `docs/constitutional_invariants.md` and the relevant constitutional document in
   `docs/` to describe the new law.
4. Update the gate laws table in `README.md`.
5. Write tests that verify the law is enforced (both violation and satisfaction paths).

---

## Commit Messages

Use the conventional commits format:

```
<type>(<scope>): <short summary>

[optional body]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

Examples:
```
feat(singular): add morphological pattern rank closure
docs(constitutional): promote new gate law GL-005
test(e2e): add world model proof end-to-end test
```
