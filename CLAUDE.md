# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Setup

This is a Python project managed with uv (https://docs.astral.sh/uv/). The main application is a Streamlit-based stock analysis tool that fetches data from Yahoo Finance and provides interactive visualizations.

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

### Streamlit Application
- `uv run streamlit run stock_analyzer.py` - Start the stock analysis web application
- `uv run streamlit run stock_analyzer.py --server.port 8502` - Run on custom port
- `uv run streamlit run stock_analyzer.py --server.headless true` - Run in headless mode

### Project Structure
- `stock_analyzer.py` - Main Streamlit application for stock analysis
- `main.py` - Basic Python script (legacy)
- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Python version specification (3.12)
- `uv.lock` - Lockfile with exact dependency versions
- `.venv/` - Virtual environment (auto-created by uv)

## Application Details

### Main Features
- Interactive stock price analysis using Yahoo Finance data
- Candlestick charts with customizable time periods
- Volume analysis and statistical summaries
- Moving averages (20-day and 50-day)
- Japanese language interface

### Key Dependencies
- `streamlit` - Web application framework
- `yfinance` - Yahoo Finance API wrapper
- `pandas` - Data manipulation
- `plotly` - Interactive charts

### Development Notes
- The application is primarily in Japanese
- Error handling includes network connectivity and invalid ticker validation
- Uses Plotly for interactive charting
- Responsive design with Streamlit columns layout