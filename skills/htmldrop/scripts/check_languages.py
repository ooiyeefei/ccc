#!/usr/bin/env python3
"""Check a multi-language page before it ships.

The page marks each translation with a lang attribute, side by side:
  <span lang="en">Price</span><span lang="zh">价格</span>
and the toggle shows one language at a time (see references/languages.md).

  check_languages.py PAGE [--langs en,zh] [--show 20]

Reports:
  - unpaired: sibling translations where a language is missing, so that text
    vanishes when the reader switches. Also catches a lang element nested inside
    another language's text, which hides with the wrong language.
  - shared: visible text outside any lang element, which every reader sees in one
    language. Fine for numbers and names. Mark deliberate shared areas (in-app text
    on mock screens, the language buttons) with translate="no" to skip them.
Exits 1 when anything is unpaired.
"""
import argparse, collections, html.parser, pathlib, re, sys

SKIP = {"script", "style", "template", "svg", "code", "pre", "noscript", "title"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
WORDY = re.compile(r"[A-Za-z]{3,}|[㐀-鿿]")


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.top = {"tag": None, "lang": None, "skip": False, "item": None, "kids": []}
        self.stack = []
        self.counts = collections.Counter()
        self.runs, self.shared = [], []

    def cur(self):
        return self.stack[-1] if self.stack else self.top

    def handle_starttag(self, tag, attrs):
        if tag == "html":
            return
        a, parent = dict(attrs), self.cur()
        lang = (a.get("lang") or "").split("-")[0].lower() or None
        item = None
        if lang and not parent["skip"]:
            item = [lang, self.getpos()[0], []]
            self.counts[lang] += 1
        parent["kids"].append(item)  # None: a plain element, which ends a run of translations
        if tag in VOID:
            return
        skip = parent["skip"] or tag in SKIP or a.get("translate") == "no"
        self.stack.append({"tag": tag, "lang": lang, "skip": skip, "item": item, "kids": []})

    def handle_endtag(self, tag):
        if tag == "html" or not any(e["tag"] == tag for e in self.stack):
            return
        while self.stack:
            e = self.stack.pop()
            self._end(e)
            if e["tag"] == tag:
                break

    def _end(self, e):
        run = []
        for k in e["kids"] + [None]:
            if k is None:
                if run:
                    self.runs.append(run)
                run = []
            else:
                run.append(k)

    def handle_data(self, data):
        text = " ".join(data.split())
        cur = self.cur()
        if not text or cur["skip"]:
            return
        owner = next((e for e in reversed(self.stack) if e["lang"]), None)
        if owner:
            if owner["item"]:
                owner["item"][2].append(text)
        elif WORDY.search(text):
            self.shared.append((self.getpos()[0], text))
            cur["kids"].append(None)

    def done(self):
        while self.stack:
            self._end(self.stack.pop())
        self._end(self.top)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--langs", help="expected languages, comma separated (default: every language found)")
    ap.add_argument("--show", type=int, default=20, help="how many examples to print per problem")
    a = ap.parse_args()
    p = Page()
    p.feed(pathlib.Path(a.page).read_text("utf-8"))
    p.close()
    p.done()
    langs = a.langs.split(",") if a.langs else sorted(p.counts)
    print("translations: " + (", ".join(f"{l} {p.counts[l]}" for l in langs) or "none found"))
    if len(langs) < 2:
        print("Fewer than two languages are marked; nothing to pair.")
        return 0
    unpaired = []
    for run in p.runs:
        c = collections.Counter(k[0] for k in run if k[0] in langs)
        if c and len({c[l] for l in langs}) > 1:
            unpaired.append((run, c))
    print(f"unpaired: {len(unpaired)}")
    for run, c in unpaired[: a.show]:
        missing = ",".join(l for l in langs if c[l] < max(c.values()))
        text = " ".join(run[0][2])[:70]
        print(f"  line {run[0][1]}: missing {missing}  {text!r}")
    print(f"shared text (shows in every language): {len(p.shared)}")
    for line, text in p.shared[: a.show]:
        print(f"  line {line}: {text[:80]!r}")
    return 1 if unpaired else 0


if __name__ == "__main__":
    sys.exit(main())
