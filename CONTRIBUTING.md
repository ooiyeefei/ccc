# Contributing to CCC

Thank you for your interest in contributing to CCC! This collection of plugins and skills for Claude Code is open source and welcomes contributions from the community.

## Contribution Philosophy

- **Bug fixes and documentation**: PRs welcome directly
- **New features**: Please open an issue/discussion first to align on design before coding
- **Good first issues**: Look for the `good first issue` label for beginner-friendly tasks

This approach gives contributors freedom while maintaining project direction and code consistency.

---

## Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your changes
4. **Make your changes** following the guidelines below
5. **Test** your changes with Claude Code
6. **Submit a PR** using the provided template

---

## Types of Contributions

### Bug Fixes
Found a bug? Great catches are always welcome!
1. Check if an issue already exists
2. If not, create a bug report using our template
3. Fork, fix, and submit a PR

### Documentation Improvements
- Typo fixes, clarifications, better examples
- PRs welcome directly - no issue needed for small docs fixes

### New Features
**Important**: For new features, please open an issue first!

1. Open a feature request issue describing:
   - What problem it solves
   - Proposed solution
   - Any alternatives considered
2. Wait for maintainer feedback
3. Once approved, implement and submit PR

### New Skills or Plugins
Want to add a new skill or plugin to the collection?
1. Open an issue describing the skill/plugin concept
2. Include:
   - Use case and target users
   - How it fits with existing skills
   - Any external dependencies needed
3. Get approval before implementing
4. **Use Claude's skill-creator** to generate the skill (see [Creating Skills](#creating-skills) below)

---

## Development Guidelines

### Project Structure

```
ccc/
├── plugins/           # Claude Code plugins
│   └── deckling/      # PPTX generation plugin
├── skills/            # Claude Code skills
│   ├── excalidraw/    # Diagram generation skill
│   └── streak/        # Challenge tracker skill
├── commands/          # Slash command definitions
└── .claude-plugin/    # Plugin configuration
```

### Code Style

- **Skills**: Write in clear markdown with structured sections
- **Plugins**: Follow existing patterns in the codebase
- **Commands**: Use descriptive names matching skill functionality

### Testing Your Changes

Before submitting a PR:

1. **Install locally**: Test your changes with Claude Code
   ```bash
   # From the ccc directory
   /plugin marketplace add .
   /plugin install <your-plugin>@ccc
   ```

2. **Verify functionality**: Test all affected commands/skills

3. **Check for regressions**: Ensure existing features still work

### Creating Skills

**Use Claude's official skill-creator tool** when building new skills:

1. **Official Skill Creator**: Use Anthropic's [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) skill
   ```
   # In Claude Code, just ask:
   "Create a new skill for [your use case]"
   ```

2. **Official Guidelines**: Follow Claude's skill creation documentation:
   - [How to Create Custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

3. **Skill Structure**: Skills should follow this structure:

```markdown
---
name: skill-name
description: Clear one-line description
---

# Skill Name

[Clear instructions for Claude Code]

## When to Use
[Trigger conditions]

## Output Format
[Expected outputs]
```

**Why use skill-creator?** It ensures your skill follows Claude Code conventions, handles edge cases properly, and produces consistent, well-structured output.

### Commit Messages

Use clear, descriptive commit messages:
- `fix: resolve arrow rendering in excalidraw skill`
- `feat: add weekly cadence option to streak`
- `docs: clarify installation instructions`
- `chore: update dependencies`

---

## Pull Request Process

1. **Fill out the PR template** completely
2. **Link related issues** using `Fixes #123` or `Closes #123`
3. **Keep PRs focused** - one feature/fix per PR
4. **Update documentation** if your change affects user-facing features
5. **Respond to feedback** promptly

### PR Review Criteria

We review PRs for:
- [ ] Follows project structure and patterns
- [ ] Tested with Claude Code
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or clearly documented if unavoidable)
- [ ] Commit messages are clear

---

## Issue Guidelines

### Before Opening an Issue

1. **Search existing issues** to avoid duplicates
2. **Check documentation** - your answer might already be there
3. **Try the latest version** - the bug may already be fixed

### Bug Reports

Use the bug report template and include:
- Steps to reproduce
- Expected vs actual behavior
- Claude Code version
- Error messages (if any)

### Feature Requests

Use the feature request template and include:
- Problem you're trying to solve
- Proposed solution
- Alternatives you've considered

---

## Community Guidelines

We follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.

**In short:**
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

---

## Getting Help

- **Questions**: Open a discussion or issue
- **Bugs**: Use the bug report template
- **Ideas**: Open a feature request

---

## Recognition

Contributors are recognized in:
- Git commit history
- Release notes (for significant contributions)

---

## Sponsorship

Want to support CCC financially? We appreciate it!

- **Buy Me a Coffee**: [buymeacoffee.com/afYkK7e](https://buymeacoffee.com/afYkK7e)

### Setting Up GitHub Sponsors (For Maintainers)

If you're forking this project and want to enable sponsorship:
- [Displaying a sponsor button in your repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository)

---

Thank you for helping make CCC better!
