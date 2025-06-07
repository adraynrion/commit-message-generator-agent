"""CLI interface for Git Commit Message Generator Agent."""

import asyncio
import logging
import sys
from typing import Optional

import click
from rich.logging import RichHandler

from commit_message_generator.commit_generator import CommitMessageGenerator
from commit_message_generator.config import LoggingConfig, setup_logging
from commit_message_generator.rich_utils import console
from commit_message_generator.rich_utils import (
    print_commit_message as rich_print_commit_message,
)
from commit_message_generator.rich_utils import (
    print_error,
    print_header,
    print_success,
    print_warning,
)

# Configure basic logging initially (will be overridden by config)
logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            console=console,
            show_time=False,
            show_level=False,
            show_path=False,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
    ],
)

# Create logger here but don't set level yet
logger = logging.getLogger()


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
    required=True,
    help="Ticket number (e.g., AB-12aze34). Must be provided as <2-letters>-<alphanumeric>.",
)
@click.option("--verbose", "-v", is_flag=True, help="Show more detailed output")
def generate(
    ticket: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Generate a commit message based on staged changes.

    This command analyzes the currently staged changes in your git repository and
    generates a conventional commit message based on the changes found. Must be run from
    within a git repository.

    """
    asyncio.run(async_generate(ticket, verbose))


def find_config_file() -> Optional[str]:
    """Find the configuration file in standard locations.

    Returns:
        Path to the config file if found, None otherwise.

    """
    from pathlib import Path

    # Standard config file locations in order of precedence
    config_paths = [
        Path.cwd() / "config.yaml",  # ./config.yaml
        Path.home()
        / ".config"
        / "commit-msg-gen"
        / "config.yaml",  # ~/.config/commit-msg-gen/config.yaml
        Path("/etc/commit-msg-gen/config.yaml"),  # /etc/commit-msg-gen/config.yaml
    ]

    for path in config_paths:
        if path.exists():
            return str(path)
    logger.critical(
        "Could not find config file in standard locations! Refer to README for instructions."
    )
    sys.exit(1)


def setup_verbose_logging(verbose: bool) -> None:
    """Set up verbose logging if requested.

    Args:
        verbose: Whether to enable verbose logging

    """
    if verbose:
        # Set root logger and all module loggers to DEBUG level
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stderr,
        )

        # Update all existing handlers to use DEBUG level
        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            for handler in logger.handlers:
                handler.setLevel(logging.DEBUG)

    logger.debug("Verbose logging %s", "enabled" if verbose else "disabled")


async def async_generate(
    ticket: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Generate a commit message based on staged changes.

    This is the async implementation of the generate command.
    Must be run from within a git repository.

    Args:
        ticket: Optional ticket number to include in the commit message
        verbose: Whether to show verbose output

    """
    if verbose:
        print_header("Initializing commit message generator...")
        setup_verbose_logging(verbose)

    # Load configuration
    config_path = find_config_file()
    if config_path is None:
        # If no config file, use default logging
        print_warning("No configuration file found. Using default settings.")
        setup_logging(LoggingConfig())
        config = None
    else:
        if verbose:
            print_success(f"Using configuration from: {config_path}")

        from commit_message_generator.config import load_config_from_file

        try:
            config = load_config_from_file(config_path)
            if config is None:
                print_warning(
                    f"Failed to load configuration from {config_path}. Using default settings."
                )
                config = None
        except Exception as e:
            print_error(f"Error loading configuration: {e}")
            config = None

    # If config loading failed, use default config
    if config is None:
        from commit_message_generator.config import GeneratorConfig

        config = GeneratorConfig()
        logger.debug("Using default configuration")

    # Set up logging from config
    if hasattr(config, "logging") and config.logging:
        setup_logging(config.logging)

    try:
        generator = CommitMessageGenerator(config=config)

        if verbose:
            print_header("Analyzing staged changes...")

        # Get the staged diff
        from .git_utils import get_staged_diff, is_git_repo

        if not is_git_repo():
            print_error(
                "Not a git repository. Please run this command from within a git repository."
            )
            return

        diff, return_code = get_staged_diff()

        if return_code != 0:
            print_error("No staged changes to commit.")
            return

        if not diff or not diff.strip():
            print_error(
                "No staged changes found. Please stage your changes with 'git add' first."
            )
            return

        if verbose:
            # Show a summary of changes
            from .git_utils import get_staged_files_status
            from .rich_utils import print_diff_summary

            added, modified, deleted = get_staged_files_status()
            if added or modified or deleted:
                print_diff_summary(added, modified, deleted)

        if verbose:
            click.echo(f"Found staged changes (length: {len(diff)}):")
            click.echo("-" * 50)
            click.echo(diff[:500] + ("..." if len(diff) > 500 else ""))
            click.echo("-" * 50)

        # Generate the commit message
        if verbose:
            print_header("Generating commit message...")

        with console.status(
            "[bold green]Analyzing changes and generating commit message..."
        ):
            commit_message = await generator.generate_commit_message(
                diff, ticket=ticket
            )
        # Always extract .message if present
        commit_message_str: str
        if hasattr(commit_message, "message"):
            commit_message_str = commit_message.message
        rich_print_commit_message(commit_message_str)

    except ValueError as e:
        # User-friendly error message for validation errors
        print_error(str(e))
        if verbose:
            logger.debug(f"Validation error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        # Generic error handler for unexpected errors
        error_msg = "Failed to generate commit message. Please try again later."
        if verbose:
            logger.exception("Error details:")
        else:
            print_error(error_msg)
            print_warning("Use --verbose flag for more details")
        sys.exit(1)


if __name__ == "__main__":
    cli()
