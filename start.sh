#!/bin/bash
set -e

echo "=== STARTING TITAN 24/7 DOCKER MT5 ENGINE ==="

# 1. Start Virtual Display (Headless screen for Windows GUI)
Xvfb :1 -screen 0 1024x768x16 &
sleep 2

# 2. Start Virtual VNC server (optional web view)
x11vnc -display :1 -nopw -listen 0.0.0.0 -forever &
sleep 2

# 3. Setup Python venv and install dependencies
python3 -m venv /app/venv
source /app/venv/bin/activate
pip install --no-cache-dir requests yfinance pandas

# 4. Run Continuous 24/7 Trading Loop
echo "Starting continuous 24/7 market monitoring and execution loop..."
python3 titan_continuous_daemon.py
