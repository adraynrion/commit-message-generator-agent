"""Tests for the models module (updated for latest models and validation)."""

import pytest

from commit_message_generator.models import (
    ChangeType,
    CommitAnalysis,
    CommitFile,
    CommitMessageResponse,
    parse_commit_message,
)


def test_commit_message_response_creation() -> None:
    response = CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature",
        confidence=0.9,
        commit_type="FEATURE",
        severity="MEDIUM",
        ticket="AB-123",
    )
    assert response.message.startswith("FEATURE/MEDIUM: AB-123 - Add new feature")
    assert response.confidence == 0.9
    assert response.commit_type == "FEATURE"
    assert response.severity == "MEDIUM"
    assert response.ticket == "AB-123"


def test_commit_message_response_validation() -> None:
    CommitMessageResponse(
        message="FEATURE/MEDIUM: AB-123 - Add new feature",
        confidence=0.5,
        commit_type="FEATURE",
        severity="MEDIUM",
        ticket="AB-123",
    )
    with pytest.raises(ValueError):
        CommitMessageResponse(
            message="FEATURE/MEDIUM: AB-123 - Add new feature",
            confidence=1.5,  # Invalid confidence
            commit_type="FEATURE",
            severity="MEDIUM",
            ticket="AB-123",
        )


def test_commit_file_validation() -> None:
    file = CommitFile(
        path="src/file.py",
        change_type=ChangeType.ADDED,
        insertions=10,
        deletions=2,
        diff=None,
    )
    assert file.path == "src/file.py"
    assert file.change_type == ChangeType.ADDED
    with pytest.raises(ValueError):
        CommitFile(
            path="   ",
            change_type=ChangeType.ADDED,
            insertions=10,
            deletions=2,
            diff=None,
        )


def test_change_type_enum() -> None:
    assert ChangeType.ADDED == "added"
    assert ChangeType.MODIFIED == "modified"
    assert ChangeType.DELETED == "deleted"
    assert ChangeType.RENAMED == "renamed"
    assert ChangeType.COPIED == "copied"
    assert ChangeType.UNTRACKED == "untracked"


def test_parse_commit_message() -> None:
    msg = "FEATURE/MEDIUM: AB-123 - Add new feature\n\nDetails here"
    parsed = parse_commit_message(msg)
    assert parsed["type"] == "FEATURE"
    assert parsed["severity"] == "MEDIUM"
    assert parsed["ticket"] == "AB-123"
    assert parsed["description"].startswith("Add new feature")
    assert "Details here" in parsed["body"]
    # Fallback to description only
    assert parse_commit_message("") == {}
    assert parse_commit_message("Just a description") == {
        "type": None,
        "severity": None,
        "ticket": None,
        "description": "Just a description",
        "body": "",
    }

    # Test CommitAnalysis
    file1 = CommitFile(
        path="src/main.py",
        change_type=ChangeType.ADDED,
        insertions=10,
        deletions=0,
        diff=None,
    )

    file2 = CommitFile(
        path="tests/test_main.py",
        change_type=ChangeType.MODIFIED,
        insertions=5,
        deletions=2,
        diff=None,
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
    assert ChangeType.ADDED in analysis.change_types
    assert ChangeType.MODIFIED in analysis.change_types

    # Test CommitAnalysis methods
    analysis.add_file_change("src/new_file.py", ChangeType.ADDED)
    analysis.update_stats(5, 1)

    assert len(analysis.files_changed) == 3  # 2 from before + 1 new
    assert analysis.total_insertions == 20  # 15 + 5
    assert analysis.total_deletions == 3  # 2 + 1
    assert ChangeType.ADDED in analysis.change_types
    assert ChangeType.MODIFIED in analysis.change_types
