---
name: streak
description: Universal challenge tracker with flexible cadence, intelligent insights, and cross-challenge learning detection. Use when user wants to track any personal challenge - learning, habits, building, fitness, creative, or custom. Supports daily, weekly, or N-day check-ins with type-adaptive preferences, backlog, and context files.
---

# Streak

A universal, flexible challenge tracking system for Claude Code. Track any personal challenge with intelligent insights and cross-challenge learning detection.

**Works for any challenge type:** Learning, Building, Fitness, Creative, Habit, or Custom.

---

## Quick Start

**Trigger phrases -> Flows:**

| User Says | Flow |
|-----------|------|
| "new challenge", "start a streak", "track a goal" | Flow 1: New Challenge |
| "check in", "log progress", "update my streak" | Flow 2: Check-in |
| "list challenges", "show all challenges" | Flow 3: List |
| "switch to [name]", "change challenge" | Flow 4: Switch |
| "show stats", "my progress" | Flow 5: Statistics |
| "show insights", "cross-challenge" | Flow 6: Insights |
| "export calendar", "create reminders" | Flow 7: Calendar |
| "reset challenge", "start fresh" | Flow 8: Reset |
| "pause [name]", "put on hold" | Flow 9: Pause |
| "archive [name]", "shelve challenge" | Flow 10: Archive |
| "resume [name]", "reactivate" | Flow 11: Resume |
| "setup notifications", "telegram reminders" | Flow 12: Notifications |
| "setup telegram bot", "deploy telegram", "streak-telegram" | Flow 13: Telegram Bot Deploy |

---

## Data Storage

All data in `.streak/` folder:

```
.streak/
├── config.md                     # Global settings
├── active.md                     # Current challenge pointer
└── challenges/
    └── [challenge-id]/
        ├── challenge-config.md   # Metadata, goal, progress
        ├── challenge-log.md      # Progress log with summary
        ├── today.md              # Today's session context
        ├── backlog.md            # Ideas to try
        ├── preferences.md        # Type-adaptive setup
        ├── context.md            # Linked resources
        ├── insights.md           # Auto-generated insights
        └── sessions/
            └── session-XXX/
                └── notes.md      # Session notes
```

**File templates:** See `references/file-templates.md`

---

## Challenge Types

| Type | Best For | Key Questions |
|------|----------|---------------|
| **Learning** | Courses, books, skills | "Any aha moments?", "Progress on milestones?" |
| **Building** | Projects, shipping | "What did you ship?", "Any blockers?" |
| **Fitness** | Workouts, health | "What exercises?", "How did body feel?" |
| **Creative** | Art, writing, music | "What did you create?", "Any inspiration?" |
| **Habit** | Routines, consistency | "Did you complete it?", "How did it feel?" |
| **Custom** | Anything else | User-defined questions |

**Type details:** See `references/types.md`

---

## Flow 1: New Challenge

1. **Initialize** `.streak/` folder if needed
2. **Ask type:** Learning, Building, Fitness, Creative, Habit, or Custom
3. **Basic info:** Name, goal, cadence (daily/every N days/weekly)
4. **Type-specific questions:** See `references/types.md`
5. **Create files:** All templates pre-filled based on answers
6. **Set active** and confirm

**Detailed steps:** See `references/flows-detailed.md`

---

## Flow 2: Check-in

Two modes: **Pre-session** (planning) and **Post-session** (wrap-up)

### Pre-Session Mode

1. **Load context:** Read active challenge, config, today.md, preferences, backlog
2. **Show status:** Session #, streak, days since last, on-track/due/overdue
3. **Quick context:** Energy/time, specific focus or "surprise me", constraints
4. **Optional research:** For Building/Learning types
5. **Ideation:** Type-adaptive suggestions based on energy and backlog
6. **Prepare session:** Create session folder and notes template

### Post-Session Mode (user says "done")

1. **Wrap-up questions:** What worked on, how it went, what's next, key learning
2. **Type-specific questions:** See `references/types.md`
3. **Save:** Update session notes, challenge-config, challenge-log, backlog
4. **Generate insights:** Patterns, streaks, cross-challenge connections
5. **Check achievements:** See `references/achievements.md`
6. **Completion message:** Progress summary, achievements earned, insights

**Shortcuts during flow:**

| Say | Action |
|-----|--------|
| "Just research" | Only research step |
| "Skip to suggestions" | Skip research |
| "I know what I'm doing: [idea]" | Skip ideation |
| "Done" / "Finished" / "Back" | Jump to wrap-up |
| "Quick check-in" | Minimal logging |

**Detailed steps:** See `references/flows-detailed.md`

---

## Flow 3: List Challenges

Display challenges grouped by status, sorted by priority then recency.

**Default:** Show active + paused challenges
**With `--all` flag:** Include archived challenges

**Sorting order (within each group):**
1. Priority (higher number first, default 0)
2. Last check-in (most recent first)

**Display format:**

```
## Active Challenges
| | Name | Type | Pri | Streak | Last Check-in | Sessions |
|---|------|------|-----|--------|---------------|----------|
| * | python-courses | Learning | 10 | 5 days | 1 day ago | 3 |
|   | home-fitness | Fitness | 5 | 2 days | 2 days ago | 8 |

## Paused Challenges
|   | stories-to-novels | Writing | 0 | - | 10 days ago | 5 |

(2 archived challenges hidden - use --all to show)

* = Active challenge
Pri = Priority (edit in challenge-config.md)
```

**With `--all` flag, also show:**

```
## Archived Challenges
|   | old-project | Building | 0 | - | 2 months ago | 20 |
```

---

## Flow 4: Switch Challenge

1. Validate challenge exists
2. Update `active.md`
3. Load new challenge context
4. Confirm with status

---

## Flow 5: Statistics

Show for active challenge:
- **Progress:** Sessions, days since start, completion rate
- **Streaks:** Current, longest, average gap
- **Patterns:** Best day, best time, average length
- **Achievements:** Earned badges with dates
- **Backlog:** Completed, in-progress, pending items

---

## Flow 6: Cross-Challenge Insights

Analyze ALL challenges to detect:

1. **Compound Learning:** Skills from one challenge enabling another
2. **Skill Transfer:** Same concepts across challenges
3. **Cross-Domain:** Correlations between different types
4. **Patterns:** Best days, productivity trends
5. **Suggestions:** Personalized recommendations

**Insight formats:** See `references/achievements.md`

---

## Flow 7: Calendar Export

Generate `.ics` file with check-in reminders:
- Frequency based on cadence
- 30-day look-ahead (configurable)
- Works with Google, Apple, Outlook calendars

**Template:** See `references/file-templates.md`

---

## Flow 8: Reset Challenge

Archives current progress and starts fresh:
- Archives log as `challenge-log-archived-[date].md`
- Archives sessions folder
- Resets streak counters
- Keeps preferences, context, backlog intact

---

## Flow 9: Pause Challenge

Temporarily pause a challenge (plan to resume later):

1. Validate challenge exists and is active
2. Update `challenge-config.md`: set `**Status:** paused`
3. If pausing the **active** challenge:
   - List other active challenges
   - Prompt: "Paused [name]. Switch to another challenge?"
   - If yes, run Flow 4 (Switch)
4. Confirm: "Challenge [name] paused. Use `/streak-resume [name]` to reactivate."

**Use cases:** Seasonal challenges, focusing on other priorities, taking a break

---

## Flow 10: Archive Challenge

Move challenge to long-term storage (out of daily view):

1. Validate challenge exists and is not already archived
2. Update `challenge-config.md`: set `**Status:** archived`
3. If archiving the **active** challenge:
   - List other active challenges
   - Prompt: "Archived [name]. Switch to another challenge?"
   - If yes, run Flow 4 (Switch)
4. Confirm: "Challenge [name] archived. Use `/streak-list --all` to see archived challenges."

**Use cases:** Completed goals, abandoned challenges, historical record

---

## Flow 11: Resume Challenge

Bring a paused or archived challenge back to active:

1. Validate challenge exists and is paused or archived
2. Update `challenge-config.md`: set `**Status:** active`
3. Ask: "Make [name] your active challenge?"
   - If yes, update `active.md`
4. Check days since last check-in:
   - If 7+ days: Award :muscle: **Comeback** badge
5. Confirm: "Challenge [name] is now active. Ready to check in?"

**Note:** Resuming does NOT reset streak - it continues from where you left off.

---

## Flow 12: Notifications Setup

Set up push notifications for due/overdue check-ins via Telegram.

### Step 1: Create Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow prompts
3. Copy the **bot token** (looks like `123456789:ABCdefGHI...`)

### Step 2: Get Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your **chat ID** (a number like `123456789`)

### Step 3: Configure

Add to `.streak/config.md`:

```markdown
## Notifications (Optional)

- **Notifications:** enabled
- **Telegram Bot Token:** 123456789:ABCdefGHI...
- **Telegram Chat ID:** 123456789
```

### Step 4: Schedule Notifications

**Option A: Cron (Linux/Mac)**
```bash
# Run daily at 9am
0 9 * * * cd /path/to/project && python .streak/../tools/streak-notify.py
```

**Option B: GitHub Actions**
```yaml
# .github/workflows/streak-notify.yml
name: Streak Reminder
on:
  schedule:
    - cron: '0 9 * * *'  # 9am UTC daily
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python tools/streak-notify.py .streak
```

### Step 5: Test

```bash
python tools/streak-notify.py /path/to/.streak
```

**Detailed steps:** See `tools/streak-notify.py` header comments.

---

## Flow 13: Telegram Bot Deploy

One-command deployment of the interactive Telegram bot with Docker.

### Prerequisites (User Must Complete First)

1. **Create Telegram Bot:** Message @BotFather → `/newbot` → save token
2. **Get Chat ID:** Message @userinfobot → save Id number
3. **Message your bot:** Send `/start` to your bot (required before it can message you)
4. **Create `.env` file** in your project root:
   ```bash
   cat > .env << EOF
   TELEGRAM_BOT_TOKEN=your-bot-token
   ALLOWED_USERS=your-chat-id
   EOF
   ```
5. **Docker must be installed and running**

### Flow Steps

1. **Verify prerequisites:**
   - Check `.env` file exists in project root
   - Check `TELEGRAM_BOT_TOKEN` is set (not empty/placeholder)
   - Check Docker is available (`docker --version`)
   - If any missing, show specific instructions and stop

2. **Locate skill tools directory:**
   ```bash
   # Plugin location (typical paths)
   ~/.claude-code/plugins/ccc-skills@ccc/streak/tools/
   # Or within the ccc repo if running locally
   ```

3. **Copy bot files to project root:**
   ```bash
   cp [tools-dir]/streak-bot.py ./streak-bot.py
   cp [tools-dir]/Dockerfile ./Dockerfile
   cp [tools-dir]/docker-compose.yml ./docker-compose.yml
   ```

4. **Ensure .gitignore protects secrets:**
   ```bash
   # Add if not present
   echo ".env" >> .gitignore
   ```

5. **Start the bot:**
   ```bash
   docker-compose up -d --build
   ```

6. **Verify bot is running:**
   ```bash
   docker-compose ps
   docker-compose logs --tail=20
   ```

7. **Confirm to user:**
   ```
   ✅ Telegram bot deployed!

   Bot is running in Docker and will auto-restart on reboot.

   Commands:
   - docker-compose logs -f    # View logs
   - docker-compose restart    # Restart bot
   - docker-compose down       # Stop bot

   Open Telegram and send /start to your bot to test!
   ```

### Error Handling

| Issue | Response |
|-------|----------|
| No .env file | Show: "Create .env first with TELEGRAM_BOT_TOKEN and ALLOWED_USERS" |
| Empty token | Show: "TELEGRAM_BOT_TOKEN in .env is empty - add your bot token from @BotFather" |
| Docker not found | Show: "Docker not installed. Install from https://docker.com" |
| Docker not running | Show: "Docker daemon not running. Start Docker Desktop or run: sudo systemctl start docker" |
| Port conflict | Show: "Another service using the port. Stop other bots first: docker-compose down" |

---

## Achievements

### Streak Badges
| Badge | Requirement |
|-------|-------------|
| :fire: First Flame | 3-day streak |
| :fire::fire: On Fire | 7-day streak |
| :fire::fire::fire: Unstoppable | 30-day streak |
| :gem: Diamond Streak | 100-day streak |

### Milestone Badges
| Badge | Requirement |
|-------|-------------|
| :footprints: First Step | First check-in |
| :star: Dedicated | 10 sessions |
| :100: Centurion | 100 sessions |

### Special Badges
| Badge | Requirement |
|-------|-------------|
| :link: Connected | First cross-challenge insight |
| :muscle: Comeback | Resume after 7+ days |
| :mortar_board: Graduate | Complete challenge goal |

**Full list:** See `references/achievements.md`

---

## Error Handling

| Situation | Response |
|-----------|----------|
| No `.streak/` folder | "No challenges found. Say: Start a new challenge" |
| No active challenge | List available challenges, prompt to switch or create |
| Challenge not found | List available, suggest closest match |

---

## Design Philosophy

> **Your challenges are interconnected.** Your fitness affects your work. Your learning enables your building. Your habits shape your creativity.

Streak detects **cross-challenge connections** - patterns you might miss:
- "Morning workouts correlate with productive coding days"
- "Skills from 'Learn Rust' enabled progress in 'Build CLI Tools'"

**This is the unique value** - not just tracking, but understanding how challenges interact.

### One Place, All Challenges

Put ALL challenges in ONE `.streak/` folder, regardless of life area:

```
.streak/challenges/
├── work-project      # Work
├── morning-fitness   # Health
├── learn-rust        # Learning
└── daily-meditation  # Habit
```

Use `/streak-switch` to navigate. Use `/streak-insights` to discover connections.

**Don't create separate `.streak/` folders for different challenges.** That defeats the purpose.

---

## Best Practices

1. **Keep challenges together** - One `.streak/` folder for ALL challenges (work, health, learning, etc.)
2. **Be specific** in goals - "Complete Rustlings" > "Learn Rust"
3. **Start sustainable** - Every 2-3 days is easier than daily
4. **Use today.md** - Set context before sessions
5. **Maintain backlog** - Ideas for low-energy days
6. **Review insights** - Check weekly to see patterns
7. **Celebrate streaks** - Achievements are real motivation
8. **Reset guilt-free** - Archiving is progress, not failure
9. **Cross-pollinate** - Run multiple challenges to find connections

---

## Reference Files

For detailed content, see:

| File | Contains |
|------|----------|
| `references/file-templates.md` | All file templates and structures |
| `references/types.md` | Type-specific questions, preferences, ideation |
| `references/flows-detailed.md` | Step-by-step flow instructions |
| `references/achievements.md` | Achievement system, insight generation |

---

## Examples

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
