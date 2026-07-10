# Meta Pixel pre-spend verification checklist

The rule: **never run Facebook/Instagram ads to a page whose conversion you haven't watched fire correctly.** A miswired conversion makes Meta optimize toward the wrong people and inflate/miss counts — and the dashboard won't tell you it's wrong. A few minutes here protects the whole campaign budget.

Important: with `next/script` (or any deferred loader), the pixel is injected **client-side after hydration**, so it will NOT appear in server HTML / a `curl`. Don't verify with curl — verify in a real browser with the tools below.

## The check (real browser, real action)
1. **Install the Meta Pixel Helper** (Chrome extension). Load the page → the Helper icon shows your pixel is present and `PageView` fired, with your Pixel ID.
2. **Fire the real conversion** (submit the form / complete signup). The Helper should show your event (`Lead`, `CompleteRegistration`, `Purchase`) **with its parameters**.
3. **No PII:** confirm no email/phone/name is in the event parameters.
4. **Only on success:** cause a failure (bad submit) and confirm the event does NOT fire.
5. **Events Manager → your dataset → Test events:** enter the site URL and watch events arrive live server-side too — this is Meta's own confirmation the data reached them.

Then in Events Manager, the event should show as **Active** within ~20–30 minutes of real traffic.

## Common failures
- **Pixel Helper shows nothing** → base code not loading. Check the Pixel ID, check an ad-blocker isn't blocking `connect.facebook.net`, and (Next.js) confirm `window.fbq` is defined in the console.
- **PageView works but the conversion event doesn't** → the event code isn't running (JS error, or the submit handler fired the redirect before `fbq`). Fire the event *before* navigating away, or use `fbq(..., {eventID}, {eventID})` + a small delay.
- **Event fires twice** → base code included twice (e.g. a plugin AND a manual snippet). Load it once.
- **"Pixel not receiving activity" banner in Events Manager** → normal until real traffic hits the live page; Test Events bypasses this for verification.
- **Ad blocker on your own machine** hides everything → test in a clean browser profile / incognito with the blocker off.

## Then, before spending
- Confirm your conversion event is selected as the **optimization event** when you build the ad set (Leads objective → your `Lead` event).
- Only once you've seen it fire correctly does budget go live.
