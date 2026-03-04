#!/usr/bin/env python3
"""Interactive setup wizard for lobsterbot."""

import shutil
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
USER_DIR = REPO_DIR / "user"
EXAMPLE_DIR = REPO_DIR / "user.example"
CONFIG_PATH = USER_DIR / "config.yaml"


def main():
    print("=== Lobsterbot Setup Wizard ===\n")

    # Copy template if needed
    if not USER_DIR.exists():
        shutil.copytree(EXAMPLE_DIR, USER_DIR)
        print(f"Created {USER_DIR} from template.\n")
    else:
        print(f"Config directory already exists at {USER_DIR}.\n")

    # Get bot token
    print("Step 1: Telegram Bot Token")
    print("  Message @BotFather on Telegram and create a new bot.")
    print("  Copy the token it gives you.\n")
    token = input("  Bot token: ").strip()
    if not token:
        print("Error: Token is required.")
        sys.exit(1)

    # Get user ID
    print("\nStep 2: Your Telegram User ID")
    print("  Message @userinfobot on Telegram to get your user ID.\n")
    user_id = input("  User ID: ").strip()
    if not user_id.isdigit():
        print("Error: User ID must be a number.")
        sys.exit(1)

    # Write config
    config_content = f"""telegram:
  token: "{token}"
  allowed_users:
    - {user_id}

# Optional: scheduled tasks
# scheduler:
#   tasks:
#     - name: morning_brief
#       cron: "0 8 * * *"
#       prompt: "Good morning! Give me a brief overview of today."
#       chat_id: {user_id}
"""
    CONFIG_PATH.write_text(config_content)
    print(f"\nConfig written to {CONFIG_PATH}")

    print("\n=== Setup complete! ===")
    print(f"\nRun the bot:  python3 {REPO_DIR}/run.py")


if __name__ == "__main__":
    main()
