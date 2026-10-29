# Narration - plain words, written to the frame

For marketing films, tutorials and flagships whose voice a stranger or a busy user hears. The clock, budgets and the honesty pass are `pitch-craft`; the audible AI tells are its `human-voice.md`. This file adds the rules the owner enforced after hearing a film that "reads too AI", and the scan that checks them.

## When

After the take, from the delivered file's cues (`demo-video`, gate 3), one line per beat window at 2.2 to 2.6 words per second. Never write final lines from the plan: a draft in the plan sizes the beat, the frame decides the words. Order: draft to the frame, humanise, pace-check, honesty pass again, read aloud once.

The pace band applies to a voiced line and its own window. The cut holds each shot for its line plus a breath, and a held proof frame with no voice is a silent window that is not scanned. A plan's draft lines are checked early against the brief's avoid list, so a rewrite never waits for QA.

## The rules

1. **State the thing, never its opposite.** "X, not Y" and "not just X" go. If a limit has to be said, say what the product does and where its edge is, once.
   - "It does not move the money." becomes "The transfer itself is made in your bank."
2. **One denial per limit.** A run of denials ("no setup, no config, no waiting") is a drumroll. Keep the one that is true and matters.
3. **No colon in a spoken line.** A colon that introduces a list becomes a sentence.
   - "Open the claim: the receipt sits beside the fields: shop, date, amount." becomes "Open the claim and the receipt sits beside the fields. The shop, date and amount are read from it."
4. **Cut filler.** just, simply, really, very, actually, basically, rather than, instead of, at a glance, "here is everything".
5. **Cut flourish.** Promotional adjectives, tagline cadence, a closing line that sounds like a poster.
6. **One name per thing.** The product is named the same way every time; never cycled to "the system" and "the platform".
7. **Present tense, describing the screen.** What is on screen at the cue, and nothing the frame does not show.
8. **Numbers as words, spoken only where the frame proves them.** No document number or amount is voiced unless it is on screen at that second; a figure that can move never forces a re-voice.
9. **Roles, never names.** "The owner", "the farm manager", "a farm hand", and "you".
10. **Honest verbs.** Suggests, you accept. Checked against the books. Worked out from the ledger. Never "automatically", "connects to your bank", "files for you" or "pays" unless the frame shows exactly that. State each limit once.
11. **Vary openers.** No sentence opener used six or more times in a film; never the same first word in two sentences of one line.
12. **ASCII hyphens, no dashes**, in narration, captions, cards and the subtitle file. A dash gives a voice model an unpredictable pause.

Text burned into a take (a harness caption, a callout) cannot be edited in post. Write it under these rules in the plan, before recording.

## Before and after

| Before | After |
|---|---|
| Open it: the bill on one side, what Groot read on the other. It can be wrong, so you check it against the paper. | Open it for the bill on one side and what Groot read on the other. It can get things wrong, so check it against the paper. |
| Fuel at the pump is a business expense, not a purchase invoice: a running cost that goes to Other Expenses, not Credit Purchases. | Fuel is different. You pay at the pump, so it is a running cost, and it goes in Other Expenses. |
| Here is everything the farm has bought on account. | Every bill the farm has bought on account is here. |
| These are bank lines, not accounting entries. | At this point they are bank lines, and nothing has been booked. |

## The scan

`scripts/narration_scan.py lines.json` reads `[{"id", "text", "window"}]` (the same shape the voicing script takes, plus the window in seconds, or `start` and `end`) and prints, per line: words per second against its window (or "pace unchecked" when there is none), digits, dashes, and every pattern above with the words around it; then the film-wide opener counts. `--avoid word,word` adds the brief's jargon list. A hit is a prompt to look, not a verdict: an owner-approved limit line may carry a "not" on purpose. Record such a line as an approved exception in the plan with the reason, so the next scan reads it as one.
