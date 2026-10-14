# pitch-craft

The shared engine for **timed spoken scripts**: demo-video voiceovers, deck walkthrough narration, and live pitch speeches.

What it enforces:

- **Beats before words**: no prose until the beats (what's on screen) and the clock (windows or slot) exist.
- **Word budgets**: words-per-second math per segment (voiceover ~2.4-2.6 wps, live ~2.0-2.2), with the budget line written at the top of every script.
- **The craft**: hook before names, one analogy per abstraction, a throughline that bookends and is re-emphasised where earned, numbers that land twice, delivery cues, and a close that ends on the ask for customers or investors, or the name for judges.
- **Transitions and the close**: a spoken bridge wherever the beats change person, case or topic without saying so, and nowhere else; a close that lands the throughline and ends on the ask or the name.
- **Honesty**: claim only what's wired; precision rewrites over impressive vagueness.
- **Two registers**: recorded voiceover and live speech are different scripts, never reused as each other.
- **Re-sync**: the procedure for re-aligning a script after a re-record shifts the milestones.

Called by the `demo-video`, `pitch-deck`, and `pitch-package` skills whenever they need words against a clock.

## Use this, not that

- **Use pitch-craft when the deliverable is WORDS against a clock** - a voiceover, narration, or speech, new or re-synced.
- Building the deck HTML -> `pitch-deck`. Recording the footage -> `demo-video`. Deciding the whole pitch for an audience and slot -> `pitch-package` (which calls this skill for its scripts).
- Part of the pitch suite: decision guide in [skills/README.md](../README.md#the-pitch-suite---when-to-use-what).

## Structure

- `SKILL.md` - the workflow, from beats to a voiced, checked script
- `references/storytelling.md` - the craft rules, including transitions and the close
- `references/timing.md` - budgets, formats, trim points, re-sync
- `references/human-voice.md` - the audible AI tells and the carve-outs; what to respell for a voice model
