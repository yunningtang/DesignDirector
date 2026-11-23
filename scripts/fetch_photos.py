#!/usr/bin/env python3
"""Build the offline photo library that scripts/photos.py reads.

Downloads the 755 tagged Wikimedia Commons photos listed in data/hallmark_photos.json
(the list comes from Hallmark, MIT; each photo keeps its own licence: CC0, public domain,
CC BY or CC BY-SA, with author and source page in the index) at 960px wide into
data/photolib2/img/, and writes data/photolib2/index.json.

  python3 scripts/fetch_photos.py                 # everything, in list order
  python3 scripts/fetch_photos.py coffee bread    # photos matching these words first

Wikimedia rate-limits fast clients (HTTP 429). This script goes one photo at a time, backs off
on 429, uses curl (Python urllib is refused more often) and resumes where it stopped.
Needs: curl, Pillow (pip install pillow).
"""
import hashlib, io, json, os, re, subprocess, sys, time, urllib.parse
from PIL import Image

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = json.load(open(os.path.join(SKILL, 'data', 'hallmark_photos.json')))['photos']
OUT = os.environ.get('DD_PHOTO_DIR', os.path.join(SKILL, 'data', 'photolib2'))
UA = 'design-director-skill/4.16 (offline photo library)'
os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
ip = os.path.join(OUT, 'index.json')
idx = json.load(open(ip)) if os.path.exists(ip) else []
have = {x['id'] for x in idx}
order = [p for p in SRC if p['id'] not in have]
pri = [a.lower() for a in sys.argv[1:]]
if pri:
    order.sort(key=lambda p: -sum(k in (' '.join(p.get('tags', [])) + ' ' + p.get('subject', '') + ' ' + p.get('cat', '')).lower() for k in pri))


def thumb(p):
    """Wikimedia only serves standard thumbnail widths quickly; 960px is one of them."""
    parts = p['file'].split('/commons/')[1]
    name = parts.split('/')[-1]
    if p['w'] <= 960:
        return p['file']
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{parts}/960px-{name}" + ('.jpg' if name.lower().endswith(('.tif', '.tiff')) else '')


tmp = os.path.join(OUT, '.download.tmp')
wait = 2.0
print(f'{len(idx)} already here, {len(order)} to fetch', flush=True)
for n, p in enumerate(order):
    url = urllib.parse.quote(thumb(p), safe=':/%')
    for attempt in range(6):
        r = subprocess.run(['curl', '-s', '-L', '-m', '60', '-o', tmp, '-w', '%{http_code}', '-A', UA, url], capture_output=True, text=True)
        code = int(r.stdout or 0)
        if code == 429:
            wait = min(60, wait * 2); time.sleep(wait * 2); continue
        if code != 200:
            print('http', code, p['id'][:60], flush=True); break
        try:
            im = Image.open(io.BytesIO(open(tmp, 'rb').read())); im.load(); im = im.convert('RGB')
        except Exception as ex:
            print('bad image', p['id'][:60], str(ex)[:60], flush=True); break
        fn = hashlib.md5(p['id'].encode()).hexdigest()[:12] + '.jpg'
        im.save(os.path.join(OUT, 'img', fn), 'JPEG', quality=78, optimize=True, progressive=True)
        e = {k: p.get(k) for k in ('id', 'page', 'license', 'author', 'subject', 'tags', 'cat', 'tone', 'temp', 'people', 'q', 'color')}
        e.update(file=f'img/{fn}', w=im.width, h=im.height)
        idx.append(e)
        json.dump(idx, open(ip, 'w'), ensure_ascii=False)
        wait = max(1.5, wait * 0.9)
        break
    time.sleep(wait)
    if n % 10 == 0:
        print(n, 'have', len(idx), 'wait', round(wait, 1), flush=True)
if os.path.exists(tmp):
    os.remove(tmp)
print('done', len(idx))
