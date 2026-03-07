"""Tests for scripts/lib.py — shared utilities for GitHub integration scripts."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add scripts/ to path so we can import lib and config
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import lib


class TestGetRepoOwner:
    def test_returns_config_value_when_set(self, tmp_path):
        cfg_file = tmp_path / ".ralph-beads.yml"
        cfg_file.write_text("github:\n  owner: myorg\n  repo: myrepo\n")
        import config as cfg
        with patch.object(cfg, "_find_repo_root", return_value=tmp_path):
            # Reload config cache by calling get() directly
            result = lib.get_repo_owner()
        # Can't easily test without mocking _config.get; use direct approach
        with patch.object(lib._config, "get", return_value="myorg") as mock_get:
            result = lib.get_repo_owner()
            mock_get.assert_called_once_with("github", "owner")
            assert result == "myorg"

    def test_falls_back_to_gh_when_config_empty(self):
        with patch.object(lib._config, "get", return_value=""):
            with patch("lib.run", return_value="ghowner") as mock_run:
                result = lib.get_repo_owner()
                mock_run.assert_called_once_with(
                    ["gh", "repo", "view", "--json", "owner", "-q", ".owner.login"]
                )
                assert result == "ghowner"

    def test_falls_back_to_gh_when_config_unavailable(self, monkeypatch):
        monkeypatch.setattr(lib, "_config", None)
        with patch("lib.run", return_value="detected-owner") as mock_run:
            result = lib.get_repo_owner()
            mock_run.assert_called_once()
            assert result == "detected-owner"


class TestGetRepoName:
    def test_returns_config_value_when_set(self):
        with patch.object(lib._config, "get", return_value="myrepo") as mock_get:
            result = lib.get_repo_name()
            mock_get.assert_called_once_with("github", "repo")
            assert result == "myrepo"

    def test_falls_back_to_gh_when_config_empty(self):
        with patch.object(lib._config, "get", return_value=""):
            with patch("lib.run", return_value="ghrepo") as mock_run:
                result = lib.get_repo_name()
                mock_run.assert_called_once_with(
                    ["gh", "repo", "view", "--json", "name", "-q", ".name"]
                )
                assert result == "ghrepo"

    def test_falls_back_to_gh_when_config_unavailable(self, monkeypatch):
        monkeypatch.setattr(lib, "_config", None)
        with patch("lib.run", return_value="detected-repo") as mock_run:
            result = lib.get_repo_name()
            mock_run.assert_called_once()
            assert result == "detected-repo"


class TestGetProjectNumber:
    def test_returns_int_from_config(self):
        with patch.object(lib._config, "get", return_value="42"):
            result = lib.get_project_number()
            assert result == 42

    def test_returns_none_when_not_set(self):
        with patch.object(lib._config, "get", return_value=""):
            result = lib.get_project_number()
            assert result is None

    def test_returns_none_on_invalid_value(self):
        with patch.object(lib._config, "get", return_value="not-a-number"):
            result = lib.get_project_number()
            assert result is None

    def test_returns_none_when_config_unavailable(self, monkeypatch):
        monkeypatch.setattr(lib, "_config", None)
        result = lib.get_project_number()
        assert result is None
