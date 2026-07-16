# Deck patterns - the single-file skeleton

One `.html` file, all CSS/JS inline, assets inlined (SVG in markup, images as data URIs if small). It must open from `file://` on a machine you've never seen. No CDN fonts, no framework.

## Skeleton

```html
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Product - tagline</title>
<style>
  :root{ --ink:#eef; --dim:#8a93a8; --accent:#7c3aed; /* project tokens */ }
  html,body{margin:0;background:#0b0f1a;color:var(--ink);
    font-family:-apple-system,"Segoe UI",Inter,Roboto,sans-serif}
  .deck{position:fixed;inset:0}
  .slide{position:absolute;inset:0;display:none;place-items:center}
  .slide.on{display:grid}
  .wrap{max-width:960px;padding:0 48px;text-align:center}
  .kicker{font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}
  h1{font-size:clamp(1.9rem,5.4vw,4.6rem);line-height:1.1;margin:.4em 0}
  .lead{font-size:clamp(1.05rem,2.1vw,1.7rem);color:var(--dim);max-width:56ch;margin:1.2em auto 0}
  /* staggered entry: every [data-anim] fades/rises in, --i sets the order */
  @media (prefers-reduced-motion:no-preference){
    .slide.on [data-anim]{opacity:0;transform:translateY(26px);
      animation:in .8s cubic-bezier(.2,.7,.2,1) forwards;
      animation-delay:calc(var(--i,0)*110ms)}
    @keyframes in{to{opacity:1;transform:none}}}
  /* chrome */
  .progress{position:fixed;left:0;bottom:0;height:3px;width:100%}
  .progress b{display:block;height:100%;width:0;background:var(--accent);transition:width .5s}
  .counter{position:fixed;bottom:16px;right:20px;font:.72rem ui-monospace,monospace;color:var(--dim)}
  .navbtns{position:fixed;bottom:12px;left:16px;display:flex;gap:8px}
  /* persistent brand mark - EVERY slide, every frame of any recording */
  .brandmark{position:fixed;top:15px;right:20px;font-weight:800;
    pointer-events:none;user-select:none;white-space:nowrap}
</style></head><body>
<div class="deck" id="deck">
  <div class="brandmark">Product <span style="color:var(--dim);font-size:.78em">by Team</span></div>

  <section class="slide" data-name="Hook"><div class="wrap">
    <div class="kicker" data-anim>Event - Track</div>
    <h1 data-anim style="--i:1">The hook, as a fact.</h1>
    <p class="lead" data-anim style="--i:2">One supporting line.</p>
  </div></section>
  <!-- ...one <section class="slide"> per idea... -->

  <div class="progress"><b id="bar"></b></div>
  <div class="counter" id="counter"></div>
  <div class="navbtns"><button id="prev">&#8249;</button><button id="next">&#8250;</button></div>
</div>
<script>(()=>{
  const slides=[...document.querySelectorAll('.slide')];let idx=0;
  function go(i){idx=Math.max(0,Math.min(slides.length-1,i));
    slides.forEach((s,j)=>s.classList.toggle('on',j===idx));
    bar.style.width=((idx+1)/slides.length*100)+'%';
    counter.textContent=(idx+1)+' / '+slides.length;}
  next.onclick=()=>go(idx+1); prev.onclick=()=>go(idx-1);
  addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(idx+1);
    if(e.key==='ArrowLeft')go(idx-1);});
  const h=parseInt(location.hash.slice(1)); go(isNaN(h)?0:h-1); // #11 -> slide 11
})();</script></body></html>
```

Load-bearing details:

- **`#hash` deep links** (`go(h-1)` on load): the walkthrough recorder fresh-loads at `#N` so that slide's entry animation plays on camera. Do not remove.
- **`#next` as a real button**: the recorder drives the deck with `document.getElementById('next').click()` - focus-proof under a virtual display, where synthetic key events silently no-op.
- **`.brandmark` fixed, `pointer-events:none`**: rides every slide and every recorded frame; never blocks clicks.
- Entry animations keyed to `.slide.on` so they re-fire per slide; respect `prefers-reduced-motion`.

## Copy rules

- **Cited or cut**: every industry number gets a real inline hyperlink (`<a href>` on the stat itself, styled subtle). Before shipping, open each link. A deck with one dead or invented citation loses the credibility of all its numbers.
- **Vector icons, never emojis**: inline SVG paths. Emojis render differently per OS and read as unfinished on a projector.
- **Synthetic-data / disclaimer text**: one small corner legend on the slides that need it, not a per-slide banner.
- Slide text is a headline plus at most one lead line: the speech carries the detail. If a slide needs a paragraph, it is an appendix slide.

## The demo-slot slide

One slide titled to hand off ("Let's watch it work"). For a shipped deck, embed the demo lazily: `<iframe src="https://www.youtube-nocookie.com/embed/<id>" allowfullscreen>` (or a local `<video>` with poster for offline). During a walkthrough recording, Part A ends PAUSED on this slide and the demo film is stitched in - never play the embed on camera.

## Appendix slides

`data-name="Appendix - <question>"` sections after the Close, one per anticipated hard question (safety, "is this really agentic / AI-washing", adoption path, commercials). Skipped in narration and stage flow; jumped to by hash when a judge asks. This is where honest, detailed answers live so the main arc stays clean.
