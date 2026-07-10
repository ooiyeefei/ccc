# GA4 recommended events for common conversions

Use GA4's **recommended event names** where one fits your action. They're not required (you can name a custom event anything), but recommended names light up built-in reports and audiences automatically, so you get more for free. Full official list: https://support.google.com/analytics/answer/9267735

Pick the one that matches the action, fire it after the action truly succeeds, and attach only non-PII parameters.

| Action on your site | Event name | Useful (non-PII) params |
|---|---|---|
| Lead / waitlist / contact form submitted | `generate_lead` | `currency`, `value`, plus your own segmenters (persona, plan interest) |
| Account created / signed up | `sign_up` | `method` (e.g. `email`, `google`) |
| Free trial started | `sign_up` or a custom `start_trial` | plan/tier bucket |
| Added to cart | `add_to_cart` | `currency`, `value`, `items` |
| Checkout began | `begin_checkout` | `currency`, `value`, `items` |
| Purchase completed | `purchase` | `transaction_id`, `currency`, `value`, `items` |
| Search performed | `search` | `search_term` (avoid if it can contain PII) |
| Content viewed | `view_item` / `view_content` | item/content id + category |

## Custom parameters and segmentation
Anything beyond the standard params is a **custom parameter**. To use it in reports, register it as a **custom dimension** (Admin → Custom definitions → Create custom dimension) so GA4 keeps the values. Example: register `plan_tier` and `persona` once, then every `generate_lead` carrying them becomes segmentable.

Value/currency: GA4 uses `value` + `currency` to compute conversion value. For a waitlist you can pass a proxy value (e.g. the price they'd pay) to compare cohorts — just be consistent.

## Do NOT send as parameters
Email, phone, name, street address, government IDs, or anything that identifies a person. GA4's terms forbid PII and it can get data purged. Send a **bucket** instead (e.g. `value_bucket: 'high'`, `persona: 'freelancer'`) — that's what analysis actually needs.
