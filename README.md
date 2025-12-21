# Claude Code Custom Plugins & Skills

Custom plugins and skills for [Claude Code](https://github.com/anthropics/claude-code).

## Available

| Name | Type | Description | Install Command |
|------|------|-------------|-----------------|
| [deckling](./plugins/deckling) | Plugin | Generate PPTX presentations using Anthropic Platform Skills API | `/plugin install deckling@ccc` |
| [excalidraw](./skills/excalidraw) | Skill | Generate architecture diagrams as `.excalidraw` files | `/plugin install ccc-skills@ccc` |
| [streak](./skills/streak) | **Skill + Commands** | Universal challenge tracker with `/streak`, `/streak-new`, etc. | `/plugin install ccc-skills@ccc` |

---

## Installation

```bash
# Add this repo as a marketplace
/plugin marketplace add ooiyeefei/ccc

# Install the deckling plugin (has /deckling command)
/plugin install deckling@ccc

# Install the skills collection (includes excalidraw and streak)
/plugin install ccc-skills@ccc
```

---

## Plugin: Deckling

Generate and refine PowerPoint presentations using Anthropic's Platform Skills API.

```bash
/deckling "Quarterly Review - 3 slides"
/deckling "Change title to 'Q4 Results'" --refine quarterly.pptx
```

See [plugins/deckling/README.md](./plugins/deckling/README.md) for full documentation.

---

## Skill: Excalidraw Generator

Generate architecture diagrams from any codebase as `.excalidraw` files.

**After installing ccc-skills, just ask Claude Code:**
```
"Generate an architecture diagram for this project"
"Create an excalidraw diagram of the system"
"Visualize this codebase as an excalidraw file"
```

**Features:**
- Analyzes any codebase (Node.js, Python, Java, Go, etc.)
- No prerequisites - works without existing diagrams or Terraform
- Proper 90-degree elbow arrows (not curved)
- Color-coded components by type (database, API, storage, etc.)
- Dynamic IDs and labels based on discovered components

See [skills/excalidraw/SKILL.md](./skills/excalidraw/SKILL.md) for full documentation.

---

## Streak - Challenge Tracker

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
