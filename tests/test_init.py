"""Tests for scripts/init.py — Purser project initialization."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import init


class TestStepPrerequisites:
    @patch("init.prereqs")
    def test_exits_on_check_only(self, mock_prereqs):
        mock_prereqs.check_prerequisites.return_value = {
            "all_ok": True,
            "platform": "linux-apt",
            "tools": [],
        }
        with pytest.raises(SystemExit) as exc_info:
            init.step_prerequisites(check_only=True)
        assert exc_info.value.code == 0

    @patch("init.prereqs")
    def test_continues_when_all_ok(self, mock_prereqs):
        mock_prereqs.check_prerequisites.return_value = {
            "all_ok": True,
            "platform": "linux-apt",
            "tools": [],
        }
        result = init.step_prerequisites(check_only=False)
        assert result is True

    @patch("init.prereqs")
    def test_exits_when_git_missing(self, mock_prereqs):
        mock_prereqs.check_prerequisites.return_value = {
            "all_ok": False,
            "platform": "linux-apt",
            "tools": [
                {"name": "git", "found": False, "description": "", "version": None, "install": ""},
                {
                    "name": "python3",
                    "found": True,
                    "description": "",
                    "version": "3.12",
                    "install": "",
                },
            ],
        }
        with pytest.raises(SystemExit) as exc_info:
            init.step_prerequisites(check_only=False)
        assert exc_info.value.code == 1

    @patch("init.prereqs")
    def test_warns_when_optional_missing(self, mock_prereqs, caplog):
        mock_prereqs.check_prerequisites.return_value = {
            "all_ok": False,
            "platform": "linux-apt",
            "tools": [
                {"name": "git", "found": True, "description": "", "version": "2.43", "install": ""},
                {
                    "name": "python3",
                    "found": True,
                    "description": "",
                    "version": "3.12",
                    "install": "",
                },
                {"name": "gh", "found": False, "description": "", "version": None, "install": ""},
            ],
        }
        result = init.step_prerequisites(check_only=False)
        assert result is True
        assert "WARNING" in caplog.text


class TestStepVenv:
    @patch("shutil.which", return_value=None)
    def test_skips_when_uv_missing(self, _, caplog):
        init.step_venv()
        assert "uv not found" in caplog.text

    @patch("init._run")
    @patch("shutil.which", return_value="/usr/bin/uv")
    def test_syncs_when_venv_exists(self, _, mock_run, monkeypatch, tmp_path):
        monkeypatch.setattr(init, "REPO_ROOT", tmp_path)
        (tmp_path / ".venv").mkdir()
        mock_run.return_value = MagicMock(returncode=0)
        init.step_venv()
        # Should call uv sync, not uv venv
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert any("sync" in cmd for cmd in cmds)

    @patch("init._run")
    @patch("shutil.which", return_value="/usr/bin/uv")
    def test_creates_venv_when_missing(self, _, mock_run, monkeypatch, tmp_path):
        monkeypatch.setattr(init, "REPO_ROOT", tmp_path)
        mock_run.return_value = MagicMock(returncode=0)
        init.step_venv()
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert any("venv" in cmd for cmd in cmds)
        assert any("sync" in cmd for cmd in cmds)


class TestStepBeadsDb:
    @patch("init._run")
    def test_skips_when_beads_exists(self, mock_run, monkeypatch, tmp_path, caplog):
        monkeypatch.setattr(init, "REPO_ROOT", tmp_path)
        (tmp_path / ".beads").mkdir()
        mock_run.return_value = MagicMock(returncode=0, stdout="[]")
        init.step_beads_db()
        assert "exists" in caplog.text

    @patch("init._run")
    @patch("shutil.which", return_value="/usr/bin/bd")
    def test_initializes_when_missing(self, _, mock_run, monkeypatch, tmp_path, caplog):
        monkeypatch.setattr(init, "REPO_ROOT", tmp_path)
        mock_run.return_value = MagicMock(returncode=0)
        init.step_beads_db()
        assert "Initializing" in caplog.text


class TestStepGithubRemote:
    @patch("init.gh_remote")
    def test_skips_when_skip_github(self, _, caplog):
        owner, repo = init.step_github_remote(skip_github=True)
        assert owner == ""
        assert repo == ""
        assert "Skipped" in caplog.text

    @patch("init.gh_remote")
    def test_returns_owner_repo_when_found(self, mock_remote):
        mock_remote.detect_or_create.return_value = {
            "status": "found",
            "remote": {"owner": "testowner", "repo": "testrepo", "name": "origin"},
        }
        owner, repo = init.step_github_remote(skip_github=False)
        assert owner == "testowner"
        assert repo == "testrepo"

    @patch("init.gh_remote")
    def test_returns_owner_repo_when_connected(self, mock_remote):
        # First call (check_only=True) finds nothing, second call returns connected
        mock_remote.detect_or_create.side_effect = [
            {"status": "skipped", "remote": None},
            {
                "status": "connected",
                "remote": {"owner": "org", "repo": "myrepo", "name": "origin"},
                "validated": True,
            },
        ]
        owner, repo = init.step_github_remote(skip_github=False)
        assert owner == "org"
        assert repo == "myrepo"


class TestStepGithubProject:
    def test_skips_when_skip_github(self, caplog):
        result = init.step_github_project("owner", "repo", skip_github=True)
        assert result == ""
        assert "Skipped" in caplog.text

    def test_skips_when_no_remote(self):
        result = init.step_github_project("", "", skip_github=False)
        assert result == ""

    @patch("init.gh_project_setup")
    def test_returns_project_number_when_found(self, mock_setup):
        mock_setup.detect_or_setup.return_value = {
            "status": "found",
            "project": {"title": "Purser", "number": 42},
        }
        result = init.step_github_project("owner", "repo", skip_github=False)
        assert result == "42"


class TestStepLabels:
    def test_skips_when_skip_github(self, caplog):
        init.step_labels("owner", "repo", skip_github=True)
        assert "Skipped" in caplog.text

    def test_skips_when_no_remote(self, caplog):
        init.step_labels("", "", skip_github=False)
        assert "Skipped" in caplog.text

    @patch("init.gh_labels")
    @patch("init.config")
    def test_skips_when_already_bootstrapped(self, mock_config, mock_labels, caplog):
        mock_config.get.return_value = "true"
        init.step_labels("owner", "repo", skip_github=False)
        mock_labels.setup_labels.assert_not_called()
        assert "already bootstrapped" in caplog.text

    @patch("init.gh_labels")
    @patch("init.config")
    def test_runs_when_not_bootstrapped(self, mock_config, mock_labels):
        mock_config.get.return_value = "false"
        init.step_labels("owner", "repo", skip_github=False)
        mock_labels.setup_labels.assert_called_once_with(dry_run=False)


class TestStepSaveConfig:
    @patch("init.config")
    def test_saves_config(self, mock_config, tmp_path):
        mock_config.load_config.return_value = {
            "github": {"owner": "", "repo": "", "project_number": ""},
            "labels": {"bootstrap": "false"},
        }
        init.step_save_config("myowner", "myrepo", "5", skip_github=False)
        mock_config.save_config.assert_called_once()
        cfg = mock_config.save_config.call_args[0][0]
        assert cfg["github"]["owner"] == "myowner"
        assert cfg["github"]["repo"] == "myrepo"
        assert cfg["github"]["project_number"] == "5"
        assert cfg["labels"]["bootstrap"] == "true"

    @patch("init.config")
    def test_does_not_mark_bootstrap_when_skip_github(self, mock_config):
        mock_config.load_config.return_value = {
            "github": {"owner": "", "repo": "", "project_number": ""},
            "labels": {"bootstrap": "false"},
        }
        init.step_save_config("owner", "repo", "", skip_github=True)
        cfg = mock_config.save_config.call_args[0][0]
        assert cfg["labels"]["bootstrap"] == "false"


class TestStepSummary:
    def test_prints_summary(self, monkeypatch, tmp_path, caplog):
        monkeypatch.setattr(init, "REPO_ROOT", tmp_path)
        # Create .beads dir and config
        (tmp_path / ".beads").mkdir()
        monkeypatch.setattr(init.config, "config_path", lambda root: tmp_path / ".purser.yml")
        monkeypatch.setattr(init.config, "get", lambda s, k, root=None: "")
        init.step_summary()
        assert "Setup Summary" in caplog.text
        assert "Next steps:" in caplog.text


class TestMainHelpFlag:
    def test_help_flag(self, capsys):
        init.main(["--help"])
        captured = capsys.readouterr()
        assert "--check" in captured.out
        assert "--skip-github" in captured.out
