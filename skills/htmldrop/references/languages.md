# One page, several languages

When readers prefer another language (an English proposal for an owner who reads Chinese, a
brief for a Malay-speaking team), publish **one page with a language toggle**, not one file per
language. One link, one password, one comment thread, and the versions stay in step.

## The pattern: translations side by side

Mark every translation with a `lang` attribute, side by side, and let CSS show one language:

```html
<h2><span lang="en">Cost and effort</span><span lang="zh">费用与工作量</span></h2>
<p lang="en">The core build is RM 40,000.</p><p lang="zh">核心系统为 RM 40,000。</p>
```

`lang` is the web's own marker for language. Browsers also use it to choose the right Chinese
glyphs and screen-reader voice.

Paste these three parts. Add a line to the CSS rule and a button for each language you offer.

```html
<html lang="en">
<title data-title-zh="费用报价">Quotation</title>

<style>
  html[lang|="en"] body [lang]:not([lang|="en"]),
  html[lang|="zh"] body [lang]:not([lang|="zh"]) { display: none !important; }
  .langtog{display:inline-flex;gap:2px;padding:3px;border-radius:999px;border:1px solid color-mix(in srgb,currentColor 35%,transparent)}
  .langtog button{border:0;background:none;color:inherit;font:inherit;font-size:13px;font-weight:700;padding:4px 12px;border-radius:999px;cursor:pointer}
  .langtog button[aria-pressed="true"]{background:color-mix(in srgb,currentColor 18%,transparent)}
</style>

<div class="langtog" role="group" aria-label="Language" translate="no">
  <button type="button" data-set-lang="en">EN</button><button type="button" data-set-lang="zh">中文</button>
</div>

<script>
(function () {
  var root = document.documentElement, KEY = 'htmldrop-lang';
  var buttons = [].slice.call(document.querySelectorAll('[data-set-lang]'));
  var langs = buttons.map(function (b) { return b.dataset.setLang; });
  var title = document.querySelector('title'), base = title ? title.textContent : '';
  function set(l, save) {
    root.lang = l;
    buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.setLang === l)); });
    if (title) document.title = title.getAttribute('data-title-' + l) || base;
    if (save) { try { localStorage.setItem(KEY, l); } catch (e) {} }
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: l } }));
  }
  // text written by scripts: L({en: 'Total', zh: '合计'})
  window.L = function (m) { return m[root.lang] || m[langs[0]] || ''; };
  var asked = null, saved = null;
  try { asked = new URLSearchParams(location.search).get('lang'); } catch (e) {}
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  set([asked, saved, root.lang].filter(function (l) { return langs.indexOf(l) >= 0; })[0] || langs[0], false);
  buttons.forEach(function (b) { b.addEventListener('click', function () { set(b.dataset.setLang, true); }); });
})();
</script>
```

The reader's choice is remembered. A link ending in `?lang=zh` opens in Chinese, which is
handy for the one reader who needs it, and it works behind an htmldrop password.

## Where translations go wrong

- **Text written by scripts** (totals, recommendations, chart labels) has no spans. Build it
  with `L({en:…, zh:…})` and redraw it on the `langchange` event.
- **Diagrams**: keep one Mermaid source per language (`id="diagram-source-zh"` beside
  `diagram-source-en`), pick it by `document.documentElement.lang`, and call the theme-aware
  re-render from `references/design-and-visuals.md` on `langchange` too.
- **Generic span rules**: a rule such as `.card li span{display:block;color:grey}` also
  restyles the translation spans. Scope such rules to a class.
- **Flex and grid labels**: inside a flex or grid box, the space between a translation and
  the text beside it disappears ("Counter15,000"). Put the whole label, number included,
  inside each translation.
- **Nesting**: an English word marked `lang="en"` inside a Chinese sentence hides together
  with the English. Leave product names unmarked inside the sentence.
- **The toggle buttons** carry no `lang` of their own, or one of them would hide.
- **Shared on purpose**: mock screens show the app's real wording in one language. Mark that
  area `translate="no"` and translate only its caption.
- **Attributes**: `title`, `aria-label`, `placeholder` and `alt` don't switch by themselves.
  Set them from a script with `L()` on `langchange`, or avoid relying on them.

## Write it, then check it

1. Write the source language first and finish it. Translate whole sentences, not words;
   numbers, currency and dates stay identical across languages.
2. Run the check. It lists sentences missing a translation and text that every reader sees
   in one language:
   ```bash
   python3 <this skill>/scripts/check_languages.py /abs/page.html --langs en,zh
   ```
   It exits 1 while anything is unpaired. Shared text can be fine (names, figures); read the
   list.
3. Switch the toggle in a browser and read both languages from top to bottom.
4. Tell the user who should read the translation before it ships. Machine translation of a
   commercial document needs a native reader; say so rather than claim it is checked.
