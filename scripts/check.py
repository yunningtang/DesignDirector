#!/usr/bin/env python3
"""Mechanical self-check v6 (V4.14: + small object repeated over pictures in a strong colour; v5 V4.13: + broken images, first-screen task, sample-data label, button family, generic headings and filler, 320px overflow, focus ring; v4 V4.12: v2 + legibility, top-bar and drag checks from V4.6-V4.9, rebuilt; + cut-off strips)
Originally: mechanical self-check v2 for one page (rule:mechanical-check). Craft only, not taste.
rule:eval-separation (until V4.16): nothing the default-looks radar scored was checked here. V4.16.1 adds the default
looks that can be measured (edge bars, caps labels, dotted meta, identical card rows), because unchecked bans were
narrowed away in real use; pass --no-style to keep a benchmark radar clean.
v2 (2026-11-04): adds overlapping words, checked after scrolling the whole page; the only extra rule
that held up against judge scores when 23 rules adapted from the impeccable detector were tried on 470 pages.

  python3 check.py index.html [--primary CSS] [--core CSS] [--route CDN_SUBSTRING=LOCAL_PATH ...]
  python3 check.py --url http://localhost:5173/orders [...]    # V4.16.1: a page that needs its server (an app)
  --real-data: the figures come from the brief or a real source, so no "sample data" label is required.
  --no-style:  skip the default-looks checks (only for benchmark scoring, where the radar judges them).
  --allow-net: let the page reach other hosts too (by default only the page's own origin, localhost and fonts load).
  --primary: the control that starts the primary task (a button, the search field, the first form field).
  --core: the working area of the primary task (the board, the form, the chart, the game canvas).

Checks at 1440x900 and 375x812: JS errors, sideways overflow on phone (and which elements cause it),
small text below 4.5:1, text under 12px, gradient-filled text, hard zero-blur shadows, stray
fixed/sticky boxes with nothing in them (hidden toasts that still show), phone tap targets under 32px,
words drawn on top of each other (for example an inherited negative text-indent on per-word spans).
Prints one line per finding; nothing listed means nothing found. Fix what it lists in your fix pass.
"""
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__))); import fontroute
import argparse, asyncio, os, sys
from playwright.async_api import async_playwright

JS = r"""
([mobile, vw, primarySel, coreSel, realData]) => {
  const out = [];
  const vis = el => { const s = getComputedStyle(el); const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const name = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.classList.length ? '.' + [...el.classList].slice(0, 2).join('.') : '');
  const rgba = c => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  const lum = ([r, g, b]) => { const f = c => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4 }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const s = getComputedStyle(e);
      if (s.backgroundImage !== 'none') return null; const c = rgba(s.backgroundColor); if (c && c[3] > 0.9) return c; }
    return [255, 255, 255, 1]; };
  // overflow
  if (mobile) {
    const sw = document.documentElement.scrollWidth;
    if (sw > vw) {
      const wide = [...document.querySelectorAll('body *')].filter(e => vis(e) && e.getBoundingClientRect().right > vw + 2)
        .filter(e => !e.parentElement || e.parentElement.getBoundingClientRect().right <= vw + 2).slice(0, 4).map(name);
      out.push(`overflow: page is ${sw}px wide at ${vw}px; widest culprits: ${wide.join(', ')}`);
    }
  }
  // text checks
  let low = [], tiny = 0, grad = [];
  const texts = [...document.querySelectorAll('body *')].filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1) && vis(e)).slice(0, 600);
  for (const e of texts) {
    const s = getComputedStyle(e), fs = parseFloat(s.fontSize), bold = +s.fontWeight >= 700;
    if (fs < 12) tiny++;
    if ((s.backgroundClip || s.webkitBackgroundClip) === 'text' || s.webkitTextFillColor === 'transparent') grad.push(name(e));
    const fg = rgba(s.color), bg = bgOf(e);
    if (!fg || !bg || fg[3] < 0.5 || e.closest(':disabled,[aria-disabled=true]')) continue;
    const large = fs >= 24 || (bold && fs >= 18.66);
    const L1 = lum(fg), L2 = lum(bg), cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    if (cr < (large ? 3 : 4.5)) low.push(`${name(e)} ${cr.toFixed(2)}:1 "${e.textContent.trim().slice(0, 30)}"`);
  }
  if (low.length) out.push(`low contrast (${low.length}): ${low.slice(0, 5).join(' | ')}`);
  if (tiny > 3) out.push(`text under 12px: ${tiny} elements`);
  if (grad.length) out.push(`gradient-filled text: ${grad.slice(0, 3).join(', ')}`);
  // hard shadows
  const hard = [...document.querySelectorAll('body *')].filter(e => { const b = getComputedStyle(e).boxShadow; if (!b || b === 'none') return false;
    return b.split(/,(?![^(]*\))/).some(x => { const n = (x.replace(/rgba?\([^)]*\)/, '').match(/-?\d+(\.\d+)?px/g) || []).map(parseFloat);
      return n.length >= 3 && (n[0] || n[1]) && n[2] === 0 && !/inset/.test(x); }); }).filter(vis);
  if (hard.length) out.push(`zero-blur offset shadows: ${hard.length} (e.g. ${hard.slice(0, 2).map(name).join(', ')})`);
  // stray fixed boxes
  const stray = [...document.querySelectorAll('body *')].filter(e => { const s = getComputedStyle(e); return (s.position === 'fixed' || s.position === 'sticky') && vis(e)
    && !e.textContent.trim() && !e.querySelector('svg,img,canvas,video,input,button') && !['svg','img','canvas','video'].includes(e.tagName.toLowerCase()); });
  if (stray.length) out.push(`empty fixed/sticky boxes visible (hidden toast or drawer still showing?): ${stray.slice(0, 3).map(name).join(', ')}`);
  // tap targets
  if (mobile) {
    const small = [...document.querySelectorAll('button, a[href], input, select, [role=button]')].filter(e => { if (!vis(e)) return false; const r = e.getBoundingClientRect();
      return r.top < window.innerHeight * 3 && (r.height < 32 || r.width < 32) && e.closest('p,li') === null; });
    if (small.length > 2) out.push(`tap targets under 32px on phone: ${small.length} (e.g. ${small.slice(0, 3).map(name).join(', ')})`);
  }
  // overlapping words (after scroll, so lazily built text is included)
  const own = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const cand = new Set(); [...document.querySelectorAll('body *')].filter(own).forEach(e => { if (e.parentElement) { cand.add(e.parentElement); if (e.parentElement.parentElement) cand.add(e.parentElement.parentElement); } });
  let lap = 0, lapEx = [];
  for (const p of cand) { const kids = [...p.children].filter(c => { const st = getComputedStyle(c), r = c.getBoundingClientRect(); return (c.textContent || '').trim() && /^inline/.test(st.display) && /static|relative/.test(st.position) && !(c instanceof SVGElement) && st.visibility !== 'hidden' && r.width > 0; }).slice(0, 80);
    if (kids.length < 2) continue;
    const rs = kids.map(c => { const g = document.createRange(); g.selectNodeContents(c); const l = [...g.getClientRects()].filter(r => r.width > 1); return l.length ? l : [c.getBoundingClientRect()]; }); let hit = 0;
    const ov = (a, b) => { const w = Math.min(a.right, b.right) - Math.max(a.left, b.left), h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top); return w > 0 && h > 0 && w * h > 0.3 * Math.min(a.width * a.height, b.width * b.height); };
    for (let i = 0; i < rs.length; i++) for (let j = i + 1; j < Math.min(rs.length, i + 6); j++) { if (rs[i].some(a => rs[j].some(b => ov(a, b)))) hit++; }
    if (hit >= 2) { lap += hit; if (lapEx.length < 2) lapEx.push(p.textContent.trim().replace(/\s+/g, ' ').slice(0, 40)); } }
  if (lap >= 4) out.push(`overlapping words (${lap} pairs drawn on top of each other), e.g. "${lapEx.join('" | "')}"`);
  // v3 legibility (V4.6, reconstructed): first-screen text covered, cut off without an ellipsis, or crushed
  let cov = [], cut = [], crush = [];
  for (const e of texts) { const r = e.getBoundingClientRect(); if (r.top > window.innerHeight || r.bottom < 0 || r.left > vw || r.right < 0) continue;
    const s = getComputedStyle(e), fs = parseFloat(s.fontSize), t = e.textContent.trim();
    const cx = Math.min(vw - 1, Math.max(0, r.left + Math.min(r.width / 2, 20))), cy = Math.min(window.innerHeight - 1, Math.max(0, r.top + r.height / 2));
    const top = document.elementFromPoint(cx, cy);
    if (top && top !== e && !e.contains(top) && !top.contains(e) && !(top.closest && top.closest('label') && top.closest('label').contains(e))) {
      const ts = getComputedStyle(top); if (+ts.opacity > 0.3 && (ts.backgroundColor !== 'rgba(0, 0, 0, 0)' || top.textContent.trim())) cov.push(`${name(e)} under ${name(top)}`); }
    if ((s.overflow.includes('hidden') || s.overflowX === 'hidden' || s.overflowX === 'clip') && e.scrollWidth > e.clientWidth + 2 && s.textOverflow !== 'ellipsis' && s.whiteSpace === 'nowrap') cut.push(`${name(e)} "${t.slice(0, 20)}"`);
    // V4.16.1: squeezed means a word does not fit its box (or the box is shorter than a line), not "a short label"
    if (t.length > 3 && !/^inline$/.test(s.display)) {
      const ctx2 = (window.__cv = window.__cv || document.createElement('canvas')).getContext('2d'); ctx2.font = `${s.fontStyle} ${s.fontWeight} ${s.fontSize} ${s.fontFamily}`;
      const ls = parseFloat(s.letterSpacing) || 0;
      const widest = Math.max(...t.split(/\s+/).filter(Boolean).map(w => ctx2.measureText(w).width + ls * w.length));
      const pad = parseFloat(s.paddingLeft) + parseFloat(s.paddingRight);
      if ((widest > r.width - pad + 2 && e.scrollWidth > e.clientWidth + 1 && s.textOverflow !== 'ellipsis' && s.overflowWrap !== 'anywhere' && s.wordBreak !== 'break-all') || r.height < fs * 0.85) crush.push(`${name(e)} ${Math.round(r.width)}x${Math.round(r.height)}px "${t.slice(0, 16)}"`);
    }
  }
  if (cov.length) out.push(`text covered by another element on the first screen (${cov.length}): ${cov.slice(0, 4).join(' | ')}`);
  if (cut.length) out.push(`text cut off without an ellipsis (${cut.length}): ${cut.slice(0, 4).join(' | ')}`);
  if (crush.length > 1) out.push(`text squeezed into boxes too small to read (${crush.length}): ${crush.slice(0, 4).join(' | ')}`);
  // V4.7: count badges showing 0 in the top bar
  const bar = document.querySelector('header, nav, [role=banner]');
  if (bar) { const zeros = [...bar.querySelectorAll('*')].filter(e => vis(e) && !e.children.length && e.textContent.trim() === '0'); if (zeros.length) out.push(`count badge showing 0 in the top bar: ${zeros.slice(0, 2).map(name).join(', ')}`);
    // V4.9: wordmark split into two weights or colours
    const mark = bar.querySelector('a, .logo, [class*=brand], [class*=logo]');
    if (mark) { const parts = [...mark.querySelectorAll('*')].filter(c => vis(c) && [...c.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) && !c.closest('svg'));
      const ms = getComputedStyle(mark); const diff = parts.filter(c => { const cs = getComputedStyle(c); return cs.fontWeight !== ms.fontWeight || cs.color !== ms.color || cs.fontStyle !== ms.fontStyle; });
      if (parts.length && diff.length && mark.textContent.trim().length < 40) out.push(`wordmark split into two weights, colours or styles: "${mark.textContent.trim().slice(0, 30)}"`); } }
  // V4.8: draggable surfaces that still let the pointer select text
  const drag = [...document.querySelectorAll('body *')].filter(e => vis(e) && /grab|move|crosshair/.test(getComputedStyle(e).cursor) && getComputedStyle(e).userSelect !== 'none' && (e.textContent || '').trim()).slice(0, 3);
  if (drag.length) out.push(`draggable surfaces without user-select:none: ${drag.map(name).join(', ')}`);
  // V4.12 (rule:strip-fit): a row of steps, tabs or chips cut off at the phone edge
  if (mobile) {
    const strips = [...document.querySelectorAll('body *')].filter(e => { if (!vis(e) || e.children.length < 3) return false; const s = getComputedStyle(e);
      const row = s.display.includes('flex') && !s.flexDirection.startsWith('column') && s.flexWrap === 'nowrap' || s.display.includes('grid') && s.gridAutoFlow.includes('column');
      if (!row) return false; const r = e.getBoundingClientRect(); const kids = [...e.children].filter(vis);
      const outside = kids.filter(k => { const kr = k.getBoundingClientRect(); return kr.right > Math.min(vw, r.right) + 2 || kr.left < Math.max(0, r.left) - 2; });
      const scrolls = /auto|scroll/.test(s.overflowX);
      const steps = e.tagName === 'OL' || /step|progress|stage|wizard|stepper/i.test((e.className && e.className.baseVal === undefined ? e.className : '') + ' ' + e.id + ' ' + (e.getAttribute('aria-label') || ''));
      return outside.length && (steps || !scrolls); });
    const top = strips.filter(e => !strips.some(o => o !== e && o.contains(e))).slice(0, 3);
    if (top.length) out.push(`row cut off at the phone edge (a step or progress row must fit or stack: show 'Step 2 of 6' plus the current step; a tab or chip row must wrap or scroll): ${top.map(name).join(', ')}`);
  }

  // V4.13 (rule:photo-decode): images that failed to load or decode
  const broken = [...document.images].filter(i => i.getAttribute('src') && i.complete && i.naturalWidth === 0);
  if (broken.length) out.push(`broken images (${broken.length} of ${document.images.length}): ${broken.slice(0, 3).map(i => (i.getAttribute('src') || '').slice(0, 50)).join(' | ')}`);
  // V4.13 (rule:first-screen-task, from Impeccable's first-viewport): primary control and working area on the first screen
  const H = window.innerHeight;
  const firstVis = el => { const r = el.getBoundingClientRect(); return vis(el) && r.top >= -2 && r.top < H - 20 && r.left < vw && r.right > 0; };
  if (primarySel) { const pe = document.querySelector(primarySel);
    if (!pe) out.push(`--primary "${primarySel}" matches nothing`);
    else if (!firstVis(pe)) out.push(`primary control ${name(pe)} is not on the first screen (top at ${Math.round(pe.getBoundingClientRect().top)}px of ${H}px)`); }
  else { const ctl = [...document.querySelectorAll('button, input:not([type=hidden]), select, textarea, a[href][class*=btn], a[href][class*=button], [role=button]')].filter(firstVis);
    if (!ctl.length) out.push('first screen has no control at all (no button, field or button-styled link); pass --primary to check the real one'); }
  if (coreSel) { const ce = document.querySelector(coreSel);
    if (!ce) out.push(`--core "${coreSel}" matches nothing`);
    else { const r = ce.getBoundingClientRect(); const vis_h = Math.max(0, Math.min(r.bottom, H) - Math.max(r.top, 0)); const need = Math.min(r.height, H) * 0.5;
      if (vis_h < need) out.push(`working area ${name(ce)}: only ${Math.round(vis_h)}px of it shows on the first screen (need about half of it, or half the screen)`); } }
  // V4.13 (rule:sample-label, from Impeccable): many invented figures and no word saying they are sample
  const figs = texts.filter(e => /^[\s$£€¥+−-]*\d[\d,.\s]*(%|k|m|bn|ms|s|h|pts?)?$/i.test(e.textContent.trim())).length;
  const bodyText = document.body.innerText;
  if (!realData && figs >= 10 && !/sample|example|demo|illustrative|fictional|made[- ]up|placeholder|simulated|test data|示例|模拟/i.test(bodyText)) out.push(`${figs} stand-alone figures and no "sample data" label anywhere: mark invented numbers as sample (rule:sample-label; if the figures are real, run with --real-data)`);
  // V4.13 (rule:button-family, from Taste): too many button looks
  const btns = [...document.querySelectorAll('button, [role=button], a[class*=btn], a[class*=button], input[type=submit]')].filter(e => { if (!vis(e)) return false;
    const r = e.getBoundingClientRect(); return r.height >= 30 && r.width >= 60 && !e.matches('[role=tab],[aria-pressed],[aria-selected],[role=option],[role=switch]'); });
  const looks = new Set(btns.map(e => { const s = getComputedStyle(e); const bg = rgba(s.backgroundColor) || [0,0,0,0]; const bc = rgba(s.borderTopColor) || [0,0,0,0];
    const filled = bg[3] > 0.5 ? s.backgroundColor : 'none'; const edged = parseFloat(s.borderTopWidth) > 0 && bc[3] > 0.3 ? 'edge' : 'noedge';
    return [filled, edged, Math.round(parseFloat(s.borderTopLeftRadius) / 4)].join('|'); }));
  if (looks.size > 4) out.push(`${looks.size} different button looks (keep one primary, one secondary, one quiet style; rule:button-family)`);
  // V4.13 (rule:copy-first, from Taste's copy-lint): headings that name nothing, filler words
  const generic = /^(features|how it works|why (choose )?us|our story|about( us)?|get started|testimonials|benefits|overview|solutions|what we do|our mission|services|learn more|discover more|welcome)\.?$/i;
  const gh = [...document.querySelectorAll('h1,h2,h3')].filter(h => vis(h) && generic.test(h.textContent.trim()));
  if (gh.length) out.push(`headings that name nothing (say what is in the section): ${gh.slice(0, 4).map(h => '"' + h.textContent.trim() + '"').join(', ')}`);
  const filler = (bodyText.match(/\b(revolutioni[sz]e|unlock|seamless(ly)?|supercharge|elevate|effortless(ly)?|cutting-edge|game[- ]chang(er|ing)|empower|next-level|reimagine[ds]?|unleash)\b/gi) || []);
  if (filler.length) out.push(`filler words: ${[...new Set(filler.map(w => w.toLowerCase()))].slice(0, 6).join(', ')}`);

  // V4.14 (rule:object-host, rule:object-quiet): an object repeated on 4+ cards, laid over a picture, in a saturated colour
  {
    const sat = c => { const v = rgba(c); if (!v || v[3] < 0.4) return 0; const [r, g, b] = v.slice(0, 3).map(x => x / 255); const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2;
      if (mx === mn || l < 0.15 || l > 0.9) return 0; return (mx - mn) / (1 - Math.abs(2 * l - 1)); };
    const pics = [...document.querySelectorAll('img, svg, canvas, picture, [style*="background-image"]')].filter(e => { if (!vis(e)) return false; const r = e.getBoundingClientRect(); return r.width > 120 && r.height > 90; });
    const over = el => { const r = el.getBoundingClientRect(); return pics.some(p => { if (p.contains(el) && p.tagName.toLowerCase() === 'svg') return true; if (el.contains(p)) return false; const q = p.getBoundingClientRect();
      const w = Math.min(r.right, q.right) - Math.max(r.left, q.left), h = Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top); return w > r.width * 0.6 && h > r.height * 0.6; }); };
    const groups = {};
    for (const e of document.querySelectorAll('body *')) {
      if (!vis(e) || e.matches('button, a, input, select, label, [role=button]')) continue;
      const st = getComputedStyle(e); if (!/absolute|fixed/.test(st.position) && !(e instanceof SVGElement && e.parentElement && getComputedStyle(e.parentElement).position === 'absolute')) continue;
      const r = e.getBoundingClientRect(); if (r.width < 24 || r.height < 18 || r.width > 260) continue;
      const s1 = Math.max(sat(st.color), sat(st.borderTopColor), sat(st.backgroundColor), sat(st.stroke || ''), sat(st.fill || ''));
      if (s1 < 0.35 || !over(e)) continue;
      const key = e.tagName + '.' + (typeof e.className === 'string' ? e.className : (e.className && e.className.baseVal) || '');
      (groups[key] = groups[key] || []).push(e);
    }
    const hits = Object.entries(groups).filter(([, v]) => v.length >= 4);
    if (hits.length) out.push(`small object repeated over pictures in a strong colour (${hits.map(([k, v]) => k.slice(0, 40) + ' x' + v.length).slice(0, 2).join(', ')}): move it onto a label, tag or edge, make it ink or neutral, keep the accent for the main button (rule:object-host, rule:object-quiet)`);
  }
  return out;
}
"""

FOCUS = r"""
() => { const e = document.activeElement; if (!e || e === document.body) return null;
  const s = getComputedStyle(e); const ring = (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) || (s.boxShadow && s.boxShadow !== 'none');
  const tmp = e.style.cssText; e.blur(); const t = getComputedStyle(e); const base = (t.outlineStyle !== 'none' && parseFloat(t.outlineWidth) > 0) || (t.boxShadow && t.boxShadow !== 'none');
  const bgChange = s.backgroundColor !== t.backgroundColor || s.borderColor !== t.borderColor; e.focus({preventScroll: true});
  return (ring && !base) || (ring && s.outlineColor !== t.outlineColor) || bgChange; }
"""

# V4.16.1 rule:pattern-not-element: the default looks that can be measured (defaults.md 8), on ANY element
STYLE_JS = r"""
([mobile, vw]) => {
  const out = [];
  const vis = e => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 0 && r.height > 0; };
  const name = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const rgba = c => { const m = (c || '').match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  const sat = c => { const v = rgba(c); if (!v || v[3] < 0.4) return 0; const [r, g, b] = v.slice(0, 3).map(x => x / 255); const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2;
    if (mx === mn || l < 0.12 || l > 0.92) return 0; return (mx - mn) / (1 - Math.abs(2 * l - 1)); };
  const all = [...document.querySelectorAll('body *')].filter(vis).slice(0, 4000);
  // 1. accent edge bar on one side of any block (selected nav items included)
  const bars = [];
  for (const e of all) {
    const r = e.getBoundingClientRect(); if (r.width < 40 || r.height < 16) continue;
    const s = getComputedStyle(e); const side = k => [parseFloat(s['border' + k + 'Width']) || 0, s['border' + k + 'Color'], s['border' + k + 'Style']];
    const [L, Rr, T, B] = ['Left', 'Right', 'Top', 'Bottom'].map(side);
    const one = (a, others) => a[0] >= 2 && a[2] !== 'none' && sat(a[1]) >= 0.3 && others.every(o => o[0] < 1 || o[2] === 'none' || (rgba(o[1]) || [0,0,0,0])[3] < 0.2 || o[1] !== a[1]);
    let hit = one(L, [Rr, T, B]) || one(Rr, [L, T, B]) || (one(T, [L, Rr, B]) && r.height > 60);
    if (!hit && s.boxShadow && s.boxShadow !== 'none') hit = s.boxShadow.split(/,(?![^(]*\))/).some(x => { if (!/inset/.test(x)) return false;
      const col = (x.match(/rgba?\([^)]*\)/) || [''])[0]; const n = (x.replace(/rgba?\([^)]*\)/, '').match(/-?\d+(\.\d+)?px/g) || []).map(parseFloat);
      return n.length >= 2 && ((Math.abs(n[0]) >= 2 && n[1] === 0) || (n[0] === 0 && Math.abs(n[1]) >= 2 && r.height > 60)) && (n[2] || 0) === 0 && sat(col) >= 0.3; });
    if (!hit) for (const pe of ['::before', '::after']) { const q = getComputedStyle(e, pe); if (!q.content || q.content === 'none' || q.position !== 'absolute') continue;
      const w = parseFloat(q.width), h = parseFloat(q.height); const bg = sat(q.backgroundColor) >= 0.3 || sat(q.borderLeftColor) >= 0.3 && parseFloat(q.borderLeftWidth) >= 2;
      if (bg && ((w > 0 && w <= 6 && h >= 0.6 * r.height) || (h > 0 && h <= 6 && w >= 0.6 * r.width && r.height > 60))) hit = true; }
    if (hit) bars.push(e);
  }
  const topBars = bars.filter(e => !bars.some(o => o !== e && o.contains(e)));
  if (topBars.length) out.push(`accent bar on one edge of a block (${topBars.length}; defaults.md 8, any element incl. the selected nav item): ${topBars.slice(0, 4).map(name).join(', ')}; mark selection with ground, weight or ink instead`);
  // 2. small tracked caps label right above a heading
  const caps = all.filter(e => { if (/^H[1-6]$/.test(e.tagName)) return false; const t = (e.textContent || '').trim(); if (t.length < 2 || t.length > 40 || e.children.length > 1) return false;
    const s = getComputedStyle(e), fs = parseFloat(s.fontSize), ls = parseFloat(s.letterSpacing) || 0;
    const upper = s.textTransform === 'uppercase' || (t === t.toUpperCase() && /[A-Z]{3}/.test(t)); if (!upper || fs > 14 || ls < fs * 0.04) return false;
    let n = e.nextElementSibling; while (n && !vis(n)) n = n.nextElementSibling; return !!n && (/^H[1-3]$/.test(n.tagName) || !!(n.firstElementChild && /^H[1-3]$/.test(n.firstElementChild.tagName))); });
  if (caps.length >= 2) out.push(`small tracked capitals label above a heading (${caps.length}; defaults.md 8): ${caps.slice(0, 3).map(e => '"' + e.textContent.trim().slice(0, 20) + '"').join(', ')}`);
  // 3. meta strings joined with middle dots
  const dots = all.filter(e => [...e.childNodes].some(n => n.nodeType === 3 && /\S\s*[·•∙]\s*\S/.test(n.textContent)) || ([...e.children].length >= 2 && [...e.children].some(c => /^\s*[·•∙]\s*$/.test(c.textContent)) && e.children.length < 8));
  const topDots = dots.filter(e => !dots.some(o => o !== e && o.contains(e)));
  if (topDots.length >= 3) out.push(`facts joined with middle dots (${topDots.length} lines; defaults.md 8): e.g. "${topDots[0].textContent.trim().replace(/\s+/g, ' ').slice(0, 40)}"; use commas, line breaks or separate cells`);
  // 4. a row of three or more identical icon + heading + text boxes
  const rows = [];
  for (const p of all) { if (p.closest('nav,header,footer,[role=navigation]')) continue;
    const kids = [...p.children].filter(vis); if (kids.length < 3 || kids.length > 6) continue;
    const rs = kids.map(k => k.getBoundingClientRect()); const w0 = rs[0].width, h0 = rs[0].height;
    if (w0 < 120 || !rs.every(r => Math.abs(r.width - w0) < w0 * 0.05 && Math.abs(r.height - h0) < h0 * 0.08 && Math.abs(r.top - rs[0].top) < 4)) continue;
    const shaped = kids.every(k => k.querySelector('h2,h3,h4,strong,b') && k.querySelector('p') && !k.querySelector('img[width]:not([width="0"]), picture, video') &&
      [...k.querySelectorAll('svg,img,i,[class*=icon i]')].some(ic => { const r = ic.getBoundingClientRect(); return r.width > 8 && r.width <= 72; }));
    const st = kids.map(k => { const s = getComputedStyle(k); return [s.backgroundColor, s.borderTopWidth, s.borderRadius].join('|'); });
    if (shaped && new Set(st).size === 1) rows.push(p); }
  if (rows.length) out.push(`row of identical icon + heading + text boxes (${rows.length}; defaults.md 8, review.md 4): ${rows.slice(0, 2).map(name).join(', ')}`);
  return out;
}
"""

# V4.16 rule:premium (from Hallmark layout.md 78 and imagery.md): scale of heads and of the hero visual on premium pages
PREMIUM_JS = r"""
([mobile, vw]) => {
  const out = []; const H = innerHeight;
  const vis = e => { const s = getComputedStyle(e); const r = e.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && +s.opacity > 0.05 && r.width > 0 && r.height > 0; };
  const h1 = [...document.querySelectorAll('h1')].find(vis);
  const h1px = h1 ? parseFloat(getComputedStyle(h1).fontSize) : 0;
  if (!h1) out.push('premium: no visible h1 on the first screen');
  else if (!mobile && h1px < 64) out.push(`premium: hero head is ${Math.round(h1px)}px at 1440 (want 84-120px, a long head at least 64px)`);
  else if (mobile && h1px < 36) out.push(`premium: hero head is ${Math.round(h1px)}px on the phone (want 40px or more)`);
  if (!mobile) {
    const h2 = [...document.querySelectorAll('main h2, section h2, h2')].filter(vis).map(e => parseFloat(getComputedStyle(e).fontSize));
    if (h2.length >= 2) { h2.sort((a, b) => a - b); const med = h2[Math.floor(h2.length / 2)];
      if (med < 40) out.push(`premium: section heads are about ${Math.round(med)}px (want 48-60px at 1440; under 40px reads unfinished)`); }
    // the largest picture on the first screen
    let best = 0;
    for (const e of document.querySelectorAll('img, picture, video, canvas, svg, [style*="background-image"], [class*=hero] *')) {
      if (!vis(e)) continue; const tag = e.tagName.toLowerCase();
      const bg = getComputedStyle(e).backgroundImage; const isPic = ['img', 'picture', 'video', 'canvas'].includes(tag) || (tag === 'svg' && e.getBoundingClientRect().width > 240) || (bg && bg.includes('url('));
      if (!isPic) continue;
      const r = e.getBoundingClientRect(); const w = Math.max(0, Math.min(r.right, vw) - Math.max(r.left, 0)); const h = Math.max(0, Math.min(r.bottom, H) - Math.max(r.top, 0));
      best = Math.max(best, w * h);
    }
    const share = best / (vw * H);
    if (share < 0.28 && h1px < 110) out.push(`premium: the largest picture covers ${Math.round(share * 100)}% of the first screen; make the hero visual big (6-7 of 12 columns at 60-75% of the screen tall, or full-bleed) or let the type be the visual at 110px+`);
  }
  return out;
}
"""

async def main():
    ap = argparse.ArgumentParser(); ap.add_argument("page", nargs="?"); ap.add_argument("--route", action="append", default=[]); ap.add_argument("--primary", default=""); ap.add_argument("--core", default=""); ap.add_argument("--premium", action="store_true")
    ap.add_argument("--url", help="check a served page (an app that needs its backend), e.g. http://localhost:5173/")
    ap.add_argument("--real-data", action="store_true"); ap.add_argument("--no-style", action="store_true"); ap.add_argument("--allow-net", action="store_true")
    a = ap.parse_args()
    if not a.page and not a.url: ap.error("give a page file or --url")
    target = a.url or ("file://" + os.path.abspath(a.page))
    from urllib.parse import urlparse
    origin = urlparse(target); own = f"{origin.scheme}://{origin.netloc}" if origin.scheme.startswith("http") else None
    routes = [r.split("=", 1) for r in a.route]
    async def route(r):
        u = r.request.url
        for sub, local in routes:
            if sub in u:
                ct = "application/json" if local.endswith(".json") else "application/javascript"
                return await r.fulfill(path=local, content_type=ct, headers={"Access-Control-Allow-Origin": "*"})
        if u.startswith(("file:", "data:", "blob:")): return await r.continue_()
        # V4.16.1: the page's own server and localhost load (apps with a backend); before, every non-file request was aborted
        h = urlparse(u).hostname or ""
        if (own and u.startswith(own)) or h in ("localhost", "127.0.0.1", "0.0.0.0", "::1") or h.endswith(".localhost") or a.allow_net:
            if not ("fonts.googleapis.com" in u or u.startswith(fontroute.HOST)): return await r.continue_()
        # V4.16 rule:real-fonts-in-shots: measure with the page's real faces
        if "fonts.googleapis.com" in u: return await r.fulfill(status=200, content_type="text/css", body=fontroute.css_for(u))
        if u.startswith(fontroute.HOST):
            b = fontroute._file_body(u); return await r.fulfill(status=200 if b else 404, content_type=fontroute._ctype(u), body=b or b"")
        if "fontshare.com" in u: return await r.continue_()
        return await r.abort()
    found = []
    async with async_playwright() as pw:
        br = await pw.chromium.launch()
        for label, vp, mob in (("desktop", {"width": 1440, "height": 900}, False), ("phone", {"width": 375, "height": 812}, True)):
            ctx = await br.new_context(viewport=vp, is_mobile=mob, has_touch=mob); await ctx.route("**/*", route)
            pg = await ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
            try: await pg.goto(target, wait_until="load", timeout=45000)
            except Exception as e: found.append(f"[{label}] could not open {target}: {str(e)[:120]}"); await ctx.close(); continue
            await pg.wait_for_timeout(1500)
            await pg.evaluate("async () => { const H = document.documentElement.scrollHeight; for (let y = 0, k = 0; y < H && k < 12; y += innerHeight * 0.9, k++) { scrollTo(0, y); await new Promise(r => setTimeout(r, 250)); } scrollTo(0, 0); }")
            await pg.wait_for_timeout(300)
            await pg.evaluate("document.fonts.ready")
            res = await pg.evaluate(JS, [mob, vp['width'], a.primary, a.core, a.real_data])
            if not a.no_style and not mob: res += await pg.evaluate(STYLE_JS, [mob, vp['width']])
            if a.premium: res += await pg.evaluate(PREMIUM_JS, [mob, vp['width']])
            found += [f"[{label}] JS error: {e}" for e in errs] + [f"[{label}] {x}" for x in res]
            if not mob:
                # V4.13 (rule:focus-visible, from Taste): Tab through the first controls; a focus ring must appear
                seen = shown = 0
                for _ in range(8):
                    await pg.keyboard.press("Tab")
                    r = await pg.evaluate(FOCUS)
                    if r is None: continue
                    seen += 1; shown += 1 if r else 0
                if seen >= 3 and shown == 0: found.append(f"[{label}] no visible focus ring on the first {seen} controls reached with Tab (rule:focus-visible)")
            await ctx.close()
        # V4.13: the narrowest phone (320px): only sideways overflow
        ctx = await br.new_context(viewport={"width": 320, "height": 700}, is_mobile=True, has_touch=True); await ctx.route("**/*", route)
        pg = await ctx.new_page()
        try: await pg.goto(target, wait_until="load", timeout=45000)
        except Exception: pass
        await pg.wait_for_timeout(1200)
        sw = await pg.evaluate("document.documentElement.scrollWidth")
        if sw > 322:
            wide = await pg.evaluate("[...document.querySelectorAll('body *')].filter(e => e.getBoundingClientRect().right > 322 && (!e.parentElement || e.parentElement.getBoundingClientRect().right <= 322)).slice(0, 3).map(e => e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : ''))")
            found.append(f"[320px] overflow: page is {sw}px wide; culprits: {', '.join(wide)}")
        await ctx.close()
        await br.close()
    print("\n".join(found) if found else "check: nothing found")

if __name__ == "__main__":
    asyncio.run(main())
