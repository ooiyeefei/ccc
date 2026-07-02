# Entitlement model

How access is granted, checked, and accrued. This is the behavior layer on top of the architecture.

## Deny-by-default

The central `app_access` table is a whitelist. A user has access to an app only if a row exists with `status = "enabled"` for that user and that app. No row means no access. Every protected operation checks this **server-side**. Hiding a button in the UI is not a control, because the shared session is valid at the backend too, so anything with the cookie can call the API directly.

`getAccess(appSlug)` returns the row or null. Null means deny. Simple, and safe by construction.

## Activation: how a row gets created

Two moments create an `app_access` row, and both must exist for the two sign-up paths to work.

- **Explicit opt-in** (from the hub): the user clicks "enable" on an app they have not used. The hub calls `activateApp(appSlug)`.
- **Auto-activate** (from inside an app): on first authenticated use, the app calls `ensureUser` then `activateApp(appSlug)`. The user is already using the app, so recording access and letting them through is the correct semantic.

`activateApp` is an idempotent upsert: calling it again does nothing new. `ensureUser` upserts the identity link (`users` row) so the central database has a profile for this person.

## The two sign-up paths, concretely

**Path A, hub-first.**
```
sign up at the hub -> one shared account created
open the hub's "your apps" view -> reads listMyApps (reactive)
click Enable on app X -> activateApp("X") -> row created -> card flips to enabled
```

**Path B, app-first.**
```
land on app X directly -> sign up there -> SAME shared account (shared identity)
first authenticated use -> app calls ensureUser + activateApp("X")
the central db now shows this user with X enabled, without visiting the hub
```

Both paths converge on the same account and the same user id, because identity is shared. The `app_access` rows accrue: one per app the person joins, from whichever direction. There is never a separate "per app account."

## Existing users and the migration trap

The single most common way to break a live app: switch it to hard deny-by-default while the central table is empty. Every existing user has no row yet, so every existing user is locked out at once.

Avoid it by choosing the right activation semantics per app maturity:

- **Live app with real users**: auto-activate on first authenticated use. The first time an existing user signs in after the wiring ships, the app records their access and lets them through. They are grandfathered, and the central table fills up going forward. No lockout.
- **Brand new app, or a hub listing of apps the user has never tried**: an explicit "enable this app?" gate is appropriate, because there is no existing population to lock out and opting in is a real decision.

If you genuinely need hard gating on a live app (for example a paid-only app), do not flip deny-by-default blind. Either backfill rows for existing users first, or run auto-activate for a transition window, then tighten. Name the plan; do not surprise your users.

## Tiers

`tier` on the `app_access` row (for example free, premium, paid) is a **label** that can gate premium features. It does not replace the app's own billing. The authoritative balance, quota, and payment state live in the app's own database. Read the tier for coarse gating, and keep the money truth local so it cannot drift from a second copy.

Access status and tier are the only things the central store needs. Credits and quotas are not central, ever.

## Cross-app view

Because `listMyApps` returns every app a user has enabled, a hub or account page can show "you have enabled N of M apps" and offer launch links. That view is the payoff of centralizing the thin index. Note that an anonymous hub cannot show a per-user view: the page has to be signed in to read the user's rows. Decide whether the hub is a static launcher or an authenticated account center.
