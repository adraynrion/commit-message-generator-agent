"""Rich text utilities for the commit message generator."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Global console instance with color support
console = Console(highlight=False)

def print_header(text: str) -> None:
    """Print a styled header.

    Args:
        text: Header text to display
    """
    console.print(f"[bold blue]\n{text}[/bold blue]\n")

def print_success(text: str) -> None:
    """Print a success message.

    Args:
        text: Success message to display
    """
    console.print(f"[bold green]✓ {text}[/bold green]")

def print_warning(text: str) -> None:
    """Print a warning message.

    Args:
        text: Warning message to display
    """
    console.print(f"[bold yellow]⚠️  {text}[/bold yellow]")

def print_error(text: str) -> None:
    """Print an error message.

    Args:
        text: Error message to display
    """
    console.print(f"[bold red]✗ {text}[/bold red]")

def print_commit_message(message: str) -> None:
    """Print the commit message in a clean, copy-paste friendly format.

    Args:
        message: The commit message to display
    """
    # Print a success indicator
    console.print("[green]✓[/green] [bold]Commit message generated:[/bold]\n")
    
    # Print the message with proper line breaks and no extra formatting
    console.print(message.strip(), highlight=False)
    
    # Add a newline at the end for better separation
    console.print()

def print_diff_summary(added: int, modified: int, deleted: int) -> None:
    """Print a summary of changed files.

    Args:
        added: Number of added files
        modified: Number of modified files
        deleted: Number of deleted files
    """
    table = Table(show_header=False, box=None, padding=(0, 1, 0, 0))
    table.add_column(style="green")
    table.add_column(style="cyan")

    if added > 0:
        table.add_row("Added:", f"{added} files")
    if modified > 0:
        table.add_row("Modified:", f"{modified} files")
    if deleted > 0:
        table.add_row("Deleted:", f"{deleted} files")

    if added or modified or deleted:
        console.print("\n[bold]Changes detected:[/bold]")
        console.print(table)

def confirm(prompt: str, default: bool = True) -> bool:
    """Prompt for confirmation with a default value.

    Args:
        prompt: The prompt to display
        default: Default value if user just presses Enter

    Returns:
        bool: User's confirmation
    """
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        response = console.input(f"{prompt} {suffix} ").strip().lower()
        if not response:
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        console.print("Please respond with 'y' or 'n'.")
