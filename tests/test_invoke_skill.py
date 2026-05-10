"""Test enrich field detection and invoke_skill stub."""
from __future__ import annotations

import os

from scripts.invoke_skill import invoke, is_skill_installed, EnrichmentResult


def test_returns_none_when_skill_missing(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda p: False)
    monkeypatch.setattr(os.path, "isdir", lambda p: False)
    assert invoke("nonexistent_skill", "test xxxxx") is None


def test_returns_result_when_skill_installed(monkeypatch):
    def fake_exists(path):
        return path.endswith("/dart/SKILL.md")
    monkeypatch.setattr(os.path, "exists", fake_exists)
    result = invoke("dart", "삼성전자 분기 실적")
    assert result is not None
    assert isinstance(result, EnrichmentResult)
    assert result.skill == "dart"
    assert result.success is True


def test_is_skill_installed_user_level(monkeypatch):
    def fake_exists(path):
        return path.endswith("/dart/SKILL.md")
    monkeypatch.setattr(os.path, "exists", fake_exists)
    assert is_skill_installed("dart") is True
    monkeypatch.setattr(os.path, "exists", lambda p: False)
    monkeypatch.setattr(os.path, "isdir", lambda p: False)
    assert is_skill_installed("dart") is False
