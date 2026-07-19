# Storyboard - the approved plan of the film

The storyboard is the contract between what you will film, what you will claim, and how long each claim gets. It is written BEFORE staging and approved BEFORE capture. Everything downstream - holds, milestones, narration windows - derives from it.

## The five columns

One row per beat. Four columns is not enough: the two that get dropped (`action`, `narration`) are the two that make the film honest and the holds real.

```
# | phase  | screen              | action                        | proof                          | narration (draft)                                  | dur
--|--------|---------------------|-------------------------------|--------------------------------|----------------------------------------------------|----
1 | entry  | Empty queue, logged | none (entry animation)        | this is a real product a real  | "An analyst opens a queue of twelve hundred        | 6s
  |        | in as analyst       |                               | person opens                   |  overnight alerts."                                 |
2 | setup  | Queue, 1200 rows    | click #run-triage             | it ingests real volume         | "The rule engine closes eleven hundred sixty-five  | 8s
  |        |                     |                               |                                |  under policy."                                     |
3 | loop   | Case detail, work   | click .case-row, wait for     | THE AGENT ACTUALLY RAN - tool  | "It traced the counterparty chain itself - every   | 12s
  |        | log streaming       | .worklog-done                 | log visible, steps timestamped |  step is on the record."                            |
4 | payoff | Sealed reason panel | scroll to .reason-seal        | the output is auditable        | "Each decision closes with a sealed reason."       | 6s
```

- **screen** - what a viewer sees. Name the actual view, not a feature ("Case detail with work log streaming", not "the agent working").
- **action** - what the driver does to cause the state change, in terms you can actually code (`click #run-triage`, `wait for .worklog-done`). This is the column that catches unstageable beats at planning time instead of mid-take. A beat whose action is "none" and whose screen never changes is a still image - justify it or cut it.
- **proof** - the claim this beat earns. A beat that proves nothing gets cut.
- **narration (draft)** - the actual sentence, not a topic. Topics always undercount; a real sentence tells you whether 6 seconds is honest. pitch-craft polishes it later, but the draft is what makes `dur` mean something.
- **dur** - hold seconds, `>=` the narration segment's read time (~2.4-2.6 wps for voiceover) plus ~0.5s of breathing room.

Total the `dur` column and check it against the pitch budget before you show anyone. Target duration comes from the budget, not from how much footage exists. If there is no pitch budget - demo-video used standalone - ask for the target length or the submission cap *before* writing durations; a storyboard sized to nothing has to be re-cut after approval.

## Journey coverage

The film must let someone who has never seen the product follow a real user from opening it to the result. Tag each row with its phase (`entry` / `setup` / `loop` / `payoff`) - a sixth column, or a marker in the `screen` cell. Coverage you can see in the table is coverage you can check; coverage described in prose gets skipped. Before approval, confirm all four phases appear:

| Phase | Must show | Common miss |
|---|---|---|
| **Entry** | The real entry point - the state a user actually lands in | Opening mid-flow on a pre-populated screen |
| **Setup** | How the user gets the system to the interesting state (the input, the config, the trigger) | Cutting straight to results, so the input is invisible |
| **Core loop** | The thing the product does, happening on camera | Showing the output without the work that produced it |
| **Payoff** | The result, and why it beats the alternative | Present - this is the beat nobody forgets |

Demos fail this by being built backwards from the money shot. A film that opens on the final feature reads as a mockup: it answers "what does the screen look like" and none of "what is this, who uses it, how do you get there".

The strongest proof should still land last - but get there by ordering the journey correctly, not by front-loading spectacle. In a well-chosen flow the payoff *is* the last step of the loop.

Phases must be real beats, not token rows. If the payoff eats more than ~40% of total runtime, or entry/setup/loop are one perfunctory second each, the film is still a money-shot demo wearing a journey's clothes.

## The claim-to-frame audit

Run the storyboard in both directions before approving it:

- **Forward** (beat -> claim): every beat's `proof` column is filled. No proof, no beat.
- **Backward** (claim -> beat): every claim the narration will make names the beat whose frame shows it. Walk the draft narration sentence by sentence and write the mapping out - an audit you only run in your head leaves nothing for the user to check at the gate.

The backward pass is the one that catches overclaiming, and it binds hardest on **agent actions**, which are invisible by default:

| Claim | What must be on screen |
|---|---|
| "the agent searched the case history" | the tool-call log, with the search visible |
| "it updated its memory" | the memory/state panel, before and after |
| "it chose the cheaper model" | the route badge, cost line, or model label |
| "it caught the discrepancy itself" | the flagged row highlighted by the system, not by you |

**A label is not a trace.** The commonest way this rule gets faked: the `proof` column reads "UI shows 'Searched 42 sources'". A status string in which the app *asserts* the action is exactly as unfalsifiable as narration asserting it - both are claims, neither is evidence. What counts is the artifact of the work: the sources listed, the tool call with its arguments, the memory entry with its content, the before/after diff. Ask of each proof cell: could this pixel be rendered by a product that never did the thing? If yes, it is not proof.

If the app renders none of that, you have three options in order of preference: **add a beat** that surfaces the evidence (often the app already has a debug/log panel worth showing), **build the surface** if the demo depends on it, or **cut the claim**. What you may not do is narrate invisible work over a static screen - that is the exact move that makes a demo feel fabricated, and it poisons the true claims around it.

Narration is written after the recording (pitch-craft, against verified timestamps), but the *claims* are fixed here. Discovering at scripting time that your best claim has no frame means re-shooting.

## Running the approval gate

1. Show the user the storyboard - the whole table, plus the total duration against the budget.
2. **Assert journey coverage explicitly**: name which row carries entry, setup, loop, and payoff. If a phase has no row, say so and say why. This is the check most likely to be skipped, because the film still looks fine without it.
3. **Emit the backward audit**: list each claim the narration will make and the row whose frame shows it. A claim with no row, or one whose only proof is the app's own status label, gets cut or gets a real beat. Walking it "in your head" produces nothing reviewable - write the mapping out.
4. State explicitly what you will NOT show, and why (beats you cut, claims you dropped for lack of a frame). Silent omissions surface later as "why isn't X in here".
5. Flag anything you could not stage, and the option you recommend (add a beat / build the surface / cut the claim).
6. **Stop. Wait for approval or amendments.** No staging, no smoke take, no capture.

A blanket "just do it" / "I trust you" given *before* the storyboard existed is not approval of it - the user has not seen the plan. Show the table and wait. (Approval also expires if the beat list later changes; see SKILL.md step 7.)

A three-beat demo gets a three-row storyboard. The gate is the round-trip, not the paperwork - do not inflate a small film into a document, and do not skip the round-trip because the film is small.

If the user asks for a title card, a logo bookend, or a caption overlay, that is their call - record it as an approved exception in the storyboard with the beat number it applies to. The default remains: the demo film shows the running product.

Re-records are cheap in tooling and expensive in narration re-sync, so the gate pays for itself the first time it catches a missing journey phase.
