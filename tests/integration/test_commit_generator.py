"""Integration tests for the commit generator (updated for latest async API and error
handling)."""

from unittest.mock import MagicMock, patch

import pytest

from commit_message_generator.commit_generator import CommitMessageGenerator
from commit_message_generator.config import GeneratorConfig
from commit_message_generator.models import CommitMessageResponse


@pytest.mark.asyncio
async def test_generate_commit_message() -> None:
    mock_ai = MagicMock()
    mock_response = CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature\n\nDetailed description",
        confidence=0.9,
        commit_type="FEATURE",
        severity="MEDIUM",
        ticket="AB-123",
    )
    mock_ai.complete.return_value = mock_response
    config = GeneratorConfig()
    generator = CommitMessageGenerator(config=config)
    generator.ai = mock_ai
    diff = "diff --git a/file.txt b/file.txt\n+++ b/file.txt\n+new line\n"

    class MockAIResponse:
        def __init__(self, output) -> None:
            self.output = output

    mock_response = CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature\n\nDetailed description",
        confidence=0.9,
        commit_type="FEATURE",
        severity="MEDIUM",
        ticket="AB-123",
    )

    async def mock_run(prompt, output_type=None):
        return MockAIResponse(mock_response)

    mock_ai.run = mock_run
    result = await generator.generate_commit_message(diff, ticket="AB-123")
    print(f"DEBUG: type(result)={type(result)}, value={result}")
    assert isinstance(result, CommitMessageResponse)
    assert result.message.startswith("FEATURE/MEDIUM: AB-123 - Add new feature")
    assert result.confidence == 0.9
    assert result.commit_type == "FEATURE"
    assert result.severity == "MEDIUM"
    assert result.ticket == "AB-123"


@pytest.mark.asyncio
async def test_generate_commit_message_with_custom_prompt() -> None:
    mock_ai = MagicMock()
    mock_response = CommitMessageResponse(
        message="DOC: Add documentation",
        confidence=0.5,
        commit_type="DOC",
        severity=None,
        ticket=None,
    )
    mock_ai.complete.return_value = mock_response
    config = GeneratorConfig()
    generator = CommitMessageGenerator(config=config)

    # Patch generator.ai.run to return a valid CommitMessageResponse in .output
    class MockAIResponse:
        def __init__(self, output) -> None:
            self.output = output

    async def mock_run(prompt, output_type=None):
        return MockAIResponse(
            CommitMessageResponse(
                message="DOC: Add documentation",
                confidence=0.5,
                commit_type="DOC",
                severity=None,
                ticket="DOC-1",
            )
        )

    generator.ai = MagicMock()
    generator.ai.run = mock_run
    diff = "diff --git a/README.md b/README.md\n+Add docs\n"
    context = {
        "branch_name": "docs/update-docs",
        "author_name": "Doc Writer",
        "author_email": "doc@example.com",
    }
    result = await generator.generate_commit_message(diff, ticket="DOC-1")
    assert hasattr(result, "message")
    assert result.message.startswith("DOC: Add documentation")


@pytest.mark.asyncio
async def test_generate_commit_message_with_error() -> None:
    mock_ai = MagicMock()
    mock_ai.complete.side_effect = Exception("AI error")
    config = GeneratorConfig()
    generator = CommitMessageGenerator(config=config)
    generator.ai = mock_ai
    diff = "diff --git a/file.txt b/file.txt\n+fail\n"

    with pytest.raises(ValueError, match="Failed to generate commit message"):
        await generator.generate_commit_message(diff, ticket="FAIL-1")


@pytest.mark.asyncio
async def test_generate_commit_message_with_custom_prompt_and_ticket() -> None:
    mock_ai = MagicMock()
    mock_response = CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature",
        confidence=0.9,
        commit_type="FEATURE",
        severity="MEDIUM",
        ticket="AB-123",
    )

    class MockAIResponse:
        def __init__(self, output) -> None:
            self.output = output

    async def mock_run(prompt, output_type=None):
        return MockAIResponse(mock_response)

    mock_ai.run = mock_run

    custom_prompt = "Custom prompt for testing"
    with patch.object(
        CommitMessageGenerator, "_build_system_prompt", return_value=custom_prompt
    ):
        generator = CommitMessageGenerator(config=GeneratorConfig())
        generator.ai = mock_ai

        # Call the method
        result = await generator.generate_commit_message("test diff", ticket="TEST-1")

        # Verify the response is correct
        assert result.message == "FEATURE/MEDIUM: AB-123 - Add new feature"
        assert result.confidence == 0.9
        assert result.commit_type == "FEATURE"
        assert result.severity == "MEDIUM"
        assert result.ticket == "AB-123"


@pytest.mark.asyncio
async def test_generate_commit_message_with_ai_error() -> None:
    """Test error handling when AI generation fails due to service error."""
    # Create a mock AI that raises an exception
    mock_ai = MagicMock()
    mock_ai.complete.side_effect = Exception("AI service error")

    # Create a generator with the mock AI
    generator = CommitMessageGenerator()
    generator.ai = mock_ai

    # Call the method and expect an exception
    with pytest.raises(Exception) as exc_info:
        await generator.generate_commit_message("test diff", ticket="ERR-1")

    # Check that the exception was the generic error message
    assert "Failed to generate commit message" in str(exc_info.value)
