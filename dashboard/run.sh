#!/bin/bash

# Activate virtual environment and run the rescue dashboard
echo "🚁 Starting Rescue Dashboard..."
echo "📍 Make sure you're in the dashboard directory"

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated"
echo "🚀 Starting Flask server..."

# Run the dashboard
python server.py
