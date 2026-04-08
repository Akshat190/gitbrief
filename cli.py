"""CLI entry point for gitbrief."""

import typer
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Optional
import sys

from git_reader import GitReader
from summarizer import Summarizer, OpenAISummarizer
from utils import get_time_range

app = typer.Typer(
    name="gitbrief",
    help="Your daily developer standup - powered by your Git history",
    add_completion=False,
)
console = Console(force_terminal=True, no_color=False)

VERSION = "0.2.0"

AI_PROVIDERS = ["ollama", "openai"]


@app.command()
def today(
    path: Optional[str] = typer.Option(
        ".", "--path", "-p", help="Path to Git repository or directory of repos"
    ),
    model: Optional[str] = typer.Option("llama3", "--model", "-m", help="Ollama model to use"),
    provider: Optional[str] = typer.Option(
        "ollama", "--provider", help=f"AI provider: {', '.join(AI_PROVIDERS)}"
    ),
    no_ai: bool = typer.Option(False, "--no-ai", help="Skip AI summarization, show raw commits"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Show summary of Git activity from the last 24 hours."""
    run_briefing(path, days=1, model=model, provider=provider, no_ai=no_ai, json_output=json_output)


@app.command()
def week(
    path: Optional[str] = typer.Option(
        ".", "--path", "-p", help="Path to Git repository or directory of repos"
    ),
    model: Optional[str] = typer.Option("llama3", "--model", "-m", help="Ollama model to use"),
    provider: Optional[str] = typer.Option(
        "ollama", "--provider", help=f"AI provider: {', '.join(AI_PROVIDERS)}"
    ),
    no_ai: bool = typer.Option(False, "--no-ai", help="Skip AI summarization, show raw commits"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Show summary of Git activity from the last 7 days."""
    run_briefing(path, days=7, model=model, provider=provider, no_ai=no_ai, json_output=json_output)


@app.command()
def standup(
    path: Optional[str] = typer.Option(
        ".", "--path", "-p", help="Path to Git repository or directory of repos"
    ),
    model: Optional[str] = typer.Option("llama3", "--model", "-m", help="Ollama model to use"),
    provider: Optional[str] = typer.Option(
        "ollama", "--provider", help=f"AI provider: {', '.join(AI_PROVIDERS)}"
    ),
    no_ai: bool = typer.Option(False, "--no-ai", help="Skip AI summarization"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """Generate a ready-to-paste standup message (Yesterday / Today / Blockers)."""
    reader = GitReader(str(path))
    commits = reader.get_commits(days=1)

    if not commits:
        if json_output:
            output = {
                "yesterday": ["No commits found"],
                "today": ["To be determined"],
                "blockers": ["None"],
            }
            console.print(json.dumps(output, indent=2))
        else:
            standup_text = """**Yesterday:**
- No commits found

**Today:**
- To be determined

**Blockers:**
- None"""
            console.print(standup_text)
        raise typer.Exit(0)

    if no_ai:
        if json_output:
            output = {
                "yesterday": [c["message"] for c in commits[:5]],
                "today": ["To be determined"],
                "blockers": ["None"],
            }
            console.print(json.dumps(output, indent=2))
        else:
            standup_text = f"""**Yesterday:**
{chr(10).join(f"- {c['message']}" for c in commits[:5])}

**Today:**
- To be determined

**Blockers:**
- None"""
            console.print(standup_text)
        raise typer.Exit(0)

    summarizer = get_summarizer(provider, model)
    summary = summarizer.summarize_for_standup(commits)

    standup_text = f"""**Yesterday:**
{chr(10).join(f"- {item}" for item in summary.get("yesterday", []))}

**Today:**
{chr(10).join(f"- {item}" for item in summary.get("today", ["Continue working on pending tasks"]))}

**Blockers:**
{chr(10).join(f"- {item}" for item in summary.get("blockers", ["None"]))}"""

    if json_output:
        output = {
            "yesterday": summary.get("yesterday", []),
            "today": summary.get("today", []),
            "blockers": summary.get("blockers", []),
            "commits_count": len(commits),
        }
        console.print(json.dumps(output, indent=2))
    else:
        console.print(standup_text)


def get_summarizer(provider: str, model: str):
    """Get the appropriate summarizer based on provider."""
    if provider == "openai":
        return OpenAISummarizer(model=model)
    return Summarizer(model=model)


def run_briefing(path: str, days: int, model: str, provider: str, no_ai: bool, json_output: bool):
    """Run the briefing workflow."""
    console.print(
        Panel.fit("[bold cyan][ Scanning repositories... ][/bold cyan]", border_style="cyan")
    )

    reader = GitReader(str(path))
    commits = reader.get_commits(days=days)

    if not commits:
        console.print("[yellow]No commits found in the specified time range.[/yellow]")
        raise typer.Exit(0)

    console.print(
        f"[green]Found {len(commits)} commits across {len(reader.repos)} repositories[/green]"
    )

    if no_ai:
        display_raw_commits(commits, json_output)
        raise typer.Exit(0)

    console.print(
        Panel.fit("[bold purple][ Generating AI summary... ][/bold purple]", border_style="purple")
    )

    summarizer = get_summarizer(provider, model)
    summary = summarizer.summarize(commits)

    if json_output:
        output = {
            "yesterday": summary.get("yesterday", []),
            "risks": summary.get("risks", []),
            "next_steps": summary.get("next_steps", []),
            "commits_count": len(commits),
            "repos": reader.repos,
        }
        console.print(json.dumps(output, indent=2))
    else:
        display_summary(summary)


def display_raw_commits(commits: list, json_output: bool = False):
    """Display raw commit data without AI."""
    if json_output:
        output = [
            {"repo": c["repo"], "message": c["message"], "author": c["author"], "date": c["date"]}
            for c in commits
        ]
        console.print(json.dumps(output, indent=2))
    else:
        for commit in commits:
            console.print(f"[bold]{commit['repo']}[/bold]")
            console.print(f"  {commit['message']}")
            console.print(f"  [dim]{commit['author']} - {commit['date']}[/dim]")
            console.print()


def display_summary(summary: dict):
    """Display the AI-generated summary."""
    if "yesterday" in summary and summary["yesterday"]:
        console.print(
            Panel.fit(
                "\n".join(f"- {item}" for item in summary["yesterday"]),
                title=" Yesterday ",
                border_style="green",
                padding=(0, 1),
            )
        )

    if "risks" in summary and summary["risks"]:
        console.print(
            Panel.fit(
                "\n".join(f"! {item}" for item in summary["risks"]),
                title=" Risks ",
                border_style="yellow",
                padding=(0, 1),
            )
        )

    if "next_steps" in summary and summary["next_steps"]:
        console.print(
            Panel.fit(
                "\n".join(f"> {item}" for item in summary["next_steps"]),
                title=" Next Steps ",
                border_style="blue",
                padding=(0, 1),
            )
        )


@app.command()
def version():
    """Show gitbrief version."""
    console.print(f"[bold]gitbrief[/bold] version {VERSION}")
    raise typer.Exit(0)


if __name__ == "__main__":
    app()
