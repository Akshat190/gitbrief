"""CLI entry point for gitbrief."""
import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
import sys

from git_reader import GitReader
from summarizer import Summarizer
from utils import get_time_range

app = typer.Typer(
    name="gitbrief",
    help="Your daily developer standup - powered by your Git history",
    add_completion=False,
)
console = Console(force_terminal=True, no_color=False)

VERSION = "0.1.0"


@app.command()
def today(
    path: Optional[str] = typer.Option(
        ".",
        "--path", "-p",
        help="Path to Git repository or directory of repos"
    ),
    model: Optional[str] = typer.Option(
        "llama3",
        "--model", "-m",
        help="Ollama model to use"
    ),
    no_ai: bool = typer.Option(
        False,
        "--no-ai",
        help="Skip AI summarization, show raw commits"
    ),
):
    """Show summary of Git activity from the last 24 hours."""
    run_briefing(path, days=1, model=model, no_ai=no_ai)


@app.command()
def week(
    path: Optional[str] = typer.Option(
        ".",
        "--path", "-p",
        help="Path to Git repository or directory of repos"
    ),
    model: Optional[str] = typer.Option(
        "llama3",
        "--model", "-m",
        help="Ollama model to use"
    ),
    no_ai: bool = typer.Option(
        False,
        "--no-ai",
        help="Skip AI summarization, show raw commits"
    ),
):
    """Show summary of Git activity from the last 7 days."""
    run_briefing(path, days=7, model=model, no_ai=no_ai)


def run_briefing(path: str, days: int, model: str, no_ai: bool):
    """Run the briefing workflow."""
    console.print(Panel.fit(
        "[bold cyan][ Scanning repositories... ][/bold cyan]",
        border_style="cyan"
    ))

    reader = GitReader(str(path))
    commits = reader.get_commits(days=days)
    commits = reader.get_commits(days=days)

    if not commits:
        console.print("[yellow]No commits found in the specified time range.[/yellow]")
        raise typer.Exit(0)

    console.print(f"[green]Found {len(commits)} commits across {len(reader.repos)} repositories[/green]")

    if no_ai:
        display_raw_commits(commits)
        raise typer.Exit(0)

    console.print(Panel.fit(
        "[bold purple][ Generating AI summary... ][/bold purple]",
        border_style="purple"
    ))

    summarizer = Summarizer(model=model)
    summary = summarizer.summarize(commits)

    display_summary(summary)


def display_raw_commits(commits: list):
    """Display raw commit data without AI."""
    for commit in commits:
        console.print(f"[bold]{commit['repo']}[/bold]")
        console.print(f"  {commit['message']}")
        console.print(f"  [dim]{commit['author']} - {commit['date']}[/dim]")
        console.print()


def display_summary(summary: dict):
    """Display the AI-generated summary."""
    if "yesterday" in summary and summary["yesterday"]:
        console.print(Panel.fit(
            "\n".join(f"- {item}" for item in summary["yesterday"]),
            title=" Yesterday ",
            border_style="green",
            padding=(0, 1)
        ))

    if "risks" in summary and summary["risks"]:
        console.print(Panel.fit(
            "\n".join(f"! {item}" for item in summary["risks"]),
            title=" Risks ",
            border_style="yellow",
            padding=(0, 1)
        ))

    if "next_steps" in summary and summary["next_steps"]:
        console.print(Panel.fit(
            "\n".join(f"> {item}" for item in summary["next_steps"]),
            title=" Next Steps ",
            border_style="blue",
            padding=(0, 1)
        ))


@app.command()
def version():
    """Show gitbrief version."""
    console.print(f"[bold]gitbrief[/bold] version {VERSION}")
    raise typer.Exit(0)


if __name__ == "__main__":
    app()
