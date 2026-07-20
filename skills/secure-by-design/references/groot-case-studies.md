# Groot case studies — shipped implementations to copy the shape from

Concrete, in-production examples of each control from a Next.js + Convex + Clerk multi-tenant financial SaaS. Use these to copy the *shape*, not the exact code.

## Deny-by-default capability model on two axes

`convex/lib/crm/capabilities.ts` — five staff roles (`sales`, `support`, `product`, `engineering`, `super`) as **explicit capability sets**, not a ladder. `support` and `product` are **siblings**: Support holds `start_viewas` (reproduce issues), Product holds `view_product_analytics` — neither is a superset of the other. `super` holds the union. `normalizeRole(unknown|absent|legacy) ⇒ 'sales'` (least privilege). An unmapped capability is denied to every role.

Two axes: **scope** (`resolveAccountVisibility.ts`) × **role** (the capability sets). The engineering "lens" (`view_dspy_metrics`) is a third orthogonal predicate — granted by a flag, never by role — showing how to add an axis without touching the ladder.

## Read vs write scope split

`convex/lib/crm/resolveAccountVisibility.ts` — `resolveScope`/`assertAccountInScope` (READ) return all-scope for any holder of `view_all_accounts` (support/product/engineering/super). `resolveWriteScope`/`assertAccountInWriteScope` (WRITE) are narrower: only `super` writes any account; everyone else — **including engineering** — must be *assigned*. All-scope is read breadth only. Per-account write mutations (`adminBilling`, `trialBundles.apply`, `featureEntitlementsAdmin.setFeatureOverride`, `memberships.inviteRoster`) use the write check; the choice contains a single credential's blast radius.

## Fail-closed guards

`convex/lib/crm/requireStaffCapability.ts` — throws `NOT_STAFF_CAPABILITY` on any miss. The internal-key HTTP doors in `convex/http.ts` return 503/401 when the service key is unavailable — an unauthenticated caller can never fall through.

## Anti-IDOR

`assertAccountInScope` independently resolves the caller's scope and checks membership; a client-supplied `businessId` is never a grant. This is the property that stops a staffer widening their own access by passing an arbitrary id.

## Append-only, atomic audit

`convex/lib/crm/staffAudit.ts` — `recordStaffAudit` is called **inside** the guarded mutation handler (one Convex transaction: no change without its audit row), the actor is bound from the guard's returned user doc (never a client arg), and the module exports **only** an insert (no update/delete). `staff_audit_events` is the immutable trail.

## JIT time-boxed access ("eligible-not-active")

`convex/functions/crm/accessRequests.ts` + table `access_requests` — Product's per-account PII access is JIT: `request → approve (different super) → activate (requester starts clock) → auto-expire`. Justification required; `hasActiveJitAccess` treats an expired-but-unswept row as inactive (fail-closed on time). The older `viewAsSessions.ts` shows the same TTL + consent pattern for support view-as.

## Four-eyes / dual control

`convex/functions/crm/criticalActionApprovals.ts` + table `critical_action_approvals` — `propose → approveAndExecute (different super)`. The proposer can never approve their own proposal (`SELF_APPROVAL`). `grant_super`/`revoke_super` execute in-tx; a `revoke_super` that would drop below one super throws `LAST_SUPER` and rolls the whole transaction back. `delete_tenant`/`bulk_delete`/`disable_control`/`platform_config` are **gated-only** (approved, but no blind destructive executor).

## Data minimization

Account 360 exposes `pqlUserCount` (an aggregate) instead of raw PQL user ids; financials are masked below the role that needs them; PII is reachable only through consented, time-boxed, read-only, audited view-as. The standalone CRM contract hands out handwritten DTOs, not the full schema.

## M2M keyed door

`convex/http.ts` — the `X-Internal-Key` HTTP-action archetype: the document-processor Lambda and MCP callers hit a single keyed, allowlisted door (`MCP_INTERNAL_SERVICE_KEY`); off-allowlist ⇒ 403, missing key ⇒ 503. Previously these were public functions "protected" by an unguessable id — the lesson: unguessability is not authorization.

## Deploy-authority separation

Production Convex deploys run only through Vercel `prebuild → convex:deploy:ci` (gated on `VERCEL_ENV=production`); the deploy key lives only in CI secrets; local `convex deploy` from feature branches is prohibited.

## The two control planes (no false comfort)

The `critical_action_approvals` table makes `grant_super` need a second super — but it **cannot** make a `git push --force` or a `DROP TABLE` need a second person, because those never reach the app. Infra two-person integrity is GitHub branch protection + CI-only deploy + cloud MFA — a *configuration* plane, documented separately from the app.

## Right-sizing in practice

For a two-founder team the program shipped the **primitives** (5-role model, JIT + four-eyes state machines, append-only audit) but **deferred** MFA (parked as an issue), destructive-action executors (gated-only), hash-chained logs, and anomaly detection. "Bones now, ceremony later."
