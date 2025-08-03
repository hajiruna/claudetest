# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Setup

This is a Python project managed with uv (https://docs.astral.sh/uv/).

## Development Commands

### Package Management
- `uv add <package>` - Add a dependency
- `uv add --dev <package>` - Add a development dependency
- `uv remove <package>` - Remove a dependency
- `uv sync` - Install dependencies from lockfile
- `uv lock` - Update lockfile

### Python Environment
- `uv run <command>` - Run command in virtual environment
- `uv run python <script.py>` - Run Python script
- `uv shell` - Activate virtual environment

### Project Structure
- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Python version specification (3.12)
- `uv.lock` - Lockfile with exact dependency versions
- `.venv/` - Virtual environment (auto-created by uv)