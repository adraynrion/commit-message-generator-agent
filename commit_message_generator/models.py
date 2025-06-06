"""Pydantic models for the commit message generator."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

__all__ = [
    "ChangeType",
    "CommitFile",
    "CommitMessageResponse",
    "CommitAnalysis",
    "CommitContext",
    "extract_ticket_from_branch",
    "parse_commit_message",
]
import re

from pydantic import BaseModel, Field, field_validator


class ChangeType(str, Enum):
    """Types of changes that can be made to a file."""

    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"
    COPIED = "copied"
    UNTRACKED = "untracked"


class CommitFile(BaseModel):
    """Represents a file changed in a commit."""

    path: str = Field(..., description="Path to the file")

    change_type: ChangeType = Field(..., description="Type of change made to the file")

    insertions: int = Field(0, description="Number of lines added")

    deletions: int = Field(0, description="Number of lines removed")

    diff: Optional[str] = Field(None, description="Unified diff of changes")

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate that path is not empty."""
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()


class CommitMessageResponse(BaseModel):
    """Response model for the generated commit message."""

    message: str = Field(..., description="The generated commit message")

    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the generated message (0.0 to 1.0)",
    )

    commit_type: str = Field(
        ..., description="Type of the commit (e.g., FEATURE, BUGFIX, etc.)"
    )

    severity: str = Field(
        ..., description="Severity level of the changes (e.g., MAJOR, MEDIUM, MINOR)"
    )

    ticket: Optional[str] = Field(
        None, description="Ticket number associated with the changes"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "FEATURE/MEDIUM: AB-123 - Add new feature",
                "confidence": 0.9,
                "commit_type": "FEATURE",
                "severity": "MEDIUM",
                "ticket": "AB-123",
            }
        }

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate the commit message format."""
        if not v or not v.strip():
            raise ValueError("Commit message cannot be empty")

        # Check if the message follows the conventional commit format
        lines = v.strip().split("\n")
        first_line = lines[0]

        # Basic validation - can be enhanced based on requirements
        if len(first_line) > 72:  # Standard git commit message line length
            raise ValueError(
                "First line of commit message should be 72 characters or less"
            )

        return v.strip()


def extract_ticket_from_branch(branch_name: str) -> Optional[str]:
    """Extract a ticket number from a branch name.

    Supports both JIRA-style (ABC-123) and GitHub-style (#123) ticket numbers.

    Args:
        branch_name: Name of the git branch

    Returns:
        Extracted ticket number (with # prefix for GitHub issues) or None if no match found

    """
    if not branch_name:
        return None

    import re

    # Try JIRA-style ticket first (ABC-123)
    jira_match = re.search(r"([A-Z]{2,}-\d+)", branch_name)
    if jira_match:
        return jira_match.group(1)

    # Try GitHub-style issue number (123)
    github_match = re.search(r"(?:^|[/-])(\d+)(?:-|$)", branch_name)
    if github_match:
        return f"#{github_match.group(1)}"

    return None


def parse_commit_message(message: str) -> Dict[str, Any]:
    """Parse a commit message into its components.

    Supports formats:
    - TYPE/SEVERITY: TICKET - Description
    - TYPE: TICKET - Description
    - TYPE: Description

    Args:
        message: The commit message to parse

    Returns:
        Dictionary with parsed components (type, severity, ticket, description, body)

    """
    if not message:
        return {}

    lines = [line.strip() for line in message.split("\n") if line.strip()]
    if not lines:
        return {}

    # Initialize default values
    commit_type = None
    severity = None
    ticket = None
    description = None
    body = []

    # Parse the first line (header)
    header = lines[0]

    # Try to match format: TYPE/SEVERITY: TICKET - Description
    type_sev_match = re.match(
        r"^([A-Z]+)/([A-Z]+):\s*([A-Z]+-\d+|[#]?\d+)?\s*-?\s*(.*)$", header
    )
    if type_sev_match:
        commit_type = type_sev_match.group(1)
        severity = type_sev_match.group(2)
        ticket = type_sev_match.group(3)
        description = type_sev_match.group(4).strip()
    else:
        # Try to match format: TYPE: TICKET - Description
        type_match = re.match(
            r"^([A-Z]+):\s*([A-Z]+-\d+|[#]?\d+)?\s*-?\s*(.*)$", header
        )
        if type_match:
            commit_type = type_match.group(1)
            ticket = type_match.group(2)
            description = type_match.group(3).strip()
        else:
            # Fallback: Just a simple description
            description = header

    # Parse the rest of the message as body
    body = [line.strip() for line in lines[1:] if line.strip()]

    return {
        "type": commit_type,
        "severity": severity,
        "ticket": ticket,
        "description": description,
        "body": (
            "\n".join(body) if body else ""
        ),  # Return empty string instead of None for body
    }


class CommitAnalysis(BaseModel):
    """Analysis of the changes for commit message generation."""

    files_changed: list[Union[str, "CommitFile"]] = Field(
        default_factory=list,
        description="List of files that were changed, either as strings or CommitFile objects",
    )

    total_insertions: int = Field(0, description="Total number of insertions")

    total_deletions: int = Field(0, description="Total number of deletions")

    change_types: set[Union[str, ChangeType]] = Field(
        default_factory=set,
        description="Types of changes (added, modified, deleted, renamed, etc.)",
    )

    def add_file_change(
        self, filename: str, change_type: Union[str, ChangeType]
    ) -> None:
        """Add a file change to the analysis."""
        self.files_changed.append(filename)
        self.change_types.add(change_type)

    def update_stats(self, insertions: int, deletions: int) -> None:
        """Update the insertion/deletion statistics."""
        self.total_insertions += insertions
        self.total_deletions += deletions


class CommitContext(BaseModel):
    """Context for commit message generation."""

    branch_name: Optional[str] = Field(
        None, description="Name of the current git branch"
    )

    ticket: Optional[str] = Field(
        None, description="Ticket number extracted from branch name or provided by user"
    )

    related_issues: list[str] = Field(
        default_factory=list, description="List of related issue numbers"
    )

    is_merge: bool = Field(False, description="Whether this is a merge commit")

    is_initial_commit: bool = Field(
        False, description="Whether this is the initial commit"
    )

    # Additional fields used in tests
    author_name: Optional[str] = Field(None, description="Name of the commit author")

    author_email: Optional[str] = Field(None, description="Email of the commit author")

    commit_date: Optional[datetime] = Field(
        None, description="Date and time of the commit"
    )

    flags: list[str] = Field(
        default_factory=list, description="List of flags or tags for the commit"
    )

    def extract_ticket_from_branch(self, pattern: str = r"([A-Z]{2,}-\d+)") -> bool:
        """Extract ticket number from branch name using regex pattern.

        Args:
            pattern: Regex pattern to match ticket numbers

        Returns:
            bool: True if a ticket was extracted, False otherwise

        """
        if not self.branch_name:
            return False

        match = re.search(pattern, self.branch_name)
        if match:
            self.ticket = match.group(1)
            return True
        return False
