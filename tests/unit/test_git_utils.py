"""Tests for the git utilities module."""

from unittest.mock import MagicMock, patch

from commit_message_generator.git_utils import (
    get_commit_history,
    get_current_branch,
    get_git_config,
    get_git_status,
    get_staged_diff,
    is_git_repo,
    run_git_command,
)


def test_run_git_command_success() -> None:
    """Test running a successful git command."""
    with patch("subprocess.run") as mock_run:
        # Configure the mock to return a successful result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = b"success output\n"
        mock_result.stderr = b""
        mock_run.return_value = mock_result

        # Call the function
        result = run_git_command(["status"])

        # Check the result
        assert result == ("success output\n", "", 0)
        mock_run.assert_called_once_with(
            ["git", "status"],
            cwd=None,
            capture_output=True,
            text=False,
            check=False,
        )


def test_run_git_command_error() -> None:
    """Test running a git command that fails."""
    with patch("subprocess.run") as mock_run:
        # Configure the mock to return an error
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = b""
        mock_result.stderr = b"error message\n"
        mock_run.return_value = mock_result

        # Call the function
        result = run_git_command(["invalid-command"])

        # Check the result
        assert result == ("", "error message\n", 1)


def test_is_git_repo_positive(tmp_path) -> None:
    """Test is_git_repo with a git repository."""
    # Create a git repo
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()

    assert is_git_repo(repo_dir) is True


def test_is_git_repo_negative(tmp_path) -> None:
    """Test is_git_repo with a non-git directory."""
    # Create a non-git directory
    repo_dir = tmp_path / "not_a_repo"
    repo_dir.mkdir()

    assert is_git_repo(repo_dir) is False


def test_get_current_branch_success() -> None:
    """Test getting the current branch name."""
    with patch("commit_message_generator.git_utils.run_git_command") as mock_run:
        mock_run.return_value = ("  main\n", "", 0)

        branch, error = get_current_branch()

        assert branch == "main"
        assert error == ""


def test_get_current_branch_error() -> None:
    """Test handling when git branch command fails."""
    with patch("commit_message_generator.git_utils.run_git_command") as mock_run:
        mock_run.return_value = ("", "fatal: not a git repository", 128)

        branch, error = get_current_branch()

        assert branch is None
        assert "fatal: not a git repository" in error


def test_get_staged_diff_success() -> None:
    """Test getting staged diff."""
    with patch("commit_message_generator.git_utils.run_git_command") as mock_run:
        mock_run.return_value = (
            "diff --git a/file.txt b/file.txt\n+++ b/file.txt\n+new line\n",
            "",
            0,
        )

        diff, error = get_staged_diff()

        assert "+new line" in diff
        assert error == ""


def test_get_git_status() -> None:
    """Test getting git status."""
    with patch("commit_message_generator.git_utils.run_git_command") as mock_run:
        status_output = """
        M modified.txt
        A added.txt
        D deleted.txt
        ?? new_file.txt
        """
        mock_run.return_value = (status_output, "", 0)

        status, error = get_git_status()

        assert "M modified.txt" in status
        assert "A added.txt" in status
        assert "D deleted.txt" in status
        assert "?? new_file.txt" in status
        assert error == ""


def test_get_git_config() -> None:
    """Test getting git config values."""
    with patch("commit_message_generator.git_utils.run_git_command") as mock_run:
        mock_run.return_value = ("John Doe\n", "", 0)

        value, error = get_git_config("user.name")

        assert value == "John Doe"
        assert error == ""


def test_get_commit_history() -> None:
    """Test getting commit history."""
    with patch("commit_message_generator.git_utils.run_git_command") as mock_run:
        commit_log = """
        abc123|John Doe|john@example.com|2023-01-01T12:00:00-05:00|Initial commit
        def456|Jane Smith|jane@example.com|2023-01-02T10:30:00-05:00|Update README
        """
        mock_run.return_value = (commit_log, "", 0)

        history, error = get_commit_history(2)

        assert len(history) == 2
        assert "Initial commit" in history[0]["message"]
        assert "Update README" in history[1]["message"]
        assert error == ""
