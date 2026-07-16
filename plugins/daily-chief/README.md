# Daily Chief agent

Daily Chief provides one opt-in workflow: **Plan today**. It reads remote Daily Chief state, creates a short-lived remote preview, writes a local visual projection, and applies only after explicit confirmation.

This directory is the canonical CCC distribution source for the Daily Chief agent package. It intentionally does not copy the Daily Chief app and never creates Markdown or JSON task state.

> **Publication status:** `daily-chief-agent@1.0.0` is prepared but not yet published to npm. The install and execution examples below work after that release. The public unscoped name is deliberate because the `@daily-chief` npm scope is not provisioned.

## Install

### Claude Code

Add the CCC marketplace, then install the dedicated plugin:

```text
/plugin marketplace add ooiyeefei/ccc
/plugin install daily-chief@ccc
```

Invoke `/daily-chief` to load the workflow. It is user-invoked only and does not add an automatic Daily Chief integration to generic context.

### Pi

Install the Pi package:

```bash
pi install npm:daily-chief-agent@1.0.0
```

Then invoke `/skill:daily-chief`. The package's `pi` manifest exposes only its `skills` directory.

### Direct CLI

Run the package without a global installation:

```bash
npx daily-chief-agent@1.0.0 auth
npx daily-chief-agent@1.0.0 status --json
```

The package also declares the `daily-chief` binary for normal npm bin resolution. Node.js 22 or later is required.

## Plan today

Authenticate through the browser device flow first. The command prints the browser verification URL and user code, opens the URL best effort, then polls until browser approval. It never prints the device code or access token.

```bash
npx daily-chief-agent@1.0.0 plan-today --answers-json '{"availableHours":4,"energy":"normal","mustHappen":"Ship the review","fixedEvents":"15:00 client call","canDefer":"Inbox cleanup"}' --json
```

The command calls the non-mutating v1 preview endpoint and returns a JSON object containing:

- `out`: local HTML preview path
- `previewId` and `expiresAt`: the opaque remote preview and authoritative expiry
- `top3`: display-only recommendations
- `applyPayload`: exactly `{ "previewId", "idempotencyKey" }`
- `previewOnly: true`

The default preview is a non-networked local HTML file under `.daily-chief/drops/`. It uses selected display data only, contains no bearer token, and is not a second task store. The drop directory and file use POSIX modes `700` and `600` on a best-effort basis. The CLI refuses to overwrite an existing drop.

Inspect the preview, then require a clear user confirmation. Apply the returned `applyPayload` unchanged:

```bash
npx daily-chief-agent@1.0.0 apply-plan --json '{"previewId":"<preview-id>","idempotencyKey":"<idempotency-key>"}' --output-json
```

The CLI sends only `{ "previewId" }` to the apply endpoint and puts the exact generated key in `Idempotency-Key`. It reports success only after a successful server response. It rejects extra plan fields and replacement task selections; always reuse the exact idempotency key returned with that preview.

## Hosted and self-hosted servers

The default hosted base URL is `https://dailychief.yooi.me`. During beta, agent integration is available to every authenticated hosted Daily Chief account. It is not paid-only.

Self-hosted Daily Chief servers use the same package and v1 API contract. Set a one-command override with `DAILY_CHIEF_API_URL`, or save a server with device login:

```bash
DAILY_CHIEF_API_URL=https://daily-chief.example.test npx daily-chief-agent@1.0.0 status --json
npx daily-chief-agent@1.0.0 auth --api-url https://daily-chief.example.test
```

Changing servers requires new device credentials for that server. The API URL must be an `http` or `https` base URL without embedded credentials, a query, or a fragment.

## Privacy and local data

The only persistent non-preview data is a credential config. Its path precedence is:

1. `$DAILY_CHIEF_CONFIG_DIR/agent.json`
2. `$XDG_CONFIG_HOME/daily-chief/agent.json`
3. `~/.config/daily-chief/agent.json`

The config holds the access token, API URL, token ID, and expiry. The directory and config file use POSIX `700` and `600` modes on a best-effort basis. Do not commit, paste, log, or share this config.

Daily Chief does not automatically send HTML previews to htmldrop or another host. Task titles are private. Sharing a preview is a future explicit opt-in feature.

## Updates

The examples pin `1.0.0` so a run does not silently change package behavior. Review a later release before selecting its version in the npm, Pi, or npx install reference. The API contract is versioned separately as Daily Chief agent v1.

## Reference and development

See [API.md](API.md) for endpoint semantics, expiry and workspace binding, idempotency, safe error handling, and configuration details. Run the focused package checks from this directory:

```bash
npx daily-chief-agent@1.0.0 --help
npm test
npm run check
npm pack --dry-run
npx -y skills-ref validate skills/daily-chief
```

`skills-ref` may report `disable-model-invocation` as an unexpected frontmatter field. That is a generic Agent Skills validation false negative: Pi documents and requires this extension to keep the skill user-invoked and hidden from generic model invocation.
