"""Git Commit Message Generator Agent.

This package provides an AI-powered tool to generate clear, concise, and conventional
commit messages based on git diffs.

"""

from .cli import cli, generate
from .commit_generator import CommitMessageGenerator
from .config import (
    AIModelConfig,
    CommitMessageConfig,
    CommitType,
    GeneratorConfig,
    SeverityLevel,
)
from .git_utils import (
    get_staged_diff,
    get_staged_files_status,
    is_git_repo,
    run_git_command,
)
from .models import CommitAnalysis, CommitMessageResponse

__version__ = "1.1.2"
__all__ = [
    # Main classes
    "CommitMessageGenerator",
    "GeneratorConfig",
    "AIModelConfig",
    "CommitMessageConfig",
    # Models
    "CommitMessageResponse",
    "CommitAnalysis",
    # Enums
    "CommitType",
    "SeverityLevel",
    # Functions
    "generate",
    "cli",
    "get_staged_diff",
    "get_staged_files_status",
    "is_git_repo",
    "run_git_command",
]
