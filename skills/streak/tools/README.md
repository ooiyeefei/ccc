# Streak Tools

Supplementary tools for the Streak skill - notifications and interactive Telegram bot.

## One Bot, All Challenges

Following Streak's design philosophy:

> **Your challenges are interconnected.** Keeping them together enables cross-challenge insights.

**One Telegram bot manages ALL your challenges** - work, health, learning, habits, everything:

```
Your Bot (@mystreak_bot)
         │
         │ /list → Shows ALL challenges
         │ /switch → Change active challenge
         │ /streak → Check in
         │ /insights → Cross-challenge patterns
         │
         ▼
    .streak/challenges/
    ├── work-project
    ├── morning-fitness
    ├── learn-rust
    └── daily-meditation
```

**Don't create separate bots for different challenges.** That defeats the purpose of cross-challenge insights.

---

## Files

| File | Description |
|------|-------------|
| `streak-notify.py` | Simple notification script (one-way, cron-friendly) |
| `streak-bot.py` | Full interactive Telegram bot (two-way) |
| `Dockerfile` | Container image for the bot |
| `docker-compose.yml` | One-command deployment |
| `requirements.txt` | Python dependencies |

---

## Quick Comparison

| Feature | streak-notify.py | streak-bot.py |
|---------|------------------|---------------|
| Direction | One-way (→ Telegram) | Two-way (↔ Telegram) |
| Check-in | Manual in Claude Code | Interactive in Telegram |
| Dependencies | None (stdlib only) | python-telegram-bot |
| Deployment | Cron/scheduler | Docker/always-on |
| Best for | Simple reminders | Full mobile experience |

---

## Option 1: Simple Notifications (streak-notify.py)

Send reminders when check-ins are due/overdue. No dependencies.

### Setup

1. **Configure credentials** in `.streak/config.md`:
   ```markdown
   ## Notifications
   - **Notifications:** enabled
   - **Telegram Bot Token:** your-bot-token
   - **Telegram Chat ID:** your-chat-id
   ```

2. **Test:**
   ```bash
   python tools/streak-notify.py /path/to/.streak
   ```

3. **Schedule with cron:**
   ```bash
   # Run daily at 9am
   0 9 * * * cd /path/to/project && python tools/streak-notify.py
   ```

---

## Option 2: Interactive Bot (streak-bot.py)

Full Telegram bot with buttons, conversations, and check-in flow.

### Features

- `/start` - Main menu with buttons
- `/streak` - Interactive check-in flow
- `/list` - List all challenges
- `/stats` - View statistics
- `/insights` - Cross-challenge patterns
- `/new` - Create new challenge (guided)
- `/switch` - Switch active challenge

### Quick Start with `/streak-telegram` Command (Recommended)

1. **Create Telegram bot:** Message @BotFather → `/newbot` → save token
2. **Get chat ID:** Message @userinfobot → save Id
3. **Message your bot:** Send `/start` to it
4. **Create `.env` file** in your project root:
   ```bash
   cat > .env << EOF
   TELEGRAM_BOT_TOKEN=your-bot-token
   ALLOWED_USERS=your-chat-id
   EOF
   ```
5. **Run the command:**
   ```bash
   /streak-telegram
   ```

The command handles copying files, .gitignore, and docker-compose automatically!

### Manual Docker Setup

1. **Copy files to your project:**
   ```bash
   cp tools/streak-bot.py .
   cp tools/Dockerfile .
   cp tools/docker-compose.yml .
   ```

2. **Create `.env` file:**
   ```bash
   TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
   ALLOWED_USERS=your-chat-id
   ```

3. **Start:**
   ```bash
   docker-compose up -d
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

### Manual Setup (without Docker)

1. **Install dependencies:**
   ```bash
   pip install -r tools/requirements.txt
   ```

2. **Set environment:**
   ```bash
   export TELEGRAM_BOT_TOKEN=your-token
   export STREAK_PATH=/path/to/.streak
   ```

3. **Run:**
   ```bash
   python tools/streak-bot.py
   ```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Bot token from @BotFather |
| `STREAK_PATH` | No | `./.streak` | Path to .streak directory |
| `GIT_AUTO_SYNC` | No | `true` | Auto git pull/push |
| `ALLOWED_USERS` | Yes* | - | Your chat ID (for notifications) |
| `NOTIFICATION_ENABLED` | No | `true` | Enable daily push notifications |
| `NOTIFICATION_HOUR` | No | `9` | Hour to send reminder (0-23) |
| `NOTIFICATION_MINUTE` | No | `0` | Minute to send reminder (0-59) |
| `TIMEZONE` | No | `UTC` | Your timezone (e.g., `Asia/Singapore`) |

*Required for the bot to send you automatic push notifications.

### Git Sync

The bot can automatically sync with GitHub:
- **Pull** before reading files (ensures latest data)
- **Push** after check-ins (syncs with Claude Code)

For this to work:
1. Run bot from a git repository
2. Have git credentials configured
3. Set `GIT_AUTO_SYNC=true`

If you don't want git sync, set `GIT_AUTO_SYNC=false`.

---

## Deployment Options

### Personal Use

**Docker Compose** (recommended):
```bash
docker-compose up -d
```

**Systemd** (Linux):
```ini
# /etc/systemd/system/streak-bot.service
[Unit]
Description=Streak Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
Environment=TELEGRAM_BOT_TOKEN=your-token
Environment=STREAK_PATH=/path/to/.streak
ExecStart=/usr/bin/python3 streak-bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**PM2** (Node.js ecosystem):
```bash
pm2 start streak-bot.py --interpreter python3
pm2 save
```

### Hosted Service (Multi-tenant)

For offering as a paid service, you'd need:

1. **User management** - Each user has their own bot instance or shared bot with user isolation
2. **Storage backend** - Replace file-based storage with database (PostgreSQL, MongoDB)
3. **GitHub OAuth** - Let users connect their repos
4. **Webhook mode** - Instead of polling, use webhooks for scale

Architecture for hosted service:
```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Telegram  │────►│   API Gateway   │────►│   Bot Pool   │
│   Webhook   │     │   (Kong/AWS)    │     │   (Workers)  │
└─────────────┘     └─────────────────┘     └──────┬───────┘
                                                   │
                    ┌──────────────────────────────┼──────────────┐
                    │                              ▼              │
               ┌────┴────┐    ┌──────────┐    ┌────────┐         │
               │ User DB │    │ Redis    │    │ GitHub │         │
               │ (Auth)  │    │ (State)  │    │ API    │         │
               └─────────┘    └──────────┘    └────────┘         │
```

---

## Creating Your Bot

1. **Message @BotFather** on Telegram
2. Send `/newbot`
3. Choose a name: `My Streak Bot`
4. Choose a username: `mystreak_bot` (must end in `bot`)
5. Copy the token

**Get your chat ID:**
1. Message @userinfobot
2. Copy the `Id` number

---

## Troubleshooting

**Bot doesn't respond:**
- Check token is correct
- Ensure you've messaged the bot first (`/start`)
- Check logs: `docker-compose logs -f`

**Git sync fails:**
- Verify git credentials are mounted
- Check repo has remote configured
- Try `GIT_AUTO_SYNC=false` to disable

**Permission denied:**
- Check `ALLOWED_USERS` setting
- Verify your chat ID is in the list

---

---

## Security Notes

**Keep your credentials safe:**

1. **Never commit `.env` files** - Add to `.gitignore`:
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Never commit `config.md` with real tokens** - Either:
   - Add `.streak/config.md` to `.gitignore`
   - Or use environment variables instead of hardcoding in config.md

3. **Use `ALLOWED_USERS`** - Restrict bot access to your chat ID only

---

## License

MIT - Part of the Streak skill for Claude Code
