#!/bin/bash
set -eo pipefail

# Activate virtual environment and run the rescue dashboard
echo "🚁 Starting Rescue Dashboard..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "📍 Running from: $SCRIPT_DIR"

# Activate virtual environment when available
if [[ -f "venv/bin/activate" ]]; then
  source venv/bin/activate
  echo "✅ Virtual environment activated"
else
  echo "⚠️  No venv found at dashboard/venv; using system Python"
fi

echo "🚀 Starting Flask server..."

# Run the dashboard
python server.py
