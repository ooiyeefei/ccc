# Secure by Design - Enterprise Security Review, Grounded in Shipped Patterns

Run an enterprise security review of a system design or existing code **before it ships** — classify what you're protecting, then recommend only the controls that fit the assets, boundaries, and team scale.

---

## What It Does

This skill turns the agent into a security review partner that does the legwork first. The most common security-review failure is proposing controls before understanding what is protected — so the skill forces asset + trust-boundary classification **before** any control is recommended, then selects from a battle-tested catalog and right-sizes for team scale.

1. **Classify the assets** — PII, financials, credentials, tenant isolation, admin capability, audit integrity, availability; worst case for each.
2. **Map the trust boundaries** — client↔server, tenant↔tenant, staff↔customer, human↔machine, app↔infra, CI↔production. Names the **two control planes** (app-level approvals cannot protect infrastructure actions — no false comfort).
3. **Select controls per boundary** — from `references/control-catalog.md`, using "least privilege" and "blast radius" as the lens. A control with no asset+boundary behind it is dropped; an asset with no control is flagged as a gap.
4. **Right-size for scale** — build the primitives now (deny-by-default, anti-IDOR, append-only audit, JIT, four-eyes, read/write scope split), defer the ceremony (quarterly reviews, anomaly detection, hash-chaining). "Bones now, ceremony later."
5. **Produce a ranked output** — control → asset/boundary it protects → build-now vs defer → one-line reasoning.

### Leading words

The skill steers behavior with compact, meaning-dense phrases the agent echoes: **deny-by-default, fail-closed, least privilege, two axes (scope × role), anti-IDOR, append-only audit, eligible-not-active (JIT), four-eyes, blast radius, data minimization, deploy-authority separation, break-glass, bones now/ceremony later.**

### Grounded in real code

Every control has a shipped implementation in `references/groot-case-studies.md` (a Next.js + Convex + Clerk multi-tenant financial SaaS) — a five-role capability model, JIT time-boxed access, four-eyes dual-control, append-only audit, a keyed M2M door, deploy-authority separation — so recommendations copy a proven shape, not an abstraction.

## Structure

- `SKILL.md` — the review steps + top-level checklist + leading words (kept small).
- `references/control-catalog.md` — every control, what it defends, when it applies.
- `references/groot-case-studies.md` — shipped implementations to copy the shape from.
- `references/threat-model-steps.md` — deeper asset/boundary/attacker walkthrough for large/unfamiliar systems.
- `references/right-sizing.md` — build-now vs defer by team scale; the IAM-grade evolution path.

## Installation

```bash
# Add the ccc marketplace (if not already added)
/plugin marketplace add ooiyeefei/ccc

# Install the skills collection
/plugin install ccc-skills@ccc
```

## When to use

Triggers: "security review", "secure by design", "threat model this", "is this design secure", "what security controls do we need", "audit this for security", "harden this system", "RBAC design", "review my auth", "enterprise security checklist".

Not for: writing a specific exploit, pen-testing a system you don't own, or general non-security code review.
