#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Function to kill the background app when this script stops
cleanup() {
    echo ""
    echo "Shutting down BNL1T Web App..."
    if [ -n "$APP_PID" ]; then
        kill $APP_PID
    fi
    exit
}

# Trap Ctrl+C (SIGINT) to run cleanup
trap cleanup SIGINT

echo "---------------------------------------------------"
echo "   BNL1T Event Display - Launcher"
echo "---------------------------------------------------"

# 1. Start the Flask App in the background
echo "[1/2] Starting Web Server..."
python3 app.py > app.log 2>&1 &
APP_PID=$!

# Wait a few seconds for it to start
sleep 3

# Get Public IP
PUBLIC_IP=$(wget -qO- http://ipecho.net/plain)
if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP=$(curl -s ifconfig.me)
fi
if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP="Could not detect. Please visit http://ipecho.net/plain"
fi

echo "[2/2] Starting Public Tunnel..."
echo ""
echo "==================================================="
echo "   Public URL: https://bnl30ton-display.loca.lt"
echo "   Password:   $PUBLIC_IP"
echo ""
echo "   *IF THAT PASSWORD FAILS*: Open https://localtunnel.me/ip"
echo "   in your browser and use the IP address shown there."
echo "==================================================="
echo ""
echo "Keep this terminal OPEN. Press Ctrl+C to stop."
echo ""

# Run localtunnel in foreground
npx localtunnel --port 5001 --subdomain bnl30ton-display
