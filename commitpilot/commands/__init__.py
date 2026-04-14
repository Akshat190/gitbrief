"""CLI commands package."""

from commitpilot.commands.today import today_command
from commitpilot.commands.week import week_command
from commitpilot.commands.standup import standup_command
from commitpilot.commands.stats import stats_command
from commitpilot.commands.history import history_command

__all__ = ["today_command", "week_command", "standup_command", "stats_command", "history_command"]
