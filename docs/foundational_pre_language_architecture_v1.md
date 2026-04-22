# Foundational Pre-Language Architecture v1

## Authoritative foundation decision (v1)

- Adopt staged architecture: `reality -> percept -> proto_concept -> symbolic_encoding -> language/text`.
- In v1, `reality/percept` are **derived structural representations from text ingress**, not external runtime sensors.
- Keep `legacy_text_first` as the default mode in v1.
- Enable `concept_first` as a gated experimental/benchmarking mode in v1.
- Keep `RealityAlignment` required for trace and analysis, but non-blocking for final acceptance in v1.

## Authority alignment decision (v1)

- Reference map: `docs/foundations/reference_authority_map_v1.md`.
- Governing authorities for executable contracts and gate law are ordered as:
  - A: _Thinking_ (foundational cognition)
  - B: _Islamic Personality Part 1_ (structural concept/personality bridge)
  - C: _Islamic Personality Part 3 / Usul_ (normative judgement, dalala, hujjiyya, tarjih)
- Interpretive/supportive authorities (Qur'an, Heidegger, Wittgenstein) do not independently create mandatory executable blockers unless explicitly promoted into contracts/specs.

## Glossary

- **PreReality Gate**: derives minimal pre-language observables from text.
- **PerceptUnit**: derived unit-level percept artifact anchored to token and character positions.
- **Percept Gate**: computes `PerceptUnit` artifacts.
- **ProtoConcept**: low-level conceptual candidate inferred from percept units.
- **Proto Concept Gate**: derives `ProtoConcept` candidates.
- **RealityAlignment**: alignment estimate between derived conceptual state and ingress evidence.
- **Alignment Gate**: computes alignment score/policy under non-blocking v1 policy.
- **Naming Gate**: assigns symbolic names to proto concepts.
- **Ontological Property Layer**: summarizes foundational ontological properties for v1.
- **Symbolic Encoding Layer**: constitutional-functional letter/haraka modeling (identity, normalization, role, minimal constraints).

## Legacy-to-new mapping (v1 bridge)

| Legacy path (constitutional checks) | New pre-language counterpart | v1 status |
| --- | --- | --- |
| `unicode_ingress` + `admissibility_checked` | `pre_reality_gate` -> `percept_gate` -> `proto_concept_gate` -> `alignment_gate` -> `naming_gate` | Added as trace/validation-first |
| `singular_perceptual_closure` | Derived percept evidence in `conceptual_state.pre_language.percept_units` | Compatibility preserved |
| `singular_informational_closure` | Derived proto concepts + names | Compatibility preserved |
| `singular_conceptual_closure` | Ontological layer summaries + alignment context | Compatibility preserved |
| Existing singular/composition/proposition/judgement chain | Runs unchanged as constitutional validation over staged pre-language outputs | Mandatory baseline in v1 |

## Package placement

New staged architecture modules are added under:

- `src/arabic_engine/foundational/`
- `src/arabic_engine/symbolic/`
- `src/arabic_engine/language/`

This avoids breaking existing `src/core/...` execution paths while introducing the new foundation incrementally.

## v1 policy and gate posture

1. `pre_reality_gate`
2. `percept_gate`
3. `proto_concept_gate`
4. `alignment_gate`
5. `naming_gate`
6. `unicode_ingress`

In v1:

- These are trace + validation oriented.
- `RealityAlignment` remains non-blocking for final acceptance.
- `concept_first` mode may enforce full pre-language trace coverage as a gated architecture proof mode.
- Critical new foundational layers are blocking in `concept_first`.
- In `legacy_text_first`, those layers remain trace-required and non-blocking for v1 acceptance.
