"""Invoke another Claude Code skill via Task/Agent dispatch.

Used by /roasting Phase 2 SEED LOAD when a case defines `enrich:`. Returns
structured output that gets embedded into BLACK's prompt.

Graceful degradation: if the target skill isn't installed, returns None
and /roasting proceeds in base 5-Color mode.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EnrichmentResult:
    skill: str
    summary: str
    raw_output: str
    success: bool


def is_skill_installed(skill_name: str) -> bool:
    """Best-effort check that another Claude Code skill is available.

    For v0.2, we check `~/.claude/skills/{skill_name}/SKILL.md` and the
    plugin directories. Returns True if the skill is reachable.
    """
    # User-level skill
    user_path = os.path.expanduser(f"~/.claude/skills/{skill_name}/SKILL.md")
    if os.path.exists(user_path):
        return True
    # Plugin-installed skill (heuristic: look for skill name in any installed plugin)
    plugins_dir = os.path.expanduser("~/.claude/plugins")
    if os.path.isdir(plugins_dir):
        for root, _, files in os.walk(plugins_dir):
            if "SKILL.md" in files and root.endswith(f"/{skill_name}"):
                return True
    return False


def invoke(skill_name: str, xxxxx: str) -> Optional[EnrichmentResult]:
    """Invoke another skill with the user's xxxxx.

    Returns None if the skill is not installed. The actual invocation in
    /roasting runtime happens via Claude Code's Task tool dispatching a
    subagent with the skill loaded; this function just prepares the spec.

    For v0.2, this is a stub that returns metadata. Runtime integration
    in v0.3 will use the Task tool API directly.
    """
    if not is_skill_installed(skill_name):
        return None
    # v0.2: stub. Returns a placeholder so the orchestrator can decide
    # whether to actually dispatch via Task tool at runtime.
    return EnrichmentResult(
        skill=skill_name,
        summary=f"[/{skill_name} enrichment ready — runtime will dispatch via Task tool]",
        raw_output="",
        success=True,
    )
