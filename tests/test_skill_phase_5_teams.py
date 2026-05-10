"""Verify Phase 5 Agent Teams primary path + auto-fallback.

After v0.2 SKILL.md cleanup, detailed pseudocode (TeamCreate args, tiebreaker
order, NotAvailable fallback) lives in references/orchestration.md.
SKILL.md keeps only the high-level flow.
"""
from __future__ import annotations

from pathlib import Path


SKILL = Path("skills/roasting/SKILL.md")
ORCH = Path("skills/roasting/references/orchestration.md")


def _both() -> str:
    return SKILL.read_text(encoding="utf-8") + "\n" + ORCH.read_text(encoding="utf-8")


def test_phase_5_has_team_create():
    body = _both()
    assert "TeamCreate" in body
    assert "SendMessage" in body
    assert "TaskCreate" in body


def test_phase_5_lifecycle_single_team_per_case():
    body = _both()
    assert "Round 2+" in body and "TeamCreate" in body
    assert "TeamDelete" in body


def test_phase_5_tiebreaker_order():
    """GOLD > RED > SILVER > BLUE priority documented in orchestration.md."""
    body = ORCH.read_text(encoding="utf-8")
    assert "GOLD" in body and "RED" in body and "SILVER" in body and "BLUE" in body
    # Tiebreaker ordering must appear with GOLD first
    gold_pos = body.find('"GOLD": 0')
    red_pos = body.find('"RED": 1')
    silver_pos = body.find('"SILVER": 2')
    blue_pos = body.find('"BLUE": 3')
    assert 0 < gold_pos < red_pos < silver_pos < blue_pos, (
        f"Tiebreaker order in orchestration.md not GOLD>RED>SILVER>BLUE: "
        f"GOLD={gold_pos}, RED={red_pos}, SILVER={silver_pos}, BLUE={blue_pos}"
    )


def test_phase_5_auto_fallback_documented():
    """Auto-fallback to sub-agent path on TeamCreate unavailability."""
    body = _both()
    assert "NotAvailable" in body or "Forbidden" in body or "폴백" in body
    assert "Sub-Agent" in body


def test_models_red_gold_opus_silver_blue_sonnet():
    """Model assignments documented in either SKILL.md or orchestration.md."""
    body = _both()
    # Opus reviewers
    for needle in ['"name": "RED"', '"name": "GOLD"', '"model": "opus"']:
        assert needle in body, f"missing '{needle}' in SKILL.md or orchestration.md"
    # Sonnet reviewers
    assert '"name": "SILVER"' in body and '"name": "BLUE"' in body
    assert '"model": "sonnet"' in body
