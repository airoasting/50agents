"""Verify all 5 agent .md files have required frontmatter fields."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml


AGENTS_DIR = Path("skills/roasting/agents")
EXPECTED_AGENTS = {"roasting-black", "roasting-red", "roasting-silver",
                   "roasting-blue", "roasting-gold"}


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    return yaml.safe_load(text[3:end]) or {}


@pytest.mark.parametrize("agent_name", sorted(EXPECTED_AGENTS))
def test_agent_frontmatter(agent_name: str) -> None:
    path = AGENTS_DIR / f"{agent_name}.md"
    assert path.exists(), f"missing {path}"
    fm = parse_frontmatter(path.read_text(encoding="utf-8"))
    assert fm.get("name") == agent_name
    assert fm.get("description"), f"empty description in {path}"
    assert isinstance(fm.get("tools"), list), f"tools must be list in {path}"
    assert fm.get("model") in {"opus", "sonnet", "haiku"}, f"bad model in {path}"


def test_all_5_agents_present() -> None:
    found = {p.stem for p in AGENTS_DIR.glob("*.md")}
    assert found == EXPECTED_AGENTS, f"missing or extra: expected={EXPECTED_AGENTS}, got={found}"


def test_reviewer_tools_readonly() -> None:
    """RED, SILVER, BLUE, GOLD must have tools=['Read'] only."""
    for name in {"roasting-red", "roasting-silver", "roasting-blue", "roasting-gold"}:
        fm = parse_frontmatter((AGENTS_DIR / f"{name}.md").read_text(encoding="utf-8"))
        assert fm.get("tools") == ["Read"], f"{name} must be read-only, got {fm.get('tools')}"
