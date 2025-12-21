# Detailed Command Flows Reference

Step-by-step instructions for each streak command flow.

---

## Flow 1: Create New Challenge

### Step 1: Initialize .streak folder if needed

```
IF .streak/ folder does NOT exist:
  - Create .streak/ folder
  - Create .streak/config.md with defaults
  - Create .streak/challenges/ folder
```

### Step 2: Ask challenge type

```
Let's create a new challenge!

**What type of challenge?**

1. **Learning** - Master a skill, complete a course, read books
2. **Building** - Ship projects, code daily, create products
3. **Fitness** - Workouts, health goals, physical challenges
4. **Creative** - Art, writing, music, content creation
5. **Habit** - Form routines, track consistency, build discipline
6. **Custom** - Define your own structure

Which type? (1-6)
```

### Step 3: Basic info (all types)

```
**Challenge name:** (short, for folder - e.g., "learn-rust", "morning-workout")
**Goal:** (one sentence - what does success look like?)
**Cadence:** How often will you check in?
  - Daily
  - Every 2 days
  - Every 3 days
  - Weekly
  - Custom (specify)
```

### Step 4: Type-specific questions

See `references/types.md` for type-specific setup questions.

### Step 5: Create all challenge files

1. Generate challenge ID from name (lowercase, hyphens)
2. Create folder: `.streak/challenges/[challenge-id]/`
3. Create all files with type-adaptive content:
   - `challenge-config.md` - filled with metadata
   - `challenge-log.md` - empty template
   - `today.md` - empty template
   - `backlog.md` - empty or with initial items from user
   - `preferences.md` - **pre-filled based on type-specific answers**
   - `context.md` - filled with any linked resources mentioned
   - `insights.md` - empty template
   - `sessions/` - empty folder

4. Update `.streak/active.md` to point to new challenge

### Step 6: Confirm creation

```
Challenge "[name]" created!

Type: [type]
Goal: [goal]
Cadence: Every [X] [days/weeks]

Files created:
 challenge-config.md  (metadata)
 challenge-log.md     (progress tracking)
 today.md             (session context)
 backlog.md           (ideas to try)
 preferences.md       (your setup - pre-filled!)
 context.md           (linked resources)
 insights.md          (auto-generated insights)
 sessions/            (session notes folder)

Ready for your first check-in? (yes/no)
```

---

## Flow 2: Regular Check-in

Two modes:
- **Pre-session mode**: Planning what to do (ideation, suggestions)
- **Post-session mode**: Logging what was done (wrap-up)

Detect mode by asking or by user saying "done", "finished", "back", "completed".

### Step 1: Load active challenge

```
1. Read .streak/active.md to get active challenge
2. Read challenge-config.md for metadata
3. Read today.md for session context (if filled)
4. Read preferences.md for context
5. Read backlog.md for pending ideas
6. Calculate days since last check-in
7. Determine if on track, due, or overdue
```

### Step 2: Display status greeting

```
Hey! Time for your "[Challenge Name]" check-in.

Session [X] | Streak: [Y] days | Last: [Z] days ago | [Status]

Yesterday/Last session: [Brief summary from last entry, or "Fresh start!" if Session 1]
```

Status indicators:
- "On track!" - within cadence
- "Due today!" - exactly on cadence
- "You're [X] days overdue - let's get back on track!" - past cadence

### Step 3: Quick context check

```
Quick check before we start:

1. **Energy/time today?** (low ~30min / normal ~1hr / high 2hr+)
2. **Anything specific in mind?** (idea, topic, or "surprise me" / "feeling lucky")
3. **Any constraints?** (limitations, mood, equipment - or "none")
```

Update `today.md` with answers.

**If user says "surprise me" or "feeling lucky"** -> Go to Step 4 (Ideation)
**If user has specific idea** -> Go to Step 5 (Prepare Session)
**If user says "done", "finished", "back"** -> Go to Step 7 (Post-Session Wrap-up)

### Step 3.5: Research (Optional - Building/Learning types)

```
Want me to scan for relevant news/updates, or skip to suggestions?
```

**If yes:** Search for updates relevant to stack/topic, summarize 2-3 findings
**If skip:** Move directly to Step 4 (Ideation)

### Step 4: Ideation (Type-Adaptive)

See `references/types.md` for type-specific ideation suggestions.

Based on user's energy level, backlog, and challenge type, suggest 2-3 options.

### Step 5: Prepare Session

1. **Auto-create session folder:**
   ```
   mkdir -p sessions/session-XXX
   ```

2. **Update `today.md`** with selected focus

3. **Create `sessions/session-XXX/notes.md`** with starter template

4. **Announce:**
   ```
   Session [X] folder created. Go [build/learn/workout/create]!

   When you're done, come back and say "done" or "check in" again.
   ```

### Step 6: Flexible Commands (During Flow)

User can shortcut at any point:

| Say This | What Happens |
|----------|--------------|
| "Just research" | Only research step, save findings to notes |
| "Skip to suggestions" | Skip research, go to Ideation |
| "I know what I'm doing: [idea]" | Skip ideation, go to Prepare Session |
| "Done" / "Finished" / "Back" | Jump to Post-Session Wrap-up |
| "Continue from last session" | Load previous session context, continue |
| "Quick check-in" | Minimal logging, skip ideation |

### Step 7: Post-Session Wrap-up

Triggered when user says "done", "finished", "back", "completed".

**Base questions (all types):**
```
Welcome back! Let's log Session [X].

1. **What did you work on?** (brief summary)
2. **How did it go?** (wins, struggles, observations)
3. **What's next?** (for next session)
4. **Key learning?** (main takeaway - optional)
```

See `references/types.md` for type-specific wrap-up questions.

### Step 8: Save session

1. Update `sessions/session-XXX/notes.md` with wrap-up answers
2. Update `challenge-config.md`:
   - Increment check-in count
   - Update last check-in date
   - Calculate and update streak
3. Update `challenge-log.md`:
   - Add row to Summary table
   - Add detailed entry to log
4. Check for backlog items to mark complete
5. Update `backlog.md` if items mentioned as done

### Step 9: Generate insights

See `references/achievements.md` for insight generation details.

1. Pattern detection
2. Streak analysis
3. Cross-challenge connections (if multiple challenges)
4. Achievement check

Update `insights.md` with findings.

### Step 10: Display completion message

```
Session [X] logged!

Progress: [X] check-ins | Streak: [Y] days
[Achievement notification if earned]

[1-2 sentence insight if detected]

See you [in X days / tomorrow]!
```

---

## Flow 3: List Challenges

**Default:** Show active + paused challenges (hide archived)
**With `--all` flag:** Show all including archived

### Sorting Order (within each status group)

1. **Priority** (higher number first, default 0)
2. **Last check-in** (most recent first)

### Display Format

```
## Active Challenges
| | Name | Type | Pri | Streak | Last Check-in | Sessions |
|---|------|------|-----|--------|---------------|----------|
| * | python-courses | Learning | 10 | 5 days | 1 day ago | 3 |
|   | home-fitness | Fitness | 5 | 2 days | 2 days ago | 8 |
|   | daily-writing | Creative | 0 | 12 days | Today | 45 |

## Paused Challenges
|   | stories-to-novels | Writing | 0 | - | 10 days ago | 5 |

(2 archived challenges hidden - use --all to show)

* = Active challenge
Pri = Priority (edit in challenge-config.md to reorder)

Commands:
- "/streak-switch [name]" - Switch active challenge
- "/streak" - Check in to active challenge
- "/streak-pause [name]" - Pause a challenge
- "/streak-resume [name]" - Resume paused/archived challenge
```

### With `--all` Flag

Also shows archived section:

```
## Archived Challenges
|   | old-project | Building | 0 | - | 2 months ago | 20 |
|   | completed-course | Learning | 0 | - | 3 months ago | 30 |
```

---

## Flow 4: Switch Challenge

```
1. Validate challenge exists in .streak/challenges/
2. Update .streak/active.md with new challenge
3. Load new challenge context
4. Display: "Switched to '[name]'.
   Type: [type] | Streak: [X] days | Last: [Y] ago
   Ready to check in?"
```

---

## Flow 5: Progress Statistics

```
[Challenge Name] Statistics

---

Progress
- Total sessions: [X]
- Days since start: [Y]
- Completion rate: [X/expected]%
- Time invested: [if tracked]

Streaks
- Current streak: [X] days
- Longest streak: [Y] days
- Average gap: [Z] days

Patterns
- Most active day: [day of week]
- Best time: [morning/afternoon/evening]
- Average session length: [if tracked]

Achievements Earned
[List with dates]

Backlog Status
- Completed: [X] items
- In progress: [Y] items
- Pending: [Z] items

[Type-specific stats based on challenge type]
```

---

## Flow 6: Cross-Challenge Insights

Analyze ALL challenges and entries to find:

### 1. Compound Learning

Skills from one challenge enabling progress in another.

### 2. Skill Transfer

Same concepts appearing across challenges.

### 3. Cross-Domain Connections

Correlations between different challenge types.

### 4. Pattern Analysis

Behavioral patterns across all challenges.

### 5. Suggestions

Personalized recommendations based on all data.

See `references/achievements.md` for detailed insight formats.

---

## Flow 7: Calendar Export (Optional)

```
Calendar Export

I'll create reminder events for "[Challenge Name]":
- Frequency: Every [X] days
- Look-ahead: 30 days (or specify different)
- Reminder time: 9:00 AM (or specify different)

Generate .ics file? (yes/no)
```

Generate `.streak/[challenge-id]-reminders.ics`.

See `references/file-templates.md` for .ics template.

```
Created: .streak/[id]-reminders.ics

Import to your calendar:
- Google Calendar: Settings > Import & Export > Import
- Apple Calendar: File > Import
- Outlook: File > Open & Export > Import/Export

Reminders set for next 30 days.
```

---

## Flow 8: Reset Challenge

```
You're about to reset "[Challenge Name]".

This will:
- Archive current log as challenge-log-archived-[date].md
- Archive sessions to sessions-archived-[date]/
- Reset streak counters to 0
- Keep preferences.md and context.md intact
- Start fresh

Continue? (yes/no)
```

If yes:
1. Rename `challenge-log.md` to `challenge-log-archived-[ISO-date].md`
2. Rename `sessions/` to `sessions-archived-[ISO-date]/`
3. Create fresh `challenge-log.md`
4. Create fresh `sessions/` folder
5. Reset counters in `challenge-config.md`
6. Keep `preferences.md`, `context.md`, `backlog.md` intact
7. Confirm: "Challenge reset! Ready for Session 1?"

---

## Flow 9: Pause Challenge

Temporarily pause a challenge to focus on other priorities.

### Step 1: Validate

```
1. Check challenge exists in .streak/challenges/
2. Check current status is 'active' (not already paused/archived)
3. If not found: "Challenge '[name]' not found. Use /streak-list to see available challenges."
4. If already paused: "Challenge '[name]' is already paused."
```

### Step 2: Update Status

```
1. Open challenge-config.md
2. Change **Status:** active → paused
3. Save file
```

### Step 3: Handle Active Challenge

```
IF pausing the currently active challenge (from active.md):
  - List other active challenges
  - Prompt: "Challenge '[name]' paused. Switch to another challenge?"
  - Show available active challenges
  - If user selects one: Run Flow 4 (Switch)
  - If no other active challenges: "No other active challenges. Create a new one with /streak-new"
```

### Step 4: Confirm

```
Challenge "[name]" paused.

It will appear in the "Paused" section of /streak-list.
To resume: /streak-resume [name]
```

---

## Flow 10: Archive Challenge

Move challenge to long-term storage (historical record, completed goals).

### Step 1: Validate

```
1. Check challenge exists in .streak/challenges/
2. Check current status is not already 'archived'
3. If not found: "Challenge '[name]' not found."
4. If already archived: "Challenge '[name]' is already archived."
```

### Step 2: Update Status

```
1. Open challenge-config.md
2. Change **Status:** [active|paused] → archived
3. Save file
```

### Step 3: Handle Active Challenge

```
IF archiving the currently active challenge (from active.md):
  - List other active challenges
  - Prompt: "Challenge '[name]' archived. Switch to another challenge?"
  - Show available active challenges
  - If user selects one: Run Flow 4 (Switch)
  - If no other active challenges: "No other active challenges. Create a new one with /streak-new"
```

### Step 4: Confirm

```
Challenge "[name]" archived.

Archived challenges are hidden from /streak-list by default.
To see all: /streak-list --all
To restore: /streak-resume [name]
```

---

## Flow 11: Resume Challenge

Bring a paused or archived challenge back to active status.

### Step 1: Validate

```
1. Check challenge exists in .streak/challenges/
2. Check current status is 'paused' or 'archived'
3. If not found: "Challenge '[name]' not found."
4. If already active: "Challenge '[name]' is already active."
```

### Step 2: Update Status

```
1. Open challenge-config.md
2. Change **Status:** [paused|archived] → active
3. Save file
```

### Step 3: Calculate Time Away

```
1. Read last check-in date from challenge-config.md
2. Calculate days since last check-in
3. Store for step 4
```

### Step 4: Check for Comeback Achievement

```
IF days_since_last_checkin >= 7:
  - Award :muscle: **Comeback** badge
  - Add to achievements in challenge-config.md
  - Note: "Welcome back! You earned the Comeback badge."
```

### Step 5: Offer to Set Active

```
Prompt: "Make '[name]' your active challenge?"
- If yes: Update active.md to point to this challenge
- If no: Keep current active challenge
```

### Step 6: Confirm

```
Challenge "[name]" is now active!

[If comeback badge]: :muscle: Comeback badge earned!

Status: [X] sessions | Last check-in: [Y] days ago
Ready to check in? (/streak)
```

---

## Error Handling

### No .streak folder
```
No challenges found. Let's create your first one!

Say: "Start a new challenge"
```

### No active challenge
```
No active challenge set.

Your challenges:
[list challenges if any exist]

Say: "Switch to [name]"
Or: "Start a new challenge"
```

### Challenge not found
```
Challenge "[name]" not found.

Available challenges:
[list]

Did you mean: [closest match]?
```
