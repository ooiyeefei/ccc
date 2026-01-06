# Streak - Universal Challenge Tracker

Track any personal challenge with flexible cadence, intelligent insights, and cross-challenge learning detection.

**Works for any challenge type:** Learning, Building, Fitness, Creative, Habit, or Custom.

---

## Design Philosophy

> **Your challenges are interconnected.** Your fitness affects your work. Your learning enables your building. Your habits shape your creativity.

Streak is designed around this insight. By keeping all your challenges together in one place, the tool can detect **cross-challenge connections** that you might miss:

- "Your 'Morning Workout' sessions correlate with higher productivity in 'Work Project'"
- "Skills from 'Learn Rust' directly enabled progress in 'Build CLI Tools'"
- "Best creative output happens 2 days after rest days"

**This is the unique value of Streak** - not just tracking individual challenges, but understanding how they interact.

### One Place, All Challenges

Put ALL your challenges in a single `.streak/` folder, regardless of "life area":

```
.streak/challenges/
├── work-project-delivery    # Work
├── morning-fitness          # Health
├── learn-rust               # Learning
├── daily-meditation         # Habit
└── weekend-sketching        # Creative
```

Use `/streak-switch` to navigate between them. Use `/streak-insights` to discover connections.

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Quick Start

### Option 1: Slash Commands (Recommended)

Use slash commands for **reliable, deterministic** triggering:

```bash
/streak              # Check in to active challenge
/streak-new          # Create a new challenge (guided)
/streak-list         # List all challenges (active + paused)
/streak-list --all   # List all including archived
/streak-switch NAME  # Switch active challenge
/streak-stats        # View progress and achievements
/streak-insights     # Cross-challenge insights
/streak-pause NAME   # Pause a challenge
/streak-archive NAME # Archive a challenge
/streak-resume NAME  # Resume paused/archived challenge
```

### Option 2: Natural Language (Alternative)

You can also ask Claude Code naturally - it will invoke the skill when relevant:

```
"Start a new streak challenge"
"Check in to my challenge"
"Show my challenges"
"Show my streak stats"
```

## Commands Reference

| Command | What It Does |
|---------|--------------|
| `/streak` | Check in to active challenge - log progress, get insights |
| `/streak-new` | Create a new challenge with guided setup |
| `/streak-list` | List challenges (active + paused), sorted by priority |
| `/streak-list --all` | Include archived challenges in the list |
| `/streak-switch NAME` | Switch to a different active challenge |
| `/streak-stats` | View progress, streaks, patterns, achievements |
| `/streak-insights` | Cross-challenge connections and compound learning |
| `/streak-pause NAME` | Temporarily pause a challenge |
| `/streak-archive NAME` | Move challenge to long-term storage |
| `/streak-resume NAME` | Bring paused/archived challenge back to active |
| `/streak-telegram` | Deploy Telegram bot with Docker (one command) |

## Challenge Types

| Type | Best For | Example |
|------|----------|---------|
| **Learning** | Courses, skills, books | "Learn Rust", "Read 12 Books" |
| **Building** | Projects, shipping, coding | "30 Days of AI/ML", "Ship Daily" |
| **Fitness** | Workouts, health goals | "Morning Workout", "Run 5K" |
| **Creative** | Art, writing, music | "Daily Sketching", "Write 500 Words" |
| **Habit** | Routines, consistency | "Morning Meditation", "No Sugar" |
| **Custom** | Anything else | Define your own structure |

## Features

### Universal Files, Type-Adaptive Content

Each challenge gets these files, with content tailored to your challenge type:

| File | Purpose |
|------|---------|
| `challenge-config.md` | Metadata, goal, progress tracking |
| `challenge-log.md` | Progress log with summary table |
| `today.md` | Today's session context (energy, focus, constraints) |
| `backlog.md` | Ideas and things to try |
| `preferences.md` | Your setup - **pre-filled based on type!** |
| `context.md` | Linked resources, tools, people |
| `insights.md` | Auto-generated insights |
| `sessions/` | Folder for detailed session notes |

### Type-Adaptive Preferences

When you create a challenge, the skill asks type-specific questions and pre-fills your `preferences.md`:

**Learning:** Topics, resources, learning style
**Building:** Stack, tools, deployment targets
**Fitness:** Equipment, workout types, location
**Creative:** Medium, style, sharing platform
**Habit:** Trigger, duration, rewards

### Flexible Cadence

Set your check-in frequency per challenge:
- Daily
- Every 2-3 days
- Weekly
- Custom interval

### Priority Ordering

Control the display order of your challenges in `/streak-list`:
- Set `**Priority:**` in `challenge-config.md` (0-100, default 0)
- Higher priority = shown first in each status group
- Within same priority, sorted by most recent check-in

### Challenge Lifecycle

Manage challenge status to keep your list organized:
- **Active** - Current challenges you're working on
- **Paused** - Temporarily on hold, plan to resume later
- **Archived** - Long-term storage, hidden by default

Commands: `/streak-pause`, `/streak-archive`, `/streak-resume`

### Auto-Insights

At each check-in, Streak analyzes your progress:
- Pattern detection (best days, themes)
- Streak analysis
- Cross-challenge connections
- Personalized suggestions

### Cross-Challenge Connections

Streak detects when skills from one challenge help another:
```
Your "Learn Rust" challenge (Session 12) directly enabled
your "Build CLI Tools" challenge (Session 3) where you
shipped a concurrent file processor.
```

### Achievements

Earn badges as you progress:
- :fire: **First Flame** - 3-day streak
- :fire::fire: **On Fire** - 7-day streak
- :fire::fire::fire: **Unstoppable** - 30-day streak
- :gem: **Diamond Streak** - 100-day streak
- :footprints: **First Step** - First check-in
- :star: **Dedicated** - 10 sessions
- :link: **Connected** - First cross-challenge insight
- :muscle: **Comeback** - Resume after 7+ days

### Calendar Export (Optional)

Generate .ics files for calendar reminders by asking:
```
"Export calendar reminders for my challenge"
"Create an .ics file for my streak"
```
Works with Google Calendar, Apple Calendar, Outlook.

## Data Storage

All data stored locally in `.streak/` folder:
```
.streak/
├── config.md                     # Global settings
├── active.md                     # Current challenge pointer
└── challenges/
    └── [challenge-id]/
        ├── challenge-config.md   # Metadata
        ├── challenge-log.md      # Progress log
        ├── today.md              # Session context
        ├── backlog.md            # Ideas to try
        ├── preferences.md        # Your setup
        ├── context.md            # Linked resources
        ├── insights.md           # Auto-generated
        └── sessions/
            └── session-XXX/
                └── notes.md      # Session notes
```

No external dependencies. No cloud sync required.

## Example Challenges

### 30 Days of AI/ML (Building)
```
Type: Building
Goal: Ship one AI-powered micro-app per day
Cadence: Daily
Stack: Python, TypeScript, Claude Code
```

### Learn Rust (Learning)
```
Type: Learning
Goal: Complete Rustlings and build a CLI tool
Cadence: Every 2 days
Resources: Rustlings, The Rust Book
```

### Morning Workout (Fitness)
```
Type: Fitness
Goal: Build consistent strength training habit
Cadence: Daily (with rest days)
Equipment: Home gym - dumbbells, pull-up bar
```

### Daily Sketching (Creative)
```
Type: Creative
Goal: Draw one sketch per day for 100 days
Cadence: Daily
Medium: Digital art (Procreate)
```

### Morning Meditation (Habit)
```
Type: Habit
Goal: Meditate 10 minutes every morning
Cadence: Daily
Trigger: After coffee, before email
```

## Tips

1. **Start sustainable** - Every 2-3 days is more realistic than daily
2. **Be specific** - "Complete Rustlings" > "Learn Rust"
3. **Use today.md** - Set context before sessions
4. **Keep backlog fresh** - Ideas for low-energy days
5. **Check insights weekly** - See your patterns
6. **Reset guilt-free** - Archiving is progress

---

## Telegram Bot (Optional)

Get push notifications and check in from your phone via Telegram.

### One Bot, All Your Challenges

Following our design philosophy, **one Telegram bot manages all your challenges**:

```
┌─────────────────────────────────────────────────────────┐
│                  Your Telegram Bot                       │
│                                                          │
│  /list  →  Shows ALL challenges (work, fitness, etc.)   │
│  /switch → Change active challenge                       │
│  /streak → Check in to active challenge                  │
│  /insights → Cross-challenge patterns                    │
└─────────────────────────────────────────────────────────┘
                          │
                     reads/writes
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Single .streak/ folder                      │
│                                                          │
│  challenges/                                             │
│  ├── work-project     ← /switch work-project            │
│  ├── morning-fitness  ← /switch morning-fitness         │
│  ├── learn-rust       ← /switch learn-rust              │
│  └── daily-meditation ← /switch daily-meditation        │
└─────────────────────────────────────────────────────────┘
```

**Don't create separate bots for separate challenges.** That defeats the purpose of cross-challenge insights.

### Two Options

| Tool | Type | Best For |
|------|------|----------|
| `streak-notify.py` | One-way notifications | Simple reminders when check-ins are due |
| `streak-bot.py` | Interactive bot | Full mobile experience with buttons and check-in flow |

### Prerequisites

1. **Create a Telegram Bot:**
   - Open Telegram and message [@BotFather](https://t.me/BotFather)
   - Send `/newbot` and follow the prompts
   - Save the **bot token** (looks like `123456789:ABCdefGHIjklMNO...`)

2. **Get Your Chat ID:**
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - Save the **Id** number it returns (your chat ID)

3. **Start a chat with your bot:**
   - Find your bot by username (e.g., `@mystreak_bot`)
   - Send `/start` to it (required before bot can message you)

---

### Option A: Simple Notifications (No Dependencies)

Get reminders when check-ins are due/overdue. Zero dependencies, runs via cron.

**Setup:**

1. Add to `.streak/config.md`:
   ```markdown
   ## Notifications

   - **Notifications:** enabled
   - **Telegram Bot Token:** YOUR_BOT_TOKEN
   - **Telegram Chat ID:** YOUR_CHAT_ID
   ```

2. Test:
   ```bash
   python tools/streak-notify.py /path/to/.streak
   ```

3. Schedule with cron (daily at 9am):
   ```bash
   crontab -e
   # Add this line:
   0 9 * * * cd /path/to/project && python tools/streak-notify.py
   ```

---

### Option B: Interactive Bot (Full Mobile Experience)

Full Telegram bot with buttons, conversations, and interactive check-in flow.

**Bot Commands:**

| Telegram | Claude Code | Description |
|----------|-------------|-------------|
| `/start` | - | Main menu with buttons |
| `/streak` | `/streak` | Interactive check-in |
| `/list` | `/streak-list` | List challenges |
| `/stats` | `/streak-stats` | View statistics |
| `/insights` | `/streak-insights` | Cross-challenge patterns |
| `/new` | `/streak-new` | Create challenge (guided) |
| `/switch` | `/streak-switch` | Switch active challenge |

**Quick Start (Recommended):**

```bash
# Step 1: Create Telegram bot
# - Message @BotFather on Telegram
# - Send /newbot, follow prompts
# - Save the token

# Step 2: Get your chat ID
# - Message @userinfobot on Telegram
# - Save the Id number

# Step 3: Message your bot
# - Find your bot by username and send /start

# Step 4: Create .env file in your project root
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your-bot-token-here
ALLOWED_USERS=your-chat-id-here
TIMEZONE=Asia/Singapore
EOF

# Step 5: Deploy with one command
/streak-telegram
```

The `/streak-telegram` command will:
- Verify your .env file has the required credentials
- Copy bot files (streak-bot.py, Dockerfile, docker-compose.yml)
- Add .env to .gitignore for security
- Start the bot with docker-compose

**Manual Setup (Without the Command):**

```bash
# Copy files manually
cp ~/.claude-code/plugins/ccc-skills@ccc/streak/tools/streak-bot.py .
cp ~/.claude-code/plugins/ccc-skills@ccc/streak/tools/Dockerfile .
cp ~/.claude-code/plugins/ccc-skills@ccc/streak/tools/docker-compose.yml .

# Start
docker-compose up -d
```

**Without Docker:**

```bash
# 1. Install dependency
pip install python-telegram-bot==21.0

# 2. Set environment variables
export TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
export STREAK_PATH=./.streak
export ALLOWED_USERS=YOUR_CHAT_ID

# 3. Run
python tools/streak-bot.py
```

---

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Bot token from @BotFather |
| `STREAK_PATH` | No | `./.streak` | Path to .streak directory |
| `GIT_AUTO_SYNC` | No | `true` | Auto git pull/push for sync |
| `ALLOWED_USERS` | Yes* | `""` | Your chat ID (required for push notifications) |
| `NOTIFICATION_ENABLED` | No | `true` | Enable daily push notifications |
| `NOTIFICATION_HOUR` | No | `9` | Hour to send reminder (0-23) |
| `NOTIFICATION_MINUTE` | No | `0` | Minute to send reminder (0-59) |
| `TIMEZONE` | No | `UTC` | Your timezone (e.g., `Asia/Singapore`) |

*`ALLOWED_USERS` is required for the bot to send you push notifications.

---

### Push Notifications

The bot automatically sends you a reminder when challenges are due or overdue:

```
🔔 Streak Check-in Reminder

❗ Overdue:
• morning-workout (2d overdue)

📅 Due Today:
• learn-rust (streak: 5 days)

Tap /streak to check in

[✓ Check In Now]  [📋 List All]
```

**Configuration:**
- Default: 9:00 AM in your timezone
- Customize with `NOTIFICATION_HOUR`, `NOTIFICATION_MINUTE`, `TIMEZONE`
- Disable with `NOTIFICATION_ENABLED=false`

**Example for Singapore (9:30 AM):**
```bash
TIMEZONE=Asia/Singapore
NOTIFICATION_HOUR=9
NOTIFICATION_MINUTE=30
```

---

### Architecture: Both Interfaces Stay in Sync

```
┌─────────────────────────────────────────────────────────────┐
│                 Local .streak/ Files                         │
│                 (Source of Truth)                            │
└─────────────────────┬───────────────────────┬───────────────┘
                      │                       │
                 reads/writes            reads/writes
                      │                       │
                      ▼                       ▼
        ┌─────────────────────┐   ┌─────────────────────┐
        │   Claude Code       │   │   Telegram Bot      │
        │   (Terminal UI)     │   │   (Mobile UI)       │
        └─────────────────────┘   └─────────────────────┘
```

Both interfaces read/write the same `.streak/` files, so they stay in sync automatically.

**Optional GitHub Sync:** If you want to access from multiple devices, commit your `.streak/` folder to a git repo and enable `GIT_AUTO_SYNC=true`.

---

### Deployment Options

| Method | Persistence | Best For |
|--------|-------------|----------|
| **Docker Compose** | Survives terminal close, auto-restarts on reboot | Recommended for daily use |
| **systemd service** | Runs as system service | Linux servers |
| **PM2** | Process manager | If you use Node.js ecosystem |
| **Manual** | Stops when terminal closes | Testing only |

---

### Tools Reference

Files in `tools/` directory:

| File | Description |
|------|-------------|
| `streak-notify.py` | Simple notification script (no dependencies) |
| `streak-bot.py` | Full interactive Telegram bot |
| `Dockerfile` | Container image for the bot |
| `docker-compose.yml` | One-command deployment |
| `requirements.txt` | Python dependencies |
| `README.md` | Detailed tools documentation |

---

## License

MIT
