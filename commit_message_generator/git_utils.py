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


def get_staged_files_status() -> Tuple[int, int, int]:
    """Get the count of added, modified, and deleted files in the staging area.

    Returns:
        Tuple of (added_count, modified_count, deleted_count)
    """
    if not is_git_repo():
        return 0, 0, 0
    
    # Get the status of staged files
    status_output, return_code = run_git_command(["status", "--porcelain", "--untracked-files=no"])
    
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
        if status[0] == 'A':
            added += 1
        elif status[0] == 'M':
            modified += 1
        elif status[0] == 'D':
            deleted += 1
        elif status[0] == 'R' or status[0] == 'C':
            # Renamed or Copied files count as modified
            modified += 1
    
    return added, modified, deleted
