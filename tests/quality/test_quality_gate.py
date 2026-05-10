"""Quality gate: 15 scenarios, average final_score >= 9.0 (beta v0.1).

Marked @pytest.mark.slow — requires live Claude API access via `claude` CLI.
Run explicitly via: .venv/bin/pytest tests/quality/test_quality_gate.py -v -m slow -s

Expected cost: ~$5-7 per full run (15 scenarios, 1-2 rounds each).
Budget cap: $10 per run. Do not iterate if gate fails — report baseline honestly.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import pytest

from tests.quality.run_scenario import run_one


pytestmark = pytest.mark.slow


def test_quality_gate():
    scenarios = json.loads(
        Path("tests/quality/scenarios.json").read_text(encoding="utf-8"))
    scores: list[float] = []
    failures: list[tuple[str, str, float]] = []
    errors: list[tuple[str, str, str]] = []

    for s in scenarios:
        result = run_one(case_id=s["case_id"], xxxxx=s["xxxxx"])
        scores.append(result.final_score)

        if result.error:
            errors.append((s["case_id"], s["xxxxx"][:40], result.error[:100]))

        if result.final_score < s["min_score"]:
            failures.append((s["case_id"], s["xxxxx"][:40], result.final_score))

    avg = statistics.fmean(scores)
    print(f"\nQuality gate: avg={avg:.2f}, scores={[f'{s:.2f}' for s in scores]}")

    if errors:
        print(f"\nScenarios with errors ({len(errors)}):")
        for c, x, err in errors:
            print(f"  {c}: '{x}...' -> ERROR: {err}")

    if failures:
        print(f"\nBelow per-scenario threshold ({len(failures)}/{len(scenarios)}):")
        for c, x, sc in failures:
            print(f"  {c}: '{x}...' -> {sc:.2f} (< 9.0)")

    print(f"\nPassing scenarios: {len(scores) - len(failures)}/{len(scenarios)}")
    print(f"Error scenarios: {len(errors)}/{len(scenarios)}")

    assert avg >= 9.0, (
        f"Quality gate FAILED: avg={avg:.2f} < 9.0. "
        f"Passing={len(scores)-len(failures)}/15. "
        f"Errors={len(errors)}/15. "
        f"Scores={[f'{s:.2f}' for s in scores]}"
    )
