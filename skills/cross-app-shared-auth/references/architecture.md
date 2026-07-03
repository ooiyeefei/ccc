# Architecture

This describes the shared-auth pattern in a vendor-neutral way. Swap in whatever identity provider and databases you use. Nothing here is specific to one product, and no secrets or keys belong in this document.

## The two layers

The whole design rests on separating two things that people constantly conflate.

- **Identity**: who a person is. One shared provider issues one stable user id for the whole family. Signing in on one app signs the person in on the others (single sign-on across subdomains). Identity says nothing about access.
- **Entitlement**: what a person may use. Stored centrally, keyed on the shared user id, one record per app the person has joined. Each app checks it. No record means no access.

Keep them independent and the rest falls into place. One login, and access that is still per app and opt-in, are the intended combination, not a contradiction.

## The three integration points

Every app in the family connects to three things. Note that the app's database never talks to the identity provider directly. The app's **auth layer** verifies identity tokens, and the database simply stores rows keyed on the user id that the auth layer extracts.

| # | Connects to | For | How |
|---|-------------|-----|-----|
| 1 | the shared identity provider | identity | the app's auth layer trusts the shared issuer and keys, and pins its own origin (`authorizedParties`) |
| 2 | the central accounts database | authorization | the app calls `getAccess(appSlug)` and gates server-side, deny-by-default |
| 3 | the app's own database (any vendor) | domain data, tier, quota, billing | rows keyed on the shared user id |

## Diagram

```
                         SHARED IDENTITY PROVIDER
                     (one instance, rooted at the parent domain)
                                     |
             one shared user id + one session cookie across *.example.com
                                     |
        +----------------------------+----------------------------+
        |                            |                            |
   landing / hub               app A (a.example.com)        app B (b.example.com)
   (example.com)                     |                            |
        |                            |                            |
        |  reads/writes access       |  reads/writes access       |  reads/writes access
        v                            v                            v
                      CENTRAL ACCOUNTS DATABASE (one)
                users(userId, ...)   app_access(userId, appSlug, status, tier)
                        the entitlement whitelist, keyed on userId
        ^                            ^                            ^
        |                            |                            |
        |                    app A's OWN db               app B's OWN db
        |                 (domain data, tier,           (domain data, tier,
        |                  quota, credits, billing)       quota, credits, billing)
        |
   the hub can also live-render "your apps" from app_access
```

Everything joins on the **shared user id**. The central accounts database holds the thin "which apps, what status" index. Each app's own database holds the heavy, authoritative domain data and any money state.

## The token audience: one clean session token, per-service templates

Integration point 1 hides a detail that silently breaks the whole chain if you miss it. A backend that verifies a JWT (the central accounts store, and equally any other app backend) checks the token's audience claim (`aud`) against the audience it is configured to accept. A token whose `aud` does not match is rejected as "no matching provider," even though the person is perfectly signed in.

The generic session token an identity provider issues carries no `aud`, because it is meant to be universal. So you do not send it to an audience-checking backend directly. Instead you define one named token template per backend, each stamping that backend's expected audience, and each app requests the template for the backend it is calling:

| Token | Requested with | `aud` claim | Used by |
|-------|----------------|-------------|---------|
| session token | the default `getToken()` | none | generic identity, anything that does not check `aud` |
| central-store template | `getToken({ template: "<store-name>" })` | the central store's id | the central accounts store |
| another backend's template | `getToken({ template: "<other>" })` | that backend's audience | for example a Supabase app (`authenticated`), a gateway authorizer, an identity-aware proxy |

The rule that keeps a multi-database portfolio correct: **never stamp a service's audience onto the shared session token.** Doing so makes every app's identity token claim it is for that one service, which breaks every other backend that validates a different audience. Keep the session token clean and add one template per backend, so only the tokens bound for a given backend carry that backend's audience.

## Where each kind of data lives

- **Identity** (email, profile, credentials, sessions): the shared identity provider. Never copied into app databases.
- **Cross-app entitlement** (which apps a user joined, per-app status and tier label): the central accounts database. Thin. Rarely changes shape.
- **Domain data + system of record for money** (the app's actual content, real credit balances, quota counters, billing): the app's own database. Never centralized, or you get a second source of truth that drifts.
- **Optional usage rollup** (a per-app summary for a cross-app dashboard): the central database, pushed up by each app. A summary, not the authoritative counter.

## Subdomains versus separate domains

Silent single sign-on through a shared cookie spans **subdomains of one parent domain** only. Two consequences:

- Apps on `*.example.com` share the cookie and the user id automatically. This is the happy path.
- An app on a **different root domain** cannot share that cookie. Options: give it its own identity instance (a clean island with its own separate accounts, no cross-domain link), or bridge it deliberately (some providers offer cross-domain SSO as a paid add-on). Pick consciously and write down the tradeoff, because the cost is a person ending up with two separate accounts if you do neither.

## Why one shared identity instance, not one per app

It is tempting to give each app its own identity instance, especially if the provider makes extra instances cheap or free. Resist it for apps that should share a user. Separate instances mean the same human gets a **different user id in each app**, so there is nothing to join on, no single account, and no place to hang the cross-app "which apps" record. The shared instance is the whole reason the model works.

## Security note that is easy to miss

Because the session cookie is shared across subdomains, every app backend must confirm that a token was minted for **its own origin** before trusting it (`authorizedParties`, or the equivalent for your provider). Skip it and a compromised or hostile sibling subdomain can present the shared session to another app's API. This is a per-app requirement, not a one-time platform setting.
