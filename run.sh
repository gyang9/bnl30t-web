#!/bin/bash
# Script to run the BNL1T Web App

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found."
    exit 1
fi

# Install dependencies if needed (optional, uncomment if desired)
# pip install -r requirements.txt

# Run the app
echo "Starting BNL1T Web App..."
echo "Please open your browser and go to http://localhost:5001"
python3 app.py
