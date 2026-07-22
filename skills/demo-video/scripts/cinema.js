// cinema.js - in-page motion and annotation layer for demo films.
//
// Injected once per document by record_template.py via
// Page.addScriptToEvaluateOnNewDocument, so it survives navigation. Everything
// here is purely visual: it draws over live product state and never replaces it.
// Real input (mouse, keys) is dispatched driver-side over CDP so the app
// receives genuine events - see the Input helpers in record_template.py.
//
// The problem this exists to solve: a capture can be 100% real browser video and
// still read as a slideshow, because scrollIntoView() teleports and .value =
// inserts text in a single frame. Both endpoints are correct; the motion between
// them is what a viewer reads as "a person did this".
//
// Every function returns a Promise. Beats await them.

(() => {
  if (window.__cine) return;

  const NS = '__cine_layer';
  const EASE = 'cubic-bezier(.22,.61,.36,1)';
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const $ = (sel) => {
    const el = document.querySelector(sel);
    if (!el) throw new Error(`cinema: no element for ${sel}`);
    return el;
  };

  function layer() {
    let el = document.getElementById(NS);
    if (!el) {
      el = document.createElement('div');
      el.id = NS;
      Object.assign(el.style, {
        position: 'fixed', inset: '0', zIndex: '2147483647', pointerEvents: 'none',
      });
      document.documentElement.appendChild(el);
    }
    return el;
  }

  // --- camera ---------------------------------------------------------------

  /**
   * Eased scroll. The single highest-value primitive here: scrollIntoView jumps
   * between two still frames, which a viewer reads as a cut, not a camera move.
   */
  async function glide(selector, { ms = 1400, offset = 90 } = {}) {
    const el = $(selector);
    const from = window.scrollY;
    const to = Math.max(0, from + el.getBoundingClientRect().top - offset);
    const delta = to - from;
    if (Math.abs(delta) < 2) return;
    const t0 = performance.now();
    await new Promise((done) => {
      const step = (now) => {
        const p = Math.min(1, (now - t0) / ms);
        const e = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
        window.scrollTo(0, from + delta * e);
        p < 1 ? requestAnimationFrame(step) : done();
      };
      requestAnimationFrame(step);
    });
    await sleep(150);
  }

  /** Fade the frame to a colour and back. Makes a navigation read as an edit. */
  async function fade(dir = 'out', { ms = 420, color = '#0b1211' } = {}) {
    let v = document.getElementById(`${NS}-veil`);
    if (!v) {
      v = document.createElement('div');
      v.id = `${NS}-veil`;
      Object.assign(v.style, {
        position: 'fixed', inset: '0', background: color,
        zIndex: '2147483646', pointerEvents: 'none', opacity: dir === 'out' ? '0' : '1',
      });
      document.documentElement.appendChild(v);
    }
    v.style.background = color;
    v.style.transition = `opacity ${ms}ms ease`;
    await new Promise((r) => requestAnimationFrame(() => {
      v.style.opacity = dir === 'out' ? '1' : '0';
      r();
    }));
    await sleep(ms + 80);
  }

  // --- cursor ---------------------------------------------------------------
  // The framebuffer recipe records with -draw_mouse 0, so the OS pointer is
  // deliberately absent. This draws one instead: it can be eased, it renders
  // identically on every machine, and it never lands in a frame we did not plan.

  function cursorEl() {
    let c = document.getElementById(`${NS}-cursor`);
    if (!c) {
      c = document.createElement('div');
      c.id = `${NS}-cursor`;
      c.innerHTML = '<svg width="26" height="26" viewBox="0 0 26 26" fill="none">'
        + '<path d="M5 2.5L20.5 12L13.2 13.6L9.6 20.6L5 2.5Z" fill="#0f172a" '
        + 'stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
      Object.assign(c.style, {
        position: 'absolute', top: '0', left: '0', width: '26px', height: '26px',
        transform: 'translate3d(-100px,-100px,0)', opacity: '0',
        filter: 'drop-shadow(0 2px 6px rgba(15,23,42,.45))',
        transition: 'opacity .25s ease',
      });
      layer().appendChild(c);
    }
    return c;
  }

  async function cursorTo(x, y, ms = 650) {
    const c = cursorEl();
    c.style.opacity = '1';
    c.style.transition = `transform ${ms}ms ${EASE}, opacity .25s ease`;
    c.style.transform = `translate3d(${x}px,${y}px,0)`;
    window.__cine._pos = { x, y };
    await sleep(ms);
  }

  async function cursorToEl(selector, ms) {
    const r = $(selector).getBoundingClientRect();
    const x = Math.round(r.left + r.width / 2);
    const y = Math.round(r.top + r.height / 2);
    await cursorTo(x, y, ms);
    return { x, y };
  }

  /** Click ripple. Pair with a real CDP Input click for the actual event. */
  async function ripple(x, y) {
    const el = document.createElement('div');
    Object.assign(el.style, {
      position: 'absolute', left: '0', top: '0', width: '38px', height: '38px',
      marginLeft: '-19px', marginTop: '-19px', borderRadius: '50%',
      border: '2px solid #38bdf8', opacity: '.9',
      transform: `translate3d(${x}px,${y}px,0) scale(.3)`,
    });
    layer().appendChild(el);
    await new Promise((r) => requestAnimationFrame(() => {
      el.style.transition = 'transform .5s ease-out, opacity .5s ease-out';
      el.style.transform = `translate3d(${x}px,${y}px,0) scale(1.5)`;
      el.style.opacity = '0';
      r();
    }));
    await sleep(520);
    el.remove();
  }

  // --- annotation -----------------------------------------------------------

  /**
   * A labelled pointer anchored to an element, with a ring around the referenced
   * region. This is what lets the film explain itself on mute.
   *
   * It draws OVER live product state. It must never be used to stand in for a
   * screen the product cannot actually show - that is the line the recording
   * contract draws, and it is the whole reason overlays are safe here.
   */
  async function callout(selector, text, { side = 'right', hold = 2600 } = {}) {
    const el = $(selector);
    const r = el.getBoundingClientRect();
    const host = layer();

    const ring = document.createElement('div');
    Object.assign(ring.style, {
      position: 'absolute', left: `${r.left - 5}px`, top: `${r.top - 5}px`,
      width: `${r.width + 10}px`, height: `${r.height + 10}px`,
      border: '2px solid #38bdf8', borderRadius: '9px', opacity: '0',
      transition: 'opacity .45s ease',
    });

    const wrap = document.createElement('div');
    Object.assign(wrap.style, {
      position: 'absolute', opacity: '0', transform: 'translateY(6px)',
      transition: 'opacity .45s ease, transform .45s ease',
      display: 'flex', alignItems: 'center', gap: '8px',
    });

    const chip = document.createElement('div');
    chip.textContent = text;                       // textContent: never parse text as HTML
    Object.assign(chip.style, {
      background: '#0f172a', color: '#f1f5f9', borderRadius: '10px',
      font: '600 15px/1.35 ui-sans-serif,system-ui,sans-serif',
      padding: '10px 14px', maxWidth: '330px', border: '1px solid #334155',
      boxShadow: '0 10px 30px rgba(15,23,42,.35)',
    });

    const arrow = document.createElement('div');
    arrow.textContent = side === 'top' ? '▼' : side === 'right' ? '◀' : '▶';
    Object.assign(arrow.style, { color: '#38bdf8', fontSize: '17px', lineHeight: '1' });

    if (side === 'top') {
      wrap.style.flexDirection = 'column';
      wrap.append(chip, arrow);
      wrap.style.left = `${Math.max(14, Math.min(r.left + r.width / 2 - 165, innerWidth - 344))}px`;
      wrap.style.top = `${Math.max(12, r.top - 76)}px`;
    } else {
      // Flip to whichever side has room, so a label never clips off-frame.
      const fitsLeft = r.left > 360;
      const place = side === 'left' && fitsLeft ? 'left'
        : (fitsLeft && r.right + 360 > innerWidth) ? 'left' : 'right';
      if (place === 'right') {
        wrap.append(arrow, chip);
        wrap.style.left = `${Math.min(r.right + 14, innerWidth - 356)}px`;
      } else {
        wrap.append(chip, arrow);
        wrap.style.left = `${Math.max(14, r.left - 352)}px`;
      }
      wrap.style.top = `${Math.max(12, r.top + r.height / 2 - 24)}px`;
    }

    host.append(ring, wrap);
    await new Promise((res) => requestAnimationFrame(() => {
      ring.style.opacity = '1';
      wrap.style.opacity = '1';
      wrap.style.transform = 'translateY(0)';
      res();
    }));
    await sleep(hold);
    ring.style.opacity = '0';
    wrap.style.opacity = '0';
    await sleep(520);
    ring.remove();
    wrap.remove();
  }

  /**
   * Lift a clone of an element into a centred card and dim the rest. A diagram
   * or table sized for a document column is unreadable at video scale.
   *
   * A clone, not the element itself: transforming the original grows it over its
   * siblings and reads as a broken layout.
   */
  // Magnify a single element by CLONING it into a centred card. Correct for a
  // self-contained node (one chart, one number, one card). WRONG for a
  // responsive multi-column target: a `grid-cols-1 sm:grid-cols-3` row reflows
  // to a single stacked column inside the clone. For those, use `frameRegion`,
  // which scales the real node in place and keeps its true columns.
  async function spotlight(selector, { scale = 1.5, hold = 3000, rise = 900 } = {}) {
    const el = $(selector);
    const r = el.getBoundingClientRect();

    const dim = document.createElement('div');
    Object.assign(dim.style, {
      position: 'fixed', inset: '0', background: 'rgba(12,20,18,.68)', opacity: '0',
      zIndex: '2147483644', pointerEvents: 'none', transition: `opacity ${rise}ms ease`,
    });

    const card = document.createElement('div');
    Object.assign(card.style, {
      position: 'fixed', zIndex: '2147483645', pointerEvents: 'none',
      left: `${r.left}px`, top: `${r.top}px`, width: `${r.width}px`,
      background: '#fff', border: '1px solid rgba(0,0,0,.10)', borderRadius: '16px',
      padding: '22px', boxShadow: '0 30px 80px rgba(12,20,18,.45)',
      transformOrigin: 'center center', opacity: '0',
      transition: `transform ${rise}ms ${EASE}, opacity ${rise * 0.6}ms ease`,
      display: 'flex', justifyContent: 'center', alignItems: 'center',
    });

    const clone = el.cloneNode(true);
    // A cloned node is a flex item with no width, so an SVG at width:100%
    // collapses toward its viewBox minimum. Pin both explicitly.
    Object.assign(clone.style, { width: '100%', minHeight: '0', display: 'block' });
    clone.querySelectorAll('svg').forEach((s) => {
      Object.assign(s.style, { width: '100%', height: 'auto', maxWidth: 'none', display: 'block' });
      s.removeAttribute('height');
    });
    card.appendChild(clone);
    document.documentElement.append(dim, card);

    const cr = card.getBoundingClientRect();
    const dx = innerWidth / 2 - (cr.left + cr.width / 2);
    const dy = innerHeight / 2 - (cr.top + cr.height / 2);
    const fit = Math.max(1, Math.min(scale,
      (innerWidth - 80) / cr.width, (innerHeight - 80) / cr.height));

    await new Promise((res) => requestAnimationFrame(() => {
      dim.style.opacity = '1';
      card.style.opacity = '1';
      card.style.transform = `translate(${dx}px,${dy}px) scale(${fit})`;
      res();
    }));
    await sleep(rise + hold);
    dim.style.opacity = '0';
    card.style.opacity = '0';
    card.style.transform = 'translate(0,0) scale(1)';
    await sleep(rise + 100);
    dim.remove();
    card.remove();
  }

  /**
   * Frame-and-zoom onto a live region WITHOUT cloning it, so responsive
   * multi-column layouts keep their real columns (the case `spotlight` gets
   * wrong). Scales the page so the target fills `fill` of the viewport width,
   * centred, and dims the rest. Nothing is duplicated; every pixel is the real,
   * still-live element.
   *
   * Use for a row of stat cards, a table, any target whose layout depends on
   * its width. `fill` defaults to 0.9 (leave a margin); it never scales past a
   * size that would clip the region.
   */
  async function frameRegion(selector, { fill = 0.9, hold = 3000, rise = 900 } = {}) {
    const el = $(selector);
    el.scrollIntoView({ block: 'center', behavior: 'instant' });
    await sleep(60);
    const r = el.getBoundingClientRect();
    const S = Math.min(
      (fill * innerWidth) / r.width,
      (0.8 * innerHeight) / r.height,
    );
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;
    const tx = innerWidth / 2 - S * cx;
    const ty = innerHeight / 2 - S * cy;

    const dim = document.createElement('div');
    Object.assign(dim.style, {
      position: 'fixed', inset: '0', background: 'rgba(12,20,18,.55)', opacity: '0',
      zIndex: '2147483643', pointerEvents: 'none', transition: `opacity ${rise}ms ease`,
    });
    document.documentElement.append(dim);

    // Lift the real element above the dim layer, then transform the page.
    const prev = {
      pos: document.body.style.transformOrigin,
      tr: document.body.style.transform,
      trans: document.body.style.transition,
      z: el.style.zIndex, posn: el.style.position,
    };
    document.body.style.transformOrigin = '0 0';
    document.body.style.transition = `transform ${rise}ms ${EASE}`;
    // raise the target so the dim overlay sits behind it
    if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
    el.style.zIndex = '2147483644';

    await new Promise((res) => requestAnimationFrame(() => {
      dim.style.opacity = '1';
      document.body.style.transform = `translate(${tx.toFixed(1)}px, ${ty.toFixed(1)}px) scale(${S.toFixed(3)})`;
      res();
    }));
    await sleep(rise + hold);

    dim.style.opacity = '0';
    document.body.style.transform = prev.tr || 'none';
    await sleep(rise + 100);
    document.body.style.transformOrigin = prev.pos;
    document.body.style.transition = prev.trans;
    el.style.zIndex = prev.z;
    el.style.position = prev.posn;
    dim.remove();
  }

  /**
   * A floating terminal panel over the live page, for products whose command
   * surface is part of the story. Keeps the film one continuous take instead of
   * cutting away to a separate screen recording.
   *
   * `lines` must be output the command actually produced. Typing plausible
   * output the tool never printed is fabricating evidence, not annotating it.
   */
  async function terminal(command, lines, {
    hold = 2400, typeDelay = 42, lineDelay = 220, title = 'zsh',
  } = {}) {
    const host = layer();
    const term = document.createElement('div');
    Object.assign(term.style, {
      position: 'absolute', left: '50%', bottom: '46px',
      transform: 'translate(-50%,26px)', width: 'min(980px,76vw)',
      background: '#0c1a17', color: '#dff2e8', border: '1px solid #2c4a42',
      borderRadius: '14px', opacity: '0', overflow: 'hidden',
      boxShadow: '0 26px 70px rgba(4,12,10,.55)',
      transition: `opacity .42s ease, transform .42s ${EASE}`,
      font: '14.5px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace',
    });

    const bar = document.createElement('div');
    Object.assign(bar.style, {
      display: 'flex', alignItems: 'center', gap: '8px', padding: '11px 14px',
      background: '#123028', color: '#9dc4b5', fontSize: '12px',
    });
    ['#e99472', '#e8c471', '#82c29a'].forEach((c) => {
      const d = document.createElement('i');
      Object.assign(d.style, { width: '9px', height: '9px', borderRadius: '50%', background: c });
      bar.appendChild(d);
    });
    const label = document.createElement('span');
    label.textContent = title;
    label.style.marginLeft = '6px';
    bar.appendChild(label);

    const body = document.createElement('pre');
    Object.assign(body.style, {
      margin: '0', padding: '18px 20px 22px', maxHeight: '330px', overflow: 'hidden',
      whiteSpace: 'pre-wrap', font: 'inherit', lineHeight: '1.6',
    });
    term.append(bar, body);
    host.appendChild(term);
    await new Promise((res) => requestAnimationFrame(() => {
      term.style.opacity = '1';
      term.style.transform = 'translate(-50%,0)';
      res();
    }));
    await sleep(500);

    const prompt = document.createElement('div');
    const dollar = document.createElement('span');
    dollar.textContent = '$ ';
    dollar.style.color = '#82c29a';
    const cmd = document.createElement('span');
    const caret = document.createElement('span');
    caret.textContent = '█';
    prompt.append(dollar, cmd, caret);
    body.appendChild(prompt);

    for (const ch of command) {
      cmd.textContent += ch;
      await sleep(typeDelay);
    }
    await sleep(520);
    caret.remove();

    for (const line of lines) {
      const el = document.createElement('div');
      el.textContent = line;
      el.style.opacity = '0';
      el.style.transition = 'opacity .2s ease';
      if (/^(Published|Done|Wrote|Created|Converged)/.test(line)) el.style.color = '#7fd3a6';
      else if (/^\s{2,}\S/.test(line)) el.style.color = '#9dc4b5';
      body.appendChild(el);
      await new Promise((r) => requestAnimationFrame(() => { el.style.opacity = '1'; r(); }));
      await sleep(lineDelay);
    }

    await sleep(hold);
    term.style.opacity = '0';
    term.style.transform = 'translate(-50%,26px)';
    await sleep(460);
    term.remove();
  }

  // --- selection ------------------------------------------------------------

  /**
   * Select a run of text and fire the mouseup the app listens for. Products with
   * selection-triggered UI (annotation widgets, inline toolbars) need the event,
   * not just the Range.
   */
  async function selectText(selector, { ms = 700 } = {}) {
    const el = $(selector);
    const r = el.getBoundingClientRect();
    const y = Math.round(r.top + r.height / 2);
    await cursorTo(Math.round(r.left + 4), y, 420);

    const range = document.createRange();
    range.selectNodeContents(el);
    const sel = getSelection();
    sel.removeAllRanges();

    // Sweep the cursor across the text while the selection grows, so the frame
    // shows the drag rather than the text simply becoming blue.
    const steps = 18;
    for (let i = 1; i <= steps; i += 1) {
      const sub = document.createRange();
      sub.selectNodeContents(el);
      try { sub.setEnd(range.endContainer, Math.round(range.endOffset * i / steps)); } catch (_) { /* text node math */ }
      sel.removeAllRanges();
      sel.addRange(i === steps ? range : sub);
      await cursorTo(Math.round(r.left + 4 + (r.width - 8) * i / steps), y, ms / steps);
    }
    el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, clientX: r.right - 4, clientY: y }));
    await sleep(420);
  }

  window.__cine = {
    glide, fade, cursorTo, cursorToEl, ripple, callout, spotlight, frameRegion, terminal, selectText,
    _pos: { x: -100, y: -100 },
    ready: true,
  };
})();
