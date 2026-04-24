# World Model Constitution v1

## Scope

This constitution defines the `WorldModel` layer, which is inserted between
`PropositionClosure` and `Judgement` in the proof pipeline.  It ensures that
linguistic understanding is anchored to a *world projection* — a structured
representation of reality — before any judgment is issued.

## Position in the Processing Pipeline

```
Lexeme → Sentence → Utterance → WorldModel → Judgment
```

Full pipeline order:

```
Ingress → Unicode → Admissibility → Symbolic → Singular Closure (×7 ranks)
→ Weight/Mizan → Composition → Ambiguity → Communicative → Proposition
→ WorldModel (extract + close) → Judgement
```

## Formal Definition

```
WorldModel = {Entities, Events, Relations, Laws, Causality, Goals, Judgments}
```

| Domain    | Question                                                              |
| --------- | --------------------------------------------------------------------- |
| Entities  | What things / agents exist?                                           |
| Events    | What actions or occurrences are described?                            |
| Relations | What relations hold between entities?                                 |
| Laws      | What governing rules apply? (linguistic / logical / physical / normative / social) |
| Causality | What is the cause → effect chain?                                     |
| Goals     | What is the purpose or intent?                                        |
| Judgments | What evaluative outcome follows? (true/false, valid/invalid, possible/impossible, good/bad) |

## Conditions for Real-World Understanding

```
UnderstandingPossible =
    LanguageClosed
  + WorldAnchored
  + LawChecked
  + CausalityMapped
  + GoalResolved
  + JudgmentReady
```

Linguistic intelligibility alone is insufficient.  The system must be able to
answer:

```
Who? What? Where? When? How? Why? Under which law?
```

## WorldModel Layer Matrix

| Layer     | Minimum                   | Arabic example            |
| --------- | ------------------------- | ------------------------- |
| Entity    | identity + type + attrs   | زيد = إنسان               |
| Event     | action + agent + time     | كتب زيد                   |
| Relation  | link between two parties  | زيد في البيت              |
| Law       | governing rule            | الفاعل مرفوع / النار تحرق |
| Causality | cause ⟶ effect             | اجتهد ⟶ نجح               |
| Goal      | action for a purpose      | درس لينجح                 |
| Judgment  | evaluative result         | صادق/كاذب، ممكن/ممتنع     |

## Operational Record Schema

```json
{
  "entities":   [],
  "events":     [],
  "relations":  [],
  "laws":       [],
  "causality":  [],
  "goals":      [],
  "judgments":  [],
  "uncertainty": [],
  "blockers":   [],
  "closed":     false
}
```

## Closure Conditions (`apply_world_model_closure`)

`world_model_closed = True` when **all** of the following hold:

1. `language_closed` — `proposition_closed` is `True`
2. `world_anchored` — at least one entity was extracted
3. `law_checked` — at least one law is present
4. `causality_mapped` — the causality list exists (may be empty; emptiness is
   recorded in `uncertainty`, not treated as a blocker)
5. `goal_resolved` — the goals list exists (may be empty; emptiness is recorded
   in `uncertainty`)
6. `judgment_ready` — at least one entity **and** at least one event were
   extracted, providing a minimal basis for judgment

## Gate Law

`GL-004` (in `specs/gate_laws.yaml`):

```yaml
- id: GL-004
  name: judgement_requires_world_model_closure
  when: judgement
  requires:
    - world_model_closed
```

## No-Jump Invariant

`NJ-005` (in `specs/no_jump_invariants.yaml`):

```yaml
- id: NJ-005
  name: no_judgement_before_world_model_closure
  forbidden_if_missing:
    - world_model_extracted
    - world_model_closed
```

## Required Trace Events

The following two events are now mandatory in `_REQUIRED_EVENTS_FOR_JUDGEMENT`
(in `src/core/trace/chain_validation.py`), ordered after `proposition_closure`:

1. `world_model_extracted`
2. `world_model_closure`

## Module Map

| Purpose                    | Module                                  |
| -------------------------- | --------------------------------------- |
| Data models                | `src/core/world_model/models.py`        |
| Extraction from composition| `src/core/world_model/extractor.py`     |
| Closure gate               | `src/core/world_model/closure.py`       |
| Judgement gate enforcement | `src/core/gates/validator.py`           |
| Trace chain validation     | `src/core/trace/chain_validation.py`    |

## Foundational Principle

```
UtteranceMeaning → WorldProjection → Judgment
```

Meaning expressed in language must be projected onto a world model before a
judgment — truth, validity, possibility, or moral evaluation — can be issued.
This is the transition from *understanding speech* to *understanding the world
that speech describes*.
