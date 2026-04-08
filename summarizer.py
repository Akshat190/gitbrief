"""AI summarization module using Ollama and OpenAI."""

import os
import requests
from typing import List, Dict
from prompts import get_summarization_prompt, get_standup_prompt


class Summarizer:
    """Generates AI summaries using Ollama."""

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def summarize(self, commits: List[Dict]) -> Dict[str, List[str]]:
        """Generate a summary from commits."""
        if not commits:
            return {"yesterday": [], "risks": [], "next_steps": []}

        prompt = get_summarization_prompt(commits)

        try:
            response = self._call_ollama(prompt)
            return self._parse_response(response)
        except Exception as e:
            return self._fallback_summary(commits, str(e))

    def summarize_for_standup(self, commits: List[Dict]) -> Dict[str, List[str]]:
        """Generate a standup-ready summary (Yesterday / Today / Blockers)."""
        if not commits:
            return {"yesterday": [], "today": [], "blockers": []}

        prompt = get_standup_prompt(commits)

        try:
            response = self._call_ollama(prompt)
            return self._parse_standup_response(response)
        except Exception as e:
            return self._fallback_standup(commits, str(e))

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        return response.json().get("response", "")

    def _parse_response(self, response: str) -> Dict[str, List[str]]:
        """Parse LLM response into structured sections."""
        result = {"yesterday": [], "risks": [], "next_steps": []}

        current_section = None
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            if "yesterday" in line_lower or "summary" in line_lower:
                current_section = "yesterday"
            elif "risk" in line_lower or "unfinished" in line_lower:
                current_section = "risks"
            elif "next" in line_lower or "suggest" in line_lower:
                current_section = "next_steps"
            elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
                if current_section and current_section in result:
                    clean_line = line.lstrip("•*-").strip()
                    if clean_line:
                        result[current_section].append(clean_line)
            elif current_section and line:
                result[current_section].append(line)

        if not any(result.values()):
            result = self._simple_parse(response)

        return result

    def _parse_standup_response(self, response: str) -> Dict[str, List[str]]:
        """Parse LLM response for standup format."""
        result = {"yesterday": [], "today": [], "blockers": []}

        current_section = None
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            if "yesterday" in line_lower:
                current_section = "yesterday"
            elif "today" in line_lower:
                current_section = "today"
            elif "blocker" in line_lower:
                current_section = "blockers"
            elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
                if current_section and current_section in result:
                    clean_line = line.lstrip("•*-").strip()
                    if clean_line:
                        result[current_section].append(clean_line)
            elif current_section and line:
                result[current_section].append(line)

        return result

    def _simple_parse(self, response: str) -> Dict[str, List[str]]:
        """Simple fallback parser."""
        result = {"yesterday": [], "risks": [], "next_steps": []}

        sections = response.split("\n\n")
        for section in sections:
            lines = [l.strip() for l in section.split("\n") if l.strip()]
            if not lines:
                continue

            if "yesterday" in lines[0].lower():
                result["yesterday"] = lines[1:]
            elif "risk" in lines[0].lower():
                result["risks"] = lines[1:]
            elif "next" in lines[0].lower():
                result["next_steps"] = lines[1:]

        return result

    def _fallback_summary(self, commits: List[Dict], error: str) -> Dict[str, List[str]]:
        """Generate a fallback summary when Ollama is unavailable."""
        result = {"yesterday": [], "risks": [], "next_steps": []}

        repo_groups = {}
        for commit in commits:
            repo = commit.get("repo", "unknown")
            if repo not in repo_groups:
                repo_groups[repo] = []
            repo_groups[repo].append(commit["message"])

        for repo, messages in repo_groups.items():
            result["yesterday"].append(f"[{repo}] {len(messages)} commits")

        result["risks"].append("No AI analysis available - Ollama may be offline")
        result["next_steps"].append("Ensure Ollama is running: ollama serve")

        return result

    def _fallback_standup(self, commits: List[Dict], error: str) -> Dict[str, List[str]]:
        """Generate a fallback standup when AI is unavailable."""
        return {
            "yesterday": [c["message"] for c in commits[:5]],
            "today": ["Continue working on pending tasks"],
            "blockers": ["None"],
        }


class OpenAISummarizer:
    """Generates AI summaries using OpenAI API."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def summarize(self, commits: List[Dict]) -> Dict[str, List[str]]:
        """Generate a summary from commits using OpenAI."""
        if not commits:
            return {"yesterday": [], "risks": [], "next_steps": []}

        if not self.api_key:
            return {
                "yesterday": [],
                "risks": ["OpenAI API key not set. Set OPENAI_API_KEY env variable."],
                "next_steps": [],
            }

        prompt = get_summarization_prompt(commits)

        try:
            response = self._call_openai(prompt)
            return self._parse_response(response)
        except Exception as e:
            return self._fallback_summary(commits, str(e))

    def summarize_for_standup(self, commits: List[Dict]) -> Dict[str, List[str]]:
        """Generate a standup-ready summary using OpenAI."""
        if not commits:
            return {"yesterday": [], "today": [], "blockers": []}

        if not self.api_key:
            return {
                "yesterday": [c["message"] for c in commits[:5]],
                "today": ["Continue working on pending tasks"],
                "blockers": ["OpenAI API key not set"],
            }

        prompt = get_standup_prompt(commits)

        try:
            response = self._call_openai(prompt)
            return self._parse_standup_response(response)
        except Exception as e:
            return self._fallback_standup(commits, str(e))

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    def _parse_response(self, response: str) -> Dict[str, List[str]]:
        """Parse LLM response into structured sections."""
        result = {"yesterday": [], "risks": [], "next_steps": []}

        current_section = None
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            if "yesterday" in line_lower or "summary" in line_lower:
                current_section = "yesterday"
            elif "risk" in line_lower or "unfinished" in line_lower:
                current_section = "risks"
            elif "next" in line_lower or "suggest" in line_lower:
                current_section = "next_steps"
            elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
                if current_section and current_section in result:
                    clean_line = line.lstrip("•*-").strip()
                    if clean_line:
                        result[current_section].append(clean_line)
            elif current_section and line:
                result[current_section].append(line)

        if not any(result.values()):
            result = self._simple_parse(response)

        return result

    def _parse_standup_response(self, response: str) -> Dict[str, List[str]]:
        """Parse LLM response for standup format."""
        result = {"yesterday": [], "today": [], "blockers": []}

        current_section = None
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()

            if "yesterday" in line_lower:
                current_section = "yesterday"
            elif "today" in line_lower:
                current_section = "today"
            elif "blocker" in line_lower:
                current_section = "blockers"
            elif line.startswith("•") or line.startswith("-") or line.startswith("*"):
                if current_section and current_section in result:
                    clean_line = line.lstrip("•*-").strip()
                    if clean_line:
                        result[current_section].append(clean_line)
            elif current_section and line:
                result[current_section].append(line)

        return result

    def _simple_parse(self, response: str) -> Dict[str, List[str]]:
        """Simple fallback parser."""
        result = {"yesterday": [], "risks": [], "next_steps": []}

        sections = response.split("\n\n")
        for section in sections:
            lines = [l.strip() for l in section.split("\n") if l.strip()]
            if not lines:
                continue

            if "yesterday" in lines[0].lower():
                result["yesterday"] = lines[1:]
            elif "risk" in lines[0].lower():
                result["risks"] = lines[1:]
            elif "next" in lines[0].lower():
                result["next_steps"] = lines[1:]

        return result

    def _fallback_summary(self, commits: List[Dict], error: str) -> Dict[str, List[str]]:
        """Generate a fallback summary when OpenAI fails."""
        return {
            "yesterday": [c["message"] for c in commits[:5]],
            "risks": [f"OpenAI API error: {error}"],
            "next_steps": ["Check OPENAI_API_KEY environment variable"],
        }

    def _fallback_standup(self, commits: List[Dict], error: str) -> Dict[str, List[str]]:
        """Generate a fallback standup when OpenAI fails."""
        return {
            "yesterday": [c["message"] for c in commits[:5]],
            "today": ["Continue working on pending tasks"],
            "blockers": [f"API error: {error}"],
        }
