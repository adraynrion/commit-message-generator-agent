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
from .git_utils import get_staged_diff, is_git_repo, run_git_command
from .models import CommitAnalysis, CommitContext, CommitMessageResponse

__version__ = "0.2.0"
__all__ = [
    # Main classes
    "CommitMessageGenerator",
    "GeneratorConfig",
    "AIModelConfig",
    "CommitMessageConfig",
    # Models
    "CommitMessageResponse",
    "CommitAnalysis",
    "CommitContext",
    # Enums
    "CommitType",
    "SeverityLevel",
    # Functions
    "generate",
    "cli",
    "get_staged_diff",
    "is_git_repo",
    "run_git_command",
]
