# Version history

htmldrop keeps no history: every push overwrites the page at the same link. When a page
will change after people have read it (a proposal, a quote, a spec under review), keep the
history inside the page with `scripts/versions.py`. Readers get a **Version history** button
and a sidebar, as in Google Docs; an older version opens read-only beside it. The older
versions are embedded in the page, so one link and one password cover them all.

```bash
S=<this skill>/scripts
python3 $S/versions.py snapshot /abs/page.html --label "en=Prices and add-ons" --label "zh=价格与附加选项"
python3 $S/versions.py build    /abs/page.html    # republish; the current version changes in place
python3 $S/versions.py list     /abs/page.html
python3 $S/versions.py restore  /abs/page.html    # after `htmldrop pull`, before editing
htmldrop push /abs/page.html --feedback --password  # the same password as last time
```

Versions are stored in `<page-stem>.versions/` beside the page. That folder is the history:
commit it with the page.

## Snapshot or build: decide before every push

Every push follows one of the two, so the stored current version always equals what readers
last saw.

- **snapshot** when a reader would want to compare: new scope, new prices, a new section, an
  answer to their comments. Label what the version contains, in the reader's words
  ("Appointments priced as an add-on"), never the process behind it ("after Tuesday's call").
- **build** for changes nobody needs to compare: typos, layout, wording.
- **build, never snapshot, to remove something readers should not see**, such as an internal
  rate or a colleague's note. A snapshot keeps the old copy one click away in the history.
- **Ask the user when the change is commercial** (a price, a date, a commitment) and readers
  may already have seen the old one. In place hides the old figure; a new version shows the
  change openly. That is their call, not yours.

## Rules

- **Readers' history only.** Every version stays readable by everyone with the link. Start the
  history at the first version readers may see; internal drafts never go in. To start from
  today on a page with earlier drafts, snapshot the current page as v1.
- **Same password on every push.** The password locks the page and its comments. A new one
  locks out everyone who has the old one. If it was not saved, ask the user; do not generate
  a new one.
- **Comments belong to the current version.** Older versions carry no comment widget, and
  the sidebar says so.
- Leave the block between `<!-- htmldrop-versions:start -->` and `<!-- htmldrop-versions:end -->`
  alone; `build` rewrites it.
- **After `htmldrop pull`, run `restore` before editing.** The pulled page holds the older
  versions but not the folder. Until you restore, the script refuses to snapshot or build
  rather than drop the history.

## Placement, look and limits

- Put `data-versions-slot` on the element the button should sit in, usually the header. With
  no slot the button floats at the top right. Set `--vh-accent` on `:root` for the accent
  colour; the panel uses the system `Canvas` colours, so it follows light and dark mode.
- The sidebar's own words come in English, Chinese and Malay and follow `<html lang>`, so they
  switch with the language toggle (`references/languages.md`). Labels and notes take any
  language code; a missing one falls back to English.
- An older version opens in the reader's current language, in a sandboxed frame. Its scripts
  run, but settings saved in the browser do not carry over.
- Each older version adds about a third of its size (gzip and base64): a 190 KB page adds
  about 64 KB per version. Ten versions are fine; a hundred are not.
- Opening an older version needs `DecompressionStream` (Chrome 80, Safari 16.4, Firefox 113 or
  later). Older browsers see a message instead.
