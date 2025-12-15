---
description: Create a new challenge with guided setup (learning, building, fitness, habit, creative, custom)
---

# Create New Challenge

Create a new challenge with guided discovery. Supports multiple types with type-adaptive preferences.

## Usage

```
/streak-new
```

## Challenge Types

| Type | Best For |
|------|----------|
| **Learning** | Courses, skills, books |
| **Building** | Projects, shipping, coding |
| **Fitness** | Workouts, health goals |
| **Creative** | Art, writing, music |
| **Habit** | Routines, consistency |
| **Custom** | Define your own |

## What Happens

1. Initialize `.streak/` folder if needed
2. Ask challenge type
3. Ask basic info (name, goal, cadence)
4. Ask type-specific questions
5. Create all challenge files with pre-filled preferences
6. Set as active challenge
7. Offer first check-in

## Instructions

Follow the creation flow defined in the `ccc-skills:streak` skill (Flow 1: Create New Challenge).

Create these files in `.streak/challenges/[challenge-id]/`:
- `challenge-config.md` - metadata, goal, progress tracking
- `challenge-log.md` - progress log with summary table
- `today.md` - session context template
- `backlog.md` - ideas and things to try
- `preferences.md` - pre-filled based on type-specific answers
- `context.md` - linked resources
- `insights.md` - auto-generated insights template
- `sessions/` - folder for session notes
