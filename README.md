# Allai

**Allai** is a proof-oriented Arabic language AI engine that implements a *constitutional closure proof system*. It processes Arabic text through a strictly ordered, gate-enforced pipeline — from raw Unicode ingress all the way to a final linguistic judgement — with every transition validated by machine-checkable constitutional laws.

> **Status:** Proof-Oriented MVP v1 — foundational pipeline complete; Qiyas and advanced inferential ranks are explicitly deferred.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Constitutional Pipeline](#constitutional-pipeline)
- [Gate Laws](#gate-laws)
- [Directory Structure](#directory-structure)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [PostgreSQL Schema](#postgresql-schema)
- [Key Concepts](#key-concepts)
- [Contributing](#contributing)

---

## Overview

Allai's core thesis is that Arabic language understanding must be *provable*, not merely probabilistic. Every step from perceiving a character to issuing a judgement must satisfy a set of constitutional invariants and leave an auditable trace. Key properties:

- **Zero runtime dependencies** — the engine runs on Python 3.11+ standard library only.
- **Constitutional gates** — no stage may proceed until all required prior closures are satisfied.
- **Auditable trace chain** — every state transition emits a timestamped trace event enabling deterministic replay.
- **No-jump sequencing** — progression from level `L_n` to `L_(n+2)` is constitutionally forbidden without an explicit exception.

---

## Architecture

```
src/
├── core/                     # Constitutional proof pipeline
│   ├── model.py              # ProofState — central state carrier
│   ├── constants.py          # Arabic morphology constants
│   ├── exceptions.py         # Exception hierarchy
│   ├── gates/                # Gate validators (GL-001 … GL-004)
│   ├── ingress/              # Unicode admission + admissibility pre-checks
│   ├── singular/             # 11 ordered singular closure ranks
│   ├── weight/               # Mizan (morphological weight) closure
│   ├── composition/          # Role distribution (subject + predicate)
│   ├── ambiguity/            # Detection, ranking, conflict resolution
│   ├── proposition/          # Proposition closure
│   ├── communication/        # Communicative closure
│   ├── world_model/          # World model extraction + closure
│   ├── judgement/            # Final proposition-to-judgement transition
│   └── trace/                # Trace chain validation + replay engine
│
└── arabic_engine/            # Arabic-specific NLP layers
    ├── foundational/         # Pre-language gates (percept → alignment → naming)
    ├── language/             # Concept registry, lexical enrichment, minimal encoding
    └── symbolic/             # Symbolic encoding models
```

The single shared data structure is `ProofState` (a Python `dataclass`). Every module reads from and writes to this object, appending immutable trace events via `state.add_trace()`.

---

## Constitutional Pipeline

Steps execute in the following strictly ordered sequence. Each step is a *closure gate* — it may only advance if its prerequisites are satisfied.

| # | Stage | Module(s) | Closes |
|---|-------|-----------|--------|
| 1 | **Unicode Ingress** | `core/ingress/unicode_ingress.py` | `normalized_text` |
| 2 | **Admissibility** | `core/ingress/admissibility_pre_u0.py` | `admissible` |
| 3 | **Pre-language gates** | `arabic_engine/foundational/gates.py` | percept → proto-concept → alignment → naming |
| 4 | **Symbolic encoding** | `arabic_engine/symbolic/encoding.py` | `symbolic_state` |
| 5 | **Singular closure** (×11 ranks) | `core/singular/*` | existence → designation → possibility → identity → relational → weight → logical-classificatory → unified |
| 6 | **Weight / Mizan** | `core/weight/` | `weight_closed`, `weight_label` ∈ {fa3ala, maf3ul, fi3l} |
| 7 | **Composition** | `core/composition/role_distribution.py` | `ready_for_composition`, role assignments |
| 8 | **Ambiguity** | `core/ambiguity/` | `ambiguity_outcome` ∈ {resolved, suspended} |
| 9 | **Proposition closure** | `core/proposition/proposition_closure.py` | `proposition_closed` |
| 10 | **Communicative closure** | `core/communication/communicative_closure.py` | `communicative_closed` |
| 11 | **World model** | `core/world_model/` | `world_model_closed` |
| 12 | **Judgement** | `core/judgement/proposition_to_judgement.py` | `judgement` |

---

## Gate Laws

Defined in [`specs/gate_laws.yaml`](specs/gate_laws.yaml) and enforced in [`src/core/gates/validator.py`](src/core/gates/validator.py).

| ID | Trigger | Requires |
|----|---------|----------|
| **GL-001** | Composition | Complete unified singular closure record (existence + designation + possibility + identity + relational + weight + logical-classificatory + unified) |
| **GL-002** | Judgement | Proposition closed + communicative closed + ambiguity resolved/suspended + valid trace chain |
| **GL-003** | Composition | Minimum 2 tokens (subject + predicate) |
| **GL-004** | Judgement | World model closed |

No-jump invariants are defined in [`specs/no_jump_invariants.yaml`](specs/no_jump_invariants.yaml).

---

## Directory Structure

```
Allai/
├── src/                      # Python source packages
│   ├── core/                 # Constitutional proof pipeline
│   └── arabic_engine/        # Arabic NLP layers
├── tests/                    # Unit, integration, and E2E test suites
├── specs/                    # Machine-checkable gate laws (YAML)
│   ├── gate_laws.yaml
│   └── no_jump_invariants.yaml
├── docs/                     # Constitutional documents and architecture specs
│   ├── mvp_closure_definition_v1.md
│   ├── constitutional_invariants.md
│   ├── formal_entities.md
│   ├── world_model_constitution_v1.md
│   ├── six_level_singular_closure_constitution_v1.md
│   └── foundations/
├── db/                       # PostgreSQL schema, seed data, and verification queries
│   ├── schema/sql/
│   ├── seed/sql/
│   └── queries/sql/
├── pyproject.toml            # Build config and dev dependencies
└── .flake8                   # Linter configuration
```

---

## Setup

**Requirements:** Python 3.11+. No runtime dependencies.

```bash
# Clone and enter the repository
git clone https://github.com/sonaiso/Allai.git
cd Allai

# Install dev dependencies (linting, type checking, coverage)
pip install -e ".[dev]"
```

---

## Running Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py' -v
```

Run with coverage (must meet ≥ 85% threshold):

```bash
PYTHONPATH=src python -m coverage run -m unittest discover -s tests -p 'test_*.py'
python -m coverage report
```

Run the linter and type checker:

```bash
flake8 src tests
mypy src
```

---

## PostgreSQL Schema

The database schema stores atomic Arabic phonology (segments, consonants, vowels) and lexicon layers. It is optional for the core proof pipeline.

```bash
REPO_ROOT="$(pwd)"
psql "$DATABASE_URL" -f "$REPO_ROOT/db/schema/sql/001_atomic_arabic_schema.sql"
psql "$DATABASE_URL" -f "$REPO_ROOT/db/schema/sql/002_lexicon_layer_schema.sql"
psql "$DATABASE_URL" -f "$REPO_ROOT/db/seed/sql/001_atomic_arabic_seed.sql"
psql "$DATABASE_URL" -f "$REPO_ROOT/db/queries/sql/001_atomic_arabic_checks.sql"
```

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **ProofState** | Immutable-stage logical carrier of all closure facts and trace evidence. The single shared object passed through the entire pipeline. |
| **Closure Gate** | A mandatory checkpoint. A stage is *closed* when all its minimum transition conditions are satisfied. |
| **Trace Event** | An ordered, timestamped, explainable record emitted at every state transition, enabling deterministic replay. |
| **No-Jump Invariant** | `L_n → L_(n+1)` is the only lawful progression. Skipping to `L_(n+2)` is constitutionally forbidden. |
| **Singular Closure** | The 11-rank ordered proof that a single Arabic unit (word/token) is existentially, designationally, and logically closed. |
| **Mizan / Weight** | Arabic morphological weight: one of `fa3ala` (verb pattern), `maf3ul` (object pattern), or `fi3l` (base pattern). |
| **Ambiguity Outcome** | Must be `resolved` or `suspended` (with a recorded reason) before judgement can be issued. |
| **World Model** | Structured projection of the utterance onto reality: {Entities, Events, Relations, Laws, Causality, Goals, Judgments}. Required before judgement. |
| **GateViolationError** | Raised when a constitutional gate precondition is not met. |
| **SingularClosureError** | Raised when the singular closure contract is not satisfied at the composition gate. |

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development workflow, coding standards, and how to add new gate laws or closure ranks.
