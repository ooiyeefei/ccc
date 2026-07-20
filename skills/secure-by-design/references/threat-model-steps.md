# Threat-model steps — deeper asset/boundary/attacker walkthrough

Load this when the system is large or unfamiliar and the quick classify-then-select (SKILL.md steps 1–3) isn't enough. It expands the same legwork; it does not replace it.

## 1. Assets — what has value

Enumerate concretely, not abstractly. For each, write the worst case:

| Asset | Worst case (confidentiality / integrity / availability) |
|---|---|
| Customer PII | leaked to another tenant or the public; used for phishing |
| Financial data | altered (fraud) or exposed |
| Credentials / keys | stolen → full impersonation or deploy |
| Tenant isolation | one tenant reads/writes another's data |
| Admin capability | escalated to; used to grant self more |
| Audit integrity | tampered → no forensic trail |
| Availability | a single action takes the system down |

## 2. Trust boundaries — where control changes hands

Name each, and note what crosses it:

- **Client ↔ server** — untrusted input; the client controls nothing the server doesn't re-check.
- **Tenant ↔ tenant** — the isolation boundary; anti-IDOR lives here.
- **Staff ↔ customer** — internal roles vs customer data; data minimization + JIT + view-as consent live here.
- **Human ↔ machine (M2M)** — identity-less callers; the keyed door lives here.
- **App ↔ infrastructure** — the app cannot enforce approvals below itself; the *two control planes* split lives here.
- **CI ↔ production** — deploy authority; only CI crosses it.

## 3. Attackers — who, and what they can do

Right-size the attacker set to the system; don't model nation-states for a two-founder MVP.

- **External unauthenticated** — hits public endpoints; guesses ids (IDOR); replays.
- **Authenticated tenant user** — tries to reach another tenant (horizontal) or admin (vertical).
- **Malicious/compromised staffer** — has legitimate access; the JIT + four-eyes + append-only audit + least-privilege controls exist mostly for *this* actor.
- **Compromised credential** — a stolen key or session; blast-radius minimization limits the damage.
- **Insider with DB access** — tamper-evident logs matter here (usually a defer).

## 4. Map controls to (asset × boundary × attacker)

For each boundary, ask: which attacker crosses it, which asset is exposed, and which catalog control (see `control-catalog.md`) closes it? A control with no (asset, attacker) behind it is over-engineering — drop it. An (asset, attacker) with no control is a **gap** — flag it.

## 5. Common findings (check these explicitly)

- A read endpoint that trusts a client id → **anti-IDOR** gap.
- A role that can *see* everything and therefore *change* everything → **read/write scope split** gap.
- A "protected by unguessable id" internal endpoint → needs the **keyed door**.
- Standing admin/PII access "for convenience" → convert to **JIT**.
- A destructive action any single admin can do → **four-eyes**.
- An audit written after the change (or from a client-supplied actor) → make it **atomic + auth-bound**.
- "The approval table protects our deploys" → false; separate **infra control plane**.
