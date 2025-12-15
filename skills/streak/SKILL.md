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

Display all challenges with status:

```
| Status | Name | Type | Streak | Last Check-in | Sessions |
|--------|------|------|--------|---------------|----------|
| * | learn-rust | Learning | 5 days | 1 day ago | 12 |
|   | morning-workout | Fitness | 0 days | 8 days ago | 24 |

* = Active
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

## Best Practices

1. **Be specific** in goals - "Complete Rustlings" > "Learn Rust"
2. **Start sustainable** - Every 2-3 days is easier than daily
3. **Use today.md** - Set context before sessions
4. **Maintain backlog** - Ideas for low-energy days
5. **Review insights** - Check weekly to see patterns
6. **Celebrate streaks** - Achievements are real motivation
7. **Reset guilt-free** - Archiving is progress, not failure
8. **Cross-pollinate** - Run multiple challenges to find connections

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
