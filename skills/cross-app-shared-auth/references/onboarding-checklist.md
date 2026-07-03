# Onboarding checklist

Two parts: a one-time platform setup, and a per-app checklist you run every time you add an app. Placeholders look like `<this>`. Replace them, and never commit real keys.

## Part 0: platform prerequisites (once, before any app)

- [ ] **One shared identity provider instance** for the whole family, rooted at the parent domain so its cookie spans subdomains.
- [ ] A **token template** on that provider that the central database can verify. Give it a stable name so backends can request that exact token, and make sure it stamps the audience the central database expects **and every profile claim your central functions read** (for example `email`, `name`). Verify by **decoding a real token on the instance you actually use**: template claims are per-instance and do not migrate, so a fresh or production instance can have the template by name yet emit nothing. (The store matches the token's `aud` claim to its configured audience. The bare session token has no `aud` and is rejected. See "The token audience" in `architecture.md`.)
- [ ] **Development keys** available for local work, since production keys are usually locked to the production domain.
- [ ] **A central accounts database** with the schema and functions from `examples.md`: `users`, `app_access`, and the functions `ensureUser`, `getAccess`, `listMyApps`, `activateApp`, all server-side and deny-by-default.
- [ ] The central database is configured to **trust the shared identity provider** (its auth points at the provider's issuer), so the same user id resolves inside it.
- [ ] An **app catalog** (a table or a small config) that lists the apps in the family: slug, name, url, status. The hub and any "your apps" view read from it.
- [ ] A **published, versioned platform contract** file that pins the platform-specific values every app needs: the token template name, the central store URL, the exact central function names, and the app-slug registry. Every app cites it by version. Without this, apps invent mismatched APIs against a store that does not have them.

## Part 1: per-app onboarding

Run this for each new app. Do the steps in order.

### Step 1: inspect before changing anything
- [ ] Identify the framework and where auth and the backend live.
- [ ] Check whether the app **already uses the shared identity provider** (shared publishable key, shared issuer). If it uses its own instance or none, that is a dependency: fix it first, do not layer accounts wiring on top of the wrong identity.
- [ ] Grep for any **existing** accounts wiring (`getAccess`, `activateApp`, a central db url, "portal", "accounts"). If something exists, align it with this checklist instead of rebuilding it.
- [ ] Write down what you found before editing.

### Step 2: confirm shared identity
- [ ] The app uses the shared provider's **publishable key + issuer**, not its own instance.
- [ ] The app pins **`authorizedParties`** (or the provider's equivalent) to its own origin, for example `https://<slug>.example.com`. This is the shared-cookie security requirement.

### Step 3: add a central-accounts client
- [ ] Add a client pointed at the **central accounts database** (a distinct connection from the app's own database).
- [ ] Authenticate it by requesting the **central-store token template** (for example `getToken({ template: "<name>" })`), not the bare session token. The template carries the audience the store checks, and the store resolves the same user id from it. Sending the plain session token is the most common cause of a silent "no matching provider" rejection.
- [ ] Call the central functions **by reference** (the app repo does not have the central database's generated types). See `examples.md`.

### Step 4: wire the gate and activation
- [ ] **Unauthenticated requests: always deny** at the backend. This layer is fixed.
- [ ] **Authenticated with no row: pick a policy and write it down.** Hub-style "enable this app?" gate, or, for a live app with existing users, **auto-activate** (grandfather anyone authenticated) so no one is locked out. Do not switch to hard deny while the central table is empty.
- [ ] When auto-activating, call `ensureUser` and `activateApp("<slug>")` as **independent best-effort calls** (one failing must not veto the other). Make each idempotent.
- [ ] Guard "first authenticated use" with a **durable** marker (cookie, token claim, or short-TTL shared cache), not an in-memory or module-level flag: on serverless that flag is per-instance and silently does not hold.
- [ ] If you fail **open** on central errors (so a central outage does not lock users out), add a post-deploy probe that reads back a written row (Step 7). Fail-open otherwise hides a broken central function indefinitely.
- [ ] Where you gate, check `getAccess("<slug>")` server-side, deny-by-default.
- [ ] If the app's backend is a **separate service**, set any identity header (for example `X-User-Id`) from the verified token at the edge and strip any client-supplied copy. Never forward a client's own identity header.
- [ ] Keep the app's own **tier, quota, credits, and billing** in the app's own database. Do not centralize them.

### Step 5: register the app
- [ ] Add the app to the central **catalog** (slug, name, url, status). Now it appears in the hub's "your apps" view and anywhere the family is listed.

### Step 6: env vars (two database URLs, different names)
Each app ends up with its own database URL and the shared accounts database URL. They must have different names or one clobbers the other.

- [ ] `<APP>_OWN_DB_URL` (or the app's existing name): the app's own database. Unchanged.
- [ ] `<PLATFORM>_ACCOUNTS_DB_URL`: the shared central accounts database. A distinct name.
- [ ] Shared identity: publishable key, secret key, issuer, and `authorizedParties=https://<slug>.example.com`.
- [ ] Set all of these in the app's **deploy environment** (its hosting dashboard), not only in local files. Local files are gitignored and do not reach production.
- [ ] Mind client-exposed prefixes. A store **URL** is safe to expose to the browser (some frameworks require a public prefix like `NEXT_PUBLIC_` for it), but a **secret** or deploy key must never carry that prefix. And confirm the URL points at the deployment that actually has the central functions, not a stray auto-generated one: a wrong-deployment URL makes every central call hang or 404 while looking correctly configured.

### Step 7: deploy and verify
- [ ] The app builds and its existing tests pass. The change is additive.
- [ ] After deploy on the real domain, sign in and confirm the central `activateApp("<slug>")` fires and writes an `app_access` row for the user.
- [ ] If the store rejects tokens with "no matching provider," or the app hangs on "loading," decode the token the app sends and confirm its `aud` claim equals the store's configured audience. A missing or wrong `aud` means the app is sending the bare session token instead of the store's template.
- [ ] Confirm a signed-out request is gated (deny-by-default) at the backend, not only in the UI.
- [ ] If local verification is blocked because production keys are domain-locked, verify on the deployed domain or with development keys.

## The per-app record (keep this in each app repo)

Drop a short block into each app repo so its state is legible. Reference the canonical platform contract; do not re-describe the whole model.

```
<app> integrates the shared-auth platform (contract vN):
  [ ] shared identity: shared publishable key + issuer
  [ ] authorizedParties = https://<slug>.example.com
  [ ] unauthenticated requests denied at the backend (always)
  [ ] authenticated-without-row policy: hub-gate OR live-app auto-activate (state which): ____
  [ ] (if auto-activate) ensureUser + activateApp("<slug>") on first authenticated use, best-effort + idempotent, grandfathering existing users
  [ ] central-store calls use the store's token template (aud matches), not the bare session token
  [ ] "first use" guard is durable (not an in-memory flag); fail-open paired with a row-existence probe
  [ ] user rows keyed on the shared user id
  [ ] tier / quota / billing stay in this app's own db
  [ ] usage rollup pushed to central (optional)
  env: <APP>_OWN_DB_URL, <PLATFORM>_ACCOUNTS_DB_URL, shared identity keys
```

Bump the contract version when the platform contract changes, so each app knows to re-check.
