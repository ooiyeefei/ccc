# Meta Pixel standard events for common conversions

Use a **standard event** name where one fits — Meta's ad optimization, reporting, and audience-building recognize standard events automatically, so you get more signal for free than with a custom event. Fire it after the action truly succeeds, with non-PII params only. Official reference: https://developers.facebook.com/docs/meta-pixel/reference

| Action on your site | `fbq('track', ...)` event | Useful (non-PII) params |
|---|---|---|
| Lead / waitlist / contact form submitted | `Lead` | `content_name`, `value`, `currency` |
| Account created / signed up | `CompleteRegistration` | `content_name`, `status` |
| Free trial started | `StartTrial` (or `Lead` if pre-launch) | `value`, `currency`, `predicted_ltv` |
| Subscribed (recurring) | `Subscribe` | `value`, `currency`, `predicted_ltv` |
| Added to cart | `AddToCart` | `content_ids`, `content_type`, `value`, `currency` |
| Checkout began | `InitiateCheckout` | `content_ids`, `value`, `currency`, `num_items` |
| Purchase completed | `Purchase` (required: `value` + `currency`) | `content_ids`, `content_type`, `value`, `currency` |
| Search performed | `Search` | `search_string` (skip if it may contain PII) |
| Content/product viewed | `ViewContent` | `content_ids`, `content_type`, `content_name` |
| Contacted business | `Contact` | `content_name` |

## How to fire
```js
fbq('track', 'Lead', { content_name: 'waitlist', value_bucket: 'high' });
fbq('track', 'Purchase', { value: 29.90, currency: 'USD', content_ids: ['sku_1'] });
```
- `Purchase` **requires** `value` and `currency` or it won't optimize properly.
- Custom (non-standard) actions use `fbq('trackCustom', 'MyEvent', {...})` — but prefer a standard event when one fits.

## Do NOT send as parameters (browser Pixel)
Email, phone, name, address, IDs. Browser-side PII is a compliance risk and not needed for optimization — send `content_name`, a `value`/`value_bucket`, a persona/category instead. (Hashed PII for match quality belongs to the Conversions API's Advanced Matching, a deliberate server-side + consent decision — see `conversions-api.md`, not browser events.)

## Deduplication note (only relevant if you later add CAPI)
If you eventually send the same event from both the browser Pixel and the Conversions API, give each a shared `eventID` so Meta de-duplicates them and doesn't double-count. Not a concern for Pixel-only setups.
