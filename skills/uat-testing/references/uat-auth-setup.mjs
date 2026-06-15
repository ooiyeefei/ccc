// uat-auth-setup.mjs — secure authentication for AI-agent-driven UAT.
//
// WHY: an AI agent must never type a password into a login field interactively.
// This script authenticates from credentials in process.env (loaded from a
// gitignored env file) and saves the authenticated browser session so the UAT
// run can reuse it. The secret flows env-file -> script -> auth field only; it
// never passes through the agent's tool calls, context, or output.
//
// USAGE:
//   node --env-file=.env.uat uat-auth-setup.mjs
//
//   .env.uat  (gitignored — NEVER commit):
//     UAT_BASE_URL=https://app.example.com
//     UAT_USER_EMAIL=test@example.com
//     UAT_USER_PASSWORD=...
//   Optional:
//     UAT_AUTH_STATE=.uat-auth/state.json   # where to save the session
//     UAT_HEADFUL=1                          # run headed (helps with bot checks)
//
// Adapt the selectors in signIn() to the app's auth provider, then reuse the
// saved state in your UAT run:  browser.newContext({ storageState: UAT_AUTH_STATE })
import { chromium } from 'playwright'

const { UAT_BASE_URL, UAT_USER_EMAIL, UAT_USER_PASSWORD } = process.env
const STATE = process.env.UAT_AUTH_STATE || '.uat-auth/state.json'

// Fail closed: error with the var NAME, never the value. Do NOT fall back to
// interactive password entry.
for (const [name, val] of Object.entries({ UAT_BASE_URL, UAT_USER_EMAIL, UAT_USER_PASSWORD })) {
  if (!val) {
    console.error(`Missing required env var: ${name} (set it in your gitignored env file)`)
    process.exit(2)
  }
}

// Adapt this to the app's login. Handles both email-first (Clerk/Auth0) and
// single-form logins. The password value is read from env and never logged.
async function signIn(page) {
  await page.goto(new URL('/sign-in', UAT_BASE_URL).href, { waitUntil: 'domcontentloaded' })

  const email = page.getByLabel(/email/i).or(page.getByPlaceholder(/email/i)).first()
  await email.fill(UAT_USER_EMAIL)
  await page.getByRole('button', { name: /continue|next|sign in|log ?in/i }).first().click()

  const password = page.getByLabel(/password/i).or(page.getByPlaceholder(/password/i)).first()
  await password.waitFor({ timeout: 15000 })
  await password.fill(UAT_USER_PASSWORD) // from env -> never logged
  await page.getByRole('button', { name: /continue|sign in|log ?in/i }).first().click()
}

const browser = await chromium.launch({ headless: !process.env.UAT_HEADFUL })
try {
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  await signIn(page)
  // Success = navigated away from the sign-in route.
  await page.waitForURL((u) => !u.pathname.includes('sign-in'), { timeout: 30000 })
  await ctx.storageState({ path: STATE })
  console.log(`[uat-auth] OK — authenticated session saved to ${STATE}`)
} catch (e) {
  console.error('[uat-auth] FAILED:', e?.message || e)
  console.error('[uat-auth] If the provider bot-challenges headless browsers, retry with UAT_HEADFUL=1,')
  console.error('[uat-auth] or have the user sign in once and export the session for this script to load.')
  process.exit(1)
} finally {
  await browser.close()
}
