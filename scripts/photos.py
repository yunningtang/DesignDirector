"""Rank the offline photo library for a subject (V4.16 rule:premium pictures).

  python3 photos.py "perfume bottle on stone" "glass still life" [--tone light|dark] [--temp warm|cool|neutral] [--n 8] [--people none]

Library: $DD_PHOTO_LIB2 (default data/photolib2/index.json in this skill; build it with scripts/fetch_photos.py), Hallmark's
755 tagged Wikimedia photos (CC0, public domain, CC BY, CC BY-SA), downloaded at 960px. Also reads $DD_PHOTO_LIB
(default data/photolib/index.json) if you keep a second library in the same format.
Prints, best first: absolute path, size, what it shows, tone and temperature, and the credit line to put in the footer.
Look at every pick with the Read tool before using it; keep only pictures on the page's own subject.
"""
import json, os, re, sys, argparse

_SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB2 = os.environ.get('DD_PHOTO_LIB2', os.path.join(_SKILL, 'data', 'photolib2', 'index.json'))
LIB1 = os.environ.get('DD_PHOTO_LIB', os.path.join(_SKILL, 'data', 'photolib', 'index.json'))


def words(s):
    return [w for w in re.findall(r'[a-z]+', s.lower()) if len(w) > 2 and w not in {'the', 'and', 'with', 'for', 'from', 'into', 'over'}]


def load():
    out = []
    for lib in (LIB2, LIB1):
        if not os.path.exists(lib):
            continue
        base = os.path.dirname(lib)
        for x in json.load(open(lib)):
            text = ' '.join([x.get('subject') or x.get('title') or '', ' '.join(x.get('tags') or []), x.get('cat') or x.get('topic') or '', x.get('query') or ''])
            out.append({'path': os.path.join(base, x['file']), 'w': x.get('w'), 'h': x.get('h'), 'shows': x.get('subject') or x.get('title') or '',
                        'tone': x.get('tone', '?'), 'temp': x.get('temp', '?'), 'people': x.get('people', '?'), 'q': x.get('q', 2),
                        'credit': f"{x.get('author') or 'unknown'}, {x.get('license') or x.get('licence')}, {x.get('page') or x.get('source')}",
                        'text': text.lower(), 'lib': 'hallmark' if lib == LIB2 else 'openverse'})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('queries', nargs='+'); ap.add_argument('--n', type=int, default=8)
    ap.add_argument('--tone'); ap.add_argument('--temp'); ap.add_argument('--people')
    ap.add_argument('--orient', choices=['landscape', 'portrait', 'square'])
    a = ap.parse_args()
    lib = load()
    if not lib:
        print('no photo library found'); return
    print(f'library: {len(lib)} photos')
    for q in a.queries:
        qw = words(q)
        scored = []
        for x in lib:
            if a.tone and x['tone'] != a.tone: continue
            if a.temp and x['temp'] != a.temp: continue
            if a.people and x['people'] != a.people: continue
            if a.orient and x['w'] and x['h']:
                r = x['w'] / x['h']
                if (a.orient == 'landscape' and r < 1.15) or (a.orient == 'portrait' and r > 0.9) or (a.orient == 'square' and not 0.85 < r < 1.18): continue
            hit = sum(2 if re.search(r'\b' + w, x['text']) else 0 for w in qw)
            if hit:
                scored.append((hit + 0.3 * (x['q'] or 2), x))
        scored.sort(key=lambda t: -t[0])
        print(f'\n"{q}": {len(scored)} matches')
        for s, x in scored[:a.n]:
            print(f"  {x['path']}  {x['w']}x{x['h']}  tone {x['tone']}, {x['temp']}, people {x['people']}\n      shows: {x['shows'][:110]}\n      credit: {x['credit']}")


if __name__ == '__main__':
    main()
