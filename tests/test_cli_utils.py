"""Tests for scripts/cli_utils.py — cross-platform CLI utilities."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import cli_utils


class TestRequireCommands:
    def test_passes_for_available_commands(self):
        # git and python3 should be available in any dev environment
        cli_utils.require_commands(["git", "python3"])

    def test_exits_for_missing_command(self):
        with pytest.raises(SystemExit) as exc_info:
            cli_utils.require_commands(["nonexistent_tool_xyz_123"])
        assert exc_info.value.code == 1

    def test_exits_for_any_missing_in_list(self):
        with pytest.raises(SystemExit) as exc_info:
            cli_utils.require_commands(["git", "nonexistent_tool_xyz_123"])
        assert exc_info.value.code == 1

    def test_prints_error_for_each_missing(self, caplog):
        with pytest.raises(SystemExit):
            cli_utils.require_commands(["missing_aaa", "missing_bbb"])
        assert "missing_aaa" in caplog.text
        assert "missing_bbb" in caplog.text

    def test_empty_list_passes(self):
        cli_utils.require_commands([])


class TestRequireGhAuth:
    @patch("subprocess.run")
    def test_passes_when_authenticated(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        # Should not raise
        cli_utils.require_gh_auth()
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_exits_when_not_authenticated(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        with pytest.raises(SystemExit) as exc_info:
            cli_utils.require_gh_auth()
        assert exc_info.value.code == 1

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_exits_when_gh_not_found(self, _):
        with pytest.raises(SystemExit) as exc_info:
            cli_utils.require_gh_auth()
        assert exc_info.value.code == 1

    @patch("subprocess.run")
    def test_prints_auth_message_on_failure(self, mock_run, caplog):
        mock_run.return_value = MagicMock(returncode=1)
        with pytest.raises(SystemExit):
            cli_utils.require_gh_auth()
        assert "gh auth login" in caplog.text


class TestRunPythonScript:
    @patch("sys.platform", "win32")
    @patch("subprocess.run")
    def test_windows_uses_subprocess(self, mock_run, tmp_path):
        script = tmp_path / "test_script.py"
        script.write_text("print('hello')")
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(SystemExit) as exc_info:
            cli_utils.run_python_script(script, ["--flag"])
        assert exc_info.value.code == 0

        call_args = mock_run.call_args[0][0]
        assert str(script) in call_args
        assert "--flag" in call_args

    @patch("sys.platform", "win32")
    @patch("subprocess.run")
    def test_sets_pythonpath(self, mock_run, tmp_path):
        script = tmp_path / "test_script.py"
        script.write_text("")
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(SystemExit):
            cli_utils.run_python_script(script)

        assert str(tmp_path) in os.environ.get("PYTHONPATH", "")

    @patch("sys.platform", "win32")
    @patch("subprocess.run")
    def test_preserves_existing_pythonpath(self, mock_run, tmp_path):
        script = tmp_path / "test_script.py"
        script.write_text("")
        mock_run.return_value = MagicMock(returncode=0)
        original = "/some/existing/path"

        with patch.dict(os.environ, {"PYTHONPATH": original}):
            with pytest.raises(SystemExit):
                cli_utils.run_python_script(script)
            pp = os.environ["PYTHONPATH"]
            assert str(tmp_path) in pp
            assert original in pp
            assert os.pathsep in pp

    @patch("sys.platform", "linux")
    @patch("os.execvp")
    def test_unix_uses_execvp(self, mock_execvp, tmp_path):
        script = tmp_path / "test_script.py"
        script.write_text("")

        cli_utils.run_python_script(script, ["--arg"])

        mock_execvp.assert_called_once()
        cmd = mock_execvp.call_args[0][1]
        assert str(script) in cmd
        assert "--arg" in cmd

    @patch("sys.platform", "win32")
    @patch("subprocess.run")
    def test_no_args_defaults_to_empty(self, mock_run, tmp_path):
        script = tmp_path / "test_script.py"
        script.write_text("")
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(SystemExit):
            cli_utils.run_python_script(script)

        call_args = mock_run.call_args[0][0]
        assert len(call_args) == 2  # [python, script]


class TestSetupLogging:
    def test_returns_logger_with_name(self):
        logger = cli_utils.setup_logging("test.module")
        assert logger.name == "test.module"

    def test_default_level_is_info(self):
        import logging

        logger = cli_utils.setup_logging("test.default_level")
        assert logger.level == logging.INFO

    def test_custom_default_level(self):
        import logging

        logger = cli_utils.setup_logging("test.custom_level", default_level=logging.DEBUG)
        assert logger.level == logging.DEBUG

    def test_env_overrides_default(self, monkeypatch):
        import logging

        monkeypatch.setenv("PURSER_LOG_LEVEL", "WARNING")
        logger = cli_utils.setup_logging("test.env_override")
        assert logger.level == logging.WARNING

    def test_invalid_env_falls_back_to_default(self, monkeypatch):
        import logging

        monkeypatch.setenv("PURSER_LOG_LEVEL", "BOGUS")
        logger = cli_utils.setup_logging("test.invalid_env")
        assert logger.level == logging.INFO

    def test_empty_env_falls_back_to_default(self, monkeypatch):
        import logging

        monkeypatch.setenv("PURSER_LOG_LEVEL", "")
        logger = cli_utils.setup_logging("test.empty_env")
        assert logger.level == logging.INFO

    def test_root_logger_gets_handler(self):
        import logging

        # Clear root handlers to test setup
        root = logging.getLogger()
        original_handlers = root.handlers[:]
        root.handlers.clear()
        try:
            cli_utils.setup_logging("test.handler_check")
            assert len(root.handlers) >= 1
            assert isinstance(root.handlers[0], logging.StreamHandler)
        finally:
            root.handlers = original_handlers

    def test_format_is_message_only(self):
        import logging

        root = logging.getLogger()
        original_handlers = root.handlers[:]
        root.handlers.clear()
        try:
            cli_utils.setup_logging("test.format")
            handler = root.handlers[0]
            assert handler.formatter._fmt == "%(message)s"
        finally:
            root.handlers = original_handlers

    def test_none_name_configures_root(self):
        import logging

        logger = cli_utils.setup_logging(None)
        assert logger is logging.getLogger()
