"""Prompt templates for AI summarization."""
from typing import List, Dict


def get_summarization_prompt(commits: List[Dict]) -> str:
    """Generate prompt for summarizing Git commits."""
    
    commit_summary = []
    for commit in commits:
        files_info = ""
        if commit.get("files"):
            files_info = f" (files: {', '.join(commit['files'][:5])}"
            if len(commit['files']) > 5:
                files_info += f", +{len(commit['files']) - 5} more"
            files_info += ")"
        
        commit_summary.append(
            f"- [{commit['repo']}] {commit['message']}{files_info}"
        )

    commits_text = "\n".join(commit_summary)

    prompt = f"""You are a developer assistant that summarizes Git activity into a daily briefing.

Analyze the following commits from the last 24 hours and create a structured summary.

Commits:
{commits_text}

Generate a briefing with these three sections:

## 🧠 Yesterday
Summarize the main work done. Group by theme/project. Use bullet points.

## ⚠️ Risks  
Identify potential issues:
- Unfinished work (WIP commits, "todo" in messages)
- Risky changes (large refactors, security-related)
- Missing tests or error handling

## 🎯 Next Steps
Suggest logical next actions based on the commits.

Be concise and actionable. Focus on what matters."""

    return prompt


def get_week_summarization_prompt(commits: List[Dict]) -> str:
    """Generate prompt for weekly summary."""
    
    by_day = {}
    for commit in commits:
        day = commit.get('date', '')[:10]
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(commit)

    daily_summaries = []
    for day, day_commits in sorted(by_day.items()):
        repo_groups = {}
        for c in day_commits:
            repo = c.get("repo", "unknown")
            if repo not in repo_groups:
                repo_groups[repo] = []
            repo_groups[repo].append(c["message"])
        
        summary = f"{day}:\n"
        for repo, msgs in repo_groups.items():
            summary += f"  [{repo}]: {len(msgs)} commits\n"
        
        daily_summaries.append(summary)

    commits_text = "\n".join(daily_summaries)

    prompt = f"""You are a developer assistant that summarizes Git activity into a weekly briefing.

Analyze the following commits from the last 7 days.

Commits by day:
{commits_text}

Generate a weekly briefing with:

## 🧠 Week Summary
What was accomplished each day. Group by project.

## ⚠️ Risks
Potential issues or unfinished work.

## 🎯 This Week's Goals
What should be focused on next week.

Be concise."""

    return prompt
