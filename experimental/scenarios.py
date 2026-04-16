from __future__ import annotations

from dataclasses import dataclass

from e2e.pipeline import run_unicode_to_judgement


@dataclass(frozen=True)
class Scenario:
    name: str
    text: str
    expected_final: str


SCENARIOS = [
    Scenario("valid_arabic", "العلم نور واضح", "COMPLETE"),
    Scenario("ambiguous_arabic", "هل العلم نور؟", "SUSPEND"),
    Scenario("non_arabic", "science is light", "REJECT"),
    Scenario("incomplete", "   ", "SUSPEND"),
    Scenario("suspend_relation", "نور", "SUSPEND"),
]


def run_scenarios() -> list[tuple[str, str, bool]]:
    results: list[tuple[str, str, bool]] = []
    for scenario in SCENARIOS:
        out = run_unicode_to_judgement(scenario.text)
        final = out["final_decision"].value
        results.append((scenario.name, final, final == scenario.expected_final))
    return results


if __name__ == "__main__":
    for name, final, ok in run_scenarios():
        print(f"{name}: {final} (ok={ok})")
