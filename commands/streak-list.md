---
description: List all your challenges with status, streak, and progress
---

# List Challenges

Show all challenges with their current status, streak count, and progress.

## Usage

```
/streak-list
```

## Output Format

```
Your Challenges:

| Status | Name | Type | Streak | Last Check-in | Progress |
|--------|------|------|--------|---------------|----------|
| * | learn-rust | Learning | 5 days | 1 day ago | 12 sessions |
|   | morning-workout | Fitness | 0 days | 8 days ago | 24 sessions |

* = Active challenge

Commands:
- /streak-switch [name] - Switch active challenge
- /streak - Check in to active challenge
- /streak-new - Create new challenge
```

## Instructions

1. Read `.streak/challenges/` directory
2. For each challenge, read `challenge-config.md`
3. Calculate days since last check-in
4. Format and display table
5. Mark active challenge with `*`
