#!/usr/bin/env python3
"""Capture one live public screen into the reference library (rule:live-anchor).

  python3 shoot_ref.py <url> <kind>

Screenshots the first screen at 1440x900, refuses blank, error, bot-check and login pages, and saves usable
ones into the library (DD_REFS, default data/refimg in this skill) as live/<host>.jpg with an index entry, so the
library grows. Each run uses its own temp files, so captures can run in parallel.
(V4.12: rebuilt from the V4.10 description; the original file was lost with the earlier workspace.)
"""
import fcntl, json, os, re, sys, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image

LIB = os.environ.get('DD_REFS', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'refimg'))
BAD = re.compile(r"sign in|log in|login|sign up to|create an account|captcha|are you a robot|verify you are human|just a moment|access denied|403 forbidden|404|not found|enable javascript|cloudflare", re.I)

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
        fd, tmp = tempfile.mkstemp(suffix=".png"); os.close(fd)
        pg.screenshot(path=tmp); b.close()
    host = re.sub(r"[^a-zA-Z0-9._-]", "_", re.sub(r"^https?://", "", url))[:80]
    rel = f"live/{host}.jpg"; os.makedirs(os.path.join(LIB, "live"), exist_ok=True)
    Image.open(tmp).convert("RGB").resize((720, 450)).save(os.path.join(LIB, rel), quality=82); os.remove(tmp)
    with open(os.path.join(LIB, "index.json"), "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        idx = json.load(f); idx = [x for x in idx if x.get("img") != rel]
        idx.append({"id": "live_" + host, "lib": "app", "key": kind, "img": rel, "host": url, "ground": "white", "hue": "neutral", "anchor_ok": True, "live": True, "url": url})
        f.seek(0); json.dump(idx, f, indent=0); f.truncate()
    print(f"SAVED {os.path.join(LIB, rel)}  ({url}, {kind}). Read it with the Read tool.")

if __name__ == "__main__":
    main()
