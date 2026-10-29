# Staging - the film workspace

Staging is its own phase because every later cost comes from it. It starts after the plan is approved, because the plan says what data each beat needs. Writing a staging plan is not staging: draft it at any time, and run it only after the nod. Do it fully, keep a write ledger, rehearse on a twin, and only then hand over to recording. Nothing in this file needs the recording steps.

## The workspace

- One film workspace per body of films, with a plain made-up business name. The header, the printed documents and the e-mail subjects carry it, so a name containing a banned word fails every frame.
- A **twin**: a second workspace set up the same way under a neutral name, never filmed. Every script is proven on the twin first. Its name on screen means the take was a smoke take.
- Find out whether the workspace can be reset: ask the product's operators, since a workspace flagged as a demonstration tenant usually has a reset and any other has none. A resettable one makes a retake cost minutes. One that cannot be reset undoes a write by voiding or reversing record by record, which leaves traces on screen, so each live write there is filmed once.
- A demonstration tenant may also hide staff accounts from lists and pickers and may print words such as "presenter" or "designated". Prefer a plainly provisioned workspace. A tenant whose screens print a banned word fails the preflight and is not used.
- The twin has its own logins on the film domain, and its own anchor date for the rehearsal if D is not yet named.

## The industry brief

The brief (`industry-brief.md`) is filled in before the plan. Staging turns its first five fields into a business: the chart of accounts with the trade's own accounts on top of the standard ones, the items and parties in the trade's units, history dated in the past for as long as the plan's month needs, and the cast as real logins. Tutorials reuse whichever industry workspace exists; do not stage a second business to re-film the same screen.

## The cast

- The owner login creates, or is granted, the workspace through the product's own setup first. The other personas are then invited into it and sign up from the invitation, so no stray personal workspace is made. Personas are not platform staff.
- Prefer logins that belong to one workspace only. A login with several workspaces has a saved-workspace pointer that decides where it lands and is shared by every session using it; change it only through the real workspace switcher, log each change, read it before every take and put it back when the window closes.
- Avatars, profile menus, team lists and any e-mail column are never on a recorded frame: they show login addresses. List them in the recorder brief as forbidden screens.
- Session files are created by a re-login script that reads credentials from the environment in process and prints none. Mode 600, never in the repo.

## The guard

Four layers, in this order:

1. **Allow-list**: the write script holds exactly one workspace id and refuses any other. For the very first write (creating the workspace) there is no id yet: check that the name does not already exist, take the id from the server's reply, write it once to a read-only file, and that file becomes the allow-list. Count what the product creates by itself, so the final audit is not fooled.
2. **Read before**: it asks the server which workspace the session is acting in and aborts unless that equals the allow-listed id.
3. **Read after**: it reads the written record's own workspace id and stops the run on a mismatch, writing both reads into the log.
4. **Negative test**: aim the script at the wrong id once and watch it abort, arranged so that a broken guard would write to the twin and never to the film workspace (a session in the twin, the script aimed at the film workspace's id). A guard never seen to refuse is not a guard.

How to ask the server "which workspace is this session acting in" and "which workspace owns this record" is product-specific. Find the read the product's own UI uses for each during the rehearsal and write it into the guard. Until both are found the guard is UNVERIFIED and no write runs.

## The data pack

- Documents (bills, receipts, statements) are generated with a real text layer, plain generic vendors, no real brand or bank, and values that match the record they will be attached to. A receipt showing 45.00 on a claim typed as 12.34 teaches the reader the wrong pairing.
- Generate into the project scratch folder and upload through the real input. Never commit them.
- Dates are relative to one named recording-day parameter, D. The owner names the day. Until then D is a marked placeholder, and the pack build refuses to run while it is one. Staged history is dated before D, live beats at or just before D, and nothing after D.
- Time zone: several screens pre-fill the date in UTC while the business uses its own zone. Work inside one UTC date: for a business at UTC+8 that means starting after 08:00 local time, and finishing a posting chain before the next 08:00.
- File names show on screen. They cannot be renamed after upload, so name them plainly before staging.

## The rehearsal

Run these checks on the twin and write each result down as PASS, FAIL or UNVERIFIED in a results table in the staging folder. UNVERIFIED stays visible in the report; it is never rounded up.

1. The write path works end to end for each beat, and what is refused, with the refusal text.
2. Which screens take a typed date and which always use today.
3. What each form saves on its own before the button is pressed (autosave, drafts, numbers used).
4. What leaves traces: leftover documents, voided rows, used numbers, file names.
5. Outbound paths (e-mail, reminders, submissions): none touched, or addressed to the film domain.
6. The preflight scan: dump the page text of every planned screen, the tooltips and the generated documents to text files, then run `scripts/frame_scan.py --text dumps/*.txt --ban <the company's list> --allow-domain <film domain>`. Matching is whole word, and a locale needs its own equivalents.
7. First-load skeletons and slow panels, so pages are warmed before a take.
8. Periods open, roles visible, approval rules as the story needs; the new workspace's plan or trial state and any billing or trial e-mails; that invitation and sign-up mail to the film domain can be read.
9. Which known defects sit on the path, so the plan films around them.
10. The guard's negative test.

A beat that cannot be staged, found here, reopens the plan.

## The write ledger

One row per production write, appended at the moment of the write, in `LEDGER.md` in the film's staging folder:

`time (UTC) | step | what | where in the UI | before | after | undo`

Writes to the twin go in the same ledger, marked `twin`. A switch of a saved-workspace pointer is a write. One row is one save in the UI (an upload and its record are one row); records the product creates by itself get no row and are counted in the guard's baseline. A smoke take that stops before the first write adds no row. The write ledger is also the "left behind" list in the hand-back.

## Gate

Staging is done when: the preflight scan of all planned screens shows zero banned words and no personal address; every cast pointer was read and asserted; the write ledger is complete; the twin rehearsal results table is written and the guard's negative test passed. Then phase C.
