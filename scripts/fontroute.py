"""Serve Google Fonts offline for Playwright screenshots.

The sandbox cannot reach fonts.googleapis.com, so pages render in fallback fonts.
This module intercepts Google Fonts CSS requests and answers them with @font-face
rules built from the npm @fontsource packages (same font files, OFL), installed
on demand into FONTKIT (default ~/.cache/dd-fontkit). Needs node/npm.

Use (sync or async Playwright):
    import sys; sys.path.insert(0, '<skill>/scripts'); import fontroute
    fontroute.attach(context)            # sync API
    await fontroute.attach_async(context)  # async API
Call before page.goto. Other network requests are left alone.
"""
import os, re, subprocess, urllib.parse, threading

FONTKIT = os.environ.get('FONTKIT', os.path.expanduser('~/.cache/dd-fontkit'))
HOST = 'http://fontkit.local/'
_lock = threading.Lock()
_tried = {}


def _slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def _ensure(pkg):
    """npm-install a package once; return its folder or None."""
    d = os.path.join(FONTKIT, 'node_modules', pkg)
    if os.path.isdir(d):
        return d
    with _lock:
        if pkg in _tried:
            return d if os.path.isdir(d) else None
        _tried[pkg] = True
        os.makedirs(FONTKIT, exist_ok=True)
        if not os.path.exists(os.path.join(FONTKIT, 'package.json')):
            subprocess.run(['npm', 'init', '-y'], cwd=FONTKIT, capture_output=True)
        subprocess.run(['npm', 'i', '--no-audit', '--no-fund', pkg], cwd=FONTKIT, capture_output=True, timeout=180)
    return d if os.path.isdir(d) else None


def _parse_family(spec):
    """'Public Sans:ital,wght@0,400;1,700' -> (name, set of (weight, italic))"""
    name, _, axes = spec.partition(':')
    name = name.replace('+', ' ').strip()
    want = set()
    if not axes:
        return name, {(400, False)}
    keys, _, vals = axes.partition('@')
    keys = keys.split(',')
    for tup in vals.split(';'):
        parts = tup.split(',')
        d = dict(zip(keys, parts))
        ital = d.get('ital', '0') == '1'
        w = d.get('wght', '400')
        if '..' in w:
            a, b = w.split('..')
            for x in range(100, 1000, 100):
                if float(a) <= x <= float(b):
                    want.add((x, ital))
        else:
            try:
                want.add((int(float(w)), ital))
            except ValueError:
                want.add((400, ital))
    return name, want or {(400, False)}


def css_for(url):
    q = urllib.parse.urlparse(url).query
    fams = urllib.parse.parse_qs(q).get('family', [])
    if not fams and '/css?' in url:  # css v1: family=A:400,700|B
        for f in urllib.parse.parse_qs(q).get('family', [''])[0].split('|'):
            fams.append(f)
    out = []
    for spec in fams:
        name, want = _parse_family(spec)
        slug = _slug(name)
        d = _ensure(f'@fontsource/{slug}')
        if not d:
            continue
        for w, it in sorted(want):
            f = os.path.join(d, f'{w}{"-italic" if it else ""}.css')
            if not os.path.exists(f):
                continue
            css = open(f).read()
            css = css.replace('url(./files/', f'url({HOST}@fontsource/{slug}/files/')
            css = re.sub(r"font-family:\s*'[^']+'", f"font-family: '{name}'", css)
            out.append(css)
    return '\n'.join(out)


def _file_body(url):
    path = os.path.join(FONTKIT, 'node_modules', url[len(HOST):].split('?')[0])
    return open(path, 'rb').read() if os.path.exists(path) else None


def _ctype(url):
    return 'font/woff2' if url.endswith('.woff2') else 'font/woff' if url.endswith('.woff') else 'application/octet-stream'


def attach(context):
    def gcss(route):
        route.fulfill(status=200, content_type='text/css', body=css_for(route.request.url))
    def gfile(route):
        b = _file_body(route.request.url)
        route.fulfill(status=200 if b else 404, content_type=_ctype(route.request.url), body=b or b'')
    context.route(re.compile(r'https?://fonts\.googleapis\.com/.*'), gcss)
    context.route(re.compile(r'https?://fonts\.gstatic\.com/.*'), lambda r: r.fulfill(status=404, body=b''))
    context.route(re.compile(r'http://fontkit\.local/.*'), gfile)


async def attach_async(context):
    async def gcss(route):
        await route.fulfill(status=200, content_type='text/css', body=css_for(route.request.url))
    async def gfile(route):
        b = _file_body(route.request.url)
        await route.fulfill(status=200 if b else 404, content_type=_ctype(route.request.url), body=b or b'')
    async def g404(route):
        await route.fulfill(status=404, body=b'')
    await context.route(re.compile(r'https?://fonts\.googleapis\.com/.*'), gcss)
    await context.route(re.compile(r'https?://fonts\.gstatic\.com/.*'), g404)
    await context.route(re.compile(r'http://fontkit\.local/.*'), gfile)


if __name__ == '__main__':
    import sys
    print(css_for(sys.argv[1])[:600])
