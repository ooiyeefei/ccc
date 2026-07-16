const PACKAGE_COMMAND = "npx daily-chief-agent@1.0.0";

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function firstText(...values) {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function textFromValue(value, fallback = "Not provided") {
  if (typeof value === "string" && value.trim()) return value.trim();
  if (typeof value === "number" && Number.isFinite(value)) return String(value);
  if (Array.isArray(value)) {
    const items = value.map((item) => textFromValue(item, "")).filter(Boolean);
    return items.length ? items.join("; ") : fallback;
  }
  return fallback;
}

function formatEffort(value) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return `${value} ${value === 1 ? "hour" : "hours"}`;
  }
  return textFromValue(value, "Not provided");
}

/** Escape every dynamic value before it is interpolated into the local HTML. */
export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

/** Narrow the remote response to display-only recommendation fields. */
export function normalizeRecommendations(preview) {
  const source = isRecord(preview) && Array.isArray(preview.recommendations)
    ? preview.recommendations
    : [];

  return source.slice(0, 3).map((item, index) => {
    const recommendation = isRecord(item) ? item : {};
    return {
      id: firstText(recommendation.id),
      title: firstText(recommendation.title) || `Recommendation ${index + 1}`,
      effort: formatEffort(recommendation.effort),
      energy: textFromValue(recommendation.energy, "Not provided"),
      deadline: firstText(recommendation.deadline) || "No deadline",
      project: firstText(recommendation.project) || "No project",
      why: textFromValue(recommendation.why, "No explanation supplied."),
    };
  });
}

export function buildApplyCommand(applyPayload) {
  return `${PACKAGE_COMMAND} apply-plan --json '${JSON.stringify(applyPayload).replaceAll("'", "'\"'\"'")}' --output-json`;
}

function answerCards(answers) {
  return [
    ["Genuinely available time", formatEffort(answers?.availableHours)],
    ["Energy", textFromValue(answers?.energy)],
    ["Must happen today", textFromValue(answers?.mustHappen)],
    ["Fixed events", textFromValue(answers?.fixedEvents)],
    ["Can defer", textFromValue(answers?.canDefer)],
  ];
}

function challengeName(preview) {
  return firstText(isRecord(preview?.challenge) ? preview.challenge.name : "") || "Daily Chief";
}

/**
 * Render a standalone local projection. It accepts selected display fields only
 * and never serializes the API response, credential config, or access token.
 */
export function renderPlanToday({ preview, expiresAt, applyPayload }) {
  const answers = isRecord(preview?.answers) ? preview.answers : {};
  const recommendations = normalizeRecommendations(preview);
  const date = firstText(preview?.date) || "Today";
  const command = buildApplyCommand(applyPayload);
  const recommendationMarkup = recommendations.length
    ? recommendations.map((recommendation, index) => `
          <li class="recommendation">
            <div class="rank" aria-label="Rank ${index + 1}">${index + 1}</div>
            <div class="recommendation-content">
              <h3>${escapeHtml(recommendation.title)}</h3>
              <dl class="details">
                <div><dt>Effort</dt><dd>${escapeHtml(recommendation.effort)}</dd></div>
                <div><dt>Energy</dt><dd>${escapeHtml(recommendation.energy)}</dd></div>
                <div><dt>Project</dt><dd>${escapeHtml(recommendation.project)}</dd></div>
                <div><dt>Deadline</dt><dd>${escapeHtml(recommendation.deadline)}</dd></div>
              </dl>
              <p class="why"><span>Why this now</span>${escapeHtml(recommendation.why)}</p>
            </div>
          </li>`).join("")
    : "<li class=\"empty\">No recommendations were returned for this preview.</li>";

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>Plan today preview | ${escapeHtml(date)}</title>
  <style>
    :root { color: #1c1917; background: #faf9f7; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #faf9f7; color: #1c1917; line-height: 1.5; }
    main { width: min(100% - 2rem, 54rem); margin: 0 auto; padding: 3rem 0 4rem; }
    .eyebrow { margin: 0 0 .45rem; color: #78716c; font-size: .72rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; }
    header { display: flex; align-items: end; justify-content: space-between; gap: 1rem; border-bottom: 1px solid #e7e5e4; padding-bottom: 1.5rem; }
    h1 { margin: 0; font-size: clamp(1.65rem, 5vw, 2.35rem); letter-spacing: -.035em; line-height: 1.1; }
    .date { color: #78716c; font-size: .9rem; font-weight: 600; white-space: nowrap; }
    .challenge { margin: .7rem 0 0; color: #57534e; font-size: .95rem; }
    section { margin-top: 1.5rem; }
    h2 { margin: 0 0 .75rem; font-size: 1rem; letter-spacing: -.01em; }
    .notice { border: 1px solid #fde68a; border-radius: 1rem; background: #fffbeb; padding: .9rem 1rem; color: #92400e; font-size: .92rem; font-weight: 650; }
    .answers { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: .65rem; }
    .answer { min-width: 0; border: 1px solid #e7e5e4; border-radius: 1rem; background: #fff; box-shadow: 0 1px 2px rgb(28 25 23 / .05); padding: .9rem; }
    .answer dt { color: #78716c; font-size: .7rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
    .answer dd { margin: .38rem 0 0; font-size: .88rem; font-weight: 600; overflow-wrap: anywhere; }
    .recommendations { display: grid; gap: .7rem; margin: 0; padding: 0; list-style: none; }
    .recommendation, .empty { display: flex; gap: .9rem; border: 1px solid #e7e5e4; border-radius: 1rem; background: #fff; box-shadow: 0 1px 2px rgb(28 25 23 / .05); padding: 1rem; }
    .rank { display: grid; flex: 0 0 1.75rem; width: 1.75rem; height: 1.75rem; place-items: center; border-radius: 999px; background: #1c1917; color: #fff; font-size: .8rem; font-weight: 750; }
    .recommendation-content { min-width: 0; flex: 1; }
    h3 { margin: .05rem 0 0; font-size: 1rem; overflow-wrap: anywhere; }
    .details { display: flex; flex-wrap: wrap; gap: .45rem .9rem; margin: .7rem 0 0; }
    .details div { display: flex; gap: .28rem; font-size: .78rem; }
    .details dt { color: #78716c; }
    .details dd { margin: 0; color: #44403c; font-weight: 600; overflow-wrap: anywhere; }
    .why { margin: .7rem 0 0; color: #57534e; font-size: .84rem; overflow-wrap: anywhere; }
    .why span { display: block; margin-bottom: .12rem; color: #78716c; font-size: .7rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
    .apply { border: 1px solid #d6d3d1; border-radius: 1rem; background: #f5f5f4; padding: 1rem; }
    .apply p { margin: 0 0 .75rem; color: #44403c; font-size: .9rem; }
    code { display: block; overflow-wrap: anywhere; border-radius: .7rem; background: #1c1917; padding: .85rem 1rem; color: #fafaf9; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: .76rem; line-height: 1.55; white-space: pre-wrap; }
    footer { margin-top: 2rem; color: #a8a29e; font-size: .75rem; text-align: center; }
    @media (max-width: 720px) { .answers { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 460px) { main { width: min(100% - 1.25rem, 54rem); padding-top: 1.5rem; } header { align-items: start; flex-direction: column; } .answers { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <p class="eyebrow">Daily Chief</p>
        <h1>Plan today preview</h1>
        <p class="challenge">Challenge: ${escapeHtml(challengeName(preview))}</p>
      </div>
      <div class="date">${escapeHtml(date)}</div>
    </header>

    <section class="notice" aria-label="Preview status">Preview only. Nothing changed. Expires: ${escapeHtml(textFromValue(expiresAt, "not provided"))}</section>

    <section aria-labelledby="answers-heading">
      <h2 id="answers-heading">Your answers</h2>
      <dl class="answers">
        ${answerCards(answers).map(([label, value]) => `<div class="answer"><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join("")}
      </dl>
    </section>

    <section aria-labelledby="top-three-heading">
      <h2 id="top-three-heading">Ranked top 3</h2>
      <ol class="recommendations">
        ${recommendationMarkup}
      </ol>
    </section>

    <section class="apply" aria-labelledby="apply-heading">
      <h2 id="apply-heading">Apply this plan</h2>
      <p>Run this command only after explicitly confirming that this exact preview should be applied.</p>
      <code>${escapeHtml(command)}</code>
    </section>

    <footer>Local preview projection. Daily Chief remains the source of truth.</footer>
  </main>
</body>
</html>`;
}
