# Examples

Framework-neutral snippets. The concrete flavor below uses a reactive TypeScript backend for the central store and a token-based identity provider, because that is a common pairing, but the shapes translate to Postgres, Supabase, Firebase, or any stack. No real keys, urls, or deployment ids belong here. Use placeholders.

## 1. Central accounts schema

Three tables. The first two are required. The third is optional.

```ts
// users: the identity link. One row per person, keyed on the shared user id.
users: {
  authId: string,          // the identity provider's stable subject/user id
  email: string,
  name?: string,
  role: "owner" | "member",
  createdAt: number,
}                          // index by authId

// app_access: the whitelist. One row per (user, app) the person has joined.
app_access: {
  authId: string,          // same shared user id
  appSlug: string,         // "app-a", "app-b", ...
  status: "enabled" | "disabled",
  tier: "free" | "premium" | "paid",
  activatedAt: number,
}                          // index by (authId, appSlug) and by authId

// usage_rollup (optional): a thin per-app summary for a cross-app dashboard.
usage_rollup: {
  authId: string, appSlug: string, period: string,
  metric: string, value: number, updatedAt: number,
}                          // index by (authId, appSlug, period)
```

## 2. Central accounts API

Every function reads the caller's identity from the verified token and uses its subject as `authId`. Never trust an id passed from the client. Deny-by-default.

```ts
function requireUser(ctx) {
  const identity = ctx.auth.getUserIdentity();   // resolved from the verified token
  if (!identity) throw new Error("unauthenticated");
  return identity;                               // identity.subject is the shared user id
}

// upsert the identity link on first sign in. Treat profile claims (email, name)
// as OPTIONAL best-effort: the token template may not emit them, and hard-requiring
// a claim that is absent makes this throw on every call (a 500 even though auth is fine).
ensureUser = mutation(ctx => {
  const id = requireUser(ctx);
  upsert(users, { authId: id.subject, email: id.email /* may be undefined */, role: "member", createdAt: now() });
});

// deny-by-default read: the caller's access to one app, or null
getAccess = query((ctx, { appSlug }) => {
  const id = requireUser(ctx);
  return findOne(app_access, { authId: id.subject, appSlug }) ?? null;
});

// every app the caller has enabled (powers the hub's "your apps")
listMyApps = query(ctx => {
  const id = requireUser(ctx);
  return find(app_access, { authId: id.subject });
});

// opt-in / auto-activate: idempotent upsert of an enabled row
activateApp = mutation((ctx, { appSlug, tier = "free" }) => {
  const id = requireUser(ctx);
  upsert(app_access,
    { authId: id.subject, appSlug },
    { status: "enabled", tier, activatedAt: now() });
});
```

## 3. Central store trusts the shared identity provider

Configure the central store's auth to accept tokens from the shared provider, using the named token template from the checklist.

```ts
// central store auth config
// applicationID is the audience the store REQUIRES: an incoming token's `aud` must equal it.
export default {
  providers: [
    { domain: process.env.SHARED_IDENTITY_ISSUER, applicationID: "<token-template-name>" },
  ],
};
```

## 4. Per-app gate and auto-activate

Inside an app, add a client to the central store (separate from the app's own database), authed with the shared identity token. Call the central functions by reference, because this repo does not have the central store's generated types.

```ts
// a client pointed at the CENTRAL accounts store, authed with the store's TEMPLATE token
// (see section 6: the template token carries the audience the store checks, not the bare session token)
const accounts = makeCentralClient(process.env.PLATFORM_ACCOUNTS_DB_URL, storeTemplateToken);

// on first authenticated use per session. Guard this with a DURABLE marker
// (cookie / token claim / short-TTL cache), not an in-memory flag: on serverless
// an in-memory flag is per-instance and silently does not hold.
const safe = fn => fn().catch(err => log("central call failed (fail-open)", err));
async function onAuthenticated() {
  // independent best-effort calls: one failing must not veto the other.
  // activateApp upserts its own user row too, so activation survives an ensureUser outage.
  await safe(() => accounts.call("ensureUser"));
  await safe(() => accounts.call("activateApp", { appSlug: "<this-slug>" }));   // auto-activate, no lockout
}
// fail-open trap: the catch above hides a broken central function. Pair it with a
// post-deploy probe that reads back a row you just wrote (see the deploy/verify step).

// server-side gate on a protected route (deny-by-default)
async function requireAppAccess(userToken) {
  const access = await accounts.call("getAccess", { appSlug: "<this-slug>" }, userToken);
  if (!access || access.status !== "enabled") throw forbidden();
  return access;   // access.tier is available for premium gating; billing stays local
}
```

## 5. Per-app env checklist

Two database urls with different names, plus shared identity. Set these in the app's deploy environment, not only in local files.

```
# shared identity (same values across every app in the family)
SHARED_IDENTITY_PUBLISHABLE_KEY = <public key>
SHARED_IDENTITY_SECRET_KEY      = <secret>
SHARED_IDENTITY_ISSUER          = https://id.example.com
AUTHORIZED_PARTIES              = https://<slug>.example.com   # this app's own origin

# the shared central accounts store (same value across every app)
PLATFORM_ACCOUNTS_DB_URL        = <central accounts store url>

# the app's OWN database (different per app, unchanged by this integration)
APP_OWN_DB_URL                  = <this app's own db url>
```

The failure modes to watch: giving the app's own database and the accounts store the **same** env var name (one clobbers the other); setting these only locally so production has nothing; pointing the store URL at the wrong deployment (a stray auto-generated one that lacks the central functions), which makes every call hang or 404 while looking configured; and, on frameworks that expose a public-prefixed URL to the browser (for example `NEXT_PUBLIC_`), letting a **secret** or deploy key accidentally carry that same public prefix. The store URL is safe to expose; secrets are not.

## 6. The token the app sends: the audience must match

The store verifies that the token's `aud` claim equals the `applicationID` from section 3. The identity provider's default session token has no `aud`, so the store rejects it as "no matching provider." Request the per-service template instead, and never put a service's audience on the shared session token, because that would break any other backend that checks `aud`.

```ts
// WRONG: the bare session token has no aud, so the store rejects it as "no matching provider"
const token = await getToken();

// RIGHT: request the template that stamps aud = "<token-template-name>"
const token = await getToken({ template: "<token-template-name>" });
const accounts = makeCentralClient(process.env.PLATFORM_ACCOUNTS_DB_URL, token);
```

One session token stays clean (no service `aud`), and you add one template per backend. A Supabase-backed app requests its own template (`aud = "authenticated"`), a gateway-authorizer app requests its own, and this central store gets the one above. Each token is bound only for its backend, so wiring one app never breaks another.
