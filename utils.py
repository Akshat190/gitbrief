"""Utility functions for gitbrief."""
from datetime import datetime, timedelta


def get_time_range(days: int) -> tuple:
    """Get the time range for commit filtering."""
    end = datetime.now()
    start = end - timedelta(days=days)
    return start, end


def format_date(date: datetime) -> str:
    """Format a date for display."""
    return date.strftime("%Y-%m-%d %H:%M")


def truncate(text: str, max_length: int = 50) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def group_by_repo(commits: list) -> dict:
    """Group commits by repository."""
    result = {}
    for commit in commits:
        repo = commit.get("repo", "unknown")
        if repo not in result:
            result[repo] = []
        result[repo].append(commit)
    return result
