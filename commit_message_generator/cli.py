"""CLI interface for Git Commit Message Generator Agent."""

import asyncio
import logging
import sys
from typing import Optional

import click

from commit_message_generator.commit_generator import CommitMessageGenerator
from commit_message_generator.config import LoggingConfig, setup_logging

# Configure basic logging initially (will be overridden by config)
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
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
    help="Ticket number (e.g., AB-12aze34). Must be provided as <2-letters>-<X-letters-or-digits>.",
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
        click.echo("Initializing commit message generator...")
        setup_verbose_logging(verbose)

    # Load configuration
    config_path = find_config_file()
    if config_path is None:
        # If no config file, use default logging
        logger.warning("No configuration file found. Using default settings.")
        setup_logging(LoggingConfig())
        config = None
    else:
        if verbose:
            click.echo(f"Using configuration from: {config_path}")

        from commit_message_generator.config import load_config_from_file

        try:
            config = load_config_from_file(config_path)
            if config is None:
                logger.warning(
                    f"Failed to load configuration from {config_path}. Using default settings."
                )
                config = None
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
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
            click.echo("Analyzing staged changes...")

        # Get the staged diff
        from .git_utils import get_staged_diff, is_git_repo

        if not is_git_repo():
            click.echo(
                "Error: Not a git repository. Please run this command from within a git repository.",
                err=True,
            )
            return

        diff, return_code = get_staged_diff()

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

        print_commit_message(result)

    except Exception as e:
        click.echo(f"An error occurred: {str(e)}", err=True)
        if verbose:
            import traceback

            click.echo("\nStack trace:")
            traceback.print_exc()


if __name__ == "__main__":
    cli()
