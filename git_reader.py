"""Git data extraction module."""
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from git import Repo, InvalidGitRepositoryError
from pathlib import Path


class GitReader:
    """Reads Git commit data from repositories."""

    def __init__(self, path: str = "."):
        self.path = Path(path).resolve()
        self.repos: List[str] = []
        self.commits: List[Dict] = []

    def get_commits(self, days: int = 1) -> List[Dict]:
        """Get commits from the last N days."""
        self.commits = []
        
        if self._is_git_repo(self.path):
            self.repos.append(str(self.path))
            self._scan_repo(self.path, days)
        else:
            self._scan_directory(self.path, days)

        return self.commits

    def _is_git_repo(self, path: Path) -> bool:
        """Check if a path is a Git repository."""
        try:
            Repo(str(path))
            return True
        except InvalidGitRepositoryError:
            return False

    def _scan_directory(self, directory: Path, days: int):
        """Scan a directory for Git repositories."""
        if not directory.exists() or not directory.is_dir():
            return

        for entry in directory.iterdir():
            if entry.name.startswith('.'):
                continue
            
            if entry.is_dir() and self._is_git_repo(entry):
                self.repos.append(str(entry))
                self._scan_repo(entry, days)
            elif entry.is_dir():
                self._scan_directory(entry, days)

    def _scan_repo(self, repo_path: Path, days: int):
        """Scan a single repository for commits."""
        try:
            repo = Repo(str(repo_path))
            cutoff = datetime.now() - timedelta(days=days)
            
            for commit in repo.iter_commits(all=True, max_count=100):
                commit_time = commit.committed_datetime.replace(tzinfo=None)
                
                if commit_time >= cutoff:
                    self.commits.append({
                        "repo": repo_path.name,
                        "message": commit.message.strip(),
                        "author": commit.author.name,
                        "date": commit.committed_datetime.strftime("%Y-%m-%d %H:%M"),
                        "files": list(commit.stats.files.keys()),
                        "insertions": commit.stats.total.get('insertions', 0),
                        "deletions": commit.stats.total.get('deletions', 0),
                    })
        except Exception as e:
            print(f"Error scanning {repo_path}: {e}")

    def get_repos(self) -> List[str]:
        """Get list of scanned repositories."""
        return self.repos


def get_time_range(days: int) -> tuple:
    """Get the time range for commit filtering."""
    end = datetime.now()
    start = end - timedelta(days=days)
    return start, end
