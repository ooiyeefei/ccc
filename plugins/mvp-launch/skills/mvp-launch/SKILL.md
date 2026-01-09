---
name: mvp-launch
description: Web app MVP launch checklist knowledge. Auto-triggered when conversation involves "launch readiness", "MVP checklist", "production ready", "go live", or pre-launch verification. Provides the 10-point criteria for what counts as "done" in each area. Based on "Realistic MVP Launch Checklist (from building 30+ apps)".
---

# MVP Launch Checklist

A battle-tested 10-point checklist for web app MVP launches. Based on building 30+ apps.

**Philosophy:** "Don't overbuild. Just make it stable, usable, and something people can trust."

---

## The 10-Point Checklist

### 1. Stripe Setup (Payment Infrastructure)

**What counts as DONE:**
- Trials configured with appropriate period
- Plan switching works (upgrade/downgrade)
- Failed payment handling with retry logic
- Webhook endpoint registered in Stripe Dashboard
- Live keys tested (not just test mode)

**Required Webhook Events:**
- `customer.subscription.trial_will_end`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `invoice.created`
- `checkout.session.completed`

**Verification:** See `references/stripe-testing.md`

---

### 2. Mobile-First Design

**What counts as DONE:**
- Tested on real phones (not just browser resize)
- Touch targets appropriately sized (44x44px minimum)
- Forms work on mobile keyboards
- No horizontal scroll on mobile

**Key insight:** Browser resize mode lies. Real device testing is mandatory.

**Bonus (not required):**
- PWA manifest for installability
- Offline capability for core features

---

### 3. Smooth Onboarding

**What counts as DONE:**
- Steps kept minimal (3-5 max)
- Users guided to a fast first win
- Progress indicator if multi-step
- Can be skipped/completed later

**Anti-pattern:** Don't require 10 fields before users see value.

---

### 4. AI & Automation Stability

**What counts as DONE:**
- API errors handled gracefully
- Retry logic with exponential backoff
- Edge cases don't crash the app
- Timeouts configured appropriately
- Fallback behavior when AI fails

**Good defaults:**
- 3 retry attempts
- 30-60s timeout for complex operations
- User-friendly error messages

---

### 5. Critical Emails

**What counts as DONE:**
- Welcome email (immediate after signup)
- Trial-ending email (before trial expires)
- Failed payment email (when charge fails)
- Password reset (if not using external auth)

**Nice to have (don't overbuild):**
- Support acknowledgment email
- Usage milestone emails

---

### 6. Error Logging

**What counts as DONE:**
- Error tracking service configured (Sentry, Bugsnag, etc.)
- PII scrubbed from logs
- Critical errors trigger alerts
- Enough context to debug issues

**Goal:** Catch bugs before users notice them.

---

### 7. User Feedback Loop

**What counts as DONE:**
- Simple form or tool to collect feedback
- Screenshots/context capture (optional but helpful)
- Feedback reaches the team (email, Slack, GitHub Issues)

**Examples:** Typeform, in-app widget, email link, GitHub Issues integration.

---

### 8. Authentication & Roles

**What counts as DONE:**
- Secure page protection (no unauthorized access)
- Password reset works (or external auth handles it)
- Basic roles defined (admin vs user minimum)
- Session management (logout, expiry)

**If using external auth (Clerk, Auth0):** Most of this is handled for you.

---

### 9. Custom Domain with SSL

**What counts as DONE:**
- Own domain configured (no `.vercel.app`, `.replit.app`)
- HTTPS enabled (auto or manual SSL)
- DNS properly configured

**Why it matters:** Trust. Users won't pay for `myapp.replit.app`.

---

### 10. Real Database & Backups

**What counts as DONE:**
- Production database (not dev/local DB)
- Automated backups configured
- Point-in-time recovery possible

**Good choices:** Supabase, Neon, PlanetScale, Convex, AWS RDS.

**Anti-pattern:** Replit DB, SQLite in production, no backups.

---

## Scoring

| Score | Meaning |
|-------|---------|
| 10/10 | Fully implemented, production-ready |
| 7-9/10 | Mostly complete, minor gaps |
| 4-6/10 | Partial implementation, needs work |
| 1-3/10 | Minimal/broken implementation |
| 0/10 | Not implemented |

**Overall (sum of 10 areas):**
- 85-100: Launch Ready
- 70-84: Nearly Ready
- 50-69: Needs Work
- <50: Not Ready

---

## References

- `references/search-patterns.md` - Grep patterns for discovery
- `references/stripe-testing.md` - Stripe CLI verification commands
