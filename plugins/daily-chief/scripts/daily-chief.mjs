import { randomUUID } from "node:crypto";
import { chmod, mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { homedir, platform } from "node:os";
import { dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { normalizeRecommendations, renderPlanToday } from "./render-plan-today.mjs";

export const DEFAULT_API_URL = "https://dailychief.yooi.me";
export const AGENT_NAME = "daily-chief";
export const AGENT_VERSION = "1.0.0";
const REQUEST_TIMEOUT_MS = 20_000;
const IDEMPOTENCY_KEY_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._-]{7,127}$/;

export class DailyChiefError extends Error {
  constructor(message) {
    super(message);
    this.name = "DailyChiefError";
  }
}

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function firstText(...values) {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function isDate(value) {
  return typeof value === "string" && /^\d{4}-\d{2}-\d{2}$/.test(value);
}

function jsonArgument(value, flag) {
  try {
    return JSON.parse(value);
  } catch {
    throw new DailyChiefError(`${flag} must contain valid JSON.`);
  }
}

async function chmodBestEffort(pathname, mode) {
  if (platform() === "win32") return;
  try {
    await chmod(pathname, mode);
  } catch {
    // Some filesystems do not support POSIX permissions.
  }
}

/** Resolve the one persistent local file: a credential config. */
export function resolveConfigPath(env = process.env, home = homedir()) {
  const configDir = firstText(
    env.DAILY_CHIEF_CONFIG_DIR,
    env.XDG_CONFIG_HOME ? resolve(env.XDG_CONFIG_HOME, "daily-chief") : "",
    resolve(home, ".config", "daily-chief"),
  );
  return resolve(configDir, "agent.json");
}

export function normalizeApiUrl(value = DEFAULT_API_URL) {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new DailyChiefError("The Daily Chief API URL must be a valid http or https URL.");
  }

  if (!/^https?:$/.test(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new DailyChiefError("The Daily Chief API URL must be an http or https base URL without credentials, query, or fragment.");
  }

  url.pathname = url.pathname.replace(/\/+$/, "");
  return url.toString().replace(/\/$/, "");
}

export function resolveApiUrl({ apiUrl, env = process.env, config } = {}) {
  return normalizeApiUrl(firstText(apiUrl, env.DAILY_CHIEF_API_URL, config?.apiUrl, DEFAULT_API_URL));
}

async function readConfig(env = process.env) {
  const configPath = resolveConfigPath(env);
  let source;
  try {
    source = await readFile(configPath, "utf8");
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw new DailyChiefError("Could not read the Daily Chief credential config.");
  }

  try {
    const config = JSON.parse(source);
    if (!isRecord(config)) throw new Error("config is not an object");
    return config;
  } catch {
    throw new DailyChiefError("The Daily Chief credential config is invalid. Run auth again.");
  }
}

async function writeConfig({ apiUrl, accessToken, tokenId, expiresAt }, env = process.env) {
  const configPath = resolveConfigPath(env);
  const configDir = dirname(configPath);
  const temporaryPath = `${configPath}.${randomUUID()}.tmp`;
  const config = { apiUrl, accessToken, tokenId, expiresAt };

  try {
    await mkdir(configDir, { recursive: true, mode: 0o700 });
    await chmodBestEffort(configDir, 0o700);
    await writeFile(temporaryPath, `${JSON.stringify(config, null, 2)}\n`, {
      encoding: "utf8",
      mode: 0o600,
      flag: "wx",
    });
    await chmodBestEffort(temporaryPath, 0o600);
    await rename(temporaryPath, configPath);
    await chmodBestEffort(configPath, 0o600);
  } catch {
    await rm(temporaryPath, { force: true }).catch(() => {});
    throw new DailyChiefError("Could not securely save the Daily Chief credential config.");
  }
}

async function credentialsFor(options, env = process.env) {
  const config = await readConfig(env);
  const accessToken = firstText(config?.accessToken);
  if (!accessToken) throw new DailyChiefError("No Daily Chief credentials found. Run auth first.");
  return {
    accessToken,
    apiUrl: resolveApiUrl({ apiUrl: options.apiUrl, env, config }),
  };
}

/** Make one API request without exposing response bodies in CLI errors. */
export async function request(apiUrl, endpoint, {
  method = "GET",
  accessToken,
  body,
  idempotencyKey,
  expectJson = true,
  fetchImpl = globalThis.fetch,
} = {}) {
  const headers = { Accept: "application/json" };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
    headers["X-Daily-Chief-Agent-Name"] = AGENT_NAME;
    headers["X-Daily-Chief-Agent-Version"] = AGENT_VERSION;
  }
  if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  let response;
  try {
    response = await fetchImpl(`${apiUrl}${endpoint}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
  } catch {
    throw new DailyChiefError("Could not reach the Daily Chief API. Check the API URL and your network connection.");
  }

  let payload;
  if (expectJson || !response.ok) {
    try {
      payload = await response.json();
    } catch {
      if (response.ok && expectJson) throw new DailyChiefError("The Daily Chief API returned an invalid response.");
    }
  }
  return { response, payload };
}

function requestFailure(endpoint, response) {
  if (response.status === 401 || response.status === 403) {
    return new DailyChiefError("Daily Chief credentials are invalid or expired. Run auth again.");
  }
  if (response.status === 404) {
    return new DailyChiefError(`Daily Chief endpoint ${endpoint} is unavailable. Confirm the remote backend is deployed.`);
  }
  if (response.status === 409 && endpoint === "/api/agent/v1/apply-plan") {
    return new DailyChiefError("This idempotency key belongs to a different preview. Create and confirm a new preview.");
  }
  if (response.status === 410 && endpoint === "/api/agent/v1/apply-plan") {
    return new DailyChiefError("This preview expired. Create a new preview before applying.");
  }
  if (response.status === 428 && endpoint === "/api/device/token") {
    return new DailyChiefError("Browser authorization is still pending.");
  }
  if (response.status === 429) {
    return new DailyChiefError("Daily Chief is rate limiting requests. Wait briefly and try again.");
  }
  return new DailyChiefError(`Daily Chief request to ${endpoint} failed (HTTP ${response.status}).`);
}

function openUrlBestEffort(url) {
  const [command, args] = process.platform === "darwin"
    ? ["open", [url]]
    : process.platform === "win32"
      ? ["cmd", ["/c", "start", "", url]]
      : ["xdg-open", [url]];

  import("node:child_process").then(({ spawn }) => {
    try {
      const child = spawn(command, args, { detached: true, stdio: "ignore", windowsHide: true });
      child.on("error", () => {});
      child.unref();
    } catch {
      // Opening a browser or local file is a convenience only.
    }
  }).catch(() => {});
}

function output(value, { json = false, credential } = {}) {
  const rendered = json ? JSON.stringify(value) : String(value);
  if (credential && rendered.includes(credential)) {
    throw new DailyChiefError("Refusing to print credential-bearing output.");
  }
  process.stdout.write(`${rendered}\n`);
}

function terminalText(value, fallback = "not available") {
  if (typeof value !== "string" || !value.trim()) return fallback;
  return value.trim().replace(/[\u0000-\u001f\u007f]/g, " ");
}

function stateSummary(state) {
  const challenge = isRecord(state?.challenge) ? state.challenge : null;
  return {
    authenticated: true,
    activeChallenge: challenge
      ? { id: terminalText(challenge.id), name: terminalText(challenge.name) }
      : null,
  };
}

function parseOptions(argv) {
  const [command, ...argumentsList] = argv;
  if (!command || command === "--help" || command === "-h") return { command: "help", options: {} };

  const options = {};
  for (let index = 0; index < argumentsList.length; index += 1) {
    const argument = argumentsList[index];
    if (["--api-url", "--answers-json", "--out"].includes(argument)) {
      const value = argumentsList[index + 1];
      if (!value || value.startsWith("--")) throw new DailyChiefError(`${argument} requires a value.`);
      options[argument.slice(2).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = value;
      index += 1;
      continue;
    }
    if (argument === "--json") {
      if (command === "apply-plan") {
        const value = argumentsList[index + 1];
        if (!value || value.startsWith("--")) throw new DailyChiefError("--json requires a JSON value for apply-plan.");
        options.applyJson = value;
        index += 1;
      } else {
        options.json = true;
      }
      continue;
    }
    if (argument === "--output-json") {
      options.json = true;
      continue;
    }
    throw new DailyChiefError(`Unknown option: ${argument}`);
  }

  const supported = {
    auth: new Set(["apiUrl", "json"]),
    status: new Set(["apiUrl", "json"]),
    "plan-today": new Set(["apiUrl", "answersJson", "out", "json"]),
    "apply-plan": new Set(["apiUrl", "applyJson", "json"]),
  };
  if (supported[command]) {
    for (const option of Object.keys(options)) {
      if (!supported[command].has(option)) throw new DailyChiefError(`Option --${option.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`)} is not available for ${command}.`);
    }
  }
  return { command, options };
}

function hasValidCapacity(value) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0.25 && value <= 24;
}

/** Validate and narrow the non-mutating v1 Plan today answers. */
export function normalizeAnswers(rawAnswers) {
  if (!isRecord(rawAnswers)) throw new DailyChiefError("--answers-json must contain an object.");
  const allowed = new Set(["availableHours", "energy", "mustHappen", "fixedEvents", "canDefer", "date"]);
  for (const key of Object.keys(rawAnswers)) {
    if (!allowed.has(key)) throw new DailyChiefError(`--answers-json does not allow ${key}.`);
  }
  if (!hasValidCapacity(rawAnswers.availableHours)) {
    throw new DailyChiefError("availableHours must be a number between 0.25 and 24.");
  }
  if (!["high", "normal", "low"].includes(rawAnswers.energy)) {
    throw new DailyChiefError("energy must be high, normal, or low.");
  }

  const answers = { availableHours: rawAnswers.availableHours, energy: rawAnswers.energy };
  for (const field of ["mustHappen", "fixedEvents", "canDefer"]) {
    if (Object.hasOwn(rawAnswers, field)) {
      if (typeof rawAnswers[field] !== "string" || rawAnswers[field].length > 2000) {
        throw new DailyChiefError(`${field} must be a string no longer than 2000 characters.`);
      }
      answers[field] = rawAnswers[field];
    }
  }
  if (Object.hasOwn(rawAnswers, "date")) {
    if (!isDate(rawAnswers.date)) throw new DailyChiefError("date must use YYYY-MM-DD.");
    answers.date = rawAnswers.date;
  }
  return answers;
}

/** Only a preview ID and the preview's existing retry key may confirm an apply. */
export function normalizeApplyPayload(rawPayload) {
  if (!isRecord(rawPayload)) throw new DailyChiefError("--json must contain an object.");
  const keys = Object.keys(rawPayload);
  if (keys.length !== 2 || !keys.includes("previewId") || !keys.includes("idempotencyKey")) {
    throw new DailyChiefError("apply-plan accepts only previewId and idempotencyKey from a preview applyPayload.");
  }
  if (typeof rawPayload.previewId !== "string" || !rawPayload.previewId || rawPayload.previewId.length > 200) {
    throw new DailyChiefError("previewId must be a non-empty string no longer than 200 characters.");
  }
  if (typeof rawPayload.idempotencyKey !== "string" || !IDEMPOTENCY_KEY_PATTERN.test(rawPayload.idempotencyKey)) {
    throw new DailyChiefError("idempotencyKey must be the exact key returned by the preview.");
  }
  return { previewId: rawPayload.previewId, idempotencyKey: rawPayload.idempotencyKey };
}

export function defaultDropPath(date, cwd = process.cwd(), suffix = randomUUID()) {
  if (!isDate(date)) throw new DailyChiefError("The preview response did not include a valid date.");
  return resolve(cwd, ".daily-chief", "drops", `plan-today-${date}-${suffix}.html`);
}

function resolveOutPath(out, date) {
  if (!out) return defaultDropPath(date);
  if (/^[A-Za-z][A-Za-z0-9+.-]*:\/\//.test(out)) {
    throw new DailyChiefError("--out must be a local file path, not a URL.");
  }
  return resolve(out);
}

async function writeDrop(pathname, html) {
  try {
    await mkdir(dirname(pathname), { recursive: true, mode: 0o700 });
    await chmodBestEffort(dirname(pathname), 0o700);
    await writeFile(pathname, html, { encoding: "utf8", mode: 0o600, flag: "wx" });
    await chmodBestEffort(pathname, 0o600);
  } catch (error) {
    if (error?.code === "EEXIST") {
      throw new DailyChiefError("Refusing to overwrite an existing local preview. Choose a new --out path.");
    }
    throw new DailyChiefError("Could not write the local Plan today HTML preview.");
  }
}

function parsePreviewResponse(payload) {
  if (!isRecord(payload) || typeof payload.previewId !== "string" || !payload.previewId || payload.previewId.length > 200) {
    throw new DailyChiefError("The Daily Chief API returned an incomplete preview.");
  }
  if (typeof payload.expiresAt !== "string" || Number.isNaN(Date.parse(payload.expiresAt))) {
    throw new DailyChiefError("The Daily Chief API returned a preview without a valid expiry.");
  }
  if (!isRecord(payload.preview) || !isDate(payload.preview.date)) {
    throw new DailyChiefError("The Daily Chief API returned a preview without valid display data.");
  }
  return payload;
}

function parseApplyResponse(payload) {
  if (!isRecord(payload) || !isRecord(payload.challenge) || !isRecord(payload.plan) || !isDate(payload.plan.date)) {
    throw new DailyChiefError("The Daily Chief API returned an invalid apply response.");
  }
  return payload;
}

async function auth(options, env) {
  const existingConfig = await readConfig(env);
  const apiUrl = resolveApiUrl({ apiUrl: options.apiUrl, env, config: existingConfig ?? undefined });
  const { response, payload } = await request(apiUrl, "/api/device/start", { method: "POST" });
  if (!response.ok) throw requestFailure("/api/device/start", response);

  const deviceCode = firstText(payload?.deviceCode);
  const userCode = firstText(payload?.userCode);
  const verificationUriComplete = firstText(payload?.verificationUriComplete);
  const expiresIn = Number(payload?.expiresIn);
  const interval = Number(payload?.interval);
  if (!deviceCode || !userCode || !verificationUriComplete || !Number.isFinite(expiresIn) || expiresIn <= 0) {
    throw new DailyChiefError("The Daily Chief API returned an incomplete device authorization response.");
  }

  if (options.json) {
    output({ verificationUriComplete, userCode }, { json: true });
  } else {
    output(`Verification URL: ${verificationUriComplete}`);
    output(`User code: ${userCode}`);
  }
  openUrlBestEffort(verificationUriComplete);

  const pollDelayMs = Math.max(1, Number.isFinite(interval) ? interval : 5) * 1_000;
  const deadline = Date.now() + expiresIn * 1_000;
  while (Date.now() < deadline) {
    await new Promise((done) => setTimeout(done, pollDelayMs));
    const tokenResult = await request(apiUrl, "/api/device/token", { method: "POST", body: { deviceCode } });
    if (tokenResult.response.status === 428 && tokenResult.payload?.error === "authorization_pending") continue;
    if (!tokenResult.response.ok) throw requestFailure("/api/device/token", tokenResult.response);

    const accessToken = firstText(tokenResult.payload?.accessToken);
    const tokenId = firstText(tokenResult.payload?.tokenId);
    const expiresAt = firstText(tokenResult.payload?.expiresAt);
    if (!accessToken || !tokenId || !expiresAt) {
      throw new DailyChiefError("The Daily Chief API returned an incomplete device token response.");
    }
    await writeConfig({ apiUrl, accessToken, tokenId, expiresAt }, env);
    output(options.json ? { authenticated: true } : "Daily Chief authentication saved.", {
      json: options.json,
      credential: accessToken,
    });
    return;
  }
  throw new DailyChiefError("Device authorization expired. Run auth again.");
}

async function status(options, env) {
  const credentials = await credentialsFor(options, env);
  const { response, payload } = await request(credentials.apiUrl, "/api/agent/v1/state", {
    accessToken: credentials.accessToken,
  });
  if (!response.ok) throw requestFailure("/api/agent/v1/state", response);
  const summary = stateSummary(payload);
  if (options.json) {
    output(summary, { json: true, credential: credentials.accessToken });
  } else {
    const challenge = summary.activeChallenge ? summary.activeChallenge.name : "none";
    output(`Daily Chief status\nAuthenticated: yes\nActive challenge: ${challenge}`, { credential: credentials.accessToken });
  }
}

async function planToday(options, env) {
  if (!options.answersJson) throw new DailyChiefError("plan-today requires --answers-json '<JSON>'.");
  const answers = normalizeAnswers(jsonArgument(options.answersJson, "--answers-json"));
  const credentials = await credentialsFor(options, env);
  const { response, payload } = await request(credentials.apiUrl, "/api/agent/v1/plan-today", {
    method: "POST",
    accessToken: credentials.accessToken,
    body: answers,
  });
  if (!response.ok) throw requestFailure("/api/agent/v1/plan-today", response);

  const previewResponse = parsePreviewResponse(payload);
  const applyPayload = { previewId: previewResponse.previewId, idempotencyKey: randomUUID() };
  const outPath = resolveOutPath(options.out, previewResponse.preview.date);
  const html = renderPlanToday({ preview: previewResponse.preview, expiresAt: previewResponse.expiresAt, applyPayload });
  if (html.includes(credentials.accessToken)) {
    throw new DailyChiefError("Refusing to write a preview containing a credential.");
  }
  await writeDrop(outPath, html);
  openUrlBestEffort(pathToFileURL(outPath).href);

  const recommendations = normalizeRecommendations(previewResponse.preview);
  const summary = {
    out: outPath,
    previewId: previewResponse.previewId,
    expiresAt: previewResponse.expiresAt,
    date: previewResponse.preview.date,
    top3: recommendations,
    applyPayload,
    previewOnly: true,
  };
  if (options.json) {
    output(summary, { json: true, credential: credentials.accessToken });
  } else {
    output(`Preview saved: ${outPath}\nTop 3: ${recommendations.map((item) => terminalText(item.title)).join("; ") || "none"}\nPreview only. Nothing changed.`, {
      credential: credentials.accessToken,
    });
  }
}

async function applyPlan(options, env) {
  if (!options.applyJson) throw new DailyChiefError("apply-plan requires --json '<applyPayload from plan-today>'.");
  const applyPayload = normalizeApplyPayload(jsonArgument(options.applyJson, "--json"));
  const credentials = await credentialsFor(options, env);
  const { response, payload } = await request(credentials.apiUrl, "/api/agent/v1/apply-plan", {
    method: "POST",
    accessToken: credentials.accessToken,
    idempotencyKey: applyPayload.idempotencyKey,
    body: { previewId: applyPayload.previewId },
  });
  if (!response.ok) throw requestFailure("/api/agent/v1/apply-plan", response);

  const applied = parseApplyResponse(payload);
  const summary = {
    applied: true,
    date: applied.plan.date,
    challenge: terminalText(applied.challenge.name),
  };
  if (options.json) {
    output(summary, { json: true, credential: credentials.accessToken });
  } else {
    output(`Plan applied successfully for ${summary.date}.`, { credential: credentials.accessToken });
  }
}

function help() {
  output(`Daily Chief agent CLI

Commands:
  auth [--api-url URL] [--json]
  status [--api-url URL] [--json]
  plan-today --answers-json '<JSON>' [--api-url URL] [--out PATH] [--json]
  apply-plan --json '<applyPayload>' [--api-url URL] [--output-json]

Set DAILY_CHIEF_API_URL to override the configured API base URL.`);
}

export async function main(argv = process.argv.slice(2), env = process.env) {
  const { command, options } = parseOptions(argv);
  switch (command) {
    case "help":
      help();
      return;
    case "auth":
      await auth(options, env);
      return;
    case "status":
      await status(options, env);
      return;
    case "plan-today":
      await planToday(options, env);
      return;
    case "apply-plan":
      await applyPlan(options, env);
      return;
    default:
      throw new DailyChiefError(`Unknown command: ${command}. Run --help for usage.`);
  }
}
