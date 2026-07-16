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

## The throughline, three times

One sentence IS the pitch. Say it near the open, once in the middle, and as the close. Examples that worked: "When the customer changes, the offer changes." / "The AML that learns." If you cannot write the throughline in under ten words, the pitch is not ready - fix the story, not the script.

## Numbers: few, concrete, landing twice

Pick 2-3 numbers maximum. Each lands early and returns in the close ("Twelve hundred alarms, down to thirty-five"). Spell numbers out in scripts meant to be spoken (voiceover artists and TTS both stumble on digits). Every industry number is **cited or cut** - if a claim can't name its source, it doesn't go in the script.

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

## Honesty guardrails

- **Claim only what's wired.** If a feature is roadmap, it is narrated as roadmap or not at all.
- When on-screen labels contradict reality (a demo worklog showing different model names than production), use generic tiers: "a fast model for the routine calls, our strongest model for the hard ones."
- Precision rewrites beat impressive vagueness: "we're tracing relationships between accounts, not claiming it's the same banknote"; a traversal metric is "volume traversed", not "money moved".
- Don't cram defenses into the pitch. Anticipated hard questions live in appendix slides and a Q&A brief, delivered only when asked.
