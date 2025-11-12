#!/bin/bash
# Stock Simulation Game Startup Script

echo "========================================"
echo "  Stock Simulation Game"
echo "========================================"
echo ""
echo "Starting Flask server..."
echo "Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
python3 broker_app.py
