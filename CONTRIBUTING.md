# Contributing to gitbrief

Thank you for your interest in contributing to gitbrief! This guide will help you get started.

## 🧠 What is gitbrief?

gitbrief is a CLI tool that analyzes your Git activity across repositories and generates daily intelligent briefings. It answers:
- What did I work on?
- What is unfinished?
- What should I do next?

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git
- Ollama (optional, for AI summaries)

### Setup

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/Akshat190/gitbrief.git
cd gitbrief

# Install dependencies
pip install -r requirements.txt

# Test the CLI
python -m cli --help
python -m cli today --path .
```

## 🛠️ Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Follow existing code style
- Add comments for complex logic
- Keep functions small and focused

### 3. Test Your Changes

```bash
# Test CLI commands
python -m cli today --path . --no-ai
python -m cli week --path . --no-ai
```

### 4. Submit a Pull Request

1. Push your changes:
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   git push origin your-branch-name
   ```

2. Open a Pull Request on GitHub

3. Fill in the PR template:
   - Description of changes
   - Related issues
   - Testing done

## 🎯 Good First Issues

Looking for a way to contribute? Here are some beginner-friendly issues:

### Good First Issues (Easy)

- **#1**: Add `--json` output flag
  - Output results as JSON for scripting
  
- **#2**: Improve error messages
  - Make error messages more user-friendly
  
- **#3**: Add Windows PowerShell support
  - Fix compatibility issues on Windows

### Intermediate Issues

- **#4**: Add `gitbrief replay` command
  - Timeline narration of commits
  
- **#5**: Add `--since` and `--until` date filters
  - Custom date range filtering

- **#6**: Add configuration file support
  - Store default paths and preferences

### Advanced Issues

- **#7**: Implement local caching
  - Cache summaries to detect unfinished work
  
- **#8**: Add VS Code extension
  - Integrate with VS Code

## 📝 Code Style

- Use **PEP 8** for Python code
- Use type hints where possible
- Keep lines under 100 characters
- Use descriptive variable names

## 🧪 Testing

Run tests before submitting:

```bash
# Test single repo
python -m cli today --path /path/to/repo --no-ai

# Test multi-repo
python -m cli week --path /path/to/directory --no-ai
```

## 📖 Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions
- Update this file for developer-facing changes

## 🤝 Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## 💬 Getting Help

- Open an issue for bugs or feature requests
- Star the repo if it helps you!
- Share with other developers

## ⭐ Show Your Support

If gitbrief saved you time, give it a star! It helps others discover the project.

---

**Happy Coding!** 🚀
