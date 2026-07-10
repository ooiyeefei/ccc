# GA4 pre-spend verification checklist

The rule: **never run paid traffic to a page whose conversion you haven't watched fire with correct data.** A conversion that fires on failure, misses its parameters, or never fires will silently invalidate every downstream number — you'd be optimizing ad spend against noise and not know it. Ten minutes here saves a wasted campaign budget.

## The four-point check (do a REAL action, then confirm)
Trigger the actual conversion once (submit the form / complete the signup), then verify all four:

1. **The event lands.** In GA4 → **Admin → DebugView** (add `?debug_mode=1` to the page URL, or use the *GA Debugger* Chrome extension) — or **Reports → Realtime**. You should see your event (e.g. `generate_lead`) appear within seconds.
2. **The parameters are right.** Click the event in DebugView and confirm your custom params (persona, value_bucket, etc.) carry the correct values — not `(not set)`.
3. **No PII leaked.** Confirm email/phone/name are NOT present in any parameter.
4. **It only fires on success.** Deliberately cause a failure (e.g. submit with a bad payload) and confirm the event does **not** fire. Firing on failure is the most damaging silent bug.

Then, separately: confirm the event is toggled as a **Key Event** (Admin → Events) so it counts as a conversion.

## Common "no data / wrong data" causes
- **Nothing in Realtime at all** → the tag isn't loading. Check the Measurement ID matches the stream exactly; check an ad-blocker isn't blocking `googletagmanager.com`; on Next.js confirm the `<Script>` strategy loaded (`window.gtag` defined in console).
- **PageViews show but the custom event doesn't** → the event code isn't running (JS error before it, or the handler isn't attached). Check the browser console.
- **Event fires but params are `(not set)`** → the param wasn't registered as a custom dimension (Admin → Custom definitions), or the value was undefined at fire time.
- **Duplicate/inflated counts** → the tag is included twice (e.g. both a plugin and a manual snippet, or on both a layout and a page). Load it once.
- **Data appears in DebugView but not standard reports** → standard reports lag up to 24–48h; DebugView/Realtime are the source of truth for "is it wired".
- **`?debug_mode=1` shows nothing** → try the GA Debugger extension instead, and confirm you're viewing the right property in the GA UI.
