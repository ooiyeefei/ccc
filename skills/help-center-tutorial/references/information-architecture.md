# Information architecture - domain, task, article

## The tree

Help home (search, the domains, a few starting paths) > **domain** page > **task** article. A domain page is an index: a title, a sentence, a jump list of sub-areas and, under each, a card per task with a one-line summary. It carries no steps.

- **Domain**: the noun in the product's own navigation, in the same order (Sales, Purchases, Stock, Bank, People, Reports, Settings). The help path then equals the product path, and a renamed menu is detectable from the sheets' `path` field. Group a domain's tasks into sub-areas once it holds more than eight, and keep a sub-area under about twelve so a domain page stays one scroll.
- **Task**: a verb phrase in the user's words ("Send a quotation", "Record a customer payment"). One goal per article. A task that differs by role or by web and mobile is a tab inside the article, not a new article.

## Article types

Two. A **Task** article says how to do it. A **Concept** article says how something works, and exists only when two or more tasks need the same explanation (how periods lock, what a status means). Troubleshooting lives inside the task as "If something goes wrong". A standalone troubleshooting article is for one error with many causes.

A **path** is an ordered list of tasks ("Your first invoice", "Month end", "Getting started"). It is an index page, not an article, so it never has its own steps to drift. Help home lists a few paths beside the domains.

## Naming and addresses

- Titles open with a verb. Metadata carries the user's other words for the same goal, so search finds "block off", "reserve", "holiday".
- The URL is `/help/<domain>/<task-slug>`. A slug never changes without a redirect, and a merged or retired article's slug redirects to its replacement or to its domain page. Step anchors use the sheet's step ids.
- The task slug is the sheet's `task`, so one name joins the article, the sheet, the take and the media files.

## Links

Each task links to its prerequisites ("Before you start"), up to three related tasks, and one "Up next". The app links to the article from the page it documents: the sheet's `surfaces` field is the map for a "Help for this page" link.

## Industry and role

Industry is not a level. An article may be tagged with the industry of its example data; it is never copied per industry. Role is a line ("Who can do this") and, when steps differ, a tab. A task that differs by country (tax, e-invoicing) is a tab too, with its own sheet run on that country's workspace.

## Access

State access per asset, not per site: the article text and images (fictitious data only), the overview video, the step clips, and the files that carry a clip's words or pictures (captions, chapters, poster), which take the clip's gate. `article.json` holds text and file names only and follows the page; the page is rendered on the server from it. Tutorial video and clips default to signed-in only, meaning any authenticated user of the product unless the owner narrows it to a plan or role. The text and screenshots may be public for search and support deflection if the owner agrees; that is a decision to record, not a default. Gate on the media URL, never only on the page: a page gate alone leaves the file reachable by anyone holding its address. Media that is already public is listed in the backfill inventory; if the owner wants it gated, gate it at once at the storage layer, not task by task. Unlisted public video hosting is not private: its title and thumbnail are readable by anyone holding the address, so it does not qualify.

Where they live: the video sits inside its task article, in an in-app help route for signed-in users, on private storage behind signed links, with text and images rendered from `article.json`. The hosting vendor is a separate decision; this skill states the rule, not the product.

## Localisation

The same tree per locale, under the app's own locale prefix. Text is keyed by step id. A locale's media comes from replaying the sheet in that locale, never from translating screenshots (`localisation.md`).
