#!/usr/bin/env python3
"""lobster-bot — run this and everything just works."""
import logging
import os
import shutil
import subprocess
import sys


def _check(name, cmd):
    """Check if a command exists."""
    return shutil.which(cmd) is not None


def _run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def bootstrap():
    """Install everything needed on first run."""
    missing = []

    # Python deps
    try:
        import telegram  # noqa: F401
    except ImportError:
        print("Installing Python dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])

    # Node.js (needed for Playwright)
    if not _check("node", "node"):
        missing.append("Node.js — install from https://nodejs.org")

    # Claude Code CLI
    if not _check("claude", "claude"):
        if _check("npm", "npm"):
            print("Installing Claude Code CLI...")
            subprocess.check_call(["npm", "i", "-g", "@anthropic-ai/claude-code"])
        else:
            missing.append("Claude Code CLI — run: npm i -g @anthropic-ai/claude-code")

    # Playwright browser
    if _check("npx", "npx"):
        # Check if chromium is already installed
        result = _run(["npx", "@playwright/mcp@latest", "--help"])
        if result.returncode == 0:
            # Check for actual browser binary
            check = _run(["npx", "playwright", "install", "--dry-run", "chromium"])
            if "chromium" in (check.stdout + check.stderr).lower() and "already" not in (check.stdout + check.stderr).lower():
                print("Installing Playwright Chromium (this takes a minute)...")
                subprocess.check_call(["npx", "playwright", "install", "--with-deps", "chromium"])

    # .env check
    if not os.environ.get("TELEGRAM_TOKEN"):
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            # Load .env manually
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        os.environ.setdefault(key.strip(), value.strip())

    if not os.environ.get("TELEGRAM_TOKEN"):
        missing.append("TELEGRAM_TOKEN — create a .env file (see README)")
    if not os.environ.get("TELEGRAM_USER_IDS"):
        missing.append("TELEGRAM_USER_IDS — create a .env file (see README)")

    if missing:
        print("\nMissing requirements:")
        for m in missing:
            print(f"  - {m}")
        print()
        sys.exit(1)


if __name__ == "__main__":
    bootstrap()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    from core.bot import main
    main()
