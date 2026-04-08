# gitbrief 🧠

Your daily developer standup — powered by your Git history.

---

## ✨ What it does

gitbrief scans your local repositories and tells you:

- What you worked on yesterday
- What might be broken
- What you should do next

All in seconds.

---

## ⚡ Demo

```
+------------------------------+
| [ Scanning repositories... ] |
+------------------------------+
Found 13 commits across 2 repositories
+------------------------------+
| [ Generating AI summary... ] |
+------------------------------+
+-  Yesterday  -+
| - Refactored auth system |
| - Updated payment API |
+---------------+
+---------------------  Risks  ----------------------+
| ! Login edge case may not be handled |
+----------------------------------------------------+
+--------------  Next Steps  ------------+
| > Test token validation |
| > Complete payment error handling |
+------------------------------------------+
```

**You'll be surprised how much you forget after 1 day.**

---

## 🚀 Install

```bash
pip install gitbrief
```

**Prerequisite:** [Ollama](https://ollama.ai) must be installed and running.

```bash
ollama serve
ollama pull llama3
```

---

## 🧪 Usage

```bash
# Today's summary (last 24 hours)
gitbrief today

# Weekly summary (last 7 days)
gitbrief week

# Scan a specific repository
gitbrief today --path /path/to/repo

# Scan multiple repositories
gitbrief week --path /path/to/repos

# Use different Ollama model
gitbrief today --model mistral

# Show raw commits without AI
gitbrief today --no-ai
```

---

## 📁 Options

| Option | Alias | Description | Default |
|--------|-------|-------------|---------|
| `--path` | `-p` | Path to Git repo or directory | `.` |
| `--model` | `-m` | Ollama model to use | `llama3` |
| `--no-ai` | - | Skip AI, show raw commits | `false` |

---

## 🧠 Why this exists

Developers forget context. Git stores history but not understanding.

gitbrief turns commits into insights.

> "I built this because I kept forgetting what I worked on the day before. Now I just run `gitbrief` and know exactly what to continue working on."

---

## 🔧 Development

```bash
# Clone the repo
git clone https://github.com/Akshat190/gitbrief.git
cd gitbrief

# Install dependencies
pip install -r requirements.txt

# Run locally
python -m cli today --path .
```

---

## 🤝 Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Good First Issues

- Add `--json` output flag for scripting
- Improve error messages for Windows
- Add `--since` and `--until` date filters
- Add configuration file support

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

## ⭐ Star this repo if it saved you time

[![GitHub Stars](https://img.shields.io/github/stars/Akshat190/gitbrief?style=social)](https://github.com/Akshat190/gitbrief)

---

<p align="center">
Made with ❤️ for developers
</p>
