# File Templates Reference

Complete file templates for all Streak challenge files. Claude generates these during challenge creation.

---

## Global Files

### config.md

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

### active.md

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

## Per-Challenge Files

### challenge-config.md

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
**Priority:** [0-100, higher = shown first in list, default 0]

---

## Progress

**Check-ins:** [X]
**Current Streak:** [X] days
**Longest Streak:** [X] days
**Status:** [active|paused|archived|completed]

---

## Type-Specific Info

<!-- Content varies by type - see type reference files -->

---

## Achievements

<!-- Earned achievements listed here -->
```

---

### challenge-log.md

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

### today.md

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

### backlog.md

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

### preferences.md

Universal structure with type-adaptive sections. Pre-filled during guided creation.

```markdown
# My Preferences

## Challenge Type
[auto-filled: learning | building | fitness | creative | habit | custom]

---

## [Primary Section - varies by type]

<!-- Section name and content depends on challenge type -->
<!-- See type-specific reference files for details -->

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

---

### context.md

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

### insights.md

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

### sessions/session-XXX/notes.md

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

## Calendar Export Template (.ics)

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
