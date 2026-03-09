"""Tests for scripts/gh_labels.py — GitHub label setup."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import gh_labels


class TestGetExistingLabels:
    @patch("subprocess.run")
    def test_returns_label_names(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="type:bug\npriority:0\nblocked\n")
        result = gh_labels.get_existing_labels()
        assert result == {"type:bug", "priority:0", "blocked"}

    @patch("subprocess.run")
    def test_returns_empty_on_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        result = gh_labels.get_existing_labels()
        assert result == set()

    @patch("subprocess.run")
    def test_handles_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        result = gh_labels.get_existing_labels()
        assert result == set()


class TestCreateLabel:
    @patch("subprocess.run")
    def test_creates_label(self, mock_run, caplog):
        mock_run.return_value = MagicMock(returncode=0)
        gh_labels.create_label("type:bug", "d73a4a", "Bug label", dry_run=False)
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "gh" in cmd
        assert "label" in cmd
        assert "create" in cmd
        assert "type:bug" in cmd
        assert "created: type:bug" in caplog.text

    def test_dry_run_does_not_call_gh(self, caplog):
        gh_labels.create_label("type:bug", "d73a4a", "Bug label", dry_run=True)
        assert "would create: type:bug" in caplog.text


class TestSetupLabels:
    @patch("gh_labels.create_label")
    @patch("gh_labels.get_existing_labels", return_value=set())
    def test_creates_all_labels_when_none_exist(self, mock_existing, mock_create, capsys):
        gh_labels.setup_labels(dry_run=False)
        assert mock_create.call_count == len(gh_labels.LABELS)

    @patch("gh_labels.create_label")
    @patch("gh_labels.get_existing_labels", return_value={"type:bug", "priority:0"})
    def test_skips_existing_labels(self, mock_existing, mock_create, caplog):
        gh_labels.setup_labels(dry_run=False)
        # Should not create type:bug or priority:0
        created_names = [c.args[0] for c in mock_create.call_args_list]
        assert "type:bug" not in created_names
        assert "priority:0" not in created_names
        # Should still create others
        assert len(created_names) == len(gh_labels.LABELS) - 2
        assert "skip: type:bug (exists)" in caplog.text

    @patch("gh_labels.create_label")
    @patch("gh_labels.get_existing_labels")
    def test_skips_all_when_all_exist(self, mock_existing, mock_create):
        mock_existing.return_value = {name for _, name, _, _ in gh_labels.LABELS}
        gh_labels.setup_labels(dry_run=False)
        mock_create.assert_not_called()

    @patch("gh_labels.create_label")
    @patch("gh_labels.get_existing_labels", return_value=set())
    def test_prints_categories(self, mock_existing, mock_create, caplog):
        gh_labels.setup_labels(dry_run=False)
        assert "Issue types:" in caplog.text
        assert "Priorities:" in caplog.text
        assert "Workflow:" in caplog.text
        assert "Done." in caplog.text


class TestLabelDefinitions:
    def test_all_labels_have_four_fields(self):
        for entry in gh_labels.LABELS:
            assert len(entry) == 4

    def test_colors_are_valid_hex(self):
        for _, _, color, _ in gh_labels.LABELS:
            assert len(color) == 6
            int(color, 16)  # should not raise

    def test_no_duplicate_names(self):
        names = [name for _, name, _, _ in gh_labels.LABELS]
        assert len(names) == len(set(names))
