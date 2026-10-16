# Publication history (CLI 1.16.0+)

Every `htmldrop push` includes a History viewer. No version/history flag is required; `--feedback` independently enables annotation. Readers can select an earlier version, preview it and compare added/removed readable text. Previews disable scripts and external resources. Redlines compare text, not arbitrary styling or JavaScript changes.

```bash
htmldrop push /abs/report.html             # history, no annotation widget
htmldrop push /abs/report.html --feedback  # same history, with annotation
```

Use the same file identity for revisions. Unchanged source with unchanged protection is deduplicated; changing content or protection creates a revision. `--new-doc` deliberately starts fresh history and feedback identity, so do not add it to ordinary updates. The current published URL can change behavior when feedback or protection changes; return the URL actually printed by the CLI.

History starts with publishes made using a history-enabled CLI. It cannot reconstruct unsaved older content; missing archive entries are represented as unavailable gaps. Local archives live outside deployed staging in `~/.htmldrop/history/` (or the configured profile). The published page carries its revision records, so treat publication as sharing the included history as well as the current content. If older public drafts contain text that should no longer be shared, review them before publishing; use a deliberately fresh identity when appropriate. A new identity does not revoke copies already shared.

## Private history

Use an owner-managed password through protected environment/hidden input (`--password` without a value); return only the URL. Earlier private revisions remain separately encrypted under their original passwords. Changing today's password does not unlock, re-encrypt or recover older private revisions. Going public does not decrypt those private records. Save the original passwords in the owner's password manager if earlier private versions need to remain readable.

Enabling password protection closes a formerly public Worker snapshot and rejects plaintext uploads to the protected document. It cannot retract a copy already downloaded. Feedback comments and convergence providers remain separate content paths; preserve the repository's sharing policy.

Private access registration precedes Surge deployment. If Surge then fails, local staging/history rolls back but remote access stays fail-closed. Follow the CLI's partial-transition message and retry the same push to synchronize it; do not claim cross-service atomic rollback.

## Source hand-off and files

From the target project directory, `htmldrop pull <published-url> --output report.html` reconstructs editable source and preserves history identity and records for subsequent publishing. The output must stay within the current working directory. For protected content add bare `--password` with secure input. `fetch` reads/decrypts content; use `pull` for the editable hand-off workflow.

Edit mode can serve declared sibling files, but publishing still uploads one self-contained HTML file. Inline required local assets before `push`; preflight rejects local references, missing/blocked dependencies and incomplete scans. External HTTPS/data URLs are left intact. History or a successful local preview does not bundle attachments.
