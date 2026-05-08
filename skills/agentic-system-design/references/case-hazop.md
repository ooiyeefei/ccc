# Case Study — HAZOP / Safety Analysis

## Domain summary

HAZOP (Hazard and Operability) studies walk a process design node-by-node, applying guide-words (NO, MORE, LESS, REVERSE) to each parameter (flow, pressure, temperature) and identifying causes, consequences, and safeguards. Inputs are P&IDs, equipment lists, line conditions, operational context packs, and incident-DB priors; outputs are scenarios with foreseeability verdicts, IPL (Independent Protection Layer) lists, and LOPA (Layer of Protection Analysis) inputs. Blast radius per missed scenario is enormous — one mis-scoped LOPA can leave a major hazard undetected.

## Natural council to design

- **Foreman role — HAZOP Facilitator**. Orchestrates per-deviation deliberation, enforces V3 state masking (each persona consumes a masked slice, not full state), drives the guide-word walk.
- **Process Engineer** — mechanical/flow causes, equipment internals, scope inside battery limits.
- **Safety Engineer** — consequence severity, SIF/SIL classification, escape/escalation paths, boundary scope.
- **Operator** — procedural angle, human-error modes, normal-vs-startup-vs-shutdown ops, alarm response realism.
- **Instrumentation Engineer** — BPCS/SIS interaction, alarm setpoints, control loops, override paths.
- **Maintenance** — isolation procedures, SIMOPs, common-cause failures, bypass states during maintenance windows.

**Sub-agent spawn conditions:**
- *Any persona promotes to Incident-DB Researcher* (depth-3) on `BORDERLINE` foreseeability or `HYPOTHESIS` novelty verdict — drills prior incidents at this site/industry/equipment-class. Tool palette: `incident_search`, `incident_detail`, `cite_event`. Read-only.
- *Safety Engineer spawns LOPA Boundary Tester* (depth-3) on stricter-tolerance mutation — assembles the scenario for downstream pure-Python LOPA math, never performs the math itself.

## DNA (structured state)

`StudyNodeDNA` — per-node persistent state, V3-masked per persona:

- **design_intent** — the node's intended function (e.g. "transfer feed at 50°C, 3 barg, 10 m³/h").
- **battery_limits** — physical scope boundaries; inside vs upstream/downstream.
- **equipment_tags** — canonical tag list (`P-101A/B`, `V-204`); narratives must cite, never invent.
- **pid_topology** — graph of nodes, lines, valves, instruments from P&ID.
- **line_conditions** — design pressure/temperature/flow/composition per line.
- **operational_context_packs** — startup/shutdown/maintenance/normal/emergency states, routed per persona.

V3 masking: each persona consumes only its slice. Operator does not see equipment internals; Process Engineer does not see operational packs by default. Prevents cross-role prompt-poisoning and enforces realistic role boundaries.

## Tool-loop & sub-agent design

**Foreman tools:** `call_persona(role, deviation, masked_state)`, `record_cause`, `record_consequence`, `vote_foreseeability`, `escalate_to_lopa`, `finalize_node`.

**Critic verification tools per persona:**
- Process Engineer: `lookup_equipment` (must hit `EquipmentAliasEntry`), `pid_neighbors`
- Safety Engineer: `lookup_sif_sil`, `consequence_template`, `spawn_lopa_boundary_tester`
- Operator: `lookup_procedure`, `human_error_priors`, `spawn_incident_db_researcher`
- Instrumentation Engineer: `lookup_alarm`, `lookup_loop`, `pid_valve_details`
- Maintenance: `lookup_isolation`, `simops_check`

**Sub-agent palettes:**
- Incident-DB Researcher: `incident_search`, `incident_detail`, `cite_event` — read-only; never writes back.
- LOPA Boundary Tester: `assemble_scenario`, `validate_independence` — structured payload for pure-Python LOPA solver; does no math.

System prompt skeleton for the Facilitator:

```
You are the HAZOP Facilitator running deviation {{guide_word}}+{{parameter}} on node {{node_id}}.
Tools: call_persona, record_cause, record_consequence, vote_foreseeability, escalate_to_lopa, finalize_node.
Mandatory: invoke ALL 6 personas before voting; each persona reads only its masked DNA slice.
On BORDERLINE or HYPOTHESIS verdict, instruct the persona to spawn Incident-DB Researcher.
Never call the LOPA solver — escalate_to_lopa only.
```

## Memory verdict

Mostly **context-mgmt**. Closed-loop learning exists but is bounded:

- **Signal**: held-out incident-DB recall@k on historical events; expert reviewer agreement on a sample.
- **Latency**: continuous (eval is offline).
- **Ground truth**: regression set of historical incidents the system never saw during design.
- **Critical constraint**: **never let the agent's own write-back update the incident DB.** Self-confirming loop destroys recall as a real signal.

State-cache accumulations: site-level failure modes (drift-monitored), equipment-class deviation priors (expert-gated), per-campaign episodic log. Never auto-promote site-level priors into per-node DNA without expert sign-off.

## Anti-patterns specific to this domain

| Anti-pattern | Test | Fix |
|---|---|---|
| **Generic guide-word output** | Personas produce variants of the same "MORE flow → overpressure" line | Persona-distinct prompts + V3 masked slices; mandate role-specific reasoning |
| **Hallucinated equipment specs** | Narrative cites tag `P-999` not in equipment list | Equipment cites must hit `EquipmentAliasEntry` / `pid_valve_details`; refuse otherwise |
| **LOPA done by LLMs** | Council computes risk reduction factors / IPL credit | Pure-Python deterministic LOPA; council stops at scenario assembly; LLMs never multiply PFDs |
| **Breaking V3 state masking** | Persona prompts include full StudyNodeDNA "for context" | Each persona reads its masked slice only; cross-persona flow via Foreman's `record_*` tools |
| **Incident-DB write-back self-loop** | Agent appends conclusions to the DB used as ground truth | Incident DB read-only; held-out incidents from human-curated regression set |
| **Foreseeability sycophancy** | Personas defer to whoever spoke first on borderline | Sealed-vote: each persona records verdict before seeing others; reward dissent in log |

## Recommended pattern + council shape

- **Pattern:** #4 Plan-and-Execute (`patterns-catalog.md`) — guide-word walks are largely knowable in shape; per-deviation deliberation has low real-time adaptation; auditability is paramount. Plan the node walk, execute deviation-by-deviation, re-plan only on novel hazard discovery.
- **Council shape:** #1 Parallel Critique (`council-shapes.md`) — 6 specialists with sharply distinct domains (Operator does not duplicate Process Engineer's analysis). Diverse first-drafts plus structured deliberation, NOT iterative refinement. Use #5 Devil's Advocate as a *secondary* shape on `BORDERLINE` cases — a dedicated dissent persona pre-mortems before vote.

Don't pick #6 Generator-Discriminator: HAZOP isn't about ranking many candidates, it's about exhaustive coverage. Don't pick #7 Tournament: deviations aren't competing for a single winner.

## Implementation notes

- **V3 state masking is a safety property, not optimization.** Enforced at the tool layer via `call_persona` dispatch, not by trusting prompts. Role-realism holds under model misbehavior.
- **Pure-Python LOPA math is non-negotiable.** PFDs and risk reduction multiply across IPLs — LLMs hallucinate arithmetic with no rubric to recover. Council ends at scenario assembly; math runs deterministically.
- **Incident-DB read-only invariant.** Hold even during adversarial reviewer passes. Agent-writable DB destroys recall@k as a real signal.
- **Masking matters more than model routing here.** Cross-family helps, but realistic masked slices matter more — Operator without equipment internals is a sharper Operator.
