#!/usr/bin/env bash
set -euo pipefail

# Lobsterbot — One-command Ubuntu VPS setup
# Usage: curl -sSL <raw-url> | bash
# Or: ./deploy/install.sh

REPO_DIR="${LOBSTERBOT_DIR:-$HOME/lobsterbot}"
PYTHON="${PYTHON:-python3}"

echo "=== Lobsterbot Installer ==="
echo ""

# Check prerequisites
command -v git >/dev/null 2>&1 || { echo "Error: git is required"; exit 1; }
command -v "$PYTHON" >/dev/null 2>&1 || { echo "Error: $PYTHON is required"; exit 1; }
command -v claude >/dev/null 2>&1 || { echo "Error: Claude Code CLI is required. Install from https://docs.anthropic.com/en/docs/claude-code"; exit 1; }

# Check Python version
PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
    echo "Error: Python 3.11+ required (found $PY_VERSION)"
    exit 1
fi

echo "Prerequisites OK (Python $PY_VERSION, Claude Code $(claude --version 2>/dev/null || echo 'unknown'))"
echo ""

# Clone or update repo
if [ -d "$REPO_DIR" ]; then
    echo "Updating existing installation at $REPO_DIR..."
    cd "$REPO_DIR"
    git pull --ff-only
else
    echo "Cloning lobsterbot to $REPO_DIR..."
    git clone https://github.com/aflekkas/lobsterbot.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

# Install dependencies
echo "Installing Python dependencies..."
$PYTHON -m pip install -r requirements.txt --quiet

# Install optional dependencies
echo "Installing optional dependencies (ffmpeg, faster-whisper)..."
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get install -y ffmpeg >/dev/null 2>&1 || echo "Warning: Could not install ffmpeg"
elif command -v brew >/dev/null 2>&1; then
    brew install ffmpeg >/dev/null 2>&1 || echo "Warning: Could not install ffmpeg"
fi
$PYTHON -m pip install faster-whisper --quiet 2>/dev/null || echo "Note: faster-whisper not installed (voice transcription will be unavailable)"

# Set up user config
if [ ! -d "$REPO_DIR/user" ]; then
    echo ""
    echo "Setting up user configuration..."
    cp -r "$REPO_DIR/user.example" "$REPO_DIR/user"
    echo "Created user/ directory from template."
    echo ""
    echo "IMPORTANT: Edit $REPO_DIR/user/config.yaml with your:"
    echo "  1. Telegram bot token (from @BotFather)"
    echo "  2. Your Telegram user ID (from @userinfobot)"
else
    echo "User config already exists, skipping."
fi

# Set up systemd services (Linux only)
if command -v systemctl >/dev/null 2>&1; then
    echo ""
    echo "Setting up systemd services..."
    sudo cp "$REPO_DIR/deploy/systemd/claude-bot.service" /etc/systemd/system/
    sudo cp "$REPO_DIR/deploy/systemd/claude-scheduler.service" /etc/systemd/system/

    # Replace placeholders
    sudo sed -i "s|/home/USER/lobsterbot|$REPO_DIR|g" /etc/systemd/system/claude-bot.service
    sudo sed -i "s|/home/USER/lobsterbot|$REPO_DIR|g" /etc/systemd/system/claude-scheduler.service
    sudo sed -i "s|User=USER|User=$(whoami)|g" /etc/systemd/system/claude-bot.service
    sudo sed -i "s|User=USER|User=$(whoami)|g" /etc/systemd/system/claude-scheduler.service

    sudo systemctl daemon-reload
    echo "Services installed. Enable with:"
    echo "  sudo systemctl enable --now claude-bot"
    echo "  sudo systemctl enable --now claude-scheduler"
fi

echo ""
echo "=== Installation complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit $REPO_DIR/user/config.yaml"
echo "  2. Run: cd $REPO_DIR && $PYTHON run.py"
echo ""
