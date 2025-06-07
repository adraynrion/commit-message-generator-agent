"""Integration tests for the CLI interface."""

from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from commit_message_generator.cli import cli
from commit_message_generator.models import CommitMessageResponse


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_cli_help(runner) -> None:
    """Test the CLI help output."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output


def test_cli_version(runner) -> None:
    """Test the CLI version output."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


@patch("commit_message_generator.cli.CommitMessageGenerator")
def test_generate_commit_message(mock_generator_class, runner, tmp_path) -> None:
    """Test generating a commit message via the CLI."""
    # Setup mock generator
    mock_generator = AsyncMock()
    mock_generator.generate_commit_message.return_value = CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature\n\nDetailed description",
        confidence=0.9,
        commit_type="FEATURE",
        severity="MEDIUM",
        ticket="AB-123",
    )
    mock_generator_class.return_value = mock_generator

    # Create a temporary git repo
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    (repo_dir / ".git").mkdir()
    (repo_dir / "test.txt").write_text("test")

    # Run the CLI command
    with patch("os.getcwd", return_value=str(repo_dir)):
        result = runner.invoke(
            cli,
            ["generate", "--ticket", "AB-123"],
            input="y\n",  # Confirm the generated message
        )

    # Check the output
    assert result.exit_code == 0
    assert "FEATURE/MEDIUM: AB-123 - Add new feature" in result.output
    assert "Confidence: 90%" in result.output

    # Check that the generator was called with the expected arguments
    mock_generator.generate_commit_message.assert_awaited_once()
    call_args = mock_generator.generate_commit_message.await_args[1]
    assert "diff" in call_args
    assert "AB-123" in str(call_args.get("context", {}).get("branch_name", ""))


@patch("commit_message_generator.cli.CommitMessageGenerator")
def test_generate_commit_message_dry_run(mock_generator_class, runner) -> None:
    """Test dry run mode."""
    # Setup mock generator
    mock_generator = AsyncMock()
    mock_generator.generate_commit_message.return_value = CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature",
        confidence=0.9,
    )
    mock_generator_class.return_value = mock_generator

    # Run the CLI command with dry run
    result = runner.invoke(
        cli,
        ["generate", "--ticket", "AB-123", "--dry-run"],
    )

    # Check the output
    assert result.exit_code == 0
    assert "FEATURE/MEDIUM: AB-123 - Add new feature" in result.output
    assert "(dry run)" in result.output


@patch("commit_message_generator.cli.CommitMessageGenerator")
def test_generate_commit_message_with_config(
    mock_generator_class, runner, tmp_path
) -> None:
    """Test loading configuration from a file."""
    # Create a config file
    config_file = tmp_path / "config.yaml"
    config_content = """
    ai:
      model_name: "test-model"
      temperature: 0.5
    commit:
      max_line_length: 80
    """
    config_file.write_text(config_content)

    # Setup mock generator
    mock_generator = AsyncMock()
    mock_generator.generate_commit_message.return_value = CommitMessageResponse(
        message="FEATURE: Test feature",
        confidence=0.9,
    )
    mock_generator_class.return_value = mock_generator

    # Run the CLI command with the config file
    result = runner.invoke(
        cli,
        ["generate", "--config", str(config_file), "--dry-run"],
    )

    # Check the output
    assert result.exit_code == 0
    assert "FEATURE: Test feature" in result.output

    # Check that the generator was created with the config
    mock_generator_class.assert_called_once()
    config_arg = mock_generator_class.call_args[0][0]
    assert config_arg.ai.model_name == "test-model"
    assert config_arg.ai.temperature == 0.5
    assert config_arg.commit.max_line_length == 80
