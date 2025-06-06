"""Tests for the models module."""

from datetime import datetime

import pytest

from commit_message_generator.config import CommitType, SeverityLevel
from commit_message_generator.models import (
    ChangeType,
    CommitAnalysis,
    CommitContext,
    CommitFile,
    CommitMessageResponse,
    extract_ticket_from_branch,
    parse_commit_message,
)


def test_commit_message_response_creation() -> None:
    """Test creating a CommitMessageResponse instance."""
    response = CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature",
        confidence=0.9,
        commit_type=CommitType.FEATURE,
        severity=SeverityLevel.MEDIUM,
        ticket="AB-123",
    )

    assert response.message == "FEATURE/MEDIUM: AB-123 - Add new feature"
    assert response.confidence == 0.9
    assert response.commit_type == CommitType.FEATURE
    assert response.severity == SeverityLevel.MEDIUM
    assert response.ticket == "AB-123"


def test_commit_message_response_validation() -> None:
    """Test CommitMessageResponse validation."""
    # Test with valid data
    response = CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature",
        confidence=0.5,
        commit_type=CommitType.FEATURE,
        severity=SeverityLevel.MEDIUM,
        ticket="AB-123",
    )
    assert response is not None

    # Test with invalid confidence
    with pytest.raises(ValueError):
        CommitMessageResponse(
            message="FEATURE/MEDIUM: AB-123 - Add new feature",
            confidence=1.5,  # Invalid confidence
            commit_type=CommitType.FEATURE,
            severity=SeverityLevel.MEDIUM,
            ticket="AB-123",
        )


def test_commit_analysis_creation() -> None:
    """Test creating a CommitAnalysis instance."""
    file1 = CommitFile(
        path="src/main.py",
        change_type=ChangeType.ADDED,
        insertions=10,
        deletions=0,
    )

    file2 = CommitFile(
        path="tests/test_main.py",
        change_type=ChangeType.MODIFIED,
        insertions=5,
        deletions=2,
    )

    analysis = CommitAnalysis(
        files_changed=[file1, file2],
        total_insertions=15,
        total_deletions=2,
        change_types={ChangeType.ADDED, ChangeType.MODIFIED},
    )

    assert len(analysis.files_changed) == 2
    assert analysis.total_insertions == 15
    assert analysis.total_deletions == 2
    assert len(analysis.change_types) == 2
    assert ChangeType.ADDED in analysis.change_types
    assert ChangeType.MODIFIED in analysis.change_types


def test_commit_context_creation() -> None:
    """Test creating a CommitContext instance."""
    context = CommitContext(
        branch_name="feature/AB-123-new-feature",
        author_name="John Doe",
        author_email="john@example.com",
        commit_date=datetime(2023, 1, 1, 12, 0, 0),
        related_issues=["AB-123", "#42"],
        flags=["breaking-change", "security"],
    )

    assert context.branch_name == "feature/AB-123-new-feature"
    assert context.author_name == "John Doe"
    assert context.author_email == "john@example.com"
    assert len(context.related_issues) == 2
    assert "AB-123" in context.related_issues
    assert "#42" in context.related_issues
    assert len(context.flags) == 2
    assert "breaking-change" in context.flags
    assert "security" in context.flags


def test_extract_ticket_from_branch() -> None:
    """Test extracting ticket number from branch name."""
    # Test with JIRA-style ticket
    assert extract_ticket_from_branch("feature/AB-123-new-feature") == "AB-123"

    # Test with GitHub issue style
    assert extract_ticket_from_branch("fix/123-fix-bug") == "#123"

    # Test with no ticket in branch
    assert extract_ticket_from_branch("main") is None
    assert extract_ticket_from_branch("develop") is None


def test_parse_commit_message() -> None:
    """Test parsing a commit message into its components."""
    # Test with full format
    message = "FEATURE/MEDIUM: AB-123 - Add new feature\n\nDetailed description"
    result = parse_commit_message(message)

    assert result["type"] == "FEATURE"
    assert result["severity"] == "MEDIUM"
    assert result["ticket"] == "AB-123"
    assert result["description"] == "Add new feature"
    assert result["body"] == "Detailed description"

    # Test with minimal format
    message = "DOC: Update README"
    result = parse_commit_message(message)

    assert result["type"] == "DOC"
    assert result["severity"] is None
    assert result["ticket"] is None
    assert result["description"] == "Update README"
    assert result["body"] == ""
