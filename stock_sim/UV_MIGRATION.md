# Migration to uv - Modern Python Package Manager

The Stock Simulation Game now uses **uv** for dependency management instead of pip/requirements.txt.

## Why uv?

- ⚡ **10-100x faster** than pip
- 🔒 **Reproducible builds** with uv.lock
- 🎯 **Better dependency resolution** (solves conflicts pip can't)
- 🚀 **Automatic virtual environment** management
- 📦 **Single source of truth** - pyproject.toml

## What Changed

### Files Added
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Lock file for reproducible installs
- `.gitignore` - Python/uv specific ignores

### Files Removed
- `requirements.txt` - Replaced by pyproject.toml

### Files Updated
- `broker_app.py` - Added main() entry point
- `run.sh` - Now uses uv sync and uv run
- `README.md` - Updated installation instructions
- `STOCK_SIMULATION_GUIDE.md` - Updated quick start guide

## Installation

### Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Via pip:**
```bash
pip install uv
```

**Via Homebrew:**
```bash
brew install uv
```

**Via cargo (Rust):**
```bash
cargo install uv
```

## Usage

### Quick Start (Recommended)

```bash
cd stock_sim
./run.sh
```

The script automatically:
1. Checks if uv is installed
2. Syncs dependencies (creates .venv if needed)
3. Runs the application

### Manual Commands

**Install dependencies:**
```bash
uv sync
```

**Run the application:**
```bash
uv run python broker_app.py
```

**Run a specific Python command:**
```bash
uv run python -c "print('Hello from uv!')"
```

**Add a new dependency:**
```bash
uv add package-name
```

**Add a dev dependency:**
```bash
uv add --dev pytest
```

**Update dependencies:**
```bash
uv sync --upgrade
```

## pyproject.toml Overview

```toml
[project]
name = "stock-simulation-game"
version = "1.0.0"
requires-python = ">=3.9"

dependencies = [
    "flask>=3.0.0",
    "werkzeug>=3.0.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

## Virtual Environment

uv automatically creates and manages a `.venv` directory:

```
stock_sim/
├── .venv/          # Virtual environment (auto-created)
├── pyproject.toml  # Project config
└── uv.lock        # Lock file (commit this!)
```

**Important:**
- `.venv/` is gitignored (don't commit it)
- `uv.lock` should be committed (ensures reproducible builds)

## Migration Checklist

✅ pyproject.toml created with dependencies
✅ uv.lock generated for reproducibility
✅ requirements.txt removed
✅ run.sh updated to use uv
✅ Documentation updated
✅ .gitignore configured
✅ All tests passing

## Common Commands

| Task | Command |
|------|---------|
| Install deps | `uv sync` |
| Run app | `uv run python broker_app.py` |
| Add package | `uv add package-name` |
| Add dev package | `uv add --dev package-name` |
| Update all | `uv sync --upgrade` |
| Remove package | `uv remove package-name` |
| Show deps | `uv tree` |
| Check for updates | `uv sync --upgrade-package package-name` |

## Backwards Compatibility

If you prefer pip, you can still use it:

```bash
pip install -e .
python broker_app.py
```

The pyproject.toml format is pip-compatible, so both work!

## Troubleshooting

**"uv: command not found"**
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or add to PATH: `export PATH="$HOME/.cargo/bin:$PATH"`

**Dependencies not found when running:**
- Make sure to use `uv run`: `uv run python broker_app.py`
- Or activate venv: `source .venv/bin/activate`

**Permission errors:**
- uv installs to `~/.cargo/bin` by default
- Make sure that directory is in your PATH

**Slow first install:**
- First run downloads Python if needed
- Subsequent runs are very fast
- Lock file enables instant installs

## Performance Comparison

```
Task              pip          uv           Speedup
--------------------------------------------------------
Resolve deps      ~30s         ~0.3s        100x
Install deps      ~15s         ~1s          15x
Create venv       ~5s          ~0.1s        50x
```

## Resources

- **uv documentation**: https://docs.astral.sh/uv/
- **GitHub**: https://github.com/astral-sh/uv
- **pyproject.toml spec**: https://peps.python.org/pep-0621/

## Questions?

The stock simulation game works identically with uv - same functionality,
just faster and more reliable dependency management!

For detailed usage of the game itself, see:
- `README.md` - Technical documentation
- `STOCK_SIMULATION_GUIDE.md` - User guide
