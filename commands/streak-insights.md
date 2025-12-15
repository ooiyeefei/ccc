---
description: Get cross-challenge insights, compound learning detection, and patterns
---

# Cross-Challenge Insights

Analyze all your challenges to find connections, compound learning, and patterns.

## Usage

```
/streak-insights
```

## What It Detects

### Compound Learning
Skills from one challenge enabling progress in another:
```
Your "Learn Rust" challenge (Session 12) where you learned async/await
directly enabled your "Build CLI Tools" challenge (Session 3) where
you built a concurrent file processor.
```

### Skill Transfer
Same concepts appearing across challenges:
```
"Error handling" appears in multiple challenges:
- Learn Rust: 8 sessions mention error handling
- Build CLI Tools: 3 sessions use Result types
```

### Cross-Domain Connections
Correlations between different challenge types:
```
Your morning workout (Fitness) correlates with higher productivity
in your coding sessions (Building).
```

### Patterns
- Best days for check-ins
- Check-in rate by challenge type
- Suggestions for improvement

## Instructions

Follow Flow 6: Cross-Challenge Insights from the `ccc-skills:streak` skill.

1. Scan all challenges in `.streak/challenges/`
2. Extract tags and key terms from each session
3. Find overlapping concepts across challenges
4. Detect skill transfer and compound learning
5. Analyze behavioral patterns
6. Generate personalized suggestions
