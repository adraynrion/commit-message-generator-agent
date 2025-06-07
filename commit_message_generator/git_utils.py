"""Git utilities for the commit message generator."""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Union


def run_git_command(
    command: List[str], cwd: Union[str, Path, None] = None
) -> Tuple[str, str, int]:
    """Run a git command and return (stdout, stderr, return_code) as strings.

    Args:
        command: List of command arguments
        cwd: Working directory for the command

    Returns:
        Tuple of (stdout, stderr, return_code)

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
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1


def is_git_repo(cwd: Union[str, Path, None] = None) -> bool:
    """Check if the given directory (or current) is a git repository.

    Args:
        cwd: Directory to check. Defaults to current working directory.

    Returns:
        True if .git directory exists, False otherwise.

    """
    if cwd is None:
        cwd = os.getcwd()
    return Path(cwd, ".git").is_dir()


def get_staged_diff() -> Tuple[str, int]:
    """Get the staged changes diff.

    Returns:
        Tuple of (diff_output, return_code)

    """
    if not is_git_repo():
        return "Not a git repository", -1

    stdout, stderr, return_code = run_git_command(["diff", "--cached", "-w"], cwd=None)
    return stdout, return_code


def get_staged_files_status() -> Tuple[int, int, int]:
    """Get the count of added, modified, and deleted files in the staging area.

    Returns:
        Tuple of (added_count, modified_count, deleted_count)

    """
    if not is_git_repo():
        return 0, 0, 0

    # Get the status of staged files
    status_output, _, return_code = run_git_command(
        ["status", "--porcelain", "--untracked-files=no"]
    )

    if return_code != 0:
        return 0, 0, 0

    added = 0
    modified = 0
    deleted = 0

    for line in status_output.splitlines():
        if not line.strip():
            continue

        # Status format: XY filename
        # X = status of index (staging area)
        # Y = status of working tree
        status = line[:2]

        # Check staged changes (index)
        if status[0] == "A":
            added += 1
        elif status[0] == "M":
            modified += 1
        elif status[0] == "D":
            deleted += 1
        elif status[0] == "R" or status[0] == "C":
            # Renamed or Copied files count as modified
            modified += 1

    return added, modified, deleted
