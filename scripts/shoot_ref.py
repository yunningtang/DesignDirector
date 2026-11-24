#!/usr/bin/env python3
"""Capture one live public screen into the reference library (rule:live-anchor, rule:ref-kind).

  python3 shoot_ref.py <url> <kind>

Screenshots the first screen at 1440x900, refuses blank, error, bot-check and login pages, and CLASSIFIES what it
captured before saving it (V4.16.1, rule:ref-kind):

  working_ui    the product's own working screen: many controls, a list, grid, table, board or canvas
  marketing     a homepage, template gallery or pricing page about the product (big head, sign-up actions, little UI)
  article       a changelog, blog post, help or docs page (long prose, dates, an <article>)
  obstructed    a dialog, cookie wall or overlay covers a large part of the screen
  logged_out    a login or sign-up wall, or a header with sign-in and almost nothing else

Only working_ui is saved as anchor-worthy. The others are saved as plain references (anchor_ok false) and the
script says so, so a template page, a changelog or a board under a pop-up is never taken as the structure model.
Then answer the same-kind questions it prints (rule:ref-fit) before you use the screen.

Saves into DD_REFS (default data/refimg in this skill) as live/<host>.jpg with an index entry; creates the folder
and index.json if they do not exist yet. Each run uses its own temp files, so captures can run in parallel.
"""
import fcntl, json, os, re, sys, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image

LIB = os.environ.get('DD_REFS', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'refimg'))
BAD = re.compile(r"sign in|log in|login|sign up to|create an account|captcha|are you a robot|verify you are human|just a moment|access denied|403 forbidden|404|not found|enable javascript|cloudflare", re.I)

PROBE = r"""() => {
  const vis = e => { const s = getComputedStyle(e), r = e.getBoundingClientRect();
    return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05 && r.top < innerHeight && r.bottom > 0; };
  const area = innerWidth * innerHeight;
  const all = [...document.querySelectorAll('body *')];
  // overlays: dialogs, fixed/sticky boxes with a high z-index that cover much of the screen
  let cover = 0, coverWhat = '';
  for (const e of all) { const s = getComputedStyle(e); if (!vis(e)) continue;
    const isDlg = e.matches('dialog[open],[role=dialog],[role=alertdialog],[aria-modal=true]');
    if (!(isDlg || (s.position === 'fixed' && (+s.zIndex || 0) >= 10))) continue;
    const r = e.getBoundingClientRect(); const w = Math.max(0, Math.min(r.right, innerWidth) - Math.max(r.left, 0)), h = Math.max(0, Math.min(r.bottom, innerHeight) - Math.max(r.top, 0));
    const share = w * h / area; if (share > 0.9 && !isDlg && !(e.textContent || '').trim()) continue;   // a full-screen app shell, not an overlay
    if (share > 0.9 && !isDlg && e.querySelectorAll('button,a,input').length > 15) continue;
    if (share > cover) { cover = share; coverWhat = (e.getAttribute('aria-label') || e.className || e.tagName).toString().slice(0, 40); } }
  const ctl = all.filter(e => e.matches('button,input,select,textarea,[role=button],[role=checkbox],[role=gridcell],[role=row],[role=tab],[role=treeitem],[contenteditable=true],[draggable=true]') && vis(e)).length;
  const rows = all.filter(e => e.matches('tr,li,[role=row],[role=listitem],[role=gridcell]') && vis(e)).length;
  const work = all.filter(e => e.matches('table,canvas,[role=grid],[role=table],[role=tree],[role=treegrid],[class*=board i],[class*=kanban i],[class*=column i] [class*=card i],[class*=editor i],[class*=sidebar i]') && vis(e)).length;
  const h1 = [...document.querySelectorAll('h1')].find(vis); const h1px = h1 ? parseFloat(getComputedStyle(h1).fontSize) : 0;
  const txt = (document.body ? document.body.innerText : '');
  const cta = (txt.match(/\b(get started|start (for )?free|try (it )?(for )?free|sign up|book a demo|request a demo|see pricing|download (the )?app|join (the )?waitlist|use this template|explore templates)\b/gi) || []).length;
  const article = !!document.querySelector('article') && [...document.querySelectorAll('article p, main p')].filter(vis).reduce((n, p) => n + p.innerText.split(/\s+/).length, 0) > 180;
  const prose = [...document.querySelectorAll('p')].filter(vis).reduce((n, p) => n + p.innerText.split(/\s+/).length, 0);
  const dated = (txt.slice(0, 3000).match(/\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.? \d{1,2},? \d{4}\b|\b\d{4}-\d{2}-\d{2}\b/gi) || []).length;
  const signin = /\b(sign in|log in)\b/i.test(txt.slice(0, 600));
  return {cover, coverWhat, ctl, rows, work, h1px, cta, article, prose, dated, signin, words: txt.split(/\s+/).length,
          title: document.title, url: location.href};
}"""

def classify(m, url):
    """Return (kind, reason)."""
    u = url.lower()
    if m["cover"] >= 0.3: return "obstructed", f"an overlay covers {round(m['cover'] * 100)}% of the screen ({m['coverWhat']})"
    if re.search(r"/(changelog|blog|news|releases?|updates?|docs?|help|guide|articles?|posts?)(/|$|\?)", u) or (m["article"] and m["dated"] >= 1) or (m["prose"] > 400 and m["ctl"] < 15):
        return "article", "a changelog, blog, help or docs page (long prose, dates)"
    if re.search(r"/(templates?|pricing|features?|product|solutions?|customers|enterprise)(/|$|\?)", u):
        return "marketing", "a template gallery, pricing or feature page, not the working screen"
    working = m["ctl"] >= 15 and (m["rows"] >= 8 or m["work"] >= 1)
    if m["signin"] and m["ctl"] < 8 and m["rows"] < 8: return "logged_out", "a sign-in header over a page with almost no interface"
    if not working and (m["cta"] >= 2 or m["h1px"] >= 44): return "marketing", f"a homepage-style page (head {round(m['h1px'])}px, {m['cta']} sign-up actions, {m['ctl']} controls)"
    if working: return "working_ui", f"{m['ctl']} controls, {m['rows']} rows, {m['work']} work areas"
    return "marketing", f"too little interface to be a working screen ({m['ctl']} controls, {m['rows']} rows)"

def load_index():
    os.makedirs(LIB, exist_ok=True)
    p = os.path.join(LIB, "index.json")
    if not os.path.exists(p):   # V4.16.1: a fresh install has no library yet; start an empty one instead of crashing
        with open(p, "w") as f: f.write("[]")
    return p

def main():
    if len(sys.argv) < 3: sys.exit("usage: shoot_ref.py <url> <kind>")
    url, kind = sys.argv[1], sys.argv[2]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900}, user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36")
        try:
            r = pg.goto(url, wait_until="domcontentloaded", timeout=30000); pg.wait_for_timeout(3500)
        except Exception as e:
            b.close(); sys.exit(f"REFUSED {url}: could not load ({str(e)[:80]})")
        status = r.status if r else 0
        info = pg.evaluate("""() => ({title: document.title, text: (document.body ? document.body.innerText : '').slice(0, 4000),
            pw: !!document.querySelector('input[type=password]'), h1: (document.querySelector('h1') || {}).innerText || ''})""")
        words = len(info["text"].split())
        why = None
        if status >= 400: why = f"HTTP {status}"
        elif words < 25: why = f"nearly blank ({words} words)"
        elif info["pw"] and words < 300: why = "login form"
        elif BAD.search(info["title"] + " " + info["h1"]): why = f"looks like a login, error or bot check ({(info['title'] or info['h1'])[:50]})"
        if why:
            b.close(); sys.exit(f"REFUSED {url}: {why}")
        m = pg.evaluate(PROBE)
        page_kind, reason = classify(m, pg.url)
        fd, tmp = tempfile.mkstemp(suffix=".png"); os.close(fd)
        pg.screenshot(path=tmp); b.close()
    host = re.sub(r"[^a-zA-Z0-9._-]", "_", re.sub(r"^https?://", "", url))[:80]
    rel = f"live/{host}.jpg"; os.makedirs(os.path.join(LIB, "live"), exist_ok=True)
    Image.open(tmp).convert("RGB").resize((720, 450)).save(os.path.join(LIB, rel), quality=82); os.remove(tmp)
    ok = page_kind == "working_ui"
    with open(load_index(), "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try: idx = json.load(f)
        except json.JSONDecodeError: idx = []
        idx = [x for x in idx if x.get("img") != rel]
        idx.append({"id": "live_" + host, "lib": "app", "key": kind, "img": rel, "host": url, "ground": "white", "hue": "neutral",
                    "anchor_ok": ok, "page_kind": page_kind, "live": True, "url": url})
        f.seek(0); json.dump(idx, f, indent=0); f.truncate()
    print(f"SAVED {os.path.join(LIB, rel)}  ({url}, {kind})")
    print(f"PAGE KIND {page_kind}: {reason}")
    if not ok:
        print("NOT AN ANCHOR: this is not the product's working screen. Use it for tone at most, never as the structure model.\n"
              "  Try another URL (a public board, demo instance, shared view, docs screenshot of the app is NOT enough).")
    print("Read it with the Read tool, then answer in meta.json ref_fit (rule:ref-fit), yes or no with a few words each:\n"
          "  same_user:  would the brief's user use this product?\n"
          "  same_task:  is this screen doing the brief's primary task (or the same kind of task)?\n"
          "  same_data:  does it show the same kind of records (orders, bookings, notes, photos...) at a similar volume?\n"
          "  Anchor only if page_kind is working_ui and at least same_task and same_data are yes.")

if __name__ == "__main__":
    main()
