from experimental.scenarios import run_scenarios


def test_scenario_set_is_reproducible_and_expected():
    results_first = run_scenarios()
    results_second = run_scenarios()

    assert results_first == results_second
    for _, _, ok in results_first:
        assert ok is True
