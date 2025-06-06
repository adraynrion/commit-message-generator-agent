"""CLI interface for Git Commit Message Generator Agent."""

import asyncio
import logging
from typing import Optional

import click

from .commit_generator import CommitMessageGenerator

# Configure logging
logger = logging.getLogger(__name__)


def print_commit_message(message: str) -> None:
    """Print the commit message in a formatted way.

    Args:
        message: The commit message to print

    """
    click.echo("\n" + "=" * 70)
    click.echo("Generated commit message:")
    click.echo("-" * 70)
    click.echo(message)
    click.echo("-" * 70)
    click.echo("=" * 70)


@click.group()
def cli() -> None:
    """Git Commit Message Generator Agent CLI.

    This tool helps generate conventional commit messages based on your staged changes.
    It analyzes the changes and suggests an appropriate commit message following the
    conventional commit format:

        <type>/<severity>: <ticket> - <description>

        <detailed description>

    """
    pass



@cli.command()
@click.option(
    "--ticket",
    "-t",
    help="Ticket number (e.g., AB-1234). If not provided, will try to extract from branch name.",
)
@click.option(
    "--repo",
    "-r",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    help="Path to the git repository (default: current directory)",
)
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making any changes"
)
@click.option("--verbose", "-v", is_flag=True, help="Show more detailed output")
def generate(
    ticket: Optional[str] = None,
    repo: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    """Generate a commit message based on staged changes.

    This command analyzes the currently staged changes in your git repository and
    generates a conventional commit message based on the changes found.

    """
    asyncio.run(async_generate(ticket, repo, dry_run, verbose))

def find_config_file() -> Optional[str]:
    """Find the configuration file in standard locations.

    Returns:
        Path to the config file if found, None otherwise.
    """
    from pathlib import Path

    # Standard config file locations in order of precedence
    config_paths = [
        Path.cwd() / "config.yaml",  # ./config.yaml
        Path.home() / ".config" / "commit-msg-gen" / "config.yaml",  # ~/.config/commit-msg-gen/config.yaml
        Path("/etc/commit-msg-gen/config.yaml"),  # /etc/commit-msg-gen/config.yaml
    ]

    for path in config_paths:
        if path.exists():
            return str(path)
    return None

async def async_generate(
    ticket: Optional[str] = None,
    repo: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> None:
    """Generate a commit message based on staged changes.

    This command analyzes the currently staged changes in your git repository and
    generates a conventional commit message based on the changes found.

    """
    if verbose:
        click.echo("Initializing commit message generator...")

    # Load configuration
    config_path = find_config_file()
    if config_path is None:
        raise click.UsageError("No configuration file found. Please create a config.yaml file in one of the standard locations.")

    if verbose:
        click.echo(f"Using configuration from: {config_path}")

    from commit_message_generator.config import load_config_from_file
    config = load_config_from_file(config_path)
    if config is None:
        raise click.UsageError(f"Failed to load configuration from {config_path}")

    try:
        generator = CommitMessageGenerator(config=config)

        if verbose:
            click.echo("Analyzing staged changes...")

        # Get the staged diff
        from .git_utils import get_staged_diff, is_git_repo

        if not is_git_repo(repo):
            click.echo(
                "Error: Not a git repository. Please run this command from within a git repository.",
                err=True,
            )
            return

        diff, return_code = get_staged_diff(cwd=repo)

        if return_code != 0:
            click.echo(f"Error getting staged changes: {diff}", err=True)
            return

        if not diff or not diff.strip():
            click.echo(
                "No staged changes found. Please stage your changes with 'git add' first.",
                err=True,
            )
            return

        if verbose:
            click.echo(f"Found staged changes (length: {len(diff)}):")
            click.echo("-" * 50)
            click.echo(diff[:500] + ("..." if len(diff) > 500 else ""))
            click.echo("-" * 50)

        # Generate the commit message
        try:
            logger.info("Generating commit message...")
            result = await generator.generate_commit_message(diff=diff, ticket=ticket)
            logger.info("Successfully generated commit message")
        except Exception as e:
            logger.error(f"Failed to generate commit message: {str(e)}", exc_info=True)
            click.echo(f"Error: Failed to generate commit message: {str(e)}", err=True)
            if verbose:
                logger.debug(
                    f"Diff that caused the error (first 500 chars): {diff[:500]}"
                )
            raise

        if dry_run:
            click.echo("\n[DRY RUN] Generated commit message (not committed):")
            print_commit_message(result)
            return

        print_commit_message(result)

        if click.confirm("\nWould you like to proceed with this commit message?"):
            click.echo("Commit created successfully!")
        else:
            click.echo("Commit cancelled.")

    except Exception as e:
        click.echo(f"An error occurred: {str(e)}", err=True)
        if verbose:
            import traceback

            click.echo("\nStack trace:")
            traceback.print_exc()


if __name__ == "__main__":
    cli()
