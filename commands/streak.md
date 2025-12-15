---
description: Check in to your active challenge - log progress, get insights
---

# Streak Check-in

Check in to your active challenge to log progress, get insights, and maintain your streak.

## Usage

```
/streak
```

## What Happens

1. Load active challenge from `.streak/active.md`
2. Show status (streak count, days since last check-in, on track/overdue)
3. Ask check-in questions based on challenge type
4. Log progress to `challenge-log.md`
5. Generate insights
6. Update streak count

## Instructions

Follow the check-in flow defined in the `ccc-skills:streak` skill (Flow 2: Regular Check-in).

Key steps:
1. Read `.streak/active.md` to find active challenge
2. Read challenge config and calculate streak status
3. Ask energy/time and focus questions
4. If pre-session: offer ideation suggestions based on type
5. If post-session: ask wrap-up questions and log
6. Update files and generate insights

If no `.streak/` folder exists, prompt user to run `/streak-new` first.
