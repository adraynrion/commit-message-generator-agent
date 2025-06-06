"""Git utilities for the commit message generator."""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


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


def is_git_repo(path: Union[str, Path, None] = None) -> bool:
    """Check if the given path is a git repository.

    Args:
        path: Path to check (default: current directory)

    Returns:
        bool: True if the path is a git repository

    """
    output, code = run_git_command(["rev-parse", "--is-inside-work-tree"], cwd=path)
    return code == 0 and output.strip().lower() == "true"


def get_git_status(cwd: Union[str, Path, None] = None) -> Tuple[str, int]:
    """Get the git status output and return code.

    Args:
        cwd: Working directory (default: current directory)

    Returns:
        Tuple of (status_output, return_code)

    """
    if not is_git_repo(cwd):
        return "Not a git repository", -1

    return run_git_command(["status", "--porcelain"], cwd=cwd)


def get_staged_diff(cwd: Union[str, Path, None] = None) -> Tuple[str, int]:
    """Get the staged changes diff.

    Args:
        cwd: Working directory (default: current directory)

    Returns:
        Tuple of (diff_output, return_code)

    """
    if not is_git_repo(cwd):
        return "Not a git repository", -1

    return run_git_command(["diff", "--cached", "-w"], cwd=cwd)


def get_current_branch(cwd: Union[str, Path, None] = None) -> Tuple[Optional[str], int]:
    """Get the current git branch name.

    Args:
        cwd: Working directory (default: current directory)

    Returns:
        Tuple of (branch_name, return_code)

    """
    if not is_git_repo(cwd):
        return None, -1

    output, code = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if code != 0:
        return None, code
    return output, 0


def get_git_config(
    key: str, default: Optional[str] = None, cwd: Union[str, Path, None] = None
) -> Optional[str]:
    """Get a git configuration value.

    Args:
        key: The git config key to get (e.g., 'user.name')
        default: Default value to return if key is not set
        cwd: Working directory (default: current directory)

    Returns:
        The configuration value or default if not set

    """
    output, code = run_git_command(["config", "--get", key], cwd=cwd)
    if code == 0 and output:
        return output.strip()
    return default


def get_commit_history(
    limit: int = 10, cwd: Union[str, Path, None] = None
) -> List[Dict[str, str]]:
    """Get the commit history.

    Args:
        limit: Maximum number of commits to return
        cwd: Working directory (default: current directory)

    Returns:
        List of commit dictionaries with keys: hash, author, date, message

    """
    format_str = "%H||%an||%ad||%s"  # hash, author name, date, subject
    output, code = run_git_command(
        ["log", f"-n {limit}", f"--pretty=format:{format_str}", "--date=short"], cwd=cwd
    )

    if code != 0 or not output:
        return []

    commits = []
    for line in output.strip().split("\n"):
        if "||" not in line:
            continue

        parts = line.split("||", 3)
        if len(parts) != 4:
            continue

        commits.append(
            {
                "hash": parts[0],
                "author": parts[1],
                "date": parts[2],
                "message": parts[3],
            }
        )

    return commits


def get_commit_message_template() -> str:
    """Get the default commit message template.

    Returns:
        str: Commit message template

    """
    return (
        "# Please enter the commit message for your changes. Lines starting\n"
        "# with '#' will be ignored, and an empty message aborts the commit.\n"
        "#\n"
        "# On branch <branch>\n"
        "#\n"
        "# Changes to be committed:\n"
        "#\t<list of files>\n"
        "#"
    )
