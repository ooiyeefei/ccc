# Localisation

A locale is produced by replaying the sheet in that locale, never by translating a screenshot. The sheet is the same, the strings differ, and the take is new.

## Before you start

1. **Does the product render in this locale?** Check by opening the app in it. If it does not, there is nothing to replay. The honest fallbacks are English screenshots under translated steps with the English labels shown in brackets, or no localised article yet. The owner chooses; do not pick one silently. A third route, adding the locale to the product, is the owner's call and outside this skill. For the English-screenshot fallback, derive from the English take with wording-only strings and no `locale`, and say on the page that the pictures are in English.
2. **Is the navigation translated?** The domain names mirror the product's menu, so they need the translated menu.
3. **Does every article to translate have a sheet whose plan hash matches its take?** A legacy article has none: sheet it first (`keeping-fresh.md`, B).
4. **The new takes are new recordings.** A locale's `proof` and `action` change what is recorded, so the locale's plan is approved like a new task (`SKILL.md`, step 2), as one batch per domain. A writing task replayed in a locale is another guarded write take.

## The strings file

`strings.<locale>.json`, keyed by step id, passed to `derive.py` with `--strings`:

```json
{
  "locale": "ms",
  "title": "...", "goal": "...", "result": "...", "path": "...",
  "who": ["..."], "before": ["..."], "troubleshooting": [{"when": "...", "then": "..."}],
  "related": ["..."], "not_covered": "...",
  "_headings": {"steps": "Langkah", "checked": "Disemak pada versi {build}, {date}."},
  "open": {"do": "...", "label": "...", "caption": "...", "alt": "...", "proof": "...", "action": {"click": "..."}}
}
```

- Wording keys (`do`, `label`, `caption`, `alt`, and the top-level text) never force a re-record.
- `proof`, `action` and `locale` are recorded fields: they name what the harness waits for and clicks in that locale's UI. Record the take from `derive.py plan --strings strings.<locale>.json`, so the plan hash stamped in its sidecar is the locale's own. An English take cannot pass as a Malay one, because the locale is part of the hash.
- `label` must appear word for word in `do`. Inflection and word order make this fail more often outside English; `lint` reports it.
- A time, number, date or currency in `proof` is copied from the target locale's screen.

## Outputs

Files carry the locale: `<task>[.platform].<locale>.md`, its images, clips, captions and chapters, and `<track srclang>` in the page. One `--out` directory can hold every locale without collisions. Alt text and captions come from the same strings. The subtitle file is per locale. A voice is optional and per locale; the default tutorial clip is silent with captions.

## The tree

The same tree per locale, under the app's own locale code and prefix, with the slugs unchanged. Search words (the user's other words for a task) are per-locale metadata outside the strings file.
