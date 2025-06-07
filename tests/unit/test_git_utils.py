"""Tests for the git utilities module (updated for latest API)."""

from unittest.mock import MagicMock, patch

from commit_message_generator.git_utils import (
    get_staged_diff,
    is_git_repo,
    run_git_command,
)


def test_run_git_command_success() -> None:
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success output\n"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        result = run_git_command(["status"])
        assert result == ("success output\n", "", 0)
        mock_run.assert_called_once_with(
            ["git", "status"],
            cwd=None,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )


def test_run_git_command_error() -> None:
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error message\n"
        mock_run.return_value = mock_result
        result = run_git_command(["invalid-command"])
        assert result == ("", "error message\n", 1)


def test_is_git_repo_positive(tmp_path) -> None:
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()
    assert is_git_repo(str(repo_dir))


def test_is_git_repo_negative(tmp_path) -> None:
    """Test is_git_repo with a non-git directory."""
    # Create a non-git directory
    repo_dir = tmp_path / "not_a_repo"
    repo_dir.mkdir()

    assert is_git_repo(str(repo_dir)) is False


def test_get_staged_diff_success() -> None:
    """Test getting staged diff."""
    with patch("commit_message_generator.git_utils.run_git_command") as mock_run, patch(
        "commit_message_generator.git_utils.is_git_repo"
    ) as mock_is_git_repo:
        # Mock is_git_repo to return True
        mock_is_git_repo.return_value = True

        # Mock the git command result
        mock_run.return_value = (
            "diff --git a/file.txt b/file.txt\n+++ b/file.txt\n+new line\n",
            "",
            0,
        )

        diff, code = get_staged_diff()

        assert "+new line" in diff
        assert code == 0
