"""Tests for scripts/gh_remote.py — GitHub remote detection and creation."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import gh_remote


class TestParseGithubUrl:
    def test_ssh_url(self):
        result = gh_remote._parse_github_url("git@github.com:owner/repo.git")
        assert result == ("owner", "repo")

    def test_ssh_url_no_git_suffix(self):
        result = gh_remote._parse_github_url("git@github.com:owner/repo")
        assert result == ("owner", "repo")

    def test_https_url(self):
        result = gh_remote._parse_github_url("https://github.com/owner/repo.git")
        assert result == ("owner", "repo")

    def test_https_url_no_git_suffix(self):
        result = gh_remote._parse_github_url("https://github.com/owner/repo")
        assert result == ("owner", "repo")

    def test_ssh_protocol_url(self):
        result = gh_remote._parse_github_url("ssh://git@github.com/owner/repo.git")
        assert result == ("owner", "repo")

    def test_non_github_url_returns_none(self):
        result = gh_remote._parse_github_url("git@gitlab.com:owner/repo.git")
        assert result is None

    def test_empty_string_returns_none(self):
        result = gh_remote._parse_github_url("")
        assert result is None

    def test_trailing_whitespace(self):
        result = gh_remote._parse_github_url("  https://github.com/owner/repo.git  ")
        assert result == ("owner", "repo")

    def test_trailing_slash(self):
        result = gh_remote._parse_github_url("https://github.com/owner/repo/")
        assert result == ("owner", "repo")


class TestDetectGithubRemotes:
    @patch("gh_remote._run")
    def test_finds_github_remotes(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0,
            stdout="origin\tgit@github.com:myorg/myrepo.git (fetch)\n"
                   "origin\tgit@github.com:myorg/myrepo.git (push)\n",
            stderr="",
        )
        remotes = gh_remote.detect_github_remotes()
        assert len(remotes) == 1
        assert remotes[0]["name"] == "origin"
        assert remotes[0]["owner"] == "myorg"
        assert remotes[0]["repo"] == "myrepo"

    @patch("gh_remote._run")
    def test_multiple_remotes(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0,
            stdout="origin\tgit@github.com:org1/repo1.git (fetch)\n"
                   "origin\tgit@github.com:org1/repo1.git (push)\n"
                   "upstream\thttps://github.com/org2/repo2.git (fetch)\n"
                   "upstream\thttps://github.com/org2/repo2.git (push)\n",
            stderr="",
        )
        remotes = gh_remote.detect_github_remotes()
        assert len(remotes) == 2
        names = {r["name"] for r in remotes}
        assert "origin" in names
        assert "upstream" in names

    @patch("gh_remote._run")
    def test_skips_non_github(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0,
            stdout="origin\tgit@gitlab.com:org/repo.git (fetch)\n"
                   "origin\tgit@gitlab.com:org/repo.git (push)\n",
            stderr="",
        )
        remotes = gh_remote.detect_github_remotes()
        assert len(remotes) == 0

    @patch("gh_remote._run")
    def test_handles_no_remotes(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        remotes = gh_remote.detect_github_remotes()
        assert len(remotes) == 0

    @patch("gh_remote._run")
    def test_handles_git_failure(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess([], 128, stdout="", stderr="not a git repo")
        remotes = gh_remote.detect_github_remotes()
        assert len(remotes) == 0


class TestSelectRemote:
    def test_prefers_origin(self):
        remotes = [
            {"name": "upstream", "url": "", "owner": "a", "repo": "b"},
            {"name": "origin", "url": "", "owner": "c", "repo": "d"},
        ]
        result = gh_remote.select_remote(remotes)
        assert result["name"] == "origin"

    def test_falls_back_to_first(self):
        remotes = [
            {"name": "upstream", "url": "", "owner": "a", "repo": "b"},
        ]
        result = gh_remote.select_remote(remotes)
        assert result["name"] == "upstream"

    def test_respects_preferred(self):
        remotes = [
            {"name": "origin", "url": "", "owner": "a", "repo": "b"},
            {"name": "mine", "url": "", "owner": "c", "repo": "d"},
        ]
        result = gh_remote.select_remote(remotes, preferred="mine")
        assert result["name"] == "mine"

    def test_empty_returns_none(self):
        assert gh_remote.select_remote([]) is None


class TestDetectOrCreate:
    @patch("gh_remote.validate_remote", return_value=True)
    @patch("gh_remote.detect_github_remotes")
    def test_found_remote(self, mock_detect, mock_validate):
        mock_detect.return_value = [
            {"name": "origin", "url": "git@github.com:org/repo.git", "owner": "org", "repo": "repo"},
        ]
        result = gh_remote.detect_or_create(Path("/tmp/fake"))
        assert result["status"] == "found"
        assert result["remote"]["owner"] == "org"
        assert result["validated"] is True

    @patch("gh_remote.detect_github_remotes", return_value=[])
    @patch("gh_remote._has_gh", return_value=False)
    def test_no_remote_no_gh(self, mock_gh, mock_detect):
        result = gh_remote.detect_or_create(Path("/tmp/fake"))
        assert result["status"] == "skipped"
        assert "gh CLI" in result["message"]

    @patch("gh_remote.detect_github_remotes", return_value=[])
    def test_check_only_skips(self, mock_detect):
        result = gh_remote.detect_or_create(Path("/tmp/fake"), check_only=True)
        assert result["status"] == "skipped"

    @patch("gh_remote.config.load_config")
    @patch("gh_remote.detect_github_remotes", return_value=[])
    def test_auto_create_skip(self, mock_detect, mock_config):
        mock_config.return_value = {
            "github": {"remote": "origin", "auto_create": "skip", "owner": "", "repo": "", "project_number": ""},
            "labels": {"bootstrap": "false"},
        }
        result = gh_remote.detect_or_create(Path("/tmp/fake"))
        assert result["status"] == "skipped"


class TestJsonOutput:
    @patch("gh_remote.validate_remote", return_value=True)
    @patch("gh_remote.detect_github_remotes")
    def test_result_is_json_serializable(self, mock_detect, mock_validate):
        mock_detect.return_value = [
            {"name": "origin", "url": "u", "owner": "o", "repo": "r"},
        ]
        result = gh_remote.detect_or_create(Path("/tmp/fake"))
        output = json.dumps(result)
        parsed = json.loads(output)
        assert parsed["status"] == "found"
