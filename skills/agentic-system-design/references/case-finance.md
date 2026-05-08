# Case Study — Finance / Accounting Review

## Domain summary

Finance/accounting review systems take transactional data, journal entries, or reconciliations and produce classified outputs (postings, materiality calls, regulatory flags) plus a defensible audit trail. Inputs are GL extracts, vendor masters, prior-period comparatives, and policy docs; outputs are draft entries, exception lists, or reviewer memos. Blast radius is high — wrong materiality calls or missed related-party transactions surface weeks later as audit findings or regulator letters.

## Natural council to design

- **Foreman role — CFO**. Sets review priorities for the period (close, audit prep, ad-hoc investigation), decides what escalates to human controllers, owns the finalize step.
- **Senior Accountant** — drafts journal entries, classifications, materiality calls. Cites chart of accounts; never invents account codes.
- **Auditor** (critic) — challenges accuracy against GAAP/IFRS, looks for SoD (segregation-of-duties) violations, flags unusual variances vs prior periods.
- **Compliance Officer** (critic) — regulatory rules per jurisdiction (LHDN/IRAS/IRS), related-party flags, sanctions screening, transfer-pricing red flags.
- **Controller** (review council) — final sign-off; routes contested items to human signoff queue; never auto-applies entries beyond a configurable autonomy threshold.

**Sub-agent spawn conditions:**
- *Auditor spawns Forensic Specialist* (depth-3) on materiality ambiguity — drills into transaction history, vendor master, prior-period comparisons, related-party graph. Tool palette: `query_gl`, `vendor_lookup`, `prior_period_compare`, `related_party_check`. Cap: 2 spawns per Auditor turn; depth-3 only.

## DNA (structured state)

`AccountingPolicyDNA` — the persistent shared state:

- **chart_of_accounts** — canonical account codes + descriptions; entries cite this list, never free-form.
- **materiality_thresholds** — dollar/percentage thresholds per account class and per legal entity.
- **closed_period_rules** — which periods are locked; what re-class still allowed; who can override.
- **jurisdiction_tax_codes** — per-entity tax regime, residency, treaty applicability.
- **ifrs_home_currency** — reporting currency + FX policy; functional vs presentation currency rules.
- **sod_matrix** — who can post vs review vs approve; agent role permissions mapped to human roles.

DNA is enforced as constraints, not suggestions. The Senior Accountant cannot emit an account code outside `chart_of_accounts`.

## Tool-loop & sub-agent design

**Foreman (CFO) tools:**
- `call_senior_accountant(transactions)` — drafts entries
- `call_auditor(draft)` — challenge
- `call_compliance_officer(draft)` — regulatory check
- `call_controller(draft, critiques)` — sign-off recommendation
- `escalate_to_human(reason)` — explicit escape hatch
- `finalize(decision, dissent_log)` — terminator

**Critic verification tools:**
- Auditor: `lookup_gaap_rule(topic)`, `check_sod(role, action)`, `prior_period_variance(account, period)`, optional `spawn_forensic_specialist`
- Compliance Officer: `lookup_jurisdiction_rule(country, topic)`, `related_party_screen(vendor)`, `sanctions_screen(party)`

**Forensic Specialist palette (sub-agent, depth-3):**
- `query_gl(filter)` — read-only GL access
- `vendor_lookup(id)` — vendor master + history
- `prior_period_compare(account, periods)` — variance investigation
- `related_party_check(party)` — graph walk over known relationships
- Cap: 60s timeout, 2 spawns per Auditor turn, no write tools.

System prompt skeleton for the Auditor:

```
You are an Auditor reviewing {{draft}} for a {{jurisdiction}} entity.
Cite GAAP/IFRS standard references for every challenge.
Tools: lookup_gaap_rule, check_sod, prior_period_variance, spawn_forensic_specialist.
Refuse to evaluate any entry whose account code is not in chart_of_accounts.
On materiality ambiguity, spawn Forensic Specialist before voting.
```

## Memory verdict

Mostly **context-mgmt**, not learning. Closed-loop signal exists but is sparse and slow:

- **Signal**: audit findings (weeks), reconciliation breaks (days), regulator outcomes (months).
- **Latency**: too long for direct RL; use intermediate proxies — rule-lint violations, prior-period variance flags, controller override rate.
- **Ground truth**: external audit reports + finalized financial statements + regulator correspondence.
- **Hybrid RLAIF**: sparse human signoff plus dense automated proxies — see `feedback-signals.md`.

State-cache accumulations: "Vendor X is related party" (KV, validator-gated), "Last quarter's policy decisions" (episodic), per-entity accruals patterns (drift-monitored). Never auto-promote learnings into core policy DNA — controller-gated change.

## Anti-patterns specific to this domain

| Anti-pattern | Test | Fix |
|---|---|---|
| **Hallucinated GL entries** | Senior Accountant emits an account code or vendor ID that doesn't exist | Hard constraint: only emit codes present in `chart_of_accounts`; tool-enforced lookup, not free-form generation |
| **Materiality blindness** | Below-threshold variance ignored even when pattern is suspicious (lots of just-below-threshold entries) | Composite check: absolute threshold + frequency-of-near-threshold + variance from prior-period baseline |
| **LLM judging final IFRS treatment** | Council auto-applies a complex revenue-recognition or impairment call | Stop the council at "recommendation"; human controller signs off final treatment in regulated jurisdictions |
| **SoD violation via agent role** | Same agent persona drafts AND approves | Map agent personas to human SoD roles; Controller persona can never call `call_senior_accountant` |
| **Closed-period writeback** | Agent posts to a locked period | Tool refuses write to closed periods; raises `escalate_to_human` |
| **Related-party blindness** | Counterparty match misses transitive ownership | Compliance Officer's `related_party_screen` walks the graph at least 2 hops; spawn Forensic Specialist on ambiguous match |

## Recommended pattern + council shape

- **Pattern:** #4 Plan-and-Execute (`patterns-catalog.md`) — the period-close has largely knowable steps; cost of wrong tool calls is non-trivial; auditability matters more than real-time adaptation. CFO drafts a plan, executes step-by-step, with re-plan triggers on materiality ambiguity.
- **Council shape:** #4 Judge + Jury (`council-shapes.md`) — Senior Accountant drafts (defendant), Auditor + Compliance Officer cross-examine (jury), Controller judges. Subjective rankings happen on materiality + risk severity; dissent is valuable evidence, not noise to suppress.

Don't pick #5 Devil's Advocate by default — performative dissent on accounting entries wastes tokens. Real dissent comes from genuine policy ambiguity; Auditor should not invent flaws.

## Implementation notes

- **Hard-coded chart-of-accounts is a feature.** The council exists to refuse free-form invention. Every account code traces back to DNA via tool call — runtime check, not prompt nudge.
- **Closed-period rules and SoD matrix enforced at the tool layer.** A persona without write permission to closed periods literally cannot call the tool — safety holds under prompt injection.
- **Sparse-signal closed loops use proxies.** Don't wait weeks for audit findings; instrument rule-lint violations and override rates as fast feedback. Audit findings are for periodic recalibration.
- **Cross-family judge mandatory** for Controller sign-off — same-family bias on financial judgements is exactly the failure mode regulators distrust.
