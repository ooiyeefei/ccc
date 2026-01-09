# Search Patterns for MVP Launch Analysis

Use these grep/glob patterns during the DISCOVER phase to find implementations.

---

## 1. Stripe Setup

```bash
# Core Stripe integration
grep -r "stripe" --include="*.ts" --include="*.tsx" --include="*.js"
grep -r "webhook" --include="*.ts" --include="*.tsx"
grep -r "subscription" --include="*.ts" --include="*.tsx"
grep -r "checkout" --include="*.ts" --include="*.tsx"

# Specific webhook events
grep -r "trial_will_end" --include="*.ts"
grep -r "payment_failed" --include="*.ts"
grep -r "payment_succeeded" --include="*.ts"

# API routes
find . -path "*/api/*billing*" -o -path "*/api/*stripe*" -o -path "*/api/*webhook*"
```

**Key files to check:**
- `**/api/**/webhook*`
- `**/billing/**`
- Environment: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

---

## 2. Mobile-First Design

```bash
# Responsive patterns
grep -r "@media" --include="*.css" --include="*.scss" --include="*.tsx"
grep -r "viewport" --include="*.tsx" --include="*.html"
grep -r "responsive" --include="*.ts" --include="*.tsx"

# PWA
find . -name "manifest.json" -o -name "manifest.webmanifest"
grep -r "serviceWorker" --include="*.ts" --include="*.tsx"

# Mobile components
grep -r "mobile" --include="*.tsx"
grep -r "useMediaQuery" --include="*.ts" --include="*.tsx"
```

**Key files to check:**
- `manifest.json` or `manifest.webmanifest`
- `globals.css` or main stylesheet
- Layout components

---

## 3. Smooth Onboarding

```bash
# Onboarding flows
grep -r "onboarding" --include="*.ts" --include="*.tsx"
grep -r "welcome" --include="*.tsx"
grep -r "first.run\|firstRun" --include="*.ts" --include="*.tsx"
grep -r "setup.wizard\|setupWizard" --include="*.tsx"
grep -r "tour" --include="*.tsx"

# Step indicators
grep -r "step" --include="*.tsx" | grep -i "onboard\|wizard\|setup"
```

**Key files to check:**
- `**/onboarding/**`
- `**/welcome/**`
- Components with "wizard", "stepper", "tour"

---

## 4. AI & Automation Stability

```bash
# Error handling patterns
grep -r "retry" --include="*.ts" --include="*.tsx"
grep -r "backoff" --include="*.ts"
grep -r "timeout" --include="*.ts"
grep -r "fallback" --include="*.ts" --include="*.tsx"

# AI/ML integrations
grep -r "openai\|anthropic\|gemini\|huggingface" --include="*.ts"
grep -r "catch\|try" --include="*.ts" | grep -i "ai\|llm\|model"

# Specific patterns
grep -r "maxAttempts\|maxRetries" --include="*.ts"
grep -r "exponential" --include="*.ts"
```

**Key files to check:**
- Service files with AI calls
- Utility files with retry logic
- Config files with timeout settings

---

## 5. Critical Emails

```bash
# Email sending
grep -r "sendEmail\|send_email\|sendMail" --include="*.ts"
grep -r "SES\|ses\." --include="*.ts"
grep -r "Resend\|resend" --include="*.ts"
grep -r "nodemailer" --include="*.ts"
grep -r "postmark\|sendgrid\|mailgun" --include="*.ts"

# Email types
grep -r "welcome.*email\|welcomeEmail" --include="*.ts"
grep -r "trial.*email\|trialEmail" --include="*.ts"
grep -r "payment.*email\|paymentEmail" --include="*.ts"
grep -r "password.*reset\|passwordReset" --include="*.ts"
```

**Key files to check:**
- `**/email/**` or `**/mail/**`
- Lambda/serverless functions for email
- Webhook handlers (trigger emails)

---

## 6. Error Logging

```bash
# Error tracking services
grep -r "Sentry\|sentry" --include="*.ts" --include="*.tsx"
grep -r "bugsnag\|Bugsnag" --include="*.ts"
grep -r "logrocket\|LogRocket" --include="*.ts"
grep -r "rollbar\|Rollbar" --include="*.ts"

# Error boundaries
grep -r "ErrorBoundary\|errorBoundary" --include="*.tsx"
grep -r "captureException\|captureMessage" --include="*.ts"

# Config
find . -name "sentry*.ts" -o -name "sentry*.js"
grep -r "SENTRY_DSN" --include="*.ts" --include="*.env*"
```

**Key files to check:**
- `sentry.*.config.ts`
- Error boundary components
- Instrumentation files

---

## 7. User Feedback Loop

```bash
# Feedback mechanisms
grep -r "feedback" --include="*.ts" --include="*.tsx"
grep -r "survey" --include="*.tsx"
grep -r "report.*bug\|reportBug\|bugReport" --include="*.tsx"
grep -r "contact.*form\|contactForm" --include="*.tsx"

# External tools
grep -r "typeform\|hotjar\|intercom\|crisp" --include="*.tsx"

# GitHub Issues integration
grep -r "github.*issue\|githubIssue" --include="*.ts"
```

**Key files to check:**
- `**/feedback/**`
- Widget/modal components
- API routes for feedback submission

---

## 8. Authentication & Roles

```bash
# Auth providers
grep -r "clerk\|Clerk" --include="*.ts" --include="*.tsx"
grep -r "auth0\|Auth0" --include="*.ts"
grep -r "nextauth\|NextAuth" --include="*.ts"
grep -r "supabase.*auth" --include="*.ts"

# Role/permission patterns
grep -r "role\|Role" --include="*.ts" | grep -v "node_modules"
grep -r "permission\|Permission" --include="*.ts"
grep -r "RBAC\|rbac" --include="*.ts"
grep -r "isAdmin\|isOwner\|canAccess" --include="*.ts"

# Middleware
find . -name "middleware.ts" -o -name "middleware.js"
```

**Key files to check:**
- `middleware.ts`
- `**/auth/**` or `**/security/**`
- User/role type definitions

---

## 9. Custom Domain with SSL

```bash
# Domain configuration
find . -name "vercel.json" -o -name "netlify.toml"
grep -r "domain\|DOMAIN" --include="*.json" --include="*.toml"

# SSL references
grep -r "https\|ssl\|certificate" --include="*.json" --include="*.toml"

# Check for dev URLs that shouldn't be in prod
grep -r "vercel.app\|netlify.app\|replit.app\|localhost" --include="*.ts" --include="*.tsx"
```

**Key files to check:**
- `vercel.json`, `netlify.toml`
- Environment variable files
- Deployment configs

---

## 10. Real Database & Backups

```bash
# Database providers
grep -r "supabase" --include="*.ts"
grep -r "convex" --include="*.ts"
grep -r "prisma\|Prisma" --include="*.ts"
grep -r "neon\|planetscale" --include="*.ts"
grep -r "postgres\|postgresql" --include="*.ts"

# Backup references
grep -r "backup\|Backup" --include="*.ts"
grep -r "snapshot\|Snapshot" --include="*.ts"

# Schema files
find . -name "schema.prisma" -o -name "schema.ts" | grep -v node_modules
```

**Key files to check:**
- `prisma/schema.prisma`
- `convex/schema.ts`
- Database migration files

---

## Quick Discovery Script

Run this to get a quick overview:

```bash
echo "=== MVP Launch Discovery ==="

echo "\n1. Stripe:"
grep -rl "stripe" --include="*.ts" | head -5

echo "\n2. Mobile/PWA:"
find . -name "manifest.json" 2>/dev/null | head -3

echo "\n3. Onboarding:"
grep -rl "onboarding" --include="*.tsx" | head -3

echo "\n4. AI Stability:"
grep -rl "retry\|backoff" --include="*.ts" | head -3

echo "\n5. Email:"
grep -rl "sendEmail\|SES\|Resend" --include="*.ts" | head -3

echo "\n6. Error Logging:"
find . -name "sentry*.ts" 2>/dev/null | head -3

echo "\n7. Feedback:"
grep -rl "feedback" --include="*.tsx" | head -3

echo "\n8. Auth:"
grep -rl "clerk\|auth0\|nextauth" --include="*.ts" | head -3

echo "\n9. Domain Config:"
find . -name "vercel.json" -o -name "netlify.toml" 2>/dev/null

echo "\n10. Database:"
find . -name "schema.prisma" -o -name "schema.ts" 2>/dev/null | grep -v node_modules | head -3
```
