import assert from "node:assert/strict";
import test from "node:test";
import {
  DEFAULT_API_URL,
  normalizeAnswers,
  normalizeApplyPayload,
  resolveApiUrl,
  resolveConfigPath,
} from "../scripts/daily-chief.mjs";

test("uses the dedicated config location before XDG and home", () => {
  assert.equal(
    resolveConfigPath({ DAILY_CHIEF_CONFIG_DIR: "/private/daily-chief", XDG_CONFIG_HOME: "/xdg" }, "/home/tester"),
    "/private/daily-chief/agent.json",
  );
  assert.equal(resolveConfigPath({ XDG_CONFIG_HOME: "/xdg" }, "/home/tester"), "/xdg/daily-chief/agent.json");
  assert.equal(resolveConfigPath({}, "/home/tester"), "/home/tester/.config/daily-chief/agent.json");
});

test("resolves API URL from flag, environment, config, then hosted default", () => {
  const config = { apiUrl: "https://saved.example.test/" };
  assert.equal(
    resolveApiUrl({ apiUrl: "https://flag.example.test/", env: { DAILY_CHIEF_API_URL: "https://env.example.test" }, config }),
    "https://flag.example.test",
  );
  assert.equal(
    resolveApiUrl({ env: { DAILY_CHIEF_API_URL: "https://env.example.test/" }, config }),
    "https://env.example.test",
  );
  assert.equal(resolveApiUrl({ env: {}, config }), "https://saved.example.test");
  assert.equal(resolveApiUrl({ env: {}, config: {} }), DEFAULT_API_URL);
});

test("validates v1 preview answers and leaves an omitted date for the server", () => {
  assert.deepEqual(normalizeAnswers({ availableHours: 0.25, energy: "normal" }), {
    availableHours: 0.25,
    energy: "normal",
  });
  assert.deepEqual(
    normalizeAnswers({ availableHours: 24, energy: "high", date: "2026-07-14", mustHappen: "Ship" }),
    { availableHours: 24, energy: "high", date: "2026-07-14", mustHappen: "Ship" },
  );

  for (const availableHours of [0, 0.24, 24.01]) {
    assert.throws(() => normalizeAnswers({ availableHours, energy: "normal" }), /availableHours must be a number between 0\.25 and 24/);
  }
  assert.throws(() => normalizeAnswers({ availableHours: 4, energy: "medium" }), /energy must be high, normal, or low/);
  assert.throws(() => normalizeAnswers({ availableHours: 4, energy: "low", plan: [] }), /does not allow plan/);
  assert.throws(() => normalizeAnswers({ availableHours: 4, energy: "low", date: "14-07-2026" }), /date must use YYYY-MM-DD/);
});

test("only accepts the exact preview apply payload", () => {
  const payload = { previewId: "preview_123", idempotencyKey: "0a12bcde-1234-4bcd-8ef0-123456789abc" };
  assert.deepEqual(normalizeApplyPayload(payload), payload);

  for (const invalid of [
    { previewId: "preview_123" },
    { ...payload, top3: ["task-1"] },
    { ...payload, availableHours: 4 },
    { ...payload, idempotencyKey: "short" },
    { ...payload, previewId: "" },
  ]) {
    assert.throws(() => normalizeApplyPayload(invalid), /apply-plan accepts only|idempotencyKey must be|previewId must be/);
  }
});
