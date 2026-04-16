from formal.model import Decision, Rank
from e2e.pipeline import run_unicode_to_judgement


def test_e2e_complete_path_has_full_trace_chain():
    out = run_unicode_to_judgement("العلم نور واضح")
    trace = out["trace"]
    assert trace[0].rank == Rank.UNICODE
    assert trace[-1].rank == Rank.JUDGEMENT
    assert trace[-1].decision == Decision.COMPLETE


def test_e2e_ambiguous_input_suspends_principledly():
    out = run_unicode_to_judgement("هل العلم نور؟")
    trace = out["trace"]
    assert trace[-1].rank == Rank.ADMISSIBILITY
    assert trace[-1].decision == Decision.SUSPEND


def test_e2e_non_arabic_rejects_principledly():
    out = run_unicode_to_judgement("science is light")
    trace = out["trace"]
    assert trace[-1].rank == Rank.ADMISSIBILITY
    assert trace[-1].decision == Decision.REJECT
