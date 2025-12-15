# Achievements & Insights Reference

Achievement system, semantic detection, and insight generation.

---

## Streak Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| First Flame | 3-day streak | :fire: |
| On Fire | 7-day streak | :fire::fire: |
| Unstoppable | 30-day streak | :fire::fire::fire: |
| Diamond Streak | 100-day streak | :gem: |

---

## Milestone Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| First Step | First check-in | :footprints: |
| Getting Started | 5 sessions | :seedling: |
| Dedicated | 10 sessions | :star: |
| Committed | 25 sessions | :star2: |
| Centurion | 100 sessions | :100: |
| Multi-tasker | 3 active challenges | :juggling_person: |

---

## Special Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| Connected | First cross-challenge insight | :link: |
| Compound Learner | 5 connected sessions | :brain: |
| Graduate | Complete challenge goal | :mortar_board: |
| Comeback | Resume after 7+ days | :muscle: |

---

## Recording Achievements

Record in `challenge-config.md`:

```markdown
## Achievements
- :footprints: First Step - [date]
- :fire: First Flame - [date]
- :fire::fire: On Fire - [date]
```

Announce when earned:

```
Achievement Unlocked!
:fire: First Flame - You've maintained a 3-day streak!
```

---

## Semantic Connection Detection

At each check-in, after saving:

### 1. Extract Tags

From current session:
- Key nouns and concepts
- Technical terms, exercises, techniques
- Skills mentioned

### 2. Scan Other Challenges

For matching tags:
- Read recent sessions (last 30 days)
- Look for overlapping concepts

### 3. Score Connections

| Connection Type | Strength |
|----------------|----------|
| Direct mention: "used X from Y challenge" | Strong |
| Same skill/concept across types | Moderate |
| Thematic similarity | Weak |

### 4. Store Connections

- In session notes
- Update `insights.md`

---

## Insight Generation

Generate after each check-in:

### Pattern Detection

```
Patterns Detected:
- Best day for check-ins: Tuesday (87% rate)
- Most productive time: Morning sessions
- Average session length: 45 minutes
```

### Streak Analysis

```
Streak Analysis:
- Current streak: 5 days
- Longest streak: 12 days
- Average gap: 1.5 days
```

### Cross-Challenge Connections

```
Compound Learning Detected:

Your "Learn Rust" challenge (Session 12) where you learned async/await
directly enabled your "Build CLI Tools" challenge (Session 3) where
you built a concurrent file processor.
```

### Skill Transfer

```
Skill Transfer:

"Error handling" appears in multiple challenges:
- Learn Rust: 8 sessions mention error handling
- Build CLI Tools: 3 sessions use Result types
- Your error handling skills are compounding!
```

### Cross-Domain Insights

```
Cross-Domain Insight:

Your morning workout (Fitness) correlates with higher productivity
in your coding sessions (Building). Sessions after workouts show
30% more completed items.
```

### Suggestions

```
Suggestions:

Based on your progress:
1. Consider combining Rust + CLI into a single project challenge
2. Your fitness streak is strong - apply same trigger pattern to writing
3. Weekend check-ins are weak - consider adjusting cadence or batching
```

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

Status indicators:
- "On track!" - within cadence
- "Due today!" - exactly on cadence
- "You're [X] days overdue" - past cadence
