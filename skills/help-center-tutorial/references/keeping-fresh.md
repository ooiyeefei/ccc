# Keeping tutorials fresh

Three situations share one mechanism: the sheet is the source of truth, so a task is re-recordable by running its sheet again. Pick yours.

## A. A UI change, on tasks that have sheets

Replay needs the staged film workspace and its twin (`film-line/references/staging.md`); stage them first if they do not exist. `derive.py` ships the queue and the hash tools, not a runner: wiring `queue` into the pull-request or release job and scheduling the weekly sweep are the project's to add, and until they are, the replay is run by hand from the queue's output.

1. **Queue.** Every sheet lists `surfaces`. `scripts/derive.py queue SHEETS_DIR --changed <files from the pull request or release>` prints the sheets that name a changed surface. A script produces that list, not memory. Match rules: `file:` is a glob over the path, `route:/a/b` matches a directory part of the path, `component:Name` matches the file name with dashes and underscores ignored.
2. **Replay.** Run each queued sheet read-only on the film workspace, up to its first writing step. Check three things: every target still resolves, every proof text still shows, and each screenshot still matches its stored hash. `derived.json` holds an average hash per screenshot (needs Pillow); `derive.py distance A B` is the Hamming distance. Choose the threshold on known-good pairs: re-derive an unchanged task twice and take the largest distance seen with headroom.
3. **Decide.** All three pass for every step: restamp "checked on" and leave the media. A task is restamped only when every step was replayed. A writing task is replayed in full on the twin; where there is none, its footer keeps the old date and the report lists it as partly checked. Any fail: mark the task stale, re-record that task only, derive, replace its media. A stale task stays in the report until it passes.
4. **Sweep.** Replay every sheet weekly: read-only ones on the film workspace, writing ones on the twin. The surface map misses indirect changes, and the sweep finds what it missed.
5. **Mass failure.** A shared component change fails many sheets at once. Fix the shared selector in its one named file first, replay again, and only then re-record what still fails.
6. **Approvals.** A renamed label or a moved selector is a maintenance edit: show the approver one diff per domain. A changed step list reopens the per-task gate (`SKILL.md`, step 2).

A writing step is replayed only on a resettable workspace or its twin, under the guard and the write ledger (`film-line/references/staging.md`).

## B. Media that is already wrong, with no sheets yet

You cannot replay what has no sheet. Backfill in this order:

1. **Inventory** the articles and their media: title, domain, last edit, traffic if known. Mark each keep, merge or retire. Duplicates merge before anything is recorded.
2. **Triage** the keepers by traffic and by how wrong they are, text as well as media: a redesign renames labels, so the steps may be stale too. Start with the most-read tasks.
3. **Sheet** each kept task. One approval per domain batch, not per article; the batch table is the same `id | step | label | proof | writes` table. Draft sheets from the existing article's steps, then correct them against the real screens.
4. **Record and derive** per task. An article without a sheet is allowed to stay as it is, marked legacy, until its turn; the page says when it was last checked or that it has not been.
5. Meanwhile, an article whose pictures are known wrong carries a visible "being updated" note rather than a confident wrong picture.

## C. Making replay cheap

Prefer read-only tasks and stable selectors. Keep `surfaces` honest: a route or component that the task never touches does not belong, and one it does touch must be there. The footer "Checked against build X on date" is written by derive and updated by every passing replay; it is the only freshness claim the page makes.
