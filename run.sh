#!/bin/bash
# Script to run the PlayLister application

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install required packages
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting PlayLister application..."
python app.py

# Deactivate virtual environment when the app stops
deactivate
