"""CLI entry point for commitpilot - backward compatible shim."""

import typer

from commitpilot.cli import app

if __name__ == "__main__":
    app()
