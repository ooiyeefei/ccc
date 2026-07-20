# Right-sizing — build-now vs defer by team scale

Enterprise-from-day-one can be self-sabotage for a small team. **Bones now, ceremony later**: build the primitives into the schema early (retrofitting them onto live data is one of the most expensive migrations there is), and defer the process overhead until scale or auditors demand it.

## The rule

- **Build now (primitives, hard to retrofit)**: deny-by-default capability model, least-privilege normalization, anti-IDOR scope resolution, append-only audit, JIT state machine (TTL, eligible-vs-active), four-eyes request/approve state, read/write scope split, deploy-authority separation.
- **Defer (ceremony, easy to add later)**: quarterly access-review *meetings*, anomaly detection, hash-chained/tamper-evident logs, SOC2 formalization, MFA rollout (often a config toggle), destructive-action executors (gate them first, build the executor when actually needed).

The test: *would adding this later force a data migration or a schema change under load?* If yes, build the bone now. If it's a process or a config, defer it.

## By team scale

| Scale | Build now | Reasonably defer |
|---|---|---|
| 1–3 founders | all primitives above; multiple admins (not one); break-glass **runbook** (you *are* the emergency authority) | anomaly detection; hash-chaining; formal quarterly reviews; MFA rollout (turn on for admins, formalize later) |
| Small team (< 20) | + real access-review cadence; MFA mandatory for admins; branch protection | SOC2 automation; SIEM |
| Compliance in scope | + tamper-evident export; formal recertification; step-up auth on critical actions | — |

## Delegation of admin: multiple admins vs delegated grant

A recurring small-team question: who can invite/manage staff?

- **Simplest (recommended early)**: keep grant/role/assignment **super-only** and have **multiple supers** (e.g. both founders). A "last-super lockout" prevents locking yourselves out. Zero extra surface.
- **Delegated admin**: a capability lets a non-super manage staff *up to but never including* super — only a super mints a super. Build this only when onboarding volume makes super-only a real bottleneck. Whoever can assign roles can escalate themselves unless this "never grant super" line holds — so it is more to reason about.

## The IAM-grade evolution path (deferred, but design toward it)

The single-tenant version is the seed of a resellable module. Learn from AWS IAM / Google Workspace / Azure PIM:

- **Fixed roles → composable policies**: today N fixed roles; later, customer-defined roles built from a capability catalog.
- **Verified-domain auto-provisioning**: the "auto-staff by our email domain" rule generalizes to a tenant claiming and verifying a domain, then provisioning their own staff.
- **Scoped, expiring external guests**: an admin invites an outside email with a scoped, expiring role — exactly what the JIT + TTL primitives already enable (Azure B2B / Google external sharing).
- **Per-tenant audit + access reviews**: the append-only trail becomes a compliance feature you can charge for.

Nothing built as a primitive now is throwaway; it is the foundation of the multi-tenant product. Design the schema so these are additive later — but do **not** build them until there is a customer paying for them.
