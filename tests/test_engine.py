from formal.model import Decision, Rank, RANK_ORDER
from programmatic.engine import TransitionEngine
from programmatic.replay import replay_from_unicode


def test_valid_arabic_full_pass_to_judgement():
    state, trace = TransitionEngine().run("العلم نور واضح")
    assert trace[-1].rank == Rank.JUDGEMENT
    assert trace[-1].decision == Decision.COMPLETE
    assert state.judgement is not None


def test_trace_entries_are_mandatory_contract_fields():
    _, trace = TransitionEngine().run("العلم نور واضح")
    assert trace
    for entry in trace:
        assert entry.reason
        assert isinstance(entry.evidence, dict)
        assert entry.legality_check is True
        assert entry.anti_jump_enforced is True


def test_no_jump_order_invariant_observed():
    _, trace = TransitionEngine().run("العلم نور واضح")
    ranks = [e.rank for e in trace]
    assert ranks == RANK_ORDER[: len(ranks)]


def test_replay_is_deterministic_for_same_unicode():
    _, trace = TransitionEngine().run("العلم نور واضح")
    ok, message = replay_from_unicode("العلم نور واضح", trace)
    assert ok is True, message
