# GitHub Issue Template for Feature Requests

Template used by `/pm file` when creating GitHub Issues. Issues are designed to be **spec-kit ready**—containing all context needed for `/speckit.specify`.

---

## Full Template

```markdown
## Problem Statement

[Why this feature is needed - the core pain point]

[Evidence of pain: user reviews, support tickets, competitor success]

## User Stories

- As a [user type], I want [goal] so that [benefit]
- As a [user type], I want [goal] so that [benefit]

## Competitor Evidence

| Competitor | Has Feature? | Implementation Notes |
|------------|--------------|---------------------|
| [Name] | Yes/No | [How they do it, what users say] |
| [Name] | Yes/No | [How they do it, what users say] |

## WINNING Score: XX/60

| Criterion | Score | Notes |
|-----------|-------|-------|
| Pain Intensity | X/10 | [Evidence] |
| Market Timing | X/10 | [Evidence] |
| Execution Capability | X/10 | [Reasoning] |
| Strategic Fit | X/10 | [Reasoning] |
| Revenue Potential | X/10 | [Reasoning] |
| Competitive Moat | X/10 | [Reasoning] |
| **TOTAL** | **XX/60** | [FILE/WAIT/SKIP] |

## Constraints

- [Technical constraint 1]
- [Business constraint 1]
- [Timeline constraint if any]

## Acceptance Criteria

- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
- [ ] [Measurable criterion 3]

## Out of Scope

- [What this feature explicitly does NOT include]
- [Future enhancements to consider separately]

## Technical Notes

[Any architecture considerations, dependencies, or implementation hints from `/pm analyze`]

---

*Created by PM Skill | Source: gap-analysis-YYYY-MM-DD | Ready for spec-kit*
```

---

## Section Guidelines

### Problem Statement

**Purpose:** Establish WHY this feature matters.

**Good example:**
```markdown
## Problem Statement

Users working late at night experience eye strain from our bright UI.
This is especially problematic for developers (our primary users) who
often code in dark environments.

Evidence:
- 47 G2 reviews mention "dark mode" or "eye strain"
- 3 support tickets per week request dark mode
- Competitor X launched dark mode 6 months ago; reviews praise it
```

**Bad example:**
```markdown
## Problem Statement

We should add dark mode because competitors have it.
```

### User Stories

**Purpose:** Define WHO benefits and HOW.

**Format:** `As a [user type], I want [goal] so that [benefit]`

**Good example:**
```markdown
## User Stories

- As a developer, I want a dark theme so that I can code comfortably at night
- As a user with light sensitivity, I want reduced brightness so that I can use the app without discomfort
- As a power user, I want theme customization so that I can match my system preferences
```

**Avoid:** Generic users, vague benefits
```markdown
- As a user, I want dark mode so that the app is better  # Too vague
```

### Competitor Evidence

**Purpose:** Show market validation and implementation patterns.

**Good example:**
```markdown
## Competitor Evidence

| Competitor | Has Feature? | Implementation Notes |
|------------|--------------|---------------------|
| Notion | Yes | System-aware auto-switching, custom accent colors. Users love "just works" approach. |
| Linear | Yes | Dark-first design, no light mode originally. Developer favorite. |
| Slack | Yes | Per-workspace setting, some users confused. Suggest per-user instead. |
```

**Include:**
- How competitors implemented it
- What users say about their implementation
- Lessons to learn (good and bad)

### WINNING Score

**Purpose:** Show prioritization reasoning.

**Copy directly from gap analysis.** Include notes for each criterion so future readers understand the score.

### Constraints

**Purpose:** Set realistic boundaries.

**Types:**
- **Technical:** "Must work with existing CSS variable system"
- **Business:** "Cannot change brand colors"
- **Timeline:** "Needed before Q2 enterprise push"
- **Legal:** "Must comply with accessibility standards"

### Acceptance Criteria

**Purpose:** Define "done" measurably.

**Good criteria are:**
- Specific (not vague)
- Measurable (can verify pass/fail)
- Testable (QA can validate)

**Good example:**
```markdown
## Acceptance Criteria

- [ ] User can toggle between light and dark themes from settings
- [ ] Theme preference persists across sessions
- [ ] System preference is detected and applied by default
- [ ] All text meets WCAG AA contrast ratios in both themes
- [ ] No flash of wrong theme on page load
```

**Bad example:**
```markdown
- [ ] Dark mode works well
- [ ] Users like it
```

### Out of Scope

**Purpose:** Prevent scope creep.

**Good example:**
```markdown
## Out of Scope

- Custom theme colors (future feature request)
- Per-page theme settings
- Scheduled theme switching (e.g., dark at night)
- High contrast mode (separate accessibility feature)
```

### Technical Notes

**Purpose:** Give implementers a head start.

**Include:**
- Relevant architecture from `/pm analyze`
- Known dependencies
- Suggested approach (if obvious)
- Performance considerations

---

## gh CLI Command

When creating issue via `gh`:

```bash
gh issue create \
  --title "Dark Mode Support" \
  --body "$(cat <<'EOF'
## Problem Statement
...
EOF
)" \
  --label "pm:feature-request" \
  --label "winning:high" \
  --label "priority:now"
```

---

## Manual Creation Fallback

If `gh` CLI unavailable, output the template as markdown and prompt:

```
GitHub CLI not available. Please create issue manually:

1. Go to: https://github.com/[owner]/[repo]/issues/new
2. Title: [Feature Name]
3. Body: [Paste content below]
4. Labels: pm:feature-request, winning:high, priority:now

---
[Full issue body markdown]
---
```

---

## spec-kit Handoff

The issue IS the handoff to spec-kit. When ready to build:

1. Open the GitHub Issue
2. Copy relevant sections (Problem, User Stories, Constraints, Acceptance Criteria)
3. Run `/speckit.specify` with the context
4. spec-kit generates detailed spec from there

The footer line reminds users: `*Ready for spec-kit*`
