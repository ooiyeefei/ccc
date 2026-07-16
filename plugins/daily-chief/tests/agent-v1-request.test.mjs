import assert from "node:assert/strict";
import test from "node:test";
import { AGENT_NAME, AGENT_VERSION, request } from "../scripts/daily-chief.mjs";

function response(payload) {
  return { ok: true, status: 200, json: async () => payload };
}

test("uses the v1 preview URL, authenticated agent headers, and JSON answers", async () => {
  let captured;
  await request("https://daily-chief.example.test", "/api/agent/v1/plan-today", {
    method: "POST",
    accessToken: "test-access-token",
    body: { availableHours: 4, energy: "normal" },
    fetchImpl: async (url, init) => {
      captured = { url, init };
      return response({ previewId: "preview", expiresAt: "2026-07-14T12:00:00.000Z", preview: {} });
    },
  });

  assert.equal(captured.url, "https://daily-chief.example.test/api/agent/v1/plan-today");
  assert.equal(captured.init.method, "POST");
  assert.deepEqual(captured.init.headers, {
    Accept: "application/json",
    Authorization: "Bearer test-access-token",
    "X-Daily-Chief-Agent-Name": AGENT_NAME,
    "X-Daily-Chief-Agent-Version": AGENT_VERSION,
    "Content-Type": "application/json",
  });
  assert.equal(captured.init.body, '{"availableHours":4,"energy":"normal"}');
});

test("sends an apply body with previewId only and the exact idempotency header", async () => {
  let captured;
  await request("https://daily-chief.example.test", "/api/agent/v1/apply-plan", {
    method: "POST",
    accessToken: "test-access-token",
    idempotencyKey: "0a12bcde-1234-4bcd-8ef0-123456789abc",
    body: { previewId: "preview_123" },
    fetchImpl: async (url, init) => {
      captured = { url, init };
      return response({ challenge: {}, plan: { date: "2026-07-14" } });
    },
  });

  assert.equal(captured.url, "https://daily-chief.example.test/api/agent/v1/apply-plan");
  assert.equal(captured.init.headers["Idempotency-Key"], "0a12bcde-1234-4bcd-8ef0-123456789abc");
  assert.equal(captured.init.body, '{"previewId":"preview_123"}');
  assert.doesNotMatch(captured.init.body, /idempotencyKey|availableHours|top3/);
});

test("does not send agent authentication headers to public device endpoints", async () => {
  let captured;
  await request("https://daily-chief.example.test", "/api/device/start", {
    method: "POST",
    fetchImpl: async (_url, init) => {
      captured = init;
      return response({});
    },
  });

  assert.deepEqual(captured.headers, { Accept: "application/json" });
});
