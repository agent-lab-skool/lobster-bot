# 🦞 lobster-bot

Your self-hosted AI assistant on Telegram. Powered by Claude Code.

It browses the web, remembers your conversations, and runs 24/7 on your own server.

## Get Started

```bash
git clone https://github.com/aflekkas/lobster-bot.git
cd lobster-bot
```

Create a `.env`:

```
TELEGRAM_TOKEN=your-token-from-botfather
TELEGRAM_USER_IDS=your-telegram-user-id
```

Run:

```bash
python run.py
```

That's it. The run script installs dependencies, sets up Playwright, loads your `.env`, and starts the bot.

## Setup

1. Get a bot token — message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`
2. Get your user ID — message [@userinfobot](https://t.me/userinfobot)
3. Put both in `.env`

## What It Can Do

- **Web browsing** — navigates real websites via Playwright, not just search snippets
- **Persistent memory** — remembers facts about you and keeps daily logs
- **Conversations that stick** — sessions persist, so context carries across messages
- **Usage tracking** — know exactly what you're spending with `/usage`
- **Auto-updates** — pulls from git every 5 minutes, push a change and it goes live

## Deploy on a VPS

SSH in, then:

```bash
git clone https://github.com/aflekkas/lobster-bot.git ~/lobster-bot
cd ~/lobster-bot
# create your .env with TELEGRAM_TOKEN and TELEGRAM_USER_IDS
cp deploy/systemd/lobster-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now lobster-bot
```

## Requirements

- Python 3.11+
- Node.js
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) — `npm i -g @anthropic-ai/claude-code`

`run.py` handles installing everything else automatically.

---

If this is useful to you, a ⭐ on the repo goes a long way.
