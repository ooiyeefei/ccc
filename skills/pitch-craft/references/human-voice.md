# Human voice - written to be said, not read

A script that reads as machine-written loses the room before the content lands. But narration is not prose, and most published de-slopping advice is written for prose. Applying it wholesale to a spoken script strips things this skill deliberately puts there, and misses the tells that only surface when someone reads a line aloud.

This file is the pass, sorted for speech.

## When it runs

**Before the final pacing check, after the first draft.** The pass rewrites, so it changes word counts. Run it after pacing and every window silently drifts out of the 2.2 - 3.1 w/s band.

Two consequences worth knowing:

- **Cutting filler buys clock.** "In order to demonstrate" becomes "to show" and you get two seconds back. When a segment is over its ceiling, run this pass before you cut a claim.
- **Re-run the honesty pass afterwards.** Rewriting for flow is exactly how "traced the counterparty chain" drifts into something vaguer or larger. Every rewritten sentence goes back through step 5, and for a demo voiceover, back through the claim-to-frame audit.

## The tells

Audible in delivery. Fix every one of these.

| Tell | Sounds like | Fix |
|---|---|---|
| Significance inflation | "is a testament to", "marks a shift", "plays a crucial role" | Say what happened |
| Promotional adjectives | "stunning", "seamless", "groundbreaking", "vibrant" | Observable facts. The demo is on screen; let it carry |
| Participle depth | "symbolizing", "reflecting", "showcasing", "underscoring" | A plain verb, or cut the clause |
| Vague attribution | "experts say", "studies show", "industry reports" | Name the source and date, or drop the claim |
| AI vocabulary | "delve", "landscape", "tapestry", "leverage", "foster", "crucial", "robust" | Ordinary words. Clusters of these are the giveaway |
| Copula avoidance | "serves as", "stands as", "boasts", "offers" | "is", "has". Elaborate verbs sound written |
| Tailing negation | "not just a linter, it's a teammate", "and that's the point" | State the thing once, directly |
| Synonym cycling | "the agent", then "the system", then "the assistant" | One name per thing. A listener cannot flip back to check who you mean |
| False range | "from ingestion to insight", "from setup to scale" | List what you mean, or name the one that matters |
| Passive and subjectless | "no configuration needed", "results are preserved" | Name the actor: "you skip configuration", "it keeps results" |
| Filler | "in order to", "due to the fact that", "has the ability to" | "to", "because", "can". Costs clock and says nothing |
| Stacked hedging | "could potentially help teams possibly reduce" | One qualifier, or none |
| Generic uplift | "the future looks bright", "a major step forward" | A specific next thing, or end on the last real claim |
| Authority trope | "what really matters is", "at its core", "the real question is" | Make the point. The framing adds no information |
| Signposting | "let's dive in", "here's what you need to know" | Start with the content. In a timed script this is pure waste |
| Aphorism formula | "X is the Y of Z", "symmetry is the language of trust" | A concrete claim about your product |
| Rhetorical opener | "Honestly?", "Look,", "Here's the thing" | Drop the fake pause |
| Chatbot residue | "I hope this helps", "great question", "let me know" | Should never survive to a script. If it does, the draft was not read |
| Change narration | "we've added a new panel that replaces" | Describe what it does now. The viewer never saw the old one |

Written-only patterns that do not apply to a spoken line: bold, title case, emoji, curly quotes, heading structure, hyphenated pairs in predicate position. Ignore them in narration prose.

Two exceptions that look written-only and are not:

- **Em and en dashes.** Inaudible, but the script is a document a person or a voice model reads. A dash produces an unpredictable pause. Use a comma, a period, or restructure.
- **Digits.** Already required elsewhere in this skill: spell numbers out for the reader. "Eleven hundred sixty-five", not "1,165".

## Carve-outs: what this skill does on purpose

Generic de-slopping flags these. Do not let it strip them.

| Pattern | Why it stays |
|---|---|
| **Throughline three times** | Thematic repetition across a script is how an audience remembers one idea. What is banned is triadic *phrasing* inside a sentence ("innovation, inspiration, industry insights"). Repeating your throughline at the hook, the demo, and the close is craft |
| **Numbers landing twice** | A figure stated once is heard by nobody. Say it, then anchor it |
| **Short sentences** | Speech needs them, and a clock rewards them. The tell is a *run* of fragments all landing like closers ("No setup. No config. No waiting."), not brevity itself |
| **One term, repeated** | Prose style dislikes repetition. Speech requires it - a listener cannot re-read |
| **Present tense, describing the screen** | The recorded register. It can look flat on the page and is correct in the ear |

## Tells that only exist in speech

Nothing in a prose checklist catches these. Read the segment aloud once; each of them announces itself.

- **Unsayable sentences.** If you run out of breath, it is too long. Nested clauses and long gaps between subject and verb parse on the page and collapse in the ear.
- **Punctuation you cannot hear.** A sentence that only makes sense with a parenthetical aside will not survive being read.
- **Sibilance clusters and tongue-twisters.** "Systems that seamlessly synthesise" is a retake waiting to happen.
- **Heard ambiguity.** Homophones and unexplained acronyms that are clear on screen and ambiguous aloud.
- **Words a voice model mispronounces.** Product names, surnames, unusual capitalisation. Test them in one segment before recording the rest.

## Credit

Pattern catalogue adapted for spoken delivery from the [humanizer skill](https://github.com/blader/humanizer) (MIT) and Wikipedia's *Signs of AI writing*. Both target written prose. The sorting, the carve-outs, and the spoken-only section are this skill's own. If the upstream list grows, check it against the carve-outs above before importing anything.
