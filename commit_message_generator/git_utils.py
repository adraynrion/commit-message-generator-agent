"""Git utilities for the commit message generator."""

import subprocess
from pathlib import Path
from typing import List, Tuple, Union


def run_git_command(
    command: List[str], cwd: Union[str, Path, None] = None
) -> Tuple[str, int]:
    """Run a git command and return the output and status code.

    Args:
        command: List of command arguments
        cwd: Working directory for the command

    Returns:
        Tuple of (output, return_code)

    """
    try:
        result = subprocess.run(
            ["git"] + command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            return result.stderr or result.stdout or "Unknown error", result.returncode
        return result.stdout.strip(), 0
    except Exception as e:
        return str(e), -1


def is_git_repo() -> bool:
    """Check if the current directory is a git repository.

    Returns:
        bool: True if the current directory is a git repository

    """
    return (Path.cwd() / ".git").exists()


def get_staged_diff() -> Tuple[str, int]:
    """Get the staged changes diff.

    Returns:
        Tuple of (diff_output, return_code)

    """
    if not is_git_repo():
        return "Not a git repository", -1

    return run_git_command(["diff", "--cached", "-w"], cwd=None)
