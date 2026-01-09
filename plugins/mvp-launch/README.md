# MVP Launch Plugin

A Claude Code plugin for web app MVP launch readiness analysis. Based on the "Realistic MVP Launch Checklist (from building 30+ apps)" methodology.

## Philosophy

> "Don't overbuild. Just make it stable, usable, and something people can trust."

This plugin helps you identify what's actually needed for launch—nothing more, nothing less.

---

## Installation

### Option 1: Symlink (Development)

```bash
# From your Claude Code settings directory
ln -s /path/to/ccc/plugins/mvp-launch ~/.claude/plugins/mvp-launch
```

### Option 2: Copy

```bash
cp -r /path/to/ccc/plugins/mvp-launch ~/.claude/plugins/
```

---

## Usage

### Command

```
/launch-check
```

This runs the full 4-phase gap analysis on your codebase.

### What Happens

1. **DISCOVER** - Claude searches your codebase for implementations
2. **UNDERSTAND** - Reads key files to assess completeness
3. **CONFIRM** - Presents findings for your validation
4. **REPORT** - Generates prioritized gap analysis

### Output

Analysis saved to `.pm/gaps/[YYYY-MM-DD]-mvp-launch-analysis.md` with:
- Overall readiness score (0-100)
- Per-area assessment (10 areas)
- Prioritized action items (P0/P1/P2)
- Evidence with file paths

---

## The 10-Point Checklist

| # | Area | What Matters |
|---|------|--------------|
| 1 | **Stripe Setup** | Webhooks, trials, failed payments, live keys tested |
| 2 | **Mobile-First** | Real device testing (not just browser resize) |
| 3 | **Smooth Onboarding** | Minimal steps, fast first win |
| 4 | **AI Stability** | Error handling, retries, edge cases |
| 5 | **Critical Emails** | Welcome, trial-ending, failed payment |
| 6 | **Error Logging** | Catch bugs before users notice |
| 7 | **Feedback Loop** | Simple form or tool to collect issues |
| 8 | **Auth & Roles** | Secure pages, password resets, basic roles |
| 9 | **Custom Domain** | Own domain with HTTPS (no dev URLs) |
| 10 | **Database & Backups** | Real DB, automated backups |

---

## Scoring

| Score | Status |
|-------|--------|
| 85-100 | Launch Ready |
| 70-84 | Nearly Ready (fix P0 blockers) |
| 50-69 | Needs Work |
| <50 | Not Ready |

---

## Example Output

```markdown
# MVP Launch Readiness Gap Analysis

**Overall Score:** 87/100 - Nearly Ready

## Summary
| Area | Score | Status |
|------|-------|--------|
| Stripe Setup | 10/10 | ✅ |
| Mobile-First | 7/10 | ⚠️ |
| Onboarding | 8/10 | ✅ |
...

## Gaps (Prioritized)

### P0 - Launch Blockers
None ✅

### P1 - Should Fix Before Launch
1. Add PWA manifest for mobile installability
2. Test on real iOS device (Safari issues)

### P2 - Nice to Have
1. Add first-win guidance in onboarding
```

---

## Plugin Structure

```
mvp-launch/
├── .claude-plugin/
│   └── plugin.json           # Plugin metadata
├── commands/
│   └── launch-check.md       # /launch-check command
├── agents/
│   └── mvp-gap-analyst.md    # 4-phase analysis agent
├── skills/
│   └── mvp-launch/
│       ├── SKILL.md          # 10-point checklist criteria
│       └── references/
│           ├── search-patterns.md   # Discovery patterns
│           └── stripe-testing.md    # Stripe verification
└── README.md
```

---

## When to Use

- Before launching your MVP
- After major feature additions
- When onboarding new team members (shows what's implemented)
- Periodic health checks

---

## Credits

Based on insights from:
- [Realistic MVP Launch Checklist (Reddit r/replit)](https://www.reddit.com/r/replit/comments/1lak77y/realistic_mvp_launch_checklist_from_building_30/)
- 30+ app launches experience

---

## License

MIT
