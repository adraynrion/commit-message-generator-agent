"""Integration tests for the CLI interface (updated for latest CLI and behaviors)."""

from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from commit_message_generator.cli import cli
from commit_message_generator.models import CommitMessageResponse


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner) -> None:
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output


def test_generate_commit_message(runner, tmp_path) -> None:
    from unittest.mock import AsyncMock, patch
    from pathlib import Path

    # Create a test config file
    test_config_path = Path(__file__).parent.parent / "test_config.yaml"
    assert test_config_path.exists(), f"Test config file not found at {test_config_path}"

    with patch(
        "commit_message_generator.cli.CommitMessageGenerator"
    ) as mock_commit_msg_gen_class, patch(
        "commit_message_generator.git_utils.get_staged_diff",
        return_value=(
            "diff --git a/file.txt b/file.txt\n+++ b/file.txt\n+new line\n",
            0,
        ),
    ), patch(
        "commit_message_generator.cli.find_config_file",
        return_value=str(test_config_path)
    ), patch(
        "logging.shutdown", lambda: None
    ):
        mock_generator = AsyncMock()
        from commit_message_generator.models import CommitMessageResponse

        mock_generator.generate_commit_message = AsyncMock(
            return_value=CommitMessageResponse(
                message="FEATURE/MEDIUM: AB-123 - Add new feature\n\nDetailed description"
            )
        )
        mock_generator.ai = AsyncMock()  # Add dummy .ai attribute
        mock_commit_msg_gen_class.return_value = mock_generator
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        (repo_dir / ".git").mkdir()
        (repo_dir / "test.txt").write_text("test")
        with patch("os.getcwd", return_value=str(repo_dir)):
            result = runner.invoke(cli, ["generate", "--ticket", "AB-123"], input="y\n")
        if result.exit_code != 0 or not isinstance(result.exit_code, int):
            print("CLI TEST FAILURE: exit_code=", result.exit_code)
            print("CLI OUTPUT:\n", result.output)
            print("CLI EXC_INFO:\n", getattr(result, "exc_info", None))
        assert result.exit_code == 0
        assert "FEATURE/MEDIUM: AB-123 - Add new feature" in result.output

        # Check that the generator was called with the expected arguments
        mock_generator.generate_commit_message.assert_awaited_once_with(
            "diff --git a/file.txt b/file.txt\n+++ b/file.txt\n+new line\n",
            ticket="AB-123",
        )


# Removed test_generate_commit_message_dry_run because --dry-run is not supported by CLI
