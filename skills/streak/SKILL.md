---
name: streak
description: Universal challenge tracker with flexible cadence, intelligent insights, and cross-challenge learning detection. Use when user wants to track any personal challenge - learning, habits, building, fitness, creative, or custom. Supports daily, weekly, or N-day check-ins with type-adaptive preferences, backlog, and context files.
---

# Streak

A universal, flexible challenge tracking system for Claude Code. Track any personal challenge with intelligent insights and cross-challenge learning detection.

**Works for any challenge type:** Learning, Building, Fitness, Creative, Habit, or Custom.

---

## Quick Start

**How to use this skill:**

Users trigger this skill through natural language. Claude will invoke `ccc-skills:streak` when it detects challenge tracking intent.

**Trigger phrases → Flows:**

| User Says | Flow to Execute |
|-----------|-----------------|
| "new challenge", "start a streak", "track a goal" | Flow 1: New Challenge Creation |
| "check in", "log progress", "update my streak" | Flow 2: Regular Check-in |
| "list challenges", "show all challenges" | Flow 3: List Challenges |
| "switch to [name]", "change challenge" | Flow 4: Switch Challenge |
| "show stats", "my progress" | Flow 5: Progress Statistics |
| "show insights", "cross-challenge" | Flow 6: Cross-Challenge Insights |
| "export calendar", "create reminders" | Flow 7: Calendar Export |
| "reset challenge", "start fresh" | Flow 8: Reset Challenge |

---

## Data Storage

All data stored in `.streak/` folder in user's current working directory.

### Folder Structure
```
.streak/
├── config.md                     # Global settings
├── active.md                     # Points to current challenge
└── challenges/
    └── [challenge-id]/
        ├── challenge-config.md   # Challenge metadata, goal, type
        ├── challenge-log.md      # Progress log (summary + detailed)
        ├── today.md              # Today's session context
        ├── backlog.md            # Ideas/things to try
        ├── preferences.md        # My setup (type-adaptive)
        ├── context.md            # Linked resources/projects
        ├── insights.md           # Auto-generated insights
        └── sessions/
            └── session-XXX/      # Per check-in
                └── notes.md      # Session notes
```

---

## File Definitions

Each file has a specific purpose. Claude generates these based on challenge type during the "New Challenge Creation" flow.

### config.md (Global)

```markdown
# Streak Configuration

Global settings for all challenges.

---

## Settings
- **Default cadence:** daily
- **Achievements:** enabled
- **Auto-insights:** enabled

## Preferences
- **Preferred check-in time:** [morning/afternoon/evening]
```

---

### active.md (Global)

```markdown
# Active Challenge

Points to the currently active challenge.

---

## Current Challenge

**Name:** [Challenge Name]
**Path:** `challenges/[challenge-id]`
**Type:** [learning|building|fitness|creative|habit|custom]
**Started:** [YYYY-MM-DD]
**Goal:** [One sentence goal]

---

## Quick Actions
- "Check in" - Log progress now
- "Switch to [name]" - Change active challenge
- "List challenges" - See all challenges
```

---

### challenge-config.md (Per Challenge)

```markdown
# Challenge Config

Metadata for this challenge.

---

## Challenge Info

**Name:** [Challenge Name]
**Type:** [learning|building|fitness|creative|habit|custom]
**Goal:** [One sentence goal]
**Cadence:** Every [X] [days/weeks]
**Started:** [YYYY-MM-DD]

---

## Progress

**Check-ins:** [X]
**Current Streak:** [X] days
**Longest Streak:** [X] days
**Status:** [active|paused|completed]

---

## Type-Specific Info

<!-- Content varies by type - see Type-Adaptive Sections below -->

---

## Achievements

<!-- Earned achievements listed here -->
```

---

### challenge-log.md (Per Challenge)

```markdown
# [Challenge Name] Progress Log

**Goal:** [goal]
**Started:** [date]
**Cadence:** Every [X] [days/weeks]

---

## Summary

| # | Date | Summary | Streak | Key Learning |
|---|------|---------|--------|--------------|

---

## Detailed Log

<!-- Detailed entries added below -->

### Session [X] - [Date]
**Summary:** [what was done]
**Reflection:** [how it went]
**Next:** [what's planned next]
**Key Learning:** [main takeaway]
```

---

### today.md (Per Challenge)

Session context - works universally across all challenge types.

```markdown
# Today's Session

## Date
[YYYY-MM-DD]

---

## Energy & Time
[low ~30min | normal ~1hr | high 2hr+]

---

## Today's Focus
[specific thing to work on, or "open to suggestions"]

---

## Constraints
[any limitations today]
<!--
  Tech: "only have laptop, no external monitor"
  Fitness: "lower back tight, skip deadlifts"
  Creative: "feeling uninspired, want prompts"
  Habit: "traveling, limited space"
-->

---

## Notes
[anything else relevant]
```

---

### backlog.md (Per Challenge)

Ideas and things to try - universal concept, type-specific content.

```markdown
# Backlog

Ideas and things to try for this challenge.

---

## High Priority
- [ ] [Item] - [Why/Notes]

## Medium Priority
- [ ] [Item] - [Why/Notes]

## Someday/Maybe
- [ ] [Item] - [Why/Notes]

---

## Completed
- [x] [Item] - [Done on Session X]
```

**Type-specific backlog examples:**

| Type | Backlog Contains |
|------|------------------|
| Learning | Tutorials, courses, concepts, books to explore |
| Building | Features, apps, tools, integrations to build |
| Fitness | Workouts, exercises, challenges, routines to try |
| Creative | Prompts, themes, styles, techniques to explore |
| Habit | Variations, stacking ideas, environment experiments |

---

### preferences.md (Per Challenge)

Universal structure with type-adaptive sections. This file is pre-filled during guided creation based on user's answers.

```markdown
# My Preferences

## Challenge Type
[auto-filled: learning | building | fitness | creative | habit | custom]

---

## [Primary Section - varies by type]

<!-- Section name and content depends on challenge type -->

---

## [Secondary Section - varies by type]

<!-- Section name and content depends on challenge type -->

---

## Session Preferences

- **Preferred time:** [morning / afternoon / evening / flexible]
- **Typical duration:** [15min / 30min / 1hr / 2hr+]
- **Energy approach:** [low-key / moderate / intense]

---

## Notes
<!-- Anything else relevant to preferences -->
```

#### Type-Adaptive Sections for preferences.md

**LEARNING Type:**
```markdown
## Topics & Resources
- **Learning:** [topic/skill]
- **Resources:** [courses, books, tutorials]
- **Tools:** [apps, platforms, IDEs]

## Learning Style
- **Approach:** [videos / reading / hands-on / mixed]
- **Note-taking:** [method if any]
- **Practice:** [how you reinforce learning]
```

**BUILDING Type:**
```markdown
## Stack & Tools
- **Languages:** [languages used]
- **Frameworks:** [frameworks/libraries]
- **Tools:** [IDE, AI tools, deployment]

## Development Style
- **Approach:** [ship fast / careful / TDD]
- **Deployment:** [where you deploy/share]
- **Documentation:** [how much you document]
```

**FITNESS Type:**
```markdown
## Workout Style & Equipment
- **Focus:** [strength / cardio / flexibility / weight / mixed]
- **Equipment:** [gym / home / bodyweight / specific equipment]
- **Workout types:** [HIIT, weights, yoga, running, etc.]

## Location & Schedule
- **Where:** [gym name, home, outdoor, etc.]
- **Best days:** [weekdays / weekends / specific days]
- **Rest days:** [which days]
```

**CREATIVE Type:**
```markdown
## Medium & Style
- **Medium:** [writing / art / music / video / etc.]
- **Style:** [any specific style or approach]
- **Tools:** [software, instruments, materials]

## Inspiration & Sharing
- **Inspiration sources:** [artists, platforms, nature, etc.]
- **Share platform:** [where you publish/share]
- **Feedback:** [how you get feedback]
```

**HABIT Type:**
```markdown
## Routine Setup
- **The habit:** [specific action]
- **Trigger:** [when/where/after what]
- **Duration:** [how long each time]

## Environment & Rewards
- **Environment:** [where you do it, setup needed]
- **Reward:** [how you reward yourself]
- **Accountability:** [partner, app, community]
```

**CUSTOM Type:**
```markdown
## My Setup
<!-- User defines their own sections -->

## Custom Fields
<!-- User-defined tracking fields -->
```

---

### context.md (Per Challenge)

Linked resources and context - universal structure, type-specific content.

```markdown
# My Context

Resources and connections related to this challenge.

---

## Linked Resources
<!-- Projects, courses, gyms, platforms, portfolios, etc. -->

---

## Tools & Apps
<!-- Specific tools, apps, software being used -->

---

## People
<!-- Accountability partners, mentors, communities, trainers -->

---

## Reference Links
<!-- Useful URLs, documentation, inspiration -->
```

**Type-specific context examples:**

| Type | Context Contains |
|------|------------------|
| Learning | Courses enrolled, books, study groups, mentors |
| Building | Projects, repos, deployment targets, collaborators |
| Fitness | Gyms, fitness apps, trainers, workout buddies |
| Creative | Portfolios, platforms, collaborators, galleries |
| Habit | Environment setup, reminder apps, accountability partners |

---

### insights.md (Per Challenge)

Auto-generated insights from progress analysis.

```markdown
# [Challenge Name] Insights

Auto-generated insights from your progress.

---

## Latest Insights

_Insights are generated after each check-in._

---

## Patterns

_Behavioral patterns detected across sessions._

---

## Cross-Challenge Connections

_Connections to other challenges will appear here._

---

## Suggestions

_Personalized suggestions based on your progress._
```

---

### sessions/session-XXX/notes.md (Per Session)

```markdown
# Session [X] Notes

**Date:** [YYYY-MM-DD]
**Challenge:** [Challenge Name]

---

## Summary
[What was done this session]

---

## Details
[Detailed notes, code snippets, links, etc.]

---

## Decisions Made
<!-- Key decisions during this session -->

---

## Issues & Blockers
<!-- Any problems encountered -->

---

## Key Learning
[Main takeaway from this session]

---

## Next Steps
[What to do next session]
```

---

## Command Flows

### Flow 1: Create New Challenge

**Step 1: Initialize .streak folder if needed**

```
IF .streak/ folder does NOT exist:
  - Create .streak/ folder
  - Create .streak/config.md with defaults
  - Create .streak/challenges/ folder
```

**Step 2: Ask challenge type**

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

**Step 3: Basic info (all types)**

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

**Step 4: Type-specific questions**

For **LEARNING** type:
```
**What are you learning?** (topic/skill)
**Any resources?** (courses, books, tutorials - optional)
**How do you learn best?** (videos / reading / hands-on / mixed)
**Any milestones?** (checkpoints to celebrate - optional)
```

For **BUILDING** type:
```
**What are you building?** (project type or specific project)
**Tech stack?** (languages, frameworks - optional)
**Where will you deploy/share?** (optional)
**Any linked projects?** (existing codebases - optional)
```

For **FITNESS** type:
```
**What's the goal?** (strength / cardio / weight loss / flexibility / general)
**Equipment access?** (gym / home / bodyweight / specific equipment)
**Preferred workout types?** (HIIT, weights, yoga, running, etc.)
**Any constraints?** (injuries, limitations - optional)
```

For **CREATIVE** type:
```
**What medium?** (writing, art, music, video, etc.)
**Any theme or focus?** (optional)
**Tools you use?** (software, instruments, materials - optional)
**Where will you share?** (platform - optional)
```

For **HABIT** type:
```
**What habit specifically?** (the exact action)
**Trigger:** When/where/after what will you do it?
**How long per session?** (duration)
**What's your reward?** (optional)
```

For **CUSTOM** type:
```
**What are you tracking?** (describe the challenge)
**What fields do you want to track per session?**
**What questions should I ask at each check-in?**
```

**Step 5: Create all challenge files**

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

**Step 6: Confirm creation**

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

### Flow 2: Regular Check-in

The check-in flow has two modes:
- **Pre-session mode**: Planning what to do (ideation, suggestions)
- **Post-session mode**: Logging what was done (wrap-up)

Detect mode by asking or by user saying "done", "finished", "back", "completed".

---

**Step 1: Load active challenge**

```
1. Read .streak/active.md to get active challenge
2. Read challenge-config.md for metadata
3. Read today.md for session context (if filled)
4. Read preferences.md for context
5. Read backlog.md for pending ideas
6. Calculate days since last check-in
7. Determine if on track, due, or overdue
```

**Step 2: Display status greeting**

```
Hey! Time for your "[Challenge Name]" check-in.

Session [X] | Streak: [Y] days | Last: [Z] days ago | [Status]

Yesterday/Last session: [Brief summary from last entry, or "Fresh start!" if Session 1]
```

Status indicators:
- "On track!" - within cadence
- "Due today!" - exactly on cadence
- "You're [X] days overdue - let's get back on track!" - past cadence

**Step 3: Quick context check**

```
Quick check before we start:

1. **Energy/time today?** (low ~30min / normal ~1hr / high 2hr+)
2. **Anything specific in mind?** (idea, topic, or "surprise me" / "feeling lucky")
3. **Any constraints?** (limitations, mood, equipment - or "none")
```

Update `today.md` with answers.

**If user says "surprise me" or "feeling lucky"** → Go to Step 4 (Ideation)
**If user has specific idea** → Go to Step 5 (Prepare Session)
**If user says "done", "finished", "back"** → Go to Step 7 (Post-Session Wrap-up)

---

**Step 3.5: Research (Optional - Building/Learning types)**

For BUILDING and LEARNING challenges, offer optional research:

```
Want me to scan for relevant news/updates, or skip to suggestions?
```

**If yes (Building type):**
- Search for recent updates in the tech stack mentioned in preferences
- Look for new tools, libraries, or patterns relevant to backlog items
- Summarize 2-3 interesting findings

**If yes (Learning type):**
- Check for new resources on the topic
- Find recent articles, tutorials, or discussions
- Summarize relevant updates

**If skip:** Move directly to Step 4 (Ideation)

---

**Step 4: Ideation (Type-Adaptive Suggestions)**

Based on user's energy level, backlog, and challenge type, suggest 2-3 options.

**For BUILDING type:**
```
Based on your energy ([level]) and backlog, here are some options:

**Option 1: [Name]** 🟢 [matches energy]
- What: [Description from backlog or generated]
- Why today: [Alignment with energy/constraints]

**Option 2: [Name]** 🟡 [stretch goal]
- What: [Description]
- Why today: [Quick win or exploration]

**From your backlog:** [Relevant pending item]

Which one resonates? Or describe something else.
```

**For LEARNING type:**
```
Based on your energy and progress, here's what I suggest:

**Option 1: Continue [current topic]** 🟢
- Pick up from: [last session summary]
- Estimated time: [matches energy]

**Option 2: Try something new** 🟡
- From backlog: [pending topic/resource]
- Why: [variety or prerequisite complete]

**Option 3: Review & consolidate** 🔵
- Revisit: [recent learnings]
- Good for: low energy days

What sounds good?
```

**For FITNESS type:**
```
Based on your energy ([level]) and body state:

**Option 1: [Workout type]** 🟢 [matches energy]
- Focus: [muscle group or cardio type]
- Duration: ~[time]
- Equipment: [what's needed]

**Option 2: [Alternative]** 🟡
- Focus: [different approach]
- Good for: [reason - recovery, variety, etc.]

**Rest day option:** If your body needs it, rest is progress too.

[If constraints mentioned: "Noted: [constraint] - suggestions adjusted accordingly"]

Which workout today?
```

**For CREATIVE type:**
```
Here's some inspiration for today:

**Prompt 1:** [Creative prompt based on backlog/themes]
**Prompt 2:** [Different angle or technique to try]
**Continue:** [Pick up from last session's work]

Or tell me a theme/mood and I'll suggest something specific.
```

**For HABIT type:**
```
Ready for your [habit name]?

**Standard:** Do it as planned ([trigger] → [habit] → [reward])
**Variation:** Try [slight modification from backlog]
**Stack it:** Combine with [another habit or activity]

Or if today's different, tell me what's up.
```

**For CUSTOM type:**
Use user-defined ideation questions from challenge setup.

---

**Step 5: Prepare Session**

Once user picks an idea or states their focus:

1. **Auto-create session folder:**
   ```
   mkdir -p sessions/session-XXX
   ```

2. **Update `today.md`** with selected focus:
   ```markdown
   ## Today's Focus
   [Selected idea/topic]

   ## Plan
   [Brief plan from ideation]
   ```

3. **Create `sessions/session-XXX/notes.md`** with starter template:
   ```markdown
   # Session [X] Notes

   **Date:** [YYYY-MM-DD]
   **Challenge:** [Challenge Name]
   **Focus:** [Selected idea]

   ---

   ## Plan
   [From ideation]

   ## Progress
   <!-- Update as you work -->

   ## Decisions Made
   <!-- Key decisions during this session -->

   ## Issues & Blockers
   <!-- Any problems encountered -->
   ```

4. **Announce:**
   ```
   Session [X] folder created. Go [build/learn/workout/create]!

   When you're done, come back and say "done" or "check in" again.
   ```

---

**Step 6: Flexible Commands (During Flow)**

User can shortcut at any point:

| Say This | What Happens |
|----------|--------------|
| "Just research" | Only research step, save findings to notes |
| "Skip to suggestions" | Skip research, go to Ideation |
| "I know what I'm doing: [idea]" | Skip ideation, go to Prepare Session |
| "Done" / "Finished" / "Back" | Jump to Post-Session Wrap-up |
| "Continue from last session" | Load previous session context, continue |
| "Quick check-in" | Minimal logging, skip ideation |

---

**Step 7: Post-Session Wrap-up**

Triggered when user says "done", "finished", "back", "completed", or explicitly asks for wrap-up.

**Ask wrap-up questions:**

Base questions (all types):
```
Welcome back! Let's log Session [X].

1. **What did you work on?** (brief summary)
2. **How did it go?** (wins, struggles, observations)
3. **What's next?** (for next session)
4. **Key learning?** (main takeaway - optional)
```

Type-specific additions:

**LEARNING:**
```
- **Any aha moments?**
- **Progress on resources/milestones?**
```

**BUILDING:**
```
- **What did you ship/complete?**
- **Any blockers?**
- **Code/links to share?** (optional)
```

**FITNESS:**
```
- **What workout/exercises?**
- **How did your body feel?**
- **Any PRs or progress?** (optional)
```

**CREATIVE:**
```
- **What did you create?**
- **Any inspiration or themes?**
- **Link to work?** (optional)
```

**HABIT:**
```
- **Did you complete the habit?** (yes / no / partial)
- **How did it feel?**
- **Trigger work well?** (optional)
```

---

**Step 8: Save session**

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

**Step 9: Generate insights**

After every check-in, analyze:

1. **Pattern detection:**
   - Best days/times for check-ins
   - Common themes in summaries
   - Progress velocity

2. **Streak analysis:**
   - Current vs longest streak
   - Typical gap between check-ins

3. **Cross-challenge connections** (if multiple challenges):
   - Scan other challenge entries for related tags/topics
   - Detect skill transfer or compound learning

4. **Achievement check:**
   - First check-in (First Step)
   - 3-day streak (First Flame)
   - 7-day streak (On Fire)
   - 30-day streak (Unstoppable)
   - 100-day streak (Diamond Streak)
   - Milestone completion

Update `insights.md` with findings.

**Step 10: Display completion message**

```
Session [X] logged!

Progress: [X] check-ins | Streak: [Y] days
[Achievement notification if earned]

[1-2 sentence insight if detected]

See you [in X days / tomorrow]!
```

---

### Flow 3: List Challenges

```
Your Challenges:

| Status | Name | Type | Streak | Last Check-in | Progress |
|--------|------|------|--------|---------------|----------|
| * | learn-rust | Learning | 5 days | 1 day ago | 12 sessions |
|   | morning-workout | Fitness | 0 days | 8 days ago | 24 sessions |
|   | daily-writing | Creative | 12 days | Today | 45 sessions |

* = Active challenge

Commands:
- "Switch to [name]" - Switch active challenge
- "Check in" - Check in to active challenge
- "New challenge" - Create new challenge
```

---

### Flow 4: Switch Challenge

```
1. Validate challenge exists in .streak/challenges/
2. Update .streak/active.md with new challenge
3. Load new challenge context
4. Display: "Switched to '[name]'.
   Type: [type] | Streak: [X] days | Last: [Y] ago
   Ready to check in?"
```

---

### Flow 5: Progress Statistics

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

### Flow 6: Cross-Challenge Insights

Analyze ALL challenges and entries to find:

**1. Compound Learning**
```
Compound Learning Detected

Your "Learn Rust" challenge (Session 12) where you learned async/await
directly enabled your "Build CLI Tools" challenge (Session 3) where
you built a concurrent file processor.

Timeline:
- Session 15 (Rust): Learned tokio basics
- Session 18 (Rust): Built async file reader
- Session 5 (CLI): Applied to production tool
```

**2. Skill Transfer**
```
Skill Transfer

"Error handling" appears in multiple challenges:
- Learn Rust: 8 sessions mention error handling
- Build CLI Tools: 3 sessions use Result types
- Your error handling skills are compounding!
```

**3. Cross-Domain Connections**
```
Cross-Domain Insight

Your morning workout (Fitness) correlates with higher productivity
in your coding sessions (Building). Sessions after workouts show
30% more completed items.
```

**4. Pattern Analysis**
```
Patterns Across Challenges

- Tuesdays are your most productive day (87% check-in rate)
- Weekends see 40% fewer check-ins across all challenges
- Morning sessions have higher completion rates
- Learning challenges sustain longer streaks than habit challenges
```

**5. Suggestions**
```
Suggestions

Based on your progress:
1. Consider combining Rust + CLI into a single project challenge
2. Your fitness streak is strong - apply same trigger pattern to writing
3. Weekend check-ins are weak - consider adjusting cadence or batching
```

---

### Flow 7: Calendar Export (Optional)

```
Calendar Export

I'll create reminder events for "[Challenge Name]":
- Frequency: Every [X] days
- Look-ahead: 30 days (or specify different)
- Reminder time: 9:00 AM (or specify different)

Generate .ics file? (yes/no)
```

Generate `.streak/[challenge-id]-reminders.ics`:

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//streak//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:[Challenge Name] Check-ins
BEGIN:VEVENT
UID:[generated-uuid]
DTSTART:[next-due-date]T090000
DTEND:[next-due-date]T093000
SUMMARY:Streak: [Challenge Name]
DESCRIPTION:Time for your [type] challenge check-in!\n\nGoal: [goal]\nCurrent streak: [X] days\n\nSay: "Check in to my streak"
RRULE:FREQ=DAILY;INTERVAL=[cadence];COUNT=[30/cadence]
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Streak reminder
TRIGGER:-PT30M
END:VALARM
END:VEVENT
END:VCALENDAR
```

```
Created: .streak/[id]-reminders.ics

Import to your calendar:
- Google Calendar: Settings > Import & Export > Import
- Apple Calendar: File > Import
- Outlook: File > Open & Export > Import/Export

Reminders set for next 30 days.
```

---

### Flow 8: Reset Challenge

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
| Getting Started | 5 sessions | :seedling: |
| Dedicated | 10 sessions | :star: |
| Committed | 25 sessions | :star2: |
| Centurion | 100 sessions | :100: |
| Multi-tasker | 3 active challenges | :juggling_person: |

### Special Achievements
| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| Connected | First cross-challenge insight | :link: |
| Compound Learner | 5 connected sessions | :brain: |
| Graduate | Complete challenge goal | :mortar_board: |
| Comeback | Resume after 7+ days | :muscle: |

Record achievements in `challenge-config.md`:
```markdown
## Achievements
- :footprints: First Step - [date]
- :fire: First Flame - [date]
```

---

## Semantic Connection Detection

At each check-in, after saving:

1. **Extract tags** from current session:
   - Key nouns and concepts
   - Technical terms, exercises, techniques
   - Skills mentioned

2. **Scan other challenges** for matching tags:
   - Read recent sessions (last 30 days)
   - Look for overlapping concepts

3. **Score connections**:
   - Direct mention: "used X from Y challenge" = strong
   - Same skill/concept across types: moderate
   - Thematic similarity: weak

4. **Store connections** in session notes and update `insights.md`

---

## Overdue Detection

Calculate at each check-in:

```
daysSinceLast = today - lastCheckIn
expectedGap = cadenceFrequency
overdueBy = max(0, daysSinceLast - expectedGap)

if overdueBy > 0:
  display: "You're [X] days overdue - let's get back on track!"
  offer: "Want to do a quick catch-up?"
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

---

## Best Practices

1. **Be specific** in your goal - "Complete Rustlings exercises" > "Learn Rust"
2. **Start sustainable** - Every 2-3 days is more sustainable than daily
3. **Use today.md** - Set context before sessions for better focus
4. **Maintain backlog** - Keep ideas flowing for low-energy days
5. **Review insights** - Check weekly to see patterns
6. **Celebrate streaks** - Achievements are real motivation
7. **Reset guilt-free** - Archiving is progress, not failure
8. **Cross-pollinate** - Run multiple challenges to find connections

---

## Example Challenges

### 30 Days of AI/ML (Building)
```
Type: Building
Goal: Ship one AI-powered micro-app per day
Cadence: Daily
Stack: Python, TypeScript, Claude Code
Deploy: Vercel, Hugging Face
```

### Learn Rust (Learning)
```
Type: Learning
Goal: Complete Rustlings and build a CLI tool
Cadence: Every 2 days
Resources: Rustlings, The Rust Book
Style: Hands-on with reading
```

### Morning Workout (Fitness)
```
Type: Fitness
Goal: Build consistent strength training habit
Cadence: Daily (with rest days)
Equipment: Home gym - dumbbells, pull-up bar
Focus: Push/pull/legs split
```

### Daily Sketching (Creative)
```
Type: Creative
Goal: Draw one sketch per day for 100 days
Cadence: Daily
Medium: Digital art (Procreate)
Share: Instagram
```

### Morning Meditation (Habit)
```
Type: Habit
Goal: Meditate 10 minutes every morning
Cadence: Daily
Trigger: After coffee, before email
Duration: 10 minutes
Reward: Peaceful start to day
```

### Read 12 Books (Learning)
```
Type: Learning
Goal: Finish 12 books this year
Cadence: Weekly
Resources: Kindle, local library
Milestones: 3, 6, 9, 12 books
```
