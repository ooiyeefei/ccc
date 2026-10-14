#!/usr/bin/env python3
"""Version history for a page published with htmldrop.

htmldrop overwrites a page at the same link on every push, so the server keeps no
history. This script keeps it with the page instead: each version is stored beside
the page, and the older ones are embedded in it (gzip + base64) behind a
"Version history" button. One link and one password cover every version.

  versions.py snapshot PAGE --label "en=Scope and prices" --label "zh=范围和价格"
  versions.py build PAGE        # refresh the page; the current version changes in place
  versions.py list PAGE
  versions.py restore PAGE      # recreate the versions folder from a pulled page

Versions are stored in <page-stem>.versions/ beside the page; keep that folder with it.
Run snapshot or build before every push, so the stored current version matches what
readers see. Only snapshot what every reader may see: older versions stay readable.
"""
import argparse, base64, datetime, gzip, json, pathlib, re, sys

START, END = "<!-- htmldrop-versions:start -->", "<!-- htmldrop-versions:end -->"
BLOCK_RE = re.compile(re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"\n?")
DATA_RE = re.compile(r'<script type="application/json" id="htmldrop-versions-data">([\s\S]*?)</script>')


def strip(text):
    return BLOCK_RE.sub("", text)


def vdir(page):
    return page.with_name(page.stem + ".versions")


def load(page):
    f = vdir(page) / "versions.json"
    return json.loads(f.read_text("utf-8")) if f.exists() else []


def save(page, items):
    d = vdir(page)
    d.mkdir(exist_ok=True)
    (d / "versions.json").write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", "utf-8")


def embedded(text):
    m = DATA_RE.search(text)
    return json.loads(m.group(1)) if m else []


def guard(page, text, items):
    if not items and embedded(text):
        sys.exit(f"{page.name} already carries a version history but {vdir(page).name}/ is missing.\n"
                 f"Run `versions.py restore {page}` first, or the older versions would be dropped.")


def pairs(values, default_lang):
    out = {}
    for v in values or []:
        k, sep, text = v.partition("=")
        if sep and re.fullmatch(r"[a-z]{2,3}(-[A-Za-z0-9]+)?", k.strip().lower()):
            out[k.strip().lower()] = text.strip()
        else:
            out[default_lang] = v.strip()
    return out


def page_lang(text):
    m = re.search(r"<html\b[^>]*?\slang=[\"']?([A-Za-z-]+)", text, re.I)
    return (m.group(1) if m else "en").split("-")[0].lower()


def snapshot(page, labels, notes):
    text = page.read_text("utf-8")
    items = load(page)
    guard(page, text, items)
    lang = page_lang(text)
    label, note = pairs(labels, lang), pairs(notes, lang)
    if not label:
        sys.exit("--label is required: one short line saying what this version is")
    cur = next((i for i in items if i.get("current")), None)
    if cur and (vdir(page) / cur["file"]).read_text("utf-8") == strip(text):
        sys.exit(f"Nothing changed since {cur['id']}. Edit the page first, or use `build` to republish as is.")
    n = max((int(i["id"][1:]) for i in items), default=0) + 1
    today = datetime.date.today().isoformat()
    for i in items:
        i["current"] = False
    items.append({"id": f"v{n}", "date": today, "file": f"v{n}-{today}.html",
                  "label": label, "note": note, "current": True})
    save(page, items)
    print(f"v{n} is now the current version")
    build(page)


def build(page):
    text = page.read_text("utf-8")
    items = load(page)
    guard(page, text, items)
    if not items:
        sys.exit(f"No versions yet. Start the history with: versions.py snapshot {page} --label \"...\"")
    body = strip(text)
    if body.count("</body>") != 1:
        sys.exit("The page needs exactly one </body> tag.")
    d, data = vdir(page), []
    for i in items:
        e = {"id": i["id"], "date": i["date"], "label": i.get("label") or {}, "note": i.get("note") or {},
             "current": bool(i.get("current"))}
        if e["current"]:
            (d / i["file"]).write_text(body, "utf-8")
        else:
            raw = strip((d / i["file"]).read_text("utf-8")).encode("utf-8")
            e["blob"] = base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode("ascii")
        data.append(e)
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    block = "\n".join([START, CSS, f'<script type="application/json" id="htmldrop-versions-data">{payload}</script>',
                       JS, END]) + "\n"
    out = body.replace("</body>", block + "</body>")
    page.write_text(out, "utf-8")
    older = sum(1 for e in data if not e["current"])
    print(f"{page.name}: {older} older version(s) embedded, {len(out.encode('utf-8')) // 1024} KB")


def restore(page):
    text = page.read_text("utf-8")
    if load(page):
        sys.exit(f"{vdir(page).name}/ already exists; nothing to restore.")
    data = embedded(text)
    if not data:
        sys.exit(f"{page.name} has no embedded version history.")
    d = vdir(page)
    d.mkdir(exist_ok=True)
    items = []
    for e in data:
        f = f"{e['id']}-{e['date']}.html"
        html = strip(text) if e.get("current") else gzip.decompress(base64.b64decode(e["blob"])).decode("utf-8")
        (d / f).write_text(html, "utf-8")
        items.append({"id": e["id"], "date": e["date"], "file": f, "label": e.get("label") or {},
                      "note": e.get("note") or {}, "current": bool(e.get("current"))})
    save(page, items)
    print(f"restored {len(items)} version(s) into {d.name}/")


def show(page):
    for i in load(page):
        label = i.get("label") or {}
        first = label.get("en") or next(iter(label.values()), "")
        print(f"{i['id']:>4}  {i['date']}  {'current' if i.get('current') else '       '}  {first}")


CSS = """<style>
  .vh-btn{display:inline-flex;align-items:center;gap:6px;font:inherit;font-weight:700;font-size:13px;line-height:1.2;padding:6px 13px;border-radius:999px;cursor:pointer;color:inherit;background:rgba(127,127,127,.14);border:1px solid rgba(127,127,127,.38)}
  .vh-btn svg{width:15px;height:15px;flex:0 0 auto}
  .vh-btn.vh-float{position:fixed;top:12px;right:12px;z-index:2147482990;background:Canvas;color:CanvasText;box-shadow:0 2px 10px rgba(0,0,0,.15)}
  .vh-panel{position:fixed;top:0;right:0;bottom:0;width:min(340px,92vw);background:Canvas;color:CanvasText;border-left:1px solid rgba(127,127,127,.3);box-shadow:-8px 0 30px rgba(0,0,0,.18);z-index:2147483000;display:flex;flex-direction:column;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
  .vh-panel[hidden],.vh-view[hidden]{display:none}
  .vh-head{display:flex;align-items:center;justify-content:space-between;padding:16px 18px;border-bottom:1px solid rgba(127,127,127,.25)}
  .vh-head b{font-size:16px}
  .vh-x{border:0;background:none;color:inherit;font-size:22px;line-height:1;cursor:pointer;opacity:.6;padding:2px 6px}
  .vh-list{overflow:auto;padding:8px}
  .vh-item{display:block;width:100%;text-align:left;border:1px solid transparent;background:none;color:inherit;border-radius:10px;padding:11px 12px;cursor:pointer;font:inherit}
  .vh-item:hover,.vh-item.on{background:color-mix(in srgb,var(--vh-accent,#2563eb) 10%,Canvas)}
  .vh-item.on{border-color:color-mix(in srgb,var(--vh-accent,#2563eb) 40%,Canvas)}
  .vh-item b{display:block;font-size:14px}
  .vh-item span{display:block;font-size:13px;opacity:.85;margin-top:2px}
  .vh-item small{display:block;font-size:12px;opacity:.65;margin-top:2px}
  .vh-item b i{display:inline-block;font-style:normal;margin-left:6px;font-size:10.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:999px;background:color-mix(in srgb,#16a34a 16%,Canvas);color:#15803d;vertical-align:1px}
  .vh-foot{margin-top:auto;padding:12px 18px;border-top:1px solid rgba(127,127,127,.25);font-size:12px;opacity:.7}
  .vh-view{position:fixed;top:0;left:0;bottom:0;right:min(340px,92vw);z-index:2147482999;background:Canvas;display:flex;flex-direction:column}
  .vh-bar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:10px 16px;background:color-mix(in srgb,#d97706 14%,Canvas);border-bottom:2px solid #d97706;color:CanvasText;font:14px system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
  .vh-back{margin-left:auto;border:0;background:var(--vh-accent,#2563eb);color:#fff;font:inherit;font-weight:700;font-size:13px;padding:7px 14px;border-radius:9px;cursor:pointer}
  .vh-frame{flex:1;border:0;width:100%;background:#fff}
  @media (max-width:760px){.vh-view{right:0}}
</style>"""

JS = r"""<script>
(function(){
  var src=document.getElementById('htmldrop-versions-data'); if(!src) return;
  var data=JSON.parse(src.textContent); if(!data.length) return;
  var root=document.documentElement, viewing=null;
  var UI={
    en:{title:'Version history',cur:'Current',older:'Older version: ',back:'Back to current version',foot:'Older versions are read-only. Comments apply to the current version.',fail:'This browser cannot open older versions. Please update it.'},
    zh:{title:'版本记录',cur:'目前',older:'旧版本：',back:'返回目前版本',foot:'旧版本只供查看，留言只适用于目前版本。',fail:'此浏览器无法打开旧版本，请更新浏览器。'},
    ms:{title:'Sejarah versi',cur:'Semasa',older:'Versi lama: ',back:'Kembali ke versi semasa',foot:'Versi lama hanya boleh dibaca. Komen hanya untuk versi semasa.',fail:'Pelayar ini tidak dapat membuka versi lama. Sila kemas kini pelayar anda.'}
  };
  function lang(){return (root.lang||'en').toLowerCase().split('-')[0];}
  function ui(k){return (UI[lang()]||UI.en)[k];}
  function pick(m){if(!m)return '';if(typeof m==='string')return m;return m[lang()]||m.en||m[Object.keys(m)[0]]||'';}
  function fmt(iso){try{return new Date(iso+'T00:00:00').toLocaleDateString(root.lang||'en',{day:'numeric',month:'short',year:'numeric'});}catch(e){return iso;}}
  function inflate(b64){var bin=Uint8Array.from(atob(b64),function(c){return c.charCodeAt(0);});return new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream('gzip'))).text();}
  // open the older version in the reader's current language
  function withLang(html){var l=root.lang||'en';return html.replace(/<html\b[^>]*>/i,function(tag){return /\slang\s*=/i.test(tag)?tag.replace(/(\s)lang\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/i,'$1lang="'+l+'"'):tag.replace(/^<html/i,'<html lang="'+l+'"');});}
  var btn=document.createElement('button'); btn.type='button'; btn.className='vh-btn';
  btn.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><path d="M12 7v5l3 2"/></svg><span></span>';
  var slot=document.querySelector('[data-versions-slot]');
  if(slot) slot.appendChild(btn); else { btn.classList.add('vh-float'); document.body.appendChild(btn); }
  var panel=document.createElement('aside'); panel.className='vh-panel'; panel.hidden=true;
  panel.innerHTML='<div class="vh-head"><b></b><button type="button" class="vh-x" aria-label="Close">×</button></div><div class="vh-list"></div><div class="vh-foot"></div>';
  var view=document.createElement('div'); view.className='vh-view'; view.hidden=true;
  view.innerHTML='<div class="vh-bar"><span class="vh-msg"></span><button type="button" class="vh-back"></button></div><iframe class="vh-frame" title="Older version" sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox"></iframe>';
  document.body.appendChild(view); document.body.appendChild(panel);
  var list=panel.querySelector('.vh-list'), frame=view.querySelector('iframe');
  function render(){
    btn.querySelector('span').textContent=ui('title'); panel.setAttribute('aria-label',ui('title'));
    panel.querySelector('.vh-head b').textContent=ui('title');
    panel.querySelector('.vh-foot').textContent=ui('foot');
    view.querySelector('.vh-back').textContent=ui('back');
    list.innerHTML='';
    data.slice().reverse().forEach(function(v){
      var b=document.createElement('button'); b.type='button';
      b.className='vh-item'+((viewing?viewing===v.id:v.current)?' on':'');
      var d=document.createElement('b'); d.textContent=fmt(v.date);
      if(v.current){var c=document.createElement('i'); c.textContent=ui('cur'); d.appendChild(c);}
      var l=document.createElement('span'); l.textContent=pick(v.label);
      b.appendChild(d); b.appendChild(l);
      if(pick(v.note)){var n=document.createElement('small'); n.textContent=pick(v.note); b.appendChild(n);}
      b.addEventListener('click',function(){ v.current?close():open(v); });
      list.appendChild(b);
    });
    if(viewing){
      var v=data.filter(function(x){return x.id===viewing;})[0], m=view.querySelector('.vh-msg'), s=document.createElement('b');
      m.textContent=''; s.textContent=ui('older'); m.appendChild(s); m.appendChild(document.createTextNode(fmt(v.date)+' · '+pick(v.label)));
    }
  }
  function open(v){
    viewing=v.id; render(); view.hidden=false;
    if(typeof DecompressionStream==='undefined'){ frame.srcdoc='<p style="font:16px system-ui;padding:24px">'+ui('fail')+'</p>'; return; }
    inflate(v.blob).then(function(html){ frame.srcdoc=withLang(html); });
    if(window.matchMedia('(max-width:760px)').matches) panel.hidden=true;
  }
  function close(){ viewing=null; view.hidden=true; frame.removeAttribute('srcdoc'); render(); }
  btn.addEventListener('click',function(){ panel.hidden=!panel.hidden; render(); });
  panel.querySelector('.vh-x').addEventListener('click',function(){ panel.hidden=true; });
  view.querySelector('.vh-back').addEventListener('click',function(){ close(); panel.hidden=true; });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape'){ if(!view.hidden) close(); else panel.hidden=true; } });
  new MutationObserver(render).observe(root,{attributes:true,attributeFilter:['lang']});
  render();
})();
</script>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Version history for an htmldrop page.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot", help="save the page as a new current version, then build")
    s.add_argument("page")
    s.add_argument("--label", action="append", help='what this version is, per language: "en=..." (repeat)')
    s.add_argument("--note", action="append", help='optional second line, per language: "en=..." (repeat)')
    for name, text in (("build", "embed the history; the current version changes in place"),
                       ("list", "list the versions"), ("restore", "recreate the versions folder from the page")):
        sub.add_parser(name, help=text).add_argument("page")
    a = ap.parse_args()
    p = pathlib.Path(a.page).resolve()
    if not p.is_file():
        sys.exit(f"No such page: {p}")
    if a.cmd == "snapshot":
        snapshot(p, a.label, a.note)
    else:
        {"build": build, "list": show, "restore": restore}[a.cmd](p)
