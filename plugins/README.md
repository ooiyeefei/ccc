# Plugins

Plugins bundle commands, agents, skills, and MCP servers into installable packages for Claude Code.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [deckling](./deckling) | Generate and refine PPTX presentations using Anthropic's Platform Skills API, via the `/deckling` command |
| [daily-chief](./daily-chief) | User-invoked Daily Chief Plan today with browser device login, local preview, and explicit remote apply via `/daily-chief` |
| [mvp-launch](./mvp-launch) | MVP launch readiness checker. `/launch-check` analyzes your codebase against a battle-tested 10-point checklist (Stripe, mobile, onboarding, emails, logging, auth, backups, …) |
| [product-management](./product-management) | AI-native PM for startups: competitor research, gap analysis, and WINNING prioritization (`/pm analyze`, `/pm landscape`, `/pm gaps`, `/pm file`) with GitHub Issues integration |
| [rethink-surveys](./rethink-surveys) | Survey design framework grounded in Jarrett/Dillman/Tourangeau methods. `/design-survey`, `/critique-survey`, `/turn-into-app` commands plus a bundled `rethink-survey` MCP server |
| [agentic-toolkit](./agentic-toolkit) | **Reference TypeScript package** (copy the source, not installable as commands): multi-model gateway, models registry, depth-capped sub-agent runner, typed SSE events, and required provenance tagging |

## Installation

```bash
# Add the marketplace
/plugin marketplace add ooiyeefei/ccc

# Install a plugin
/plugin install deckling@ccc
/plugin install daily-chief@ccc
/plugin install mvp-launch@ccc
/plugin install product-management@ccc
/plugin install rethink-surveys@ccc
```

`agentic-toolkit` is a reference package — copy what you need from [its source](./agentic-toolkit/src/) instead of installing it.

## Plugin Structure

Each plugin folder contains:
- `.claude-plugin/plugin.json` - Plugin manifest (name, version, description)
- `commands/` - Slash commands (optional)
- `agents/` - Subagent definitions (optional)
- `skills/` - Bundled skills (optional)
- `README.md` - Full documentation

## See Also

For standalone skills installable as one collection (`ccc-skills`), see [skills](../skills/).
