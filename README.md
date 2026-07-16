# Claude Code Custom Plugins & Skills

Custom plugins and skills for [Claude Code](https://github.com/anthropics/claude-code).

## Available

| Name | Type | Description | Install Command |
|------|------|-------------|-----------------|
| [bash-safety-guard](./plugins/bash-safety-guard) | Plugin (hook) | Fail-closed PreToolUse bash guard: blocks prod-data loss, credential exfiltration, and catastrophic `rm -rf` before they run — even under `--dangerously-skip-permissions` | `/plugin install bash-safety-guard@ccc` |
| [deckling](./plugins/deckling) | Plugin | Generate PPTX presentations using Anthropic Platform Skills API | `/plugin install deckling@ccc` |
| [daily-chief](./plugins/daily-chief) | Plugin + Pi package | User-invoked Plan today workflow with browser device login, local preview, and explicit remote apply | `/plugin install daily-chief@ccc` |
| [mvp-launch](./plugins/mvp-launch) | Plugin | MVP launch readiness checker with `/launch-check` command | `/plugin install mvp-launch@ccc` |
| [product-management](./plugins/product-management) | Plugin | AI-native PM: competitor research, gap analysis, WINNING prioritization | `/plugin install product-management@ccc` |
| [rethink-surveys](./plugins/rethink-surveys) | Plugin | Survey design grounded in research methods (Jarrett, Dillman, Tourangeau) with design/critique/app-scaffold commands + bundled MCP server | `/plugin install rethink-surveys@ccc` |
| [agentic-toolkit](./plugins/agentic-toolkit) | Reference package | Reusable TypeScript infrastructure for multi-model councils, sub-agent hierarchies, and provenance-tracked tool loops | Copy the source — see [README](./plugins/agentic-toolkit/README.md) |
| [excalidraw](./skills/excalidraw) | Skill | Generate architecture diagrams as `.excalidraw` files with optional PNG/SVG export | `/plugin install ccc-skills@ccc` |
| [streak](./skills/streak) | **Skill + Commands** | Universal challenge tracker with `/streak`, `/streak-new`, etc. | `/plugin install ccc-skills@ccc` |
| [agentic-system-design](./skills/agentic-system-design) | Skill | 12-stage Q&A workflow for designing agentic pipelines, councils, and sub-agent hierarchies | `/plugin install ccc-skills@ccc` |
| [self-improving-systems](./skills/self-improving-systems) | Skill | Decide whether your agent actually needs memory/feedback/learning — then design the smallest thing that pays for itself | `/plugin install ccc-skills@ccc` |
| [htmldrop](./skills/htmldrop) | Skill | Publish HTML as shareable links (Surge.sh) with collaborative annotation + AI converge | `/plugin install ccc-skills@ccc` |
| [landing-page-gtm](./skills/landing-page-gtm) | Skill | High-converting SaaS landing pages with GTM-aware copy and competitive positioning | `/plugin install ccc-skills@ccc` |
| [uat-testing](./skills/uat-testing) | Skill | End-to-end UAT for web apps via Playwright: test case generation, execution, pass/fail reports | `/plugin install ccc-skills@ccc` |
| [cross-app-shared-auth](./skills/cross-app-shared-auth) | Skill | Onboard apps into a platform with one shared login and a central accounts database: per-app opt-in access, deny-by-default, dual sign-up paths | `/plugin install ccc-skills@ccc` |
| [google-analytics-setup](./skills/google-analytics-setup) | Skill | Set up GA4 on a website and wire a real conversion (form/signup/purchase) end to end — property/stream structure, tag install, event, Key Event, and DebugView verification before ad spend | `/plugin install ccc-skills@ccc` |
| [meta-pixel-setup](./skills/meta-pixel-setup) | Skill | Set up the Meta (Facebook/Instagram) Pixel and a conversion event end to end — steers past the Conversions-API push and the sensitive-category trap, with Pixel Helper verification before ad spend | `/plugin install ccc-skills@ccc` |
| [pitch-craft](./skills/pitch-craft) | Skill | Timed spoken scripts: demo voiceovers, deck narration, live pitch speeches - word budgets, storytelling rules, trim points, re-sync | `/plugin install ccc-skills@ccc` |
| [demo-video](./skills/demo-video) | Skill | Crisp hi-res product demo videos via browser-agent driving + Xvfb framebuffer capture, with milestone-synced narration | `/plugin install ccc-skills@ccc` |
| [pitch-deck](./skills/pitch-deck) | Skill | Single-file HTML pitch decks with narration and recordable walkthroughs that stitch around a demo film | `/plugin install ccc-skills@ccc` |
| [pitch-package](./skills/pitch-package) | Skill | End-to-end pitch orchestration (hackathon / VC / customer): slot budgeting, deck + demo + speech composition, rehearsal and fallbacks | `/plugin install ccc-skills@ccc` |

The four pitch skills form one suite - **preparing a whole pitch -> start with `pitch-package`** (it routes to the others); a single artifact -> call it directly (`pitch-craft` = words against a clock, `demo-video` = crisp product footage, `pitch-deck` = the deck + walkthrough). Full decision guide: [skills/README.md](./skills/README.md#the-pitch-suite---when-to-use-what).

---

## Installation

```bash
# Add this repo as a marketplace
/plugin marketplace add ooiyeefei/ccc

# Install a plugin (e.g. deckling, which has the /deckling command)
/plugin install deckling@ccc

# Install Daily Chief, then invoke /daily-chief for its explicit Plan today workflow
/plugin install daily-chief@ccc

# Install the skills collection (excalidraw, streak, agentic-system-design,
# self-improving-systems, htmldrop, landing-page-gtm, uat-testing,
# cross-app-shared-auth, google-analytics-setup, meta-pixel-setup)
/plugin install ccc-skills@ccc
```

---

# Plugins

## Plugin: Deckling

Generate and refine PowerPoint presentations using Anthropic's Platform Skills API.

```bash
/deckling "Quarterly Review - 3 slides"
/deckling "Change title to 'Q4 Results'" --refine quarterly.pptx
```

See [plugins/deckling/README.md](./plugins/deckling/README.md) for full documentation.

---

## Plugin: MVP Launch

Analyze web app codebases against a battle-tested 10-point MVP launch checklist. Based on "Realistic MVP Launch Checklist (from building 30+ apps)".

```bash
/launch-check
```

**The 10-Point Checklist:**
1. Stripe Setup (webhooks, trials, failed payments)
2. Mobile-First Design (real device testing)
3. Smooth Onboarding (minimal steps, fast first win)
4. AI & Automation Stability (retries, error handling)
5. Critical Emails (welcome, trial-ending, failed payment)
6. Error Logging (catch bugs before users)
7. User Feedback Loop (simple form or tool)
8. Auth & Roles (secure pages, basic roles)
9. Custom Domain with SSL (no dev URLs)
10. Real Database & Backups (automated backups)

**Philosophy:** "Don't overbuild. Just make it stable, usable, and something people can trust."

See [plugins/mvp-launch/README.md](./plugins/mvp-launch/README.md) for full documentation.

---

## Plugin: Product Management

AI-native product management for startups. Process signals, not features.

**After installing, just ask Claude Code:**
```
"Analyze my product"
"Research competitors"
"Find feature gaps we should build"
"What should we build next?"
```

### Key Commands

```bash
/pm analyze     # Deep product understanding
/pm landscape   # Market overview + competitors
/pm gaps        # Batch gap analysis with WINNING scores
/pm file        # Create GitHub Issues for top priorities
/pm roadmap     # Organize into Now/Next/Later
```

### WINNING Filter

Prioritize with objective scoring: `WINNING = Pain × Timing × Execution`

- **40-60**: FILE (high conviction)
- **25-39**: WAIT (monitor)
- **0-24**: SKIP (not worth it)

### spec-kit Integration

This skill handles **WHAT to build** (product discovery). For **HOW to build**, use [spec-kit](https://github.com/github/spec-kit):

```
/pm file → GitHub Issue → /speckit.specify → /speckit.plan → /speckit.implement
```

The GitHub Issue IS the handoff—no extra command needed.

See [plugins/product-management/README.md](./plugins/product-management/README.md) for full documentation.

---

## Plugin: Rethink Surveys

Survey design framework grounded in proven research methods — Caroline Jarrett's *Surveys That Work*, Dillman's Tailored Design, and Tourangeau's cognitive model. Captures what people are actually trying to do (past behavior, not hypotheticals) without leading questions, satisficing bait, or shallow Likert noise.

```bash
/design-survey     # Interactive design session for a new survey
/critique-survey   # Jarrett-style critique of an existing survey
/turn-into-app     # Turn a finalized design into a working app scaffold
```

**Features:**
- 4-part hybrid structure: discovery / diagnostic / intent / segmentation
- Question library with behavioral anchors
- Three battle-tested templates: event organizers, startup founders, gig-economy workers
- Text, voice, and AI-interviewer modalities
- Bundles the `rethink-survey` MCP server for designing, critiquing, scoring, and clustering survey responses

See [plugins/rethink-surveys](./plugins/rethink-surveys) for full documentation.

---

## Plugin: Agentic Toolkit (Reference Package)

Reusable TypeScript infrastructure for building agentic systems with multi-model councils, hierarchical sub-agents, and provenance-tracked tool loops. Lifted from production code and hardened with depth caps and required provenance.

This is a **reference package to copy from**, not an installable command plugin — the point is to save a week of plumbing per new agentic project.

**The five components:**
1. **Gateway adapter** — one provider seam for Claude / GPT / Gemini behind a unified endpoint (TokenRouter, OpenRouter, LiteLLM, Vercel AI Gateway)
2. **Models registry** — typed role → `{ model, knobs }` bindings, with per-model quirks in one place
3. **Sub-agent runner** — depth cap, per-parent spawn cap, wall-clock timeout, typed results
4. **Events** — typed `AgentSseEvent` union for streaming agent progress
5. **Provenance** — required `_source` tagging so cached vs. live generations are never ambiguous

Pairs well with the [agentic-system-design](./skills/agentic-system-design) skill: design the system with the skill, build it with the toolkit.

See [plugins/agentic-toolkit/README.md](./plugins/agentic-toolkit/README.md) for full documentation.

---

# Skills

## Skill: Excalidraw Generator

Generate architecture diagrams from any codebase as `.excalidraw` files, with optional PNG and SVG export.

**After installing ccc-skills, just ask Claude Code:**
```
"Generate an architecture diagram for this project"
"Create an excalidraw diagram of the system"
"Visualize this codebase as an excalidraw file"
"Export this diagram to PNG"
```

**Features:**
- Analyzes any codebase (Node.js, Python, Java, Go, etc.)
- No prerequisites - works without existing diagrams or Terraform
- Proper 90-degree elbow arrows (not curved)
- Color-coded components by type (database, API, storage, etc.)
- Dynamic IDs and labels based on discovered components
- PNG/SVG export via Playwright and `@excalidraw/utils` (no manual upload needed)

See [skills/excalidraw/README.md](./skills/excalidraw/README.md) for quick start guide.
See [skills/excalidraw/SKILL.md](./skills/excalidraw/SKILL.md) for full documentation.

---

## Skill: Streak - Challenge Tracker

Universal challenge tracker with flexible cadence, intelligent insights, and cross-challenge learning detection.

### Slash Commands (Recommended)

After installing ccc-skills, use these commands for **reliable, deterministic** triggering:

```bash
/streak              # Check in to active challenge
/streak-new          # Create a new challenge (guided)
/streak-list         # List all challenges
/streak-switch NAME  # Switch active challenge
/streak-stats        # View progress and achievements
/streak-insights     # Cross-challenge insights
```

### Natural Language (Alternative)

You can also ask Claude Code naturally - it will invoke the skill when relevant:
```
"Check in to my challenge"
"Start a new streak"
"Show my stats"
```

### Features

- **Universal**: Works for any challenge type (learning, habits, building, fitness, creative, custom)
- **Flexible Cadence**: Daily, weekly, or custom N-day intervals per challenge
- **AI-Powered Insights**: Auto-detects compound learning and semantic connections
- **Achievements**: Streak badges and milestone rewards
- **Calendar Export**: Optional .ics file for calendar reminders
- **Zero Config**: Works locally with no external dependencies

### Example Challenges

- 30 Days of Coding
- Read 12 Books This Year
- Morning Meditation Habit
- Daily Sketching Practice

See [skills/streak/README.md](./skills/streak/README.md) for quick start guide.
See [skills/streak/SKILL.md](./skills/streak/SKILL.md) for full documentation.

---

## Skill: Agentic System Design

Prescriptive design partner for any agentic system: tool-loop agents, multi-model councils, sub-agent hierarchies, plan-execute pipelines, handoff networks. Walks you through a 12-stage Q&A flow — one question at a time — and emits a buildable design doc with citations.

**After installing ccc-skills, just ask Claude Code:**
```
"Design an agent that does HAZOP analysis"
"Should I use a multi-model council for finance review?"
"I want to build an AI brand strategist — orchestrator-worker or handoff?"
"Real agency or workflow?"
```

**Opinionated by design:** most "agent" requests are workflows; most "council" requests are wasteful; most depth-3 hierarchies are depth-2 with a tool that needed renaming. The skill filters ruthlessly *before* you start building — via an agent-washing rubric, council-decision test, and depth-3 sanity check.

See [skills/agentic-system-design/README.md](./skills/agentic-system-design/README.md) for quick start guide.
See [skills/agentic-system-design/SKILL.md](./skills/agentic-system-design/SKILL.md) for full documentation.

---

## Skill: Self-Improving Systems

Decide whether your agent actually needs persistent memory, feedback loops, or closed-loop learning — then design the smallest thing that pays for itself.

**After installing ccc-skills, just ask Claude Code:**
```
"Add memory to my agent"
"Make my marketing agent learn from past campaigns"
"Should I use mem0 or Letta?"
"Why does my agent keep making the same mistake?"
```

**Headline message:** most agents shouldn't have persistent memory. Memory is a liability surface (drift, poisoning, debugging difficulty, GDPR/HIPAA exposure). The skill's first two stages exist to stop over-engineering — most users discover they want a state cache (or stateless RAG), not memory + learning. Default position: scratchpad-only with a stateless agent shipped first.

See [skills/self-improving-systems/README.md](./skills/self-improving-systems/README.md) for quick start guide.
See [skills/self-improving-systems/SKILL.md](./skills/self-improving-systems/SKILL.md) for full documentation.

---

## Skill: htmldrop

Publish any HTML file as a shareable link instantly, with optional collaborative review. Wraps the [`htmldrop` CLI](https://www.npmjs.com/package/@yeefeiooi/htmldrop) — you just describe what you want in natural language.

**Two modes:**
1. **Simple share** — public or password-protected link via free Surge.sh hosting
2. **Collaborative feedback + converge** — publish with an embedded annotation widget so reviewers highlight text and comment (no account needed), then pull the feedback and synthesize an improved version with AI

**After installing ccc-skills, just ask Claude Code:**
```
"Share this HTML report"
"Publish this and let people comment on it"
"What did reviewers say? Converge the feedback"
```

**Prerequisites:** Node.js >= 18 and `npm install -g @yeefeiooi/htmldrop@latest`.

See [skills/htmldrop/README.md](./skills/htmldrop/README.md) for quick start guide.
See [skills/htmldrop/SKILL.md](./skills/htmldrop/SKILL.md) for full documentation.

---

## Skill: Landing Page GTM

Build conversion-focused SaaS landing pages that sell — not just describe. Combines product research, competitive positioning, sales copywriting, and frontend implementation into a single workflow.

**After installing ccc-skills, just ask Claude Code:**
```
"Build a landing page for this product"
"Rewrite the feature cards as sales copy"
"Update the pricing page with competitive positioning"
```

**Workflow:** researches the actual product first (never invents features), studies competitors, then writes GTM-aware copy and implements it in your existing design system.

See [skills/landing-page-gtm/README.md](./skills/landing-page-gtm/README.md) for quick start guide.
See [skills/landing-page-gtm/SKILL.md](./skills/landing-page-gtm/SKILL.md) for full documentation.

---

## Skill: UAT Testing

End-to-end User Acceptance Testing for web applications: analyze → generate test cases → set up environment → execute → report.

**After installing ccc-skills, just ask Claude Code:**
```
"Run UAT on this branch"
"Test this feature against the spec"
"Generate test cases for my changes"
```

**Features:**
- Analyzes branch diff and specs to generate exhaustive test cases (happy path, errors, persistence, auth, responsive)
- Sets up local dev server or targets staging/production
- Executes tests via Playwright browser automation
- Produces pass/fail results report with screenshots and fix documentation

See [skills/uat-testing/README.md](./skills/uat-testing/README.md) for quick start guide.
See [skills/uat-testing/SKILL.md](./skills/uat-testing/SKILL.md) for full documentation.

---

## Contributing

We welcome contributions! CCC follows a **hybrid contribution model**:

| Contribution Type | Process |
|-------------------|---------|
| Bug fixes | PRs welcome directly |
| Documentation | PRs welcome directly |
| New features | Open issue first for discussion |
| New skills/plugins | Open issue first for discussion |

**Quick start:**
1. Fork the repo
2. Create a branch
3. Make changes and test with Claude Code
4. Submit a PR

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

### Good First Issues

Look for issues labeled `good first issue` - they're great for getting started!

---

## Support

If you find CCC useful, consider supporting its development:

<a href="https://buymeacoffee.com/afYkK7e"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="130"></a>

---

## License

MIT

---

## Star History

<a href="https://www.star-history.com/?repos=ooiyeefei%2Fccc&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=ooiyeefei/ccc&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=ooiyeefei/ccc&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=ooiyeefei/ccc&type=date&legend=top-left" />
 </picture>
</a>
