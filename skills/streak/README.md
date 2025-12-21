# Streak - Universal Challenge Tracker

Track any personal challenge with flexible cadence, intelligent insights, and cross-challenge learning detection.

**Works for any challenge type:** Learning, Building, Fitness, Creative, Habit, or Custom.

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

## License

MIT
