---
description: Switch to a different active challenge
---

# Switch Challenge

Switch to a different challenge as your active one.

## Usage

```
/streak-switch [challenge-name]
```

## Examples

```
/streak-switch learn-rust
/streak-switch morning-workout
```

## What Happens

1. Validate challenge exists in `.streak/challenges/`
2. Update `.streak/active.md` with new challenge
3. Display confirmation with challenge status

## Output

```
Switched to 'learn-rust'.
Type: Learning | Streak: 5 days | Last: 1 day ago
Ready to check in? Run /streak
```

## Instructions

1. Check if `[challenge-name]` exists in `.streak/challenges/`
2. If not found, list available challenges and suggest closest match
3. Update `.streak/active.md` to point to new challenge
4. Read new challenge's config and display status
