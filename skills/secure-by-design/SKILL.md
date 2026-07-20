---
name: secure-by-design
description: Run an enterprise security review of a system design or existing code before it ships. Use when the user says "security review", "secure by design", "threat model this", "is this design secure", "what security controls do we need", "audit this for security", "harden this system", "RBAC design", "review my auth", or "enterprise security checklist". Classifies assets and trust boundaries FIRST, then recommends only the controls that fit — grounded in battle-tested patterns. Right-sizes for team scale (bones now, ceremony later). Do NOT use for writing a specific exploit, penetration-testing a system the user does not own, or general non-security code review.
---

# Secure by design

A review partner for the security of any system — an RBAC model, a multi-tenant SaaS, an API, an agent. You classify what you are protecting **before** proposing controls, then recommend only what fits the assets, trust boundaries, and team scale. Output: a short, ranked list of applicable controls with the reasoning, not a generic checklist dump.

The leading words below are load-bearing. Use them in your reasoning — they carry the decisions.

## Leading words (say these)

- **deny-by-default** — an unmapped permission is denied, never allowed.
- **fail-closed** — unknown state ⇒ deny; an error path never grants access.
- **least privilege** — the smallest capability that does the job; unknown/absent role ⇒ the least-privileged role.
- **two axes (scope × role)** — *which* resources vs *what* actions are independent; do not collapse siblings onto one ladder.
- **anti-IDOR** — never trust a client-supplied id as a grant; resolve the caller's own scope independently.
- **append-only audit** — one immutable event per privileged action, in the same transaction, actor bound from auth (never a client arg).
- **eligible-not-active** (JIT) — sensitive access is requested → approved → activated → auto-expires; default OFF.
- **four-eyes** — critical actions are proposed by one person and executed only after a *different* person approves (separation of duties: requester ≠ approver).
- **blast radius** — how much one compromised credential or mistake can touch; minimize it.
- **data minimization** — mask/omit sensitive data below the role that needs it; expose aggregates, not raw PII.
- **deploy-authority separation** — only CI holds the deploy key; humans and feature branches cannot deploy.
- **break-glass** — a documented, logged, reviewed-after emergency bypass.
- **bones now, ceremony later** — build the primitives into the schema early; defer the process overhead.

## The review (do these in order — do NOT jump to controls)

**Legwork first.** The most common failure is proposing controls before understanding what is protected. Complete steps 1–2 fully before step 3.

1. **Classify the assets.** List what has value: customer data (PII, financial), credentials/keys, tenant isolation, admin capability, audit integrity, availability. For each, note the worst case if it leaks or is tampered with.

2. **Map the trust boundaries.** Where does control change hands? Client↔server, tenant↔tenant, staff↔customer, human↔machine (M2M), app↔infrastructure, CI↔production. Name every boundary; each is where a control belongs. Note the **two control planes**: the app can enforce approvals on *app* actions but **cannot** protect *infrastructure* actions (deploy, DB migration, cloud console) — those need a separate plane. State this so nobody gets false comfort.

3. **Select controls per boundary.** For each boundary, pull the applicable controls from the catalog — see `references/control-catalog.md`. Apply "least privilege" and "blast radius" as the selection lens. Do not recommend a control that doesn't map to a classified asset + boundary.

4. **Right-size for scale.** A two-person team should build primitives (TTL, eligible-vs-active, request/approve state, append-only audit) now and defer ceremony (quarterly reviews, anomaly detection, hash-chaining). See `references/right-sizing.md`. Say "bones now, ceremony later" and mark each control **build-now** vs **defer**.

5. **Produce the output.** A ranked list: control → which asset/boundary it protects → build-now or defer → the one-line reasoning. Flag any asset with no covering control as a gap.

## Top-level checklist (does the design have these where applicable?)

- [ ] **Authorization is deny-by-default** on **two axes (scope × role)**, with least-privilege normalization of unknown roles.
- [ ] **Guards fail-closed** — unknown/error state denies.
- [ ] **Anti-IDOR** — the caller's scope is resolved independently; a passed id is never a grant.
- [ ] **Reads vs writes are scoped separately** where breadth differs — all-scope *read* need not mean all-scope *write*.
- [ ] **Append-only audit** on every privileged action, actor from auth, same transaction.
- [ ] **Sensitive standing access is JIT** (eligible-not-active) with TTL + justification, not permanent.
- [ ] **Critical high-blast-radius actions use four-eyes** (requester ≠ approver).
- [ ] **Data minimization** — sensitive data masked below the role that needs it; aggregates over raw PII.
- [ ] **M2M callers** go through one keyed, allowlisted, fail-closed door — not scattered public endpoints.
- [ ] **Deploy-authority separation** — CI-only deploy; no local prod deploy.
- [ ] **Infra actions** have their own two-person control (protected branches, required reviews) — the app cannot enforce these.
- [ ] **Break-glass** path is documented and reviewed-after.
- [ ] **Access reviews** cadence exists (or is deliberately deferred with a note).

## Reference material (load only the branch you need)

- `references/control-catalog.md` — every control, what it defends, and when it applies.
- `references/groot-case-studies.md` — concrete, shipped implementations of each control (real code paths) to copy the shape from.
- `references/threat-model-steps.md` — a deeper asset/boundary/attacker walkthrough when the system is large or unfamiliar.
- `references/right-sizing.md` — build-now vs defer by team scale; the IAM-grade evolution path for a future resellable product.
