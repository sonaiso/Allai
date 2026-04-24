# MVP Closure Definition v1 (Proof-Oriented)

## Scope statement

This release is a **Proof-Oriented MVP v1**, not the final full architecture. The pipeline is
complete from Unicode ingress through a 12-stage constitutional proof to final judgement.

## Execution posture (authority + closure policy)

- Official reference authority is fixed in `docs/foundations/reference_authority_map_v1.md`.
- For foundational gaps, implementation posture is **Docs+Contracts first**, then code.
- For bounded operational gaps with stable contracts, posture can be **Docs+Code together**.
- In v1 policy: `concept_first` may block on critical new layers, while `legacy_text_first`
  keeps those layers trace-required and non-blocking.

## In scope

- Constitutional proof pipeline from Unicode ingress to judgement (12 ordered stages).
- Closure gates across singular (11 ranks), weight/mizan, composition, communication,
  proposition, world model, and judgement.
- Four machine-checkable gate laws (GL-001 … GL-004) defined in `specs/gate_laws.yaml`.
- No-jump sequencing invariants defined in `specs/no_jump_invariants.yaml`.
- Trace chain validation and deterministic replay.
- Minimum-first closure gating at each rank (mandatory transition minima + deferred analysis
  layers).
- World model layer (entities, events, relations, laws, causality, goals, judgments) as a
  mandatory pre-judgement gate (GL-004).

## Pipeline stages (v1)

| # | Stage | Gate law |
|---|-------|----------|
| 1 | Unicode ingress | — |
| 2 | Admissibility | — |
| 3 | Pre-language gates | — |
| 4 | Symbolic encoding | — |
| 5 | Singular closure ×11 ranks | GL-001 |
| 6 | Weight / Mizan | GL-001 |
| 7 | Composition | GL-001, GL-003 |
| 8 | Ambiguity resolution | GL-002 |
| 9 | Proposition closure | GL-002 |
| 10 | Communicative closure | GL-002 |
| 11 | World model | GL-004 |
| 12 | Judgement | GL-002, GL-004 |

## Out of scope (explicitly deferred)

- **Qiyas** (deliberately postponed by scope decision).
- Full final architecture and all advanced inferential ranks.
- Full higher analytical ontologies for singular/compositional categories unless promoted by
  gate law.

## Hard exclusions

- No capability that bypasses constitutional closure gates.
- No direct composition without singular + weight closure (GL-001, GL-003).
- No direct judgement without proposition + communicative closure + ambiguity
  resolution/suspend + valid trace chain + world model closure (GL-002, GL-004).
- No promotion of explanatory categories to mandatory gating without explicit constitutional
  law.
