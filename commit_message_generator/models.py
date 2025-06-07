"""Pydantic models for the commit message generator."""

import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, ValidationInfo, field_validator

# Set up logger
logger = logging.getLogger(__name__)

__all__ = [
    "ChangeType",
    "CommitFile",
    "CommitMessageResponse",
    "CommitAnalysis",
    "parse_commit_message",
]


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
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the generated message (0.0 to 1.0)",
    )

    commit_type: Optional[str] = Field(
        default=None,
        description="Type of the commit (FEATURE, IMPROVE, BUGFIX, REFACTO, CORE, TEST, DOC)",
    )

    severity: Optional[str] = Field(
        default=None,
        description="Severity level of the changes (MAJOR, MEDIUM, MINOR)",
    )

    ticket: Optional[str] = Field(
        default=None,
        description="Ticket associated with the changes (format: <2-letters>-<alphanumeric>)",
    )

    config: Optional[Any] = Field(
        default=None,
        description="Configuration object for validation",
        exclude=True,  # Don't include in serialization
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
    def validate_message(cls, v: str, info: ValidationInfo) -> str:
        """Validate the commit message format.

        The commit message must follow this format:
        <Commit Type>/<Severity>: <2-letters>-<alphanumeric> - <description>

        Where:
        - Commit Type: One of FEATURE, IMPROVE, BUGFIX, REFACTO, CORE, TEST, DOC
        - Severity: One of MAJOR, MEDIUM, MINOR (required for FEATURE, IMPROVE, BUGFIX, REFACTO)
        - Ticket number: Format <2-letters>-<alphanumeric>
        - Description: Brief description of the change

        The message must also include an empty line after the first line and a detailed description.

        Args:
            v: The commit message to validate
            info: ValidationInfo object containing the model instance being validated

        Returns:
            The validated commit message

        """

        if not v or not v.strip():
            raise ValueError("Commit message cannot be empty")

        lines = [line.rstrip() for line in v.strip().split("\n")]
        first_line = lines[0] if lines else ""
        empty_line = lines[1] if len(lines) > 1 else ""
        description = lines[2:] if len(lines) > 2 else []

        # Get max line length from config if available, otherwise use defaults
        config = info.data.get("config") if info.data else None
        max_line_length = getattr(
            getattr(config, "commit", None), "max_line_length", 80
        )

        # Check if message starts with code block
        if first_line.startswith("```"):
            raise ValueError("Response starts with code block while it should not")

        # Check prefix format
        if ":" not in first_line:
            raise ValueError(
                "Commit title (first line) is missing the ':' separator. "
                "Expected format: '<Commit Type>/<Severity>: <ticket> - <description>'"
            )

        else:
            prefix, *rest = first_line.split(":", 1)
            rest_of_line = ":".join(rest).strip() if rest else ""

            # Check prefix components if they exist
            if prefix.strip():
                if "/" in prefix:
                    parts = prefix.split("/")
                    commit_type = parts[0].strip().upper()
                    if len(parts) > 1:
                        severity = "/".join(parts[1:]).strip().upper()
                else:
                    commit_type = prefix.strip().upper()

                # Validate commit type if provided
                if commit_type:
                    valid_commit_types = [
                        "FEATURE",
                        "IMPROVE",
                        "BUGFIX",
                        "REFACTO",
                        "CORE",
                        "TEST",
                        "DOC",
                    ]
                    if commit_type not in valid_commit_types:
                        logger.warning(
                            f"Unexpected commit type: {commit_type}. "
                            f"Expected one of: {', '.join(valid_commit_types)}"
                        )
                    else:
                        # Only validate severity if we have a valid commit type that requires it
                        valid_severities = ["MAJOR", "MEDIUM", "MINOR"]
                        if (
                            commit_type in ["FEATURE", "IMPROVE", "BUGFIX", "REFACTO"]
                            and severity
                            and severity not in valid_severities
                        ):
                            logger.warning(
                                f"Unexpected severity: {severity}. "
                                f"Expected one of: {', '.join(valid_severities)}"
                            )

        # Check ticket number format if present
        if " - " in rest_of_line:
            ticket_part, *_ = rest_of_line.split(" - ", 1)
            ticket_number = ticket_part.strip()

            if ticket_number and not (
                len(ticket_number) >= 4 and ticket_number[2] == "-"
            ):
                logger.warning(
                    f"Ticket number '{ticket_number}' doesn't match expected format '<2-letters>-<alphanumeric>'"
                )

        # Check empty line after first line
        if empty_line.strip() != "":
            raise ValueError(
                "Second line must be empty. "
                "Please add a blank line between the title and description."
            )

        # Check description line lengths
        for i, line in enumerate(description):
            if (
                len(line) > max_line_length
            ):  # Using a reasonable default if not in config
                raise ValueError(
                    f"Description line {i} exceeds maximum length of {max_line_length} characters (current length: {len(line)})"
                )

        return v.strip()


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
