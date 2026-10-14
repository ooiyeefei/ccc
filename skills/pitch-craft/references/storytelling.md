# Storytelling - the craft rules

These rules are distilled from scripts that won stage time: problem-first Jobs-style narration, hackathon pitches, and VC-grade demo films. Each rule exists because its violation is a specific, observed failure.

## The opening: hook before names

Cold-open with tension or a concrete fact, never with introductions. "Every bad loan was once an approved loan" earns the next 30 seconds; "Hi, we're team X" spends them. The team intro comes **after** the hook lands, as one warm sentence, and only with real credentials - never invent a backstory:

> (warmer, look up) "I'm Yee Fei, this is Windrich, we're team Groot, and this is what we built."

If presenting solo, one line: name, team, one true credential that earns trust for THIS pitch ("I've shipped loan-document AI inside a real bank").

## Plain words, one analogy per abstraction

Every technical abstraction in the script gets exactly one everyday analogy, said once, then dropped:

- rigid rule engines that over-fire -> "a smoke detector that shrieks at burnt toast"
- a mule ring -> "a relay team for dirty money"
- a deterministic model vs an LLM -> "a calculator, not a fortune teller"

One analogy per idea. Two analogies for the same idea means neither landed. Zero means the audience is decoding jargon instead of listening. Never say the jargon word when the plain phrase exists: "a bank's compliance desk", not "AML alert triage optimization".

## The throughline: bookend it, then emphasise where it is earned

One sentence IS the pitch. Examples that worked: "When the customer changes, the offer changes." / "The AML that learns." If you cannot write the throughline in under ten words, the pitch is not ready - fix the story, not the script.

**Open with it and close on it.** A tagline that bookends the pitch reads as deliberate, and the close is where it has to land.

**In between, restate it only where the story earns the emphasis** - the moment the demo proves it, the moment a number makes it undeniable. There is no required count. A writer who knows the story decides where the weight goes; a fixed number of repeats produces a jingle, not a pitch.

**When you do restate it, paraphrase.** Same idea, different words. Verbatim repetition sounds like an ad; a rephrasing sounds like someone who means it. The bookend can be the exact tagline both times, since that is the line you want remembered. Everything in between should vary.

## Numbers: few, concrete, landing twice

Pick 2-3 numbers maximum. Each lands early and returns in the close ("Twelve hundred alarms, down to thirty-five"). Spell numbers out in scripts meant to be spoken (voiceover artists and TTS both stumble on digits). Every industry number is **cited or cut** - if a claim can't name its source, it doesn't go in the script.

## Transitions: say where we are going

A film or a talk changes person, case or topic many times. A viewer inside the domain fills the gap; a viewer outside it is lost at the first unannounced switch, and says so afterwards: "it switches people without saying so". A speaker does what the script forgot: a half-sentence that closes what was open and names what comes next.

Add a transition line **only where the change would otherwise go unannounced**. Four lines in a hundred fixed the film above. A line at every cut is signposting, which `human-voice.md` strikes; the difference is whether the change is real.

| Moment | Say | Example |
|---|---|---|
| Framing the journey, once, early | The thread the viewer will follow | "Let's follow one application from start to finish." |
| A handoff to a new person | The handoff, from the thread's point of view | "Our application now waits for the branch manager." |
| The pivot to exceptions | An expectation the viewer already shares | "But we all know that not every application goes this smoothly." |
| A new topic | What the viewer is about to see, not the topic's name | "Next, let's look at which rules the bank can change for itself." |
| The last chapter | The question it answers | "Finally, can the bank prove all of this later?" |

Three habits of a speaker who does this well:

- **Close before you open.** The handoff line says where the thread *is* ("now waits for") before the next person appears. A jump that opens the next topic without closing the last one is what "abrupt" means.
- **Preview by sight, not by label.** "Which rules the bank can change for itself" tells the viewer what to look for; "the credit policy" is a label to decode while the screen is already changing.
- **Plain words over idiom.** "Desk to desk" was struck for "from start to finish". An idiom that lands with insiders is a gap for everyone else.

In a recorded film a transition rides over an approved transition card with music ducked under it; the card holds the measured line plus a breath, and final timestamps are re-derived after assembly (demo-video's `references/structure.md`). On stage it is the sentence said while the slide changes. In both, its words come out of the next segment's budget, not from thin air.

## Registers: recorded vs live are different scripts

| | Recorded voiceover | Live speech |
|---|---|---|
| Tense & voice | Present tense, describes what IS on screen | Addresses the room ("watch what happens") |
| Team intro | Close only ("by Groot") | After the hook, one sentence |
| Stage cues | None | Parenthetical: (pause), (look up), (say it flat and certain) |
| Pace | 2.4-2.6 wps | 2.0-2.2 wps (pauses, laughs, clicker) |
| Trim points | Not needed (fixed windows) | Mandatory - live always runs long |

Reusing a voiceover as a stage script produces a robot; reusing a stage script as voiceover produces dead air. Write both when both are needed.

## Delivery cues (live only)

Stage directions are part of the script, in parentheses, italic register: where to slow down ("slow down on 'quietly sinking' - the emotional beat"), where to go flat and certain ("a warning in a prompt is not a control" - the credibility line), where to breathe before the name. A cue the speaker ignores costs nothing; a missing cue costs the beat.

## The close

The close re-lands the numbers, restates the throughline, and names the thing: "Twelve hundred alerts, down to thirty-five. Every decision accounted for, each one making the next case smarter. SenTymel. AML that learns. By Groot." Then stop. Never end on logistics or thanks-slides; end on the name.

For a customer film the close has one more job: it leaves the viewer holding the offer. The shape that shipped: the last product line is the promise in the throughline's words; then a recap, walked part by part over one card (what is built in, what is the customer's own and what stands in for it, what is set up together); then the **call to action as the last line heard**: "Start with one branch and one product, and we'll work with your team for four weeks, on your own real applications." The owner moved the pilot line to the end so the ask is what the viewer leaves with, and the picture holds a beat after it (demo-video's `references/structure.md`). A pitch to judges closes on the throughline and the name; a pitch to investors on the ask (pitch-package's `references/audiences.md`).

## Honesty guardrails

- **Claim only what's wired.** If a feature is roadmap, it is narrated as roadmap or not at all.
- When on-screen labels contradict reality (a demo worklog showing different model names than production), use generic tiers: "a fast model for the routine calls, our strongest model for the hard ones."
- Precision rewrites beat impressive vagueness: "we're tracing relationships between accounts, not claiming it's the same banknote"; a traversal metric is "volume traversed", not "money moved".
- Don't cram defenses into the pitch. Anticipated hard questions live in appendix slides and a Q&A brief, delivered only when asked.
