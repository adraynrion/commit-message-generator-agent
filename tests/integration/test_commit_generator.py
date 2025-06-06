"""Integration tests for the commit generator."""

from unittest.mock import MagicMock

import pytest

from commit_message_generator.commit_generator import CommitMessageGenerator
from commit_message_generator.config import CommitType, GeneratorConfig, SeverityLevel
from commit_message_generator.models import CommitContext, CommitMessageResponse


@pytest.mark.asyncio
async def test_generate_commit_message() -> None:
    """Test generating a commit message with a mock AI response."""
    # Create a mock AI model
    mock_ai = MagicMock()
    mock_response = {
        "message": "FEATURE/MEDIUM: AB-123 - Add new feature\n\nDetailed description",
        "confidence": 0.9,
        "commit_type": "FEATURE",
        "severity": "MEDIUM",
        "ticket": "AB-123",
    }
    mock_ai.complete.return_value = mock_response

    # Create a generator with the mock AI
    config = GeneratorConfig()
    generator = CommitMessageGenerator(config=config, ai_model=mock_ai)

    # Test data
    diff = "diff --git a/file.txt b/file.txt\n+++ b/file.txt\n+new line\n"
    context = CommitContext(
        branch_name="feature/AB-123-new-feature",
        author_name="Test User",
        author_email="test@example.com",
    )

    # Call the method
    result = await generator.generate_commit_message(diff, context=context)

    # Check the result
    assert isinstance(result, CommitMessageResponse)
    assert result.message.startswith("FEATURE/MEDIUM: AB-123 - Add new feature")
    assert result.confidence == 0.9
    assert result.commit_type == CommitType.FEATURE
    assert result.severity == SeverityLevel.MEDIUM
    assert result.ticket == "AB-123"

    # Check that the AI was called with the expected prompt
    mock_ai.complete.assert_called_once()
    call_args = mock_ai.complete.call_args[1]
    assert "system_prompt" in call_args
    assert diff in call_args["user_prompt"]
    assert "AB-123" in call_args["user_prompt"]


@pytest.mark.asyncio
async def test_generate_commit_message_with_custom_prompt() -> None:
    """Test generating a commit message with a custom prompt."""
    # Create a mock AI model
    mock_ai = MagicMock()
    mock_response = {
        "message": "FEATURE/MEDIUM: AB-123 - Add new feature\n\nDetailed description",
        "confidence": 0.9,
        "commit_type": "FEATURE",
        "severity": "MEDIUM",
        "ticket": "AB-123",
    }
    mock_ai.complete.return_value = mock_response

    # Create a generator with custom prompt
    config = GeneratorConfig()
    custom_prompt = "Custom prompt for testing"
    generator = CommitMessageGenerator(
        config=config, ai_model=mock_ai, system_prompt=custom_prompt
    )

    # Call the method
    await generator.generate_commit_message("test diff")

    # Check that the custom prompt was used
    call_args = mock_ai.complete.call_args[1]
    assert "system_prompt" in call_args
    assert call_args["system_prompt"] == custom_prompt


@pytest.mark.asyncio
async def test_generate_commit_message_with_error() -> None:
    """Test error handling when AI generation fails."""
    # Create a mock AI that raises an exception
    mock_ai = MagicMock()
    mock_ai.complete.side_effect = Exception("AI service error")

    # Create a generator with the mock AI
    generator = CommitMessageGenerator(ai_model=mock_ai)

    # Call the method and expect an exception
    with pytest.raises(Exception) as exc_info:
        await generator.generate_commit_message("test diff")

    assert "AI service error" in str(exc_info.value)
