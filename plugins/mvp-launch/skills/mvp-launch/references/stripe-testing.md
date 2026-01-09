# Stripe Testing Checklist

Complete verification checklist for Stripe integration before launch.

---

## Pre-Launch Checklist

### 1. Use Test Mode First

Turn on "View test data" in Stripe Dashboard and use test keys:
- `sk_test_...` (Secret key)
- `pk_test_...` (Publishable key)

### 2. Webhook Endpoint Setup

Register your webhook endpoint in Stripe Dashboard:
```
https://yourdomain.com/api/stripe/webhook
```
or
```
https://yourdomain.com/api/v1/billing/webhooks
```

**Get webhook signing secret:** `whsec_...`

### 3. Required Webhook Events

Your endpoint MUST handle these events:

| Event | Purpose |
|-------|---------|
| `customer.subscription.trial_will_end` | Alert before trial ends |
| `customer.subscription.created` | New subscription started |
| `customer.subscription.updated` | Plan changes |
| `customer.subscription.deleted` | Subscription cancelled |
| `invoice.payment_succeeded` | Confirms payment after trial |
| `invoice.payment_failed` | Failed/expired card |
| `invoice.created` | Useful for logging |
| `checkout.session.completed` | Checkout flow completed |

---

## Stripe CLI Testing

Install Stripe CLI:
```bash
# macOS
brew install stripe/stripe-cli/stripe

# Login
stripe login
```

### Simulate Webhook Events

```bash
# Trial ending warning
stripe trigger customer.subscription.trial_will_end

# Payment success
stripe trigger invoice.payment_succeeded

# Payment failure (card declined)
stripe trigger invoice.payment_failed

# New subscription
stripe trigger customer.subscription.created

# Subscription updated (plan change)
stripe trigger customer.subscription.updated

# Subscription cancelled
stripe trigger customer.subscription.deleted

# Checkout completed
stripe trigger checkout.session.completed
```

### Forward Webhooks to Local Dev

```bash
# Forward to local server
stripe listen --forward-to localhost:3000/api/v1/billing/webhooks

# With specific events only
stripe listen --forward-to localhost:3000/api/v1/billing/webhooks \
  --events customer.subscription.trial_will_end,invoice.payment_failed
```

---

## Test Card Numbers

| Scenario | Card Number |
|----------|-------------|
| Success | `4242 4242 4242 4242` |
| Decline | `4000 0000 0000 0002` |
| Insufficient funds | `4000 0000 0000 9995` |
| Expired card | `4000 0000 0000 0069` |
| 3D Secure required | `4000 0027 6000 3184` |

**For all test cards:**
- Expiry: Any future date (e.g., `12/34`)
- CVC: Any 3 digits (e.g., `123`)
- ZIP: Any 5 digits (e.g., `12345`)

---

## Live Key Testing (Final Step)

Before launch, test with real live keys:

1. Switch to live mode in Stripe Dashboard
2. Use `sk_live_...` and `pk_live_...`
3. Make a real $1 test purchase
4. Verify webhook fires correctly
5. Process a refund
6. Check Stripe Dashboard shows the transaction

**Important:** Don't forget to update environment variables:
- `STRIPE_SECRET_KEY` → live key
- `STRIPE_PUBLISHABLE_KEY` → live key
- `STRIPE_WEBHOOK_SECRET` → live webhook secret

---

## Verification Checklist

Before marking Stripe as "Launch Ready":

- [ ] Webhook endpoint registered in Stripe Dashboard
- [ ] All 8 required events configured
- [ ] `STRIPE_WEBHOOK_SECRET` set in production env
- [ ] Idempotency handling (don't process same event twice)
- [ ] Test mode simulations pass
- [ ] Live key test purchase successful
- [ ] Trial → paid conversion tested
- [ ] Failed payment handling tested
- [ ] Customer portal working
- [ ] Plan switching working (if applicable)

---

## Common Issues

### Webhook Not Receiving Events
1. Check endpoint URL is correct (no typos)
2. Verify HTTPS (Stripe won't call HTTP in live mode)
3. Check firewall/security rules
4. Verify endpoint returns 200 quickly (within 20s)

### Signature Verification Failing
1. Ensure `STRIPE_WEBHOOK_SECRET` matches Dashboard
2. Check you're using the raw request body (not parsed JSON)
3. Verify correct secret for mode (test vs live)

### Duplicate Processing
Implement idempotency:
```typescript
// Check if event already processed
const existingEvent = await db.query({
  table: "stripeEvents",
  filter: { eventId: event.id }
});

if (existingEvent) {
  return { received: true }; // Already processed
}

// Process and store event ID
await db.insert("stripeEvents", { eventId: event.id, ... });
```
