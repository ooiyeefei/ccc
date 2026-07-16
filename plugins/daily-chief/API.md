# Daily Chief agent API reference

The Daily Chief agent uses the versioned remote contract at `/api/agent/v1`. The remote Daily Chief service is the source of truth. This client stores no local plan or task state.

Default hosted base URL:

```text
https://dailychief.yooi.me
```

All request and response bodies are JSON. Authenticated agent requests send:

```text
Authorization: Bearer <device access token>
X-Daily-Chief-Agent-Name: daily-chief
X-Daily-Chief-Agent-Version: 1.0.0
```

The client does not print bearer tokens, device codes, or raw error response bodies.

## Browser device authorization

### Start

```text
POST /api/device/start
```

This public endpoint starts a short-lived browser authorization. It returns `deviceCode`, `userCode`, `verificationUri`, `verificationUriComplete`, `expiresIn`, and `interval`.

The CLI prints only `verificationUriComplete` and `userCode`, opens the verification URL best effort, and keeps `deviceCode` in memory only. It does not attach agent headers to this public request.

### Poll

```text
POST /api/device/token
```

Body:

```json
{ "deviceCode": "opaque device secret" }
```

Poll no faster than the returned `interval` until the browser approves the request or `expiresIn` elapses. HTTP `428` with `authorization_pending` is not approval. A successful response returns `accessToken`, `tokenId`, and `expiresAt`; the access token is saved only in local credential config. Device tokens are handed off once, so an expired or rejected device flow must be restarted with `auth`.

## Authenticated v1 endpoints

### State

```text
GET /api/agent/v1/state
```

Returns an agent-safe state projection with `settings` and the active `challenge`, if any. The CLI reports only a small authentication and challenge summary rather than writing or dumping workspace state.

### Plan today preview

```text
POST /api/agent/v1/plan-today
```

Body:

```json
{
  "availableHours": 4,
  "energy": "normal",
  "mustHappen": "optional",
  "fixedEvents": "optional",
  "canDefer": "optional",
  "date": "optional YYYY-MM-DD"
}
```

`availableHours` is from `0.25` through `24`. `energy` is exactly `high`, `normal`, or `low`. Optional text fields are at most 2000 characters. If `date` is omitted, the server uses its current UTC date.

The response contains:

```json
{
  "previewId": "opaque short-lived identifier",
  "expiresAt": "authoritative ISO timestamp",
  "preview": {
    "date": "2026-07-14",
    "challenge": { "id": "...", "name": "..." },
    "answers": { "availableHours": 4, "energy": "normal", "date": "2026-07-14" },
    "recommendations": []
  }
}
```

This endpoint does not mutate Daily Chief state. `previewId` is bound to the authenticated workspace and expires at `expiresAt`. It cannot be applied by a different workspace.

When the local HTML preview is created, the CLI generates a cryptographically strong UUID idempotency key and returns:

```json
{
  "applyPayload": {
    "previewId": "the response previewId",
    "idempotencyKey": "the generated key"
  }
}
```

The same payload is rendered into the explicit apply command. The client does not persist it outside that local preview and command output.

### Apply the stored preview

```text
POST /api/agent/v1/apply-plan
```

Required header:

```text
Idempotency-Key: <the exact generated idempotencyKey>
```

The body is deliberately narrow:

```json
{ "previewId": "opaque short-lived identifier" }
```

This is the only mutating Plan today endpoint. It applies the exact stored preview only after an explicit confirmation command. The service does not accept replacement recommendations, dates, capacity, energy, or plan fields in this request. The CLI independently rejects any `apply-plan --json` input other than `{ "previewId", "idempotencyKey" }`.

Retry a network-ambiguous apply with the same `previewId` and the exact same `Idempotency-Key`. A repeated key for the same preview returns the original result. Reusing a key with a different preview returns `idempotency_conflict` and does not apply either preview again. An expired preview returns `preview_expired`; create a new preview and obtain a new key. The CLI reports an applied plan only after an HTTP success with a valid apply response.

## Safe failures

Common response classes are handled without echoing server response bodies:

- `400`: invalid request or header
- `401` or `403`: credentials are invalid or expired; run `auth`
- `404`: endpoint or preview is unavailable
- `409`: idempotency conflict; create and confirm a new preview
- `410`: preview expired; create a new preview
- `428`: browser authorization is still pending
- `429`: wait briefly before retrying

All documented endpoint responses are `Cache-Control: no-store`. Agent v1 responses also provide contract compatibility metadata. During beta, compatibility metadata is informational and does not change authorization or account availability.

## Configuration

API URL precedence is:

1. `--api-url URL`
2. `DAILY_CHIEF_API_URL`
3. saved credential config `apiUrl`
4. hosted default

The URL must be an `http` or `https` base URL without embedded credentials, query parameters, or fragments. Self-hosted servers use the exact same device and agent v1 paths. Authenticate again after changing servers because device credentials belong to the server that issued them.

Credential config location precedence is:

1. `$DAILY_CHIEF_CONFIG_DIR/agent.json`
2. `$XDG_CONFIG_HOME/daily-chief/agent.json`
3. `~/.config/daily-chief/agent.json`

On POSIX, the CLI creates the config directory with mode `700` and config with mode `600` where the filesystem permits it. Generated HTML previews go under `.daily-chief/drops/` by default and contain no token or network behavior.
