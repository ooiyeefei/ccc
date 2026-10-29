# The article

The article is generated from the step sheet and never hand-edited. A fix goes into the sheet and the article is regenerated, so a re-export cannot lose a hand edit.

## The unit

```
Title                     verb and object
Goal                      one sentence, the outcome in the user's words
Who can do this           roles
Path                      Calendar > Add > Blocked time
Overview clip             optional, 30 to 90 s, captioned, chapters equal to steps
Before you start          prerequisites, each linking to its own article
Steps                     numbered, one action each, UI label in bold,
                          a screenshot with a highlight, an optional 3 to 8 s clip
You should see            the visible result, with its frame
If something goes wrong   two to four items from real refusals
Related                   up to three; one "Up next"
Footer                    "Checked against build X on date" and the sheet id
```

## Writing the steps

- Verb first, second person: "Click **Save**." Web steps say click, mobile steps say tap.
- Bold the exact UI label and nothing else.
- One action per step. Where the screen changes without the user doing anything, the step says what appears: "The form opens."
- The goal comes first, so a reader knows in a line whether this is the task they want.
- State the role and prerequisites before the steps, never as a surprise inside them.
- Name the result. "You should see" is a checkable sentence, not a reassurance.
- Troubleshooting repeats the product's own refusal wording so a reader can match what their screen says.

## Screenshots

Every screenshot comes from the take, at the step's proof time. It carries a highlight on the element the step names. It never shows a login address, a staff menu or a banned word (`film-line/scripts/frame_scan.py` runs on the images as on the video). The footer date says when the pictures were last checked, which is the trust signal the competitors lack.

## Alt text and captions

- **Alt text** states what the picture shows and what to do about it: "The calendar with the Add menu open and Add blocked time highlighted."
- **Captions** are the step's `caption`, short enough to read muted. The subtitle file is always produced; burned-in captions are for the overview clip only.
- Everything a clip says is also on the page as text, so the page works without sound or video and the steps are the transcript.

## The Concept article

A Concept article explains how something works and is not a sequence of steps. Layout: title (a noun phrase or "How ... works"), one paragraph saying what the reader will understand, the rules or states as a short table or list, one worked example with its screenshot, and the tasks that use it as links. It has no step sheet and no clip; a screenshot is allowed when it explains a state, and it is regenerated from a sheet whenever one task already shows that state.

## Variants

Web and mobile, or roles, are tabs with their own numbered steps and their own screenshots, each from its own sheet run. Plan limits and role limits are stated inline at the step they affect.

## Video on the page

An overview clip sits at the top with a fallback link for players that fail. Each step may deep-link to its second in the clip (`article.json` holds `video_t` per step). Loop clips are muted, autoplay and short.
