---
name: daily-chief
description: Run the user-invoked Daily Chief Plan today workflow with device login, a local preview, and explicit confirmation before remote apply.
disable-model-invocation: true
compatibility: Requires Node.js 22+, network access to a Daily Chief server, and a browser for device authorization.
---

# Daily Chief

Remote truth. Visual preview. Explicit apply.

Use this workflow only when the user invokes `/daily-chief` or `/skill:daily-chief`. Only Plan today is implemented. Daily Chief is the remote source of truth. The local HTML file is a visual preview, never task or plan state.

1. Check authentication. If credentials are missing or rejected, run browser device login and wait for approval.

   ```bash
   npx daily-chief-agent@1.0.0 status --json
   npx daily-chief-agent@1.0.0 auth
   ```

2. Read the request and prior conversation. Ask only for missing canonical answers: available hours, energy (`high`, `normal`, or `low`), must happen today, fixed events, and what can defer.

3. Create the remote, non-mutating preview. `date` is optional and the server chooses its current UTC date when omitted.

   ```bash
   npx daily-chief-agent@1.0.0 plan-today --answers-json '{"availableHours":4,"energy":"normal","mustHappen":"Ship the review","fixedEvents":"15:00 client call","canDefer":"Inbox cleanup"}' --json
   ```

4. Inspect the returned local HTML `out` file and its recommendations. It is local only and has no token. Do not publish it or use htmldrop.

5. Require clear confirmation to apply that exact preview. Viewing it, silence, or a vague acknowledgment is not confirmation.

6. Apply only the returned `applyPayload`, unchanged. It contains the stored `previewId` and its generated `idempotencyKey`.

   ```bash
   npx daily-chief-agent@1.0.0 apply-plan --json '<applyPayload from plan-today>' --output-json
   ```

Report an applied plan only after the command receives a successful remote response. Never expose, log, or embed bearer tokens. For API semantics and self-host configuration, read [the API reference](../../API.md).
