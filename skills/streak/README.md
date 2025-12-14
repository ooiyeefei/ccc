# Streak - Universal Challenge Tracker

Track any personal challenge with flexible cadence, intelligent insights, and cross-challenge learning detection.

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Quick Start

```bash
# Create your first challenge
/streak new

# Check in to your active challenge
/streak

# View all your challenges
/streak list
```

## Commands

| Command | Description |
|---------|-------------|
| `/streak` | Check-in to active challenge |
| `/streak new` | Create a new challenge (guided) |
| `/streak list` | List all challenges |
| `/streak switch [name]` | Switch active challenge |
| `/streak stats` | View progress and achievements |
| `/streak insights` | Cross-challenge insights |
| `/streak export-calendar` | Export .ics reminders (optional) |
| `/streak reset` | Archive and restart challenge |

## Challenge Types

### Built-in Types
- **Learning** - Master a skill, complete a course, read books
- **Building** - Ship projects, code daily, create products
- **Habit** - Form routines, track consistency, build discipline
- **Creative** - Art, writing, music, content creation
- **Custom** - Define your own structure and questions

### Flexible Cadence
Set your check-in frequency per challenge:
- Daily
- Every 2-3 days
- Weekly
- Custom interval

## Features

### Auto-Insights
At each check-in, Streak analyzes your progress and generates insights:
- Pattern detection (best days, common themes)
- Streak analysis (current vs longest)
- Personalized suggestions

### Cross-Challenge Connections
Streak detects when skills from one challenge help another:
```
Your "Learn Rust" challenge (Day 12) directly enabled
your "Build CLI Tools" challenge (Day 3) where you
shipped a concurrent file processor.
```

### Achievements
Earn badges as you progress:
- 🔥 **First Flame** - 3-day streak
- 🔥🔥 **On Fire** - 7-day streak
- 🔥🔥🔥 **Unstoppable** - 30-day streak
- 💎 **Diamond Streak** - 100-day streak
- 🎯 **First Step** - First check-in
- 📚 **Dedicated** - 10 check-ins
- 🔗 **Connected** - First cross-challenge insight

### Calendar Export (Optional)
Generate .ics files to import into any calendar:
```bash
/streak export-calendar
```
Works with Google Calendar, Apple Calendar, Outlook, etc.

## Data Storage

All data is stored locally in `.streak/` folder:
```
.streak/
├── config.json           # Global settings
├── active.json           # Current challenge pointer
└── challenges/
    └── [challenge-id]/
        ├── challenge.json  # Metadata
        ├── log.md          # Human-readable log
        └── entries/        # Check-in data
```

No external dependencies. No cloud sync required.

## Example Challenges

### 30 Days of Coding
```
Type: Building
Goal: Ship one micro-app per day
Cadence: Daily
```

### Read 12 Books This Year
```
Type: Learning
Goal: Finish 12 books this year
Cadence: Weekly
```

### Morning Meditation
```
Type: Habit
Goal: Meditate 10 minutes every morning
Cadence: Daily
```

### Daily Sketching
```
Type: Creative
Goal: Draw one sketch per day for 100 days
Cadence: Daily
```

## Tips

1. **Start small** - Every 2-3 days is more sustainable than daily
2. **Be specific** - "Learn Rust basics" > "Learn programming"
3. **Check insights** - Review weekly to see patterns
4. **Don't break streaks** - But if you do, reset guilt-free

## License

MIT
