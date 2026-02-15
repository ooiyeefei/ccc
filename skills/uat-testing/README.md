# UAT Testing - Automated User Acceptance Testing

End-to-end UAT workflow for web applications: analyze branch changes, generate test cases, execute via Playwright, and produce pass/fail reports.

---

## What It Does

This skill transforms Claude Code into a UAT specialist that follows a proven 5-phase workflow:

1. **Discovery** - Reads specs/requirements, analyzes `git diff` to understand what was built
2. **Environment Setup** - Checks `.env.local`, asks for credentials and test accounts
3. **Test Case Generation** - Writes prioritized `uat-test-cases.md` mapped to spec user stories
4. **Test Execution** - Runs tests via Playwright MCP browser tools with screenshot evidence
5. **Reporting** - Produces `uat-results.md` with pass/fail verdict, fix documentation, and screenshots

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Usage

Trigger the skill naturally:

```
"Run UAT on this branch"
"Test this feature against the spec"
"Generate test cases for the current branch"
"Do acceptance testing before we merge"
```

Or reference a specific spec:

```
"Run UAT based on specs/013-chat-action-cards/spec.md"
```

## How It Works

### Test Case Generation

The skill reads your spec and branch diff, then generates structured test cases with:
- Step-by-step actions and expected results (table format)
- Priority levels: Critical (P1) through Low (P4)
- Categories: happy path, error handling, persistence, auth, responsive
- Test cases are presented for review before execution

### Test Execution

Uses Playwright MCP tools (browser_navigate, browser_snapshot, browser_click, etc.) to:
- Authenticate with a test account you provide
- Navigate through each test case
- Take screenshots as evidence
- Check browser console for JS errors
- Continue on failure (doesn't stop at first failure)

### Reporting

Produces a structured report with:
- Summary table (PASS/FAIL/BLOCKED/NOT TESTED counts)
- Per-test results with specific details
- Root cause analysis for any fixes applied during testing
- PASS/FAIL/PARTIAL verdict based on priority-weighted results

## Verdict Rules

| Verdict | Criteria |
|---------|----------|
| **PASS** | All Critical (P1) and High (P2) test cases pass |
| **FAIL** | Any Critical (P1) case fails, or >50% High (P2) cases fail |
| **PARTIAL** | Critical passes but significant High (P2) failures exist |

## Environments

Works against both local dev and deployed environments:

| Aspect | Local | Production / Staging |
|--------|-------|----------------------|
| **Server** | Starts `npm run dev` (auto-detected) | Uses provided URL |
| **Env vars** | Needs `.env.local` (asks if missing) | N/A |
| **Test data** | May need seeding | Uses existing data |
| **Auth** | Test account on local provider | Test account on prod provider |

The skill asks which environment at the start of Phase 2.

## Prerequisites

- **Playwright MCP server** must be configured (for browser automation)
- **Test account credentials** - the agent cannot create new accounts due to email verification
- **Local only**: `.env.local` or equivalent environment file - the agent will ask if not found

## Skill Structure

```
uat-testing/
├── SKILL.md                          # Core 5-phase workflow
├── README.md                         # This file
└── references/
    ├── test-case-template.md         # Test case document format
    ├── results-template.md           # Results report format
    └── agent-guide.md               # Playwright tools + auth patterns
```
