#!/usr/bin/env python3
"""Pick 3-5 real reference screenshots for a page from the local library (no live scraping).

Homepage library (lib=home): real production homepages by category (49 categories, ~1200 sites).
App library (lib=app): public, logged-out app screens: dashboards, editors, calendars, boards, forms, maps...

Which library depends on the mode:
  persuade / experience : 4 homepages of the category
  transact              : 3 homepages of the category + 1 shop/checkout screen
  read                  : 3 homepages of the category + 1 docs/learning screen
  operate               : 3 app screens matching the brief + 1 homepage of the category (for tone)

Within a pool, the pick is seeded by the task and spread out: different ground (white / dark / colour) and hue.

Usage: python3 refs.py --mode operate --category oss_tools --brief brief.txt --seed 25_form-builder [--n 4]
"""
import argparse, json, os, random, re, sys, hashlib

LIB = os.environ.get('DD_REFS', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'refimg'))
APP_WORDS = [
    ('feed', r'feed|communit|social|discover|forum|follow|comment|reaction|profile'),
    ('calendar', r'calendar|schedul|appointment|event planner|week view'),
    ('booking', r'booking|reserv|availability|hotel|ryokan|check-?in|guests'),
    ('kanban', r'kanban|board|in progress|swimlane|sprint|drag-and-drop movement'),
    ('todo', r'to-?do|checklist|task list|habit'),
    ('form', r'form builder|survey|form|checkout|sign.?up flow|application'),
    ('canvas', r'canvas|editor|draw|diagram|mind.?map|whiteboard|poster|storyboard|timeline|node|workflow|graph editor'),
    ('dashboard', r'dashboard|admin|analytics|metrics|kpi|finance|budget|stats|monitor'),
    ('analytics', r'chart|data|visuali|network|explorer|report'),
    ('table', r'table|spreadsheet|list view|crm|inventory'),
    ('notes', r'note|wiki|docs|knowledge|second brain|markdown|writing'),
    ('code', r'code|ide|playground|terminal|api|developer|regex'),
    ('map', r'map|route|transit|geo|location|trip'),
    ('chat', r'chat|message|inbox|assistant|support'),
    ('media', r'music|video|player|playlist|podcast|gallery|photo'),
    ('design', r'colou?r|palette|font|type|typograph|gradient'),
    ('vocab', r'language|vocabular|flashcard|spaced|pronunc|dictionar|conjugat|syllab|phrase'),
    ('lesson', r'lesson|exercise|challenge|tutorial|quiz|hint|step-by-step|practice'),
    ('course', r'course|curriculum|syllabus|module|progress|enrol|lecture|school'),
    ('learn', r'learn|tutor|study|student'),
    ('game', r'game|puzzle|play'),
    ('orders', r'orders?\b|pickup|pick-up|deliver(y|ies)|inventory|stock level|walk-in|point of sale|\bpos\b|bakery|caf[eé]|salon'),
    ('commerce', r'shop|store|cart|product|buy|order'),
]
GOOD = {   # screens that show the working interior of that kind of tool, preferred as the anchor
    'calendar': ['calendar.com', 'fullcalendar', 'bigcalendar', 'timeanddate.com/calendar', 'cal.com'],
    'form': ['tally.so/r', 'surveyjs', 'rjsf', 'formbricks', 'checkout', 'typeform'],
    'canvas': ['excalidraw', 'tldraw', 'diagrams.net', 'markmap', 'mermaid.live', 'flowchart.fun', 'dbdiagram', 'whimsical'],
    'dashboard': ['shadcn.com/examples/dashboard', 'tailadmin', 'tremor', 'pro.ant.design', 'tabler', 'shadcn-admin', 'nextadmin'],
    'analytics': ['plausible', 'umami', 'grafana', 'posthog', 'fathom', 'electricitymaps'],
    'code': ['codesandbox', 'stackblitz', 'play.tailwindcss', 'typescriptlang', 'regex101', 'vscode.dev', 'codepen', 'svelte.dev/playground'],
    'learn': ['duolingo.com/learn', 'khanacademy.org/math', 'brilliant', 'exercism', 'freecodecamp', 'desmos', 'phet'],
    'kanban': ['projects', 'trello.com/b', 'vikunja', 'kanboard', 'linear'],
    'notes': ['stackedit', 'dillinger', 'hackmd', 'typst', 'obsidian'],
    'table': ['ag-grid', 'handsontable', 'data-grid', 'baserow', 'tanstack'],
    'map': ['openstreetmap', 'felt.com', 'kepler', 'windy', 'citymapper'],
    'media': ['open.spotify', 'soundcloud', 'youtube'],
}
NOTE = ('Look at each with the Read tool before writing the contract. Borrow STRUCTURE only (rule:borrow-layers): which panes '
        'exist and their rough widths, where navigation and the main controls sit, how dense rows are, how much colour and imagery. '
        'Do not borrow SURFACE: the selected-state treatment, tag and label colours, icon set, brand colour, wordmark or copy are '
        'that product\'s own language; derive yours from the subject\'s world.')


def app_types(text):
    t = text.lower(); hits = []
    for k, rx in APP_WORDS:
        n = len(re.findall(rx, t))
        if n: hits.append((n, k))
    return [k for n, k in sorted(hits, reverse=True)]


def spread(pool, n, rnd):
    """Greedy pick that varies ground and hue."""
    pool = pool[:]; rnd.shuffle(pool); out = []
    while pool and len(out) < n:
        seen_g = {x['ground'] for x in out}; seen_h = {x['hue'] for x in out}
        pool.sort(key=lambda x: (x['ground'] in seen_g) + (x['hue'] in seen_h))
        out.append(pool.pop(0))
    return out


def pick(mode, category, brief, seed, n=4, flow=False):
    p = f'{LIB}/index.json'
    if not os.path.exists(p): return [], app_types(brief)   # V4.16.1: no local library installed
    # V4.16.1 rule:ref-kind: a live capture that is not a working screen never anchors
    idx = [dict(x, anchor_ok=False) if x.get('page_kind') not in (None, 'working_ui') else x for x in json.load(open(p))]
    rnd = random.Random(int(hashlib.sha256(f'{seed}|{mode}|{category}'.encode()).hexdigest()[:12], 16))
    home = [x for x in idx if x['lib'] == 'home' and x['key'] == category]
    app = [x for x in idx if x['lib'] == 'app']
    types = app_types(brief)
    def app_of(ks, k):
        for t in ks:
            p = [x for x in app if x['key'] == t]
            if p: return spread(p, k, rnd)
        return []
    if mode == 'operate':
        a = []
        for t in types[:2]:   # anchor (V4.10): only a screen marked anchor-worthy, of a kind the brief names strongly
            p = [x for x in app if x['key'] == t and x.get('anchor_ok')]
            if p:
                pick1 = dict(rnd.choice(sorted(p, key=lambda x: x['id']))); pick1['is_anchor'] = True
                a = [pick1]; break
        for t in types:
            a += [x for x in spread([x for x in app if x['key'] == t and x['id'] not in {y['id'] for y in a}], 3 - len(a), rnd)]
            if len(a) >= 3: break
        res = a + spread(home, n - len(a), rnd)
        if not (a and a[0].get('is_anchor')):
            res = [dict(x, need_live=(types[0] if types else 'tool')) for x in res] or [{'need_live': types[0] if types else 'tool'}]
    elif mode == 'transact':
        res = spread(home, n - 1, rnd) + app_of(['form', 'booking'] if flow else ['commerce', 'form'], 1)
    elif mode == 'read':
        res = spread(home, n - 1, rnd) + app_of([t for t in types if t in ('learn', 'notes', 'analytics', 'map')] or ['notes'], 1)
    else:
        res = spread(home, n, rnd)
    return res, types


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', required=True); ap.add_argument('--category', required=True)
    ap.add_argument('--brief', required=True, help='brief text or a path to it'); ap.add_argument('--seed', required=True)
    ap.add_argument('--n', type=int, default=4)
    a = ap.parse_args()
    brief = open(a.brief).read() if os.path.exists(a.brief) else a.brief
    res, types = pick(a.mode, a.category, brief, a.seed, a.n)
    if not res:
        print('no references for this category; build from categories.md alone'); return
    print(f'REFERENCES ({a.mode}, {a.category}; app types read from the brief: {", ".join(types[:3])})')
    for x in res:
        lib = 'homepage' if x['lib'] == 'home' else 'app screen: ' + x['key']
        print(f"  {LIB}/{x['img']}   {x['host']}  ({lib}; ground {x['ground']}, hue {x['hue']})")
    print('NOTE  ' + NOTE)


if __name__ == '__main__':
    main()
