---
name: cross-app-shared-auth
description: Blueprint for wiring many apps to one shared login plus a central accounts database, so a person has a single account across every app and access to each app accrues per app (opt-in, deny-by-default). Use this whenever onboarding a new app into a shared-auth family, setting up cross-subdomain SSO, building a central entitlement or "app access" database, adding per-app access gating, or when the user mentions one login for many products, shared accounts across apps, subdomain SSO, a central accounts service, app entitlements, or letting people sign up from any app OR a landing page and have it register centrally. Trigger even if the user does not say "shared auth" but describes a portfolio or family of apps that should share identity.
---

# Cross-App Shared Auth

A repeatable blueprint for connecting a family of apps to **one shared identity** plus **one central accounts database**, so:

- a person has **a single account** across every app (sign in once, known everywhere),
- **access to each app is granted per app**, on demand, and accrues over time (not all-or-nothing),
- users can **sign up from any app OR from a central landing page**, and either path registers them centrally.

Use it two ways: to **stand up the platform** the first time, and to **onboard each new app** after that. When onboarding, follow the sequence in `references/onboarding-checklist.md` step by step.

---

## The one idea to hold onto

**Identity is shared. Entitlement is per app.** These are two independent layers, and conflating them is the mistake that causes almost every problem in this space.

- **Identity** (who is this person): one shared auth provider issues one stable user id used by every app. Signing in on app A signs you in on app B too (SSO across subdomains). This does **not** grant access to app B.
- **Entitlement** (what may this person use): stored in a central accounts database keyed on that shared user id. Each app checks it. No record for this user and this app means no access (deny-by-default).

So "one login" and "you only get into the apps you have actually turned on" are not in tension. They are the intended combination.

Two slots, chosen independently:

| Slot | Job | Examples |
|------|-----|----------|
| Identity provider | issue one shared user id, handle sign in / sign up | Clerk, Supabase Auth, Auth0, Firebase Auth |
| Central accounts store | hold per-app access records, keyed on the shared user id | Convex, Postgres, MySQL, any DB |

The database vendor is free per app. The only hard rule: apps that share one identity must share **one** identity provider instance, so the user id is common and joins everything.

Read `references/architecture.md` for the full picture with a diagram.

---

## Prerequisites (have these before onboarding any app)

1. **One shared identity provider instance** for the whole family (not one per app). It should:
   - be rooted at the parent domain so its session cookie is shared across subdomains (for example an instance anchored at the apex so `a.example.com` and `b.example.com` share it),
   - expose a token/claim format the central DB can verify (many providers call this a JWT template; give it a known name so backends can request it).
2. **A central accounts database and API** (the entitlement store). It needs the schema and functions in `references/examples.md`: an `app_access` table (the whitelist), a `users` table (the identity link), and server-side functions `getAccess`, `activateApp`, `listMyApps`, `ensureUser`, all keyed on the shared user id and all deny-by-default.
3. **The central DB trusts the shared identity provider.** The central store verifies the provider's tokens (configure its auth with the provider's issuer). This is what makes the same user id resolve inside the central DB.

If any of these is missing, build it first. Everything else assumes they exist.

---

## The onboarding sequence (per new app)

This is the heart of the skill. When adding an app to the family, do these in order. The full checklist with commands and gotchas is in `references/onboarding-checklist.md`.

1. **Inspect first.** Determine the app's framework, whether it already uses the shared identity provider, and whether any accounts wiring already exists. Never assume a clean slate. If the app is not yet on the shared identity provider, that is a dependency: resolve it before the accounts wiring, and do not rebuild it.
2. **Confirm shared identity.** The app uses the shared provider's keys (same publishable key + issuer), not its own instance. For a subdomain family, it pins `authorizedParties` to its own origin (see the security note below).
3. **Add a client to the central accounts DB**, separate from the app's own database. Authenticate it with the shared identity token, so the central DB sees the same user id. Call the central functions by reference, since the app repo does not have the central DB's generated types.
4. **Wire the gate.** On first authenticated use, call `ensureUser` then `activateApp("<this-app-slug>")` (see the two paths below). Check `getAccess("<this-app-slug>")` where you gate. Keep the app's own tier, quota, credits, and billing in the app's own database, never in the central store.
5. **Register the app** in the central catalog so it shows up in the portal and anywhere the family is listed.
6. **Set env vars.** Each app ends up with two database URLs: its own, and the shared accounts one. Give them **different names** so they never collide (see `references/onboarding-checklist.md`).
7. **Deploy and verify.** Confirm the central `activateApp` fires on sign in and writes a record, and that a signed-out user is gated.

---

## The two sign-up paths (both must register centrally)

A user can join the family from either direction, and both must end up recorded in the central accounts DB under the same shared identity. Support both:

**Path A, from the central landing page or portal.** The user signs up on the hub, then consciously **enables** apps (an explicit toggle that calls `activateApp`). This is discovery: the user opts into apps they have not tried yet.

**Path B, from inside an app.** The user discovers an app directly (for example lands on `app.example.com`), signs up there, and the app **auto-activates** on first authenticated use: it calls `ensureUser` then `activateApp("<slug>")`. This populates the central DB with this user and this app enabled, without the user visiting the hub first.

Because identity is shared, both paths create or reuse the **same** account and the **same** user id. There is no "app account" separate from a "hub account." The central `app_access` records simply accrue: one row per app the user has joined, from whichever direction.

Read `references/entitlement-model.md` for how activation, deny-by-default, tiers, and existing-user migration fit together.

---

## Guardrails (the non-obvious things that break)

These are the failure modes that are easy to miss. Explain them, do not just assert them.

1. **Deny-by-default versus existing users.** If an app switches on hard deny-by-default while the central DB is empty, every existing user is locked out, because none of them have a record yet. For a live app, use **auto-activate on first authenticated use** (grandfather + record). Reserve an explicit "enable this app?" gate for the hub, where users opt into apps they have never used. See `references/entitlement-model.md`.

2. **Shared-cookie security (`authorizedParties`).** When apps share a session cookie across subdomains, each app's backend must verify that a token was minted for its own origin. Otherwise a compromised sibling subdomain can replay the shared session against another app's API. Pin the allowed origin per app. This is non-negotiable for a subdomain family.

3. **The token template.** The central DB verifies the identity provider's tokens using a specific claim format. If that template does not exist on the shared provider, or the app does not request it, the central calls fail or hang (a common symptom is a portal that shows "loading" forever). Confirm the template exists.

4. **Production keys are domain-locked.** Many providers lock production keys to the production domain and its subdomains, so they do not work on `localhost`. Use the shared provider's development keys for local work, and production keys only on the real domain. Plan verification accordingly (a full click-through may need the deployed domain).

5. **Env var name collisions.** Each app has its own database plus the shared accounts database. If both use the same variable name for their URL, one clobbers the other. Give the shared accounts URL a distinct name (for example `<PLATFORM>_ACCOUNTS_DB_URL`) that never overlaps the app's own.

6. **Subdomain versus separate domain.** Silent SSO via a shared cookie only spans subdomains of one parent domain. An app on a different root domain cannot share the cookie or the user id automatically. Either give it its own identity instance (an independent island, no shared account) or bridge it deliberately (many providers charge for cross-domain SSO). Make this a conscious choice, and name the tradeoff.

7. **Entitlement truth stays local.** The central store holds the thin "which apps" index and access status. Real tier, quota, credits, and billing live in each app's own database (the system of record). Duplicating a balance centrally creates a second source of truth that drifts. Push only a usage summary up, if you need a cross-app dashboard.

---

## Reference files

- `references/architecture.md`: the full architecture with a diagram, the identity-versus-entitlement split, and where each piece of data lives.
- `references/onboarding-checklist.md`: the copy-paste per-app checklist (prerequisites, wiring, env vars, deploy, verify), including a short block each app repo can keep as its own record.
- `references/entitlement-model.md`: activation flow, deny-by-default, the two sign-up paths, existing-user migration, and tiers.
- `references/examples.md`: sanitized, framework-neutral code snippets (accounts schema, the accounts API, the gate and auto-activate, the per-app env checklist).

Adapt every example to the identity provider and databases actually in use. The pattern is the point, not any single vendor.
