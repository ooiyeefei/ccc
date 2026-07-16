import assert from "node:assert/strict";
import test from "node:test";
import { buildApplyCommand, renderPlanToday } from "../scripts/render-plan-today.mjs";

const applyPayload = {
  previewId: "preview_123",
  idempotencyKey: "0a12bcde-1234-4bcd-8ef0-123456789abc",
};

const preview = {
  date: "2026-07-14",
  accessToken: "credential-not-for-output",
  challenge: { name: "Launch <alpha>" },
  answers: {
    availableHours: 3.5,
    energy: "normal",
    mustHappen: "Review <priority> & decide",
    fixedEvents: "12:00 <script>alert(1)</script>",
    canDefer: "Email triage",
  },
  recommendations: [
    {
      id: "task-1",
      title: "Ship <script>alert(1)</script>",
      effort: 1.5,
      energy: "deep",
      deadline: "2026-07-14",
      project: "Core & Co",
      why: ["High leverage", "Due <today>"],
      bearerToken: "credential-not-for-output",
    },
  ],
};

test("renderer escapes dynamic content and excludes credential-shaped response fields", () => {
  const html = renderPlanToday({
    preview,
    expiresAt: "2026-07-14T12:00:00.000Z",
    applyPayload,
  });

  assert.match(html, /Ship &lt;script&gt;alert\(1\)&lt;\/script&gt;/);
  assert.match(html, /Review &lt;priority&gt; &amp; decide/);
  assert.doesNotMatch(html, /<script>alert\(1\)<\/script>/);
  assert.doesNotMatch(html, /credential-not-for-output/);
});

test("renderer contains the exact npx apply command and standalone preview sections", () => {
  const html = renderPlanToday({
    preview,
    expiresAt: "2026-07-14T12:00:00.000Z",
    applyPayload,
  });

  assert.equal(
    buildApplyCommand(applyPayload),
    "npx daily-chief-agent@1.0.0 apply-plan --json '{\"previewId\":\"preview_123\",\"idempotencyKey\":\"0a12bcde-1234-4bcd-8ef0-123456789abc\"}' --output-json",
  );
  assert.match(html, /^<!doctype html>/i);
  assert.match(html, /Preview only\. Nothing changed\./);
  assert.match(html, /Ranked top 3/);
  assert.match(html, /Apply this plan/);
  assert.match(html, /npx daily-chief-agent@1\.0\.0 apply-plan/);
  assert.match(html, /idempotencyKey/);
});

test("renderer supports an empty remote preview without constructing task state", () => {
  const html = renderPlanToday({
    preview: { date: "2026-07-14", answers: {}, recommendations: [] },
    expiresAt: "2026-07-14T12:00:00.000Z",
    applyPayload,
  });

  assert.match(html, /No recommendations were returned for this preview\./);
  assert.doesNotMatch(html, /\"recommendations\":\s*\[/);
});
