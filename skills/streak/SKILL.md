---
name: streak
description: Universal challenge tracker with flexible cadence, intelligent insights, and cross-challenge learning detection. Use when user wants to track any personal challenge - learning, habits, building, creative, or custom. Supports daily, weekly, or N-day check-ins.
---

# Streak

A universal, flexible challenge tracking system for Claude Code. Track any personal challenge with intelligent insights and cross-challenge learning detection.

---

## Quick Start

**Commands:**
| Command | Description |
|---------|-------------|
| `/streak` | Check-in to active challenge |
| `/streak new` | Create a new challenge |
| `/streak list` | List all challenges |
| `/streak switch [name]` | Switch active challenge |
| `/streak stats` | View progress and achievements |
| `/streak insights` | Cross-challenge insights |
| `/streak export-calendar` | Export .ics reminders (optional) |
| `/streak reset` | Archive and restart challenge |

---

## Data Storage

All data stored in `.streak/` folder in user's current working directory.

### Folder Structure
```
.streak/
├── config.json              # Global settings
├── active.json              # Points to current challenge
└── challenges/
    └── [challenge-id]/
        ├── challenge.json   # Challenge metadata
        ├── log.md           # Human-readable progress log
        ├── insights.md      # Generated insights
        └── entries/
            └── entry-XXX.json
```

---

## Command Flows

### Flow 1: `/streak new` - Create New Challenge

**Step 1: Detect existing .streak folder**

```
IF .streak/ folder does NOT exist:
  - Create .streak/ folder
  - Create .streak/config.json with defaults
  - Create .streak/challenges/ folder
```

**Step 2: Ask challenge type**

Present to user:
```
Let's create a new challenge!

**What type of challenge?**

1. **Learning** - Master a skill, complete a course, read books
2. **Building** - Ship projects, code daily, create products
3. **Habit** - Form routines, track consistency, build discipline
4. **Creative** - Art, writing, music, content creation
5. **Custom** - Define your own structure

Which type? (1-5)
```

**Step 3: Gather details based on type**

For ALL types, ask:
```
**Challenge name:** (short, for folder - e.g., "learn-rust")
**Goal:** (one sentence - what does success look like?)
**Cadence:** How often will you check in?
  - Daily
  - Every 2 days
  - Every 3 days
  - Weekly
  - Custom (specify)
```

For LEARNING type, also ask:
```
**What are you learning?** (topic/skill)
**Resources?** (optional - courses, books, tutorials)
**Milestones?** (optional - checkpoints to celebrate)
```

For BUILDING type, also ask:
```
**What are you building?** (project type or name)
**Tech stack?** (optional)
**Ship target?** (optional - where will you deploy/share)
```

For HABIT type, also ask:
```
**What habit?** (specific action)
**Trigger?** (when/where will you do it)
**Duration?** (optional - how long each session)
```

For CREATIVE type, also ask:
```
**Medium?** (writing, art, music, video, etc.)
**Theme?** (optional - any focus area)
**Share where?** (optional - platform to publish)
```

For CUSTOM type, also ask:
```
**What fields do you want to track?** (list them)
**What questions should I ask at each check-in?**
```

**Step 4: Create challenge files**

1. Generate challenge ID from name (lowercase, hyphens)
2. Create folder: `.streak/challenges/[challenge-id]/`
3. Create `challenge.json`:

```json
{
  "id": "[generated-id]",
  "name": "[user's name]",
  "type": "[learning|building|habit|creative|custom]",
  "goal": "[user's goal]",
  "cadence": {
    "frequency": [number],
    "unit": "[days|weeks]"
  },
  "created": "[ISO date]",
  "lastCheckIn": null,
  "checkInCount": 0,
  "currentStreak": 0,
  "longestStreak": 0,
  "status": "active",
  "typeFields": {
    // Type-specific fields from user
  },
  "customQuestions": [],
  "achievements": [],
  "tags": []
}
```

4. Create `log.md`:

```markdown
# [Challenge Name] Progress Log

**Goal:** [goal]
**Started:** [date]
**Cadence:** Every [X] [days/weeks]

---

## Summary

| # | Date | Summary | Streak |
|---|------|---------|--------|

---

## Entries

<!-- Entries will be added below -->
```

5. Create `insights.md`:

```markdown
# [Challenge Name] Insights

Auto-generated insights from your progress.

---

## Latest Insights

_No insights yet. Complete a few check-ins to generate insights._

---

## Connections

_Cross-challenge connections will appear here._
```

6. Create/update `.streak/active.json`:

```json
{
  "challengeId": "[challenge-id]",
  "challengePath": "challenges/[challenge-id]"
}
```

**Step 5: Confirm creation**

```
Challenge "[name]" created!

Type: [type]
Goal: [goal]
Cadence: Every [X] [days/weeks]

Ready for your first check-in? (yes/no)
```

If yes, proceed to check-in flow.

---

### Flow 2: `/streak` - Regular Check-in

**Step 1: Load active challenge**

```
1. Read .streak/active.json to get active challenge
2. Read .streak/challenges/[id]/challenge.json
3. Calculate days since last check-in
4. Determine if on track, due, or overdue
```

**Step 2: Display status greeting**

```
Hey! Time for your "[Challenge Name]" check-in.

[Status indicator based on cadence]

Examples:
- "Day 5 | Streak: 3 | Last: 1 day ago | On track!"
- "Day 12 | Streak: 0 | Last: 4 days ago | You're 2 days overdue - let's get back on track!"
- "Day 1 | First check-in! Let's go!"
```

**Step 3: Ask check-in questions**

Base questions (all types):
```
1. **What did you work on?** (brief summary)
2. **How did it go?** (any wins or struggles)
3. **What's next?** (for next check-in)
```

Type-specific additions:

LEARNING:
```
- **Any aha moments or key learnings?**
- **Progress on milestones?**
```

BUILDING:
```
- **What did you ship/complete?**
- **Any blockers?**
```

HABIT:
```
- **Did you complete the habit?** (yes/no/partial)
- **How did it feel?**
```

CREATIVE:
```
- **What did you create?**
- **Any inspiration or themes?**
```

**Step 4: Save entry**

Create `.streak/challenges/[id]/entries/entry-[XXX].json`:

```json
{
  "entryNumber": [sequential],
  "date": "[ISO date]",
  "dayOfChallenge": [calculated],
  "summary": "[from question 1]",
  "reflection": "[from question 2]",
  "nextSteps": "[from question 3]",
  "typeSpecific": {
    // Type-specific answers
  },
  "mood": "[detected or asked]",
  "tags": "[auto-extracted keywords]",
  "connections": []
}
```

**Step 5: Update challenge.json**

```json
{
  "lastCheckIn": "[now]",
  "checkInCount": [+1],
  "currentStreak": [calculated],
  "longestStreak": [max of current and longest]
}
```

**Step 6: Update log.md**

Append to Summary table:
```
| [#] | [date] | [summary] | [streak] |
```

Append to Entries section:
```markdown
### Entry [#] - [Date]
**Summary:** [summary]
**Reflection:** [reflection]
**Next:** [next steps]
[Type-specific fields if relevant]
```

**Step 7: Generate insights**

After every check-in, analyze:

1. **Pattern detection:**
   - Best days/times for check-ins
   - Common themes in summaries
   - Progress velocity

2. **Streak analysis:**
   - Current vs longest streak
   - Days typically missed

3. **Cross-challenge connections** (if multiple challenges):
   - Scan other challenge entries for related tags/topics
   - Detect skill transfer or compound learning

4. **Achievement check:**
   - First check-in
   - 3-day streak
   - 7-day streak
   - 30-day streak
   - Milestone completion

**Step 8: Display completion message**

```
Check-in logged!

Progress: [X] check-ins | Streak: [Y] days
[Achievement notification if earned]

[1-2 sentence insight if detected]

See you [in X days / tomorrow]!
```

---

### Flow 3: `/streak list` - List Challenges

Read all folders in `.streak/challenges/` and display:

```
Your Challenges:

| Status | Name | Type | Streak | Last Check-in |
|--------|------|------|--------|---------------|
| * | learn-rust | Learning | 5 days | 1 day ago |
|   | daily-writing | Creative | 0 days | 8 days ago |
|   | morning-run | Habit | 12 days | Today |

* = Active challenge

Commands:
- /streak switch [name] - Switch active challenge
- /streak - Check in to active challenge
```

---

### Flow 4: `/streak switch [name]` - Switch Challenge

```
1. Validate challenge exists in .streak/challenges/
2. Update .streak/active.json with new challenge ID
3. Confirm: "Switched to '[name]'. Ready to check in?"
```

---

### Flow 5: `/streak stats` - Progress Statistics

```
[Challenge Name] Statistics

Progress
- Total check-ins: [X]
- Days since start: [Y]
- Completion rate: [X/expected]%

Streaks
- Current streak: [X] days
- Longest streak: [Y] days
- Average streak: [Z] days

Patterns
- Most active day: [day of week]
- Best time: [if tracked]
- Total time invested: [if tracked]

Achievements
[List earned achievements with dates]

Milestones
[Progress on user-defined milestones if any]
```

---

### Flow 6: `/streak insights` - Cross-Challenge Insights

Analyze ALL challenges and entries to find:

**1. Compound Learning**
Detect when skills/knowledge from one challenge enabled success in another.

```
Compound Learning Detected

Your "Learn Rust" challenge (Entry 12) where you learned async/await
directly enabled your "Build CLI Tools" challenge (Entry 3) where
you built a concurrent file processor.

Timeline:
- Day 15 (Rust): Learned tokio basics
- Day 18 (Rust): Built async file reader
- Day 5 (CLI): Applied to production tool
```

**2. Skill Transfer**
Detect same techniques across different challenges.

```
Skill Transfer

"Error handling" appears in multiple challenges:
- Learn Rust: 8 entries mention error handling
- Build CLI Tools: 3 entries use Result types
- Your error handling skills are compound!
```

**3. Pattern Analysis**
Cross-challenge behavioral patterns.

```
Patterns Across Challenges

- Tuesdays are your most productive day (87% check-in rate)
- Weekends see 40% fewer check-ins
- Learning challenges have higher completion than habit challenges
```

**4. Suggestions**
Based on analysis, suggest:
- New challenges combining skills
- Adjustments to struggling challenges
- Connections to explore

---

### Flow 7: `/streak export-calendar` - Calendar Export (Optional)

```
Calendar Export

I'll create reminder events for "[Challenge Name]":
- Frequency: Every [X] days
- Look-ahead: 30 days (or specify)
- Time: 9:00 AM (or specify)

Generate .ics file? (yes/no)
```

If yes, generate `.streak/[challenge-id]-reminders.ics`:

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//challenge-streak//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:[Challenge Name] Reminders
BEGIN:VEVENT
UID:[generated-uuid]
DTSTART:[next-due-date]T090000
DTEND:[next-due-date]T093000
SUMMARY:Streak Check-in: [Challenge Name]
DESCRIPTION:Time for your [type] challenge check-in!\n\nGoal: [goal]\nCurrent streak: [X] days\n\nRun: /streak
RRULE:FREQ=DAILY;INTERVAL=[cadence];COUNT=[30/cadence]
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Streak reminder
TRIGGER:-PT30M
END:VALARM
END:VEVENT
END:VCALENDAR
```

Tell user:
```
Created: .streak/[id]-reminders.ics

Import to your calendar:
- Google Calendar: Settings > Import & Export > Import
- Apple Calendar: File > Import
- Outlook: File > Open & Export > Import/Export

Events created for the next 30 days.
```

---

### Flow 8: `/streak reset` - Reset Challenge

```
You're about to reset "[Challenge Name]".

This will:
- Archive current log as log-archived-[date].md
- Reset streak counters to 0
- Start fresh with same settings

Your entries will be preserved in the archive.

Continue? (yes/no)
```

If yes:
1. Rename `log.md` to `log-archived-[ISO-date].md`
2. Create fresh `log.md` from template
3. Reset counters in `challenge.json`
4. Confirm: "Challenge reset! Ready for Day 1?"

---

## Achievements System

### Streak Achievements
| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| First Flame | 3-day streak | :fire: |
| On Fire | 7-day streak | :fire::fire: |
| Unstoppable | 30-day streak | :fire::fire::fire: |
| Diamond Streak | 100-day streak | :gem: |

### Milestone Achievements
| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| First Step | First check-in | :footprints: |
| Dedicated | 10 check-ins | :star: |
| Centurion | 100 check-ins | :100: |
| Multi-tasker | 3 active challenges | :juggling_person: |

### Special Achievements
| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| Connected | First cross-challenge insight | :link: |
| Compound Learner | 5 connected entries | :brain: |
| Graduate | Complete challenge goal | :mortar_board: |

When achievement earned, add to `challenge.json`:
```json
{
  "achievements": [
    {"id": "first-flame", "earned": "[date]"}
  ]
}
```

---

## Semantic Connection Detection

### How to Detect Connections

At each check-in, after saving entry:

1. **Extract tags** from current entry:
   - Key nouns and concepts
   - Technical terms
   - Skills mentioned

2. **Scan other challenges** for matching tags:
   - Read recent entries (last 30 days)
   - Look for overlapping concepts

3. **Score connections**:
   - Direct mention: "used X from Y challenge" = strong
   - Same skill/concept: moderate
   - Thematic similarity: weak

4. **Store connections** in entry:
```json
{
  "connections": [
    {
      "targetChallenge": "learn-rust",
      "targetEntry": 12,
      "connectionType": "builds-on",
      "concept": "error handling",
      "strength": "strong"
    }
  ]
}
```

5. **Update insights.md** when strong connections found

---

## Overdue Detection

Calculate at each `/streak` command:

```
expectedCheckIns = floor(daysSinceStart / cadenceFrequency)
actualCheckIns = checkInCount
overdueBy = max(0, expectedCheckIns - actualCheckIns)

if overdueBy > 0:
  display: "You're [X] check-ins behind schedule"
  offer: "Want to do a quick catch-up entry?"
```

---

## Error Handling

### No .streak folder
```
No challenges found. Would you like to create your first challenge?
Run: /streak new
```

### No active challenge
```
No active challenge set. Your challenges:
[list challenges]

Switch with: /streak switch [name]
Or create new: /streak new
```

### Challenge not found
```
Challenge "[name]" not found.

Available challenges:
[list]
```

---

## Best Practices for Users

1. **Be specific** in your goal - "Learn Rust basics" > "Learn programming"
2. **Start small** with cadence - Daily is ambitious, every 2-3 days is sustainable
3. **Review insights** weekly to see patterns
4. **Celebrate streaks** - Achievements are real motivation
5. **Reset guilt-free** - Archiving is progress, not failure

---

## Example Challenges

### 30 Days of AI/ML
```
Type: Building
Goal: Ship one AI-powered micro-app per day
Cadence: Daily
```

### Read 12 Books in 2024
```
Type: Learning
Goal: Finish 12 books this year
Cadence: Weekly
Milestones: 3 books, 6 books, 9 books, 12 books
```

### Morning Meditation
```
Type: Habit
Goal: Meditate 10 minutes every morning
Cadence: Daily
Trigger: After coffee, before email
```

### Daily Sketching
```
Type: Creative
Goal: Draw one sketch per day for 100 days
Cadence: Daily
Share: Instagram
```
