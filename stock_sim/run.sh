#!/bin/bash
# Stock Simulation Game Startup Script
# Uses uv for fast, modern Python package management

set -e

echo "========================================"
echo "  Stock Simulation Game"
echo "========================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed!"
    echo "Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Or via pip: pip install uv"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Install/sync dependencies
echo "📦 Syncing dependencies with uv..."
uv sync --quiet

echo ""
echo "🚀 Starting Flask server..."
echo "🌐 Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
uv run python broker_app.py
