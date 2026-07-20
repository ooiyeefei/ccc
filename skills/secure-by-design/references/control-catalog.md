# Control catalog

Each control: what it defends, when it applies, and the shape. Select per trust boundary (see SKILL.md step 3) — never dump all of them.

## Authorization

### Deny-by-default capability model on two axes (scope × role)
- **Defends**: over-broad access; privilege creep.
- **When**: any system with more than one kind of user/role.
- **Shape**: an explicit capability set per role (not a monotonic ladder — siblings like "Support" and "Product" hold *different* sets, neither a superset of the other). An unmapped capability is denied to everyone. `normalizeRole(unknown) ⇒ least-privileged role`. Two independent axes: **scope** (which resources) and **role** (what actions).
- **Anti-pattern**: a single rank ladder forced onto roles that are actually siblings — it either over-grants or blocks legitimate work.

### Read vs write scope split
- **Defends**: blast radius of a broad-read role.
- **When**: a role needs to *see* everything but should only *change* a subset.
- **Shape**: `assertInReadScope` honors an all-scope capability; `assertInWriteScope` is narrower — writing a specific resource requires an explicit assignment; only the top role writes anything. All-scope is **read breadth only**, never a write grant.

### Fail-closed guards
- **Defends**: accidental grants via error/unknown paths.
- **When**: every guard.
- **Shape**: unknown state throws/denies; a missing key or unrecognized value denies (e.g. return 503/401 when a required credential is absent), never "allow because we're not sure".

### Anti-IDOR / tenant isolation
- **Defends**: horizontal privilege escalation (accessing another tenant's row by guessing its id).
- **When**: any resource addressed by a client-supplied id in a multi-tenant system.
- **Shape**: resolve the *caller's own* scope independently, then check membership. The passed id is **never** treated as a grant.

## Auditing

### Append-only, atomic audit
- **Defends**: repudiation; tampering; "who did this?".
- **When**: every privileged/state-changing action.
- **Shape**: one immutable event per action, written **in the same transaction** as the change (so no change without its audit and vice versa), with the actor **bound from the authenticated principal, never a client arg**. The audit module exports only an insert — no update/delete. Corrections are new compensating rows.

## Privileged access

### JIT time-boxed access ("eligible-not-active")
- **Defends**: standing sensitive grants that outlive their need.
- **When**: a role occasionally needs elevated/PII access but should not hold it permanently.
- **Shape**: default OFF. request → (approve by a different person) → activate (starts the clock) → **auto-expire** at TTL. Justification mandatory. Every transition audited. A live-grant check treats an expired-but-unswept row as inactive (fail-closed on time).

### Four-eyes / dual control (separation of duties)
- **Defends**: unilateral catastrophic action; insider risk.
- **When**: the highest-blast-radius actions — grant/revoke admin, delete tenant, bulk delete, disable a security control, platform-wide config.
- **Shape**: propose (row is pending and inert) → a **different** admin approves → execute. The proposer can **never** approve their own proposal, even an admin. Unsafe execution rolls back (e.g. a "last admin" lockout). Destructive executors are gated-only until separately reviewed.

## Data handling

### Data minimization / redaction
- **Defends**: PII/financial over-exposure.
- **When**: any surface where a lower-privilege role sees data derived from sensitive records.
- **Shape**: mask/omit sensitive fields below the role that needs them; expose **aggregates** (counts, scores) instead of raw records/ids. PII access is consented, time-boxed, read-only, audited (see JIT).

## Machine-to-machine

### One keyed, allowlisted, fail-closed door
- **Defends**: identity-less callers (webhooks, Lambdas) reaching internal functions.
- **When**: any server-to-server call that has no human session.
- **Shape**: a single internal-key-gated entry point; an allowlist of callable functions; fail-closed (503/401) if the key is missing. Never scatter public endpoints "protected" only by an unguessable id — unguessability is not authorization.

## Infrastructure (a separate control plane)

### Deploy-authority separation
- **Defends**: unauthorized/unreviewed production changes.
- **When**: always.
- **Shape**: only CI holds the deploy key; it lives in CI secrets, never on a laptop; no local prod deploy from feature branches; rotate on offboarding/exposure.

### Two-person integrity for infra actions
- **Defends**: unilateral DB migration / deploy / cloud change — which the app's four-eyes table **cannot** touch.
- **When**: always, as configuration (not app code).
- **Shape**: protected branches requiring ≥ 2 reviews; required reviewers on security-sensitive paths; MFA-gated cloud with no shared root; least-privilege IAM (no single credential that can bring everything down).

### Break-glass
- **Defends**: being locked out during an emergency.
- **When**: documented once; invoked rarely.
- **Shape**: written runbook — when to invoke, who authorizes, do-the-minimum, record-as-you-go, **mandatory post-incident review + audit reconciliation**, restore normal controls immediately after.

## Ongoing

### Access reviews / recertification
- **Defends**: accumulated stale access.
- **When**: quarterly (or deferred with a note at small scale).
- **Shape**: read the append-only audit + access-request + approval tables; confirm every role/assignment/standing grant is still justified.

### MFA / step-up auth
- **Defends**: credential theft; unilateral sensitive action.
- **When**: mandatory for top-role holders; step-up before the four-eyes actions.
- **Shape**: often deferrable early (an auth-layer config), but note it explicitly rather than forgetting it.

### Tamper-evident log export
- **Defends**: audit-log tampering by an insider with DB access.
- **When**: when auditors require cryptographic proof (usually later).
- **Shape**: append-only + export to a store the app cannot rewrite is enough early; hash-chaining is a **defer** until required.
