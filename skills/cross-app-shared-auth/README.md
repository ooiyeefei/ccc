# Cross-App Shared Auth

A blueprint skill for wiring a family of apps to **one shared login** plus **one central accounts database**, so a person has a single account across every app and access to each app accrues per app (opt-in, deny-by-default). It teaches Claude Code to onboard each new app into the platform end to end, in the right sequence, with the prerequisites and the non-obvious gotchas handled.

If you run a portfolio of apps (a hub plus several products on subdomains) and you want one login across all of them, but you do not want signing up once to unlock everything, this is the pattern, and this skill is the runbook.

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## Quick start

After installing, ask Claude Code things like:

```
"Onboard this app into our shared-auth platform"
"Wire this new app to the central accounts database and the shared login"
"Set up one login across our subdomains with per-app access"
"Users should be able to sign up from the app or the landing page and register centrally"
```

Claude will inspect the app, confirm the shared identity is in place, add the central accounts gate with auto-activation, register the app, set the env vars, and verify, following the checklist.

## The idea in one line

**Identity is shared. Entitlement is per app.** One provider issues one user id across every app (sign in once, known everywhere). A central database holds one record per app a person has enabled. Signing in does not grant access to every app. Access is granted per app, on demand, and it accrues.

## What it handles

- **One shared identity** across all apps, with per-app authorization on top.
- **Two sign-up paths**: from the central landing page (explicit opt-in) and from inside any app (auto-activate on first use). Both register the same account centrally.
- **Deny-by-default access** checked server-side, with the migration trap solved (auto-activate grandfathers existing users so no one is locked out when the central table is still empty).
- **The gotchas**: shared-cookie security (`authorizedParties`), matching the token audience the central store checks (request a per-service token template, and never put a service's audience on the shared session token or you break every other backend), production keys being domain-locked to the real domain, env var name collisions between an app's own database and the shared one, and subdomain versus separate-domain single sign-on.
- **Clean data ownership**: the central store holds the thin "which apps" index. Each app keeps its own tier, quota, credits, and billing as the system of record.
- **Two modes**: build a new integration, or **audit** an existing one (score each record-block line PASS/FAIL/N-A with evidence). It also insists the platform publish one versioned contract so apps stop inventing mismatched APIs, and covers the operational traps a real rollout hits: fail-open hiding a broken central call, in-memory "once per session" guards that break on serverless, and client-supplied identity headers.

## Architecture

```
              SHARED IDENTITY PROVIDER (one, rooted at the parent domain)
                    one shared user id + cookie across *.example.com
                                       |
        +------------------------------+------------------------------+
      hub (example.com)          app A (a.example.com)          app B (b.example.com)
        |                              |                              |
        +---------- read/write access on the shared user id ---------+
                                       v
                   CENTRAL ACCOUNTS DB: users + app_access (the whitelist)
        each app also has its OWN db for domain data, tier, quota, billing
```

Everything joins on the shared user id. See `references/architecture.md` for the full version.

## When to use

Reach for this when you are building or extending a platform of apps that should feel like one product with one account: a hub plus several apps on subdomains, users who might start from any of them, and a need to control which apps each user can actually use. It is equally useful for the first setup and for onboarding app number five.

## What is inside

- `SKILL.md`: the workflow, the model, the onboarding sequence, the two sign-up paths, and the guardrails.
- `references/architecture.md`: the full architecture with a diagram and where each kind of data lives.
- `references/onboarding-checklist.md`: the copy-paste per-app checklist, including a short record block each app repo keeps.
- `references/entitlement-model.md`: activation, deny-by-default, the two paths, existing-user migration, and tiers.
- `references/examples.md`: sanitized, framework-neutral snippets (schema, the accounts API, the gate and auto-activate, the env checklist).

## Notes

The skill is vendor-neutral. It works with any identity provider that issues a shared token across subdomains (Clerk, Supabase Auth, Auth0, Firebase Auth) and any database for the central store and the per-app stores (Convex, Postgres, MySQL, and so on). Adapt the examples to your stack. The pattern is the point.

## License

See the repository [LICENSE](../../LICENSE).
