#!/usr/bin/env bash
set -euo pipefail

# Lobsterbot — Pull upstream changes and restart services
# Usage: ./deploy/update.sh

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

echo "=== Lobsterbot Updater ==="
echo ""

# Pull latest changes
echo "Pulling latest changes..."
git pull --ff-only

# Update dependencies
echo "Updating dependencies..."
python3 -m pip install -r requirements.txt --quiet

# Restart services if systemd is available
if command -v systemctl >/dev/null 2>&1; then
    echo "Restarting services..."
    sudo systemctl restart claude-bot 2>/dev/null && echo "  claude-bot restarted" || echo "  claude-bot not running"
    sudo systemctl restart claude-scheduler 2>/dev/null && echo "  claude-scheduler restarted" || echo "  claude-scheduler not running"
fi

echo ""
echo "=== Update complete ==="
