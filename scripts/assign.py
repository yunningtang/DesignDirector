#!/usr/bin/env python3
"""Design Director V4.12 (rebuilt from V4.11). Shortlist the direction and reveal type and corners AFTER the ranked candidates are committed.

  python3 assign.py --candidates candidates.json --task SLUG                                   # benchmark: evals/tasks.json
  python3 assign.py --candidates candidates.json --mode persuade --category museum --seed X    # anywhere else
  python3 assign.py --candidates candidates.json --task SLUG --veto "c4: cannot show a cart"   # once, factual grounds only
  python3 assign.py --check-name "Pagewise"                                                    # is this page name already used?

rule:mode-choice          operate/read/transact: the script builds one "object" candidate from #3..#n with a job cue.
                          persuade/experience: the script shortlists three including #1; you pick (direction.md step 4).
rule:job-cue              a candidate without a job cue is never built on operate/read/transact pages.
rule:real-nav            navigation surface, layout, height, case, strip, search and action are drawn per category from 491 measured real headers (config/nav_profiles.json).
rule:anchor              operate pages: the first app reference is the structure model; it sets the ground and where colour sits.
rule:honest-sample       sample content is an ordinary day of real use; ALARM states appear once or twice and never cover text.
rule:object-visible      the object is on the first screen; on repeated items every item carries it.
rule:live-anchor         operate pages with no anchor-worthy library screen search the web and screenshot 2-3 live public screens first.
rule:refs                3-5 real screenshots from the local library (homepages by category; app screens by the brief's job for operate) are read before the contract; they inform structure, density and colour placement only.
rule:real-profile         ground, colour level, hue family, colour placement, faces' class and corners are drawn with the frequencies measured on real sites of the category (config/real_profiles.json).
rule:commit-before-reveal the candidates file is hashed on first run; a changed file is refused.
rule:used-pool            page names that recurred in earlier runs are refused (config/used.json); directions are not: the
                          subject's iconic image may recur (rule:icon-first).
rule:engine-prints-next   the remaining steps are printed below, with exact commands.
rule:no-object-in-flows   (V4.12) transact pages whose main job is a multi-step form or booking, and every government page, get no object.
rule:colour-area          (V4.12) on operate/read/transact no flat colour block over about a third of the first screen.
rule:atmospheric-imagery  (V4.12) item pictures on place, food, room, object and trip pages are varied drawn scenes, not repeated pictograms.
rule:ref-kind            (V4.16.1) a reference is classified (working_ui / marketing / article / obstructed / logged_out); only working_ui anchors.
rule:ref-fit             (V4.16.1) before following a reference, answer same_user / same_task / same_data in meta.json ref_fit.
rule:ref-fallback        (V4.16.1) no same-kind working screen (they need a login): build from categories.md and modes.md alone, say so.
rule:borrow-layers       (V4.16.1) STRUCTURE comes from the reference; SURFACE (colour, marks, selected states, tags, icons) from the subject's own world.
rule:image-as-data       (V4.16.1) pictures of what a record is (the cake ordered, the photo filed) are content and allowed on tool pages.
rule:nav-scale           (V4.16.1) nav draws that the content cannot use (menu button, search, tall bar) are dropped before drawing.
rule:final-report        (V4.16.1) the last chat message lists references, their fit, fallbacks and every deviation from the draws.
"""
import re, argparse, hashlib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
cfg = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
def fail(m): sys.exit("assign: " + m)
def norm(s): return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()
def H(*k): return int(hashlib.sha256("|".join(map(str, k)).encode()).hexdigest(), 16)

def used_hit(text, pool):
    t = " " + norm(text) + " "
    return next((u for u in pool if " " + norm(u) + " " in t), None)

def check_candidates(path, app, U, osr=False):
    d = json.load(open(path, encoding="utf-8"))
    inv, rut, cs = d.get("inventory"), d.get("rut"), d.get("candidates")
    if not isinstance(inv, list) or len(inv) < 6 or not all(isinstance(i, dict) and i.get("item") for i in inv):
        fail('need "inventory": 6-10 items {"item", "group", "can_do"} (rule:subject-inventory)')
    if not isinstance(rut, dict) or not rut.get("category_default") or not rut.get("predictable_opposite"):
        fail('need "rut": {"category_default", "predictable_opposite"} (rule:name-the-rut)')
    if not isinstance(cs, list) or not 5 <= len(cs) <= 7: fail("need 5 to 7 candidates, ranked by resonance (#1 first)")
    need = ["id", "name", "family", "kind", "looks", "serves", "audience_sees", "literal", "operated_tool"]
    for c in cs:
        miss = [k for k in need if c.get(k) in (None, "")]
        if miss: fail(f"candidate {c.get('id', '?')} missing {miss}")
        if "job_cue" not in c or "from_inventory" not in c: fail(f"candidate {c['id']} needs job_cue and from_inventory (may be empty strings) (rule:job-cue)")
        if c.get("scale") not in ("object", "page"): fail(f'candidate {c["id"]} needs "scale": "object" or "page" (rule:scale)')
        for r in (rut["category_default"], rut["predictable_opposite"]):
            if norm(c["name"]) and (norm(c["name"]) in norm(r) or norm(r) in norm(c["name"])): fail(f'candidate {c["id"]} restates the rut')
    if len({norm(c["family"]) for c in cs}) < 3: fail("need at least 3 material families")
    if sum(c["kind"] == "graphic" for c in cs) < 2: fail('need at least 2 candidates of kind "graphic"')
    if sum(c["literal"] is True for c in cs) > 1: fail("at most one literal candidate")
    if app and any(c["operated_tool"] is True for c in cs): fail("app pages: no candidate may be the tool the user operates")
    if osr and len(eligible(cs)) < 2: fail("operate, read and transact pages need at least 2 candidates ranked #3 or lower with scale \"object\" and a job_cue (rule:scale, rule:object-on-structure)")
    return d, hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()

OSR = ("operate", "read", "transact")
def eligible(cs, exclude=()):
    # V4.14 rule:object-decides: an object whose job is a stock or urgency count is not eligible
    urgent = re.compile(r"\b(left|remaining|in stock|stock count|sells? out|selling fast|hurry|only \d|scarcity|countdown)\b", re.I)
    return [i for i in range(3, len(cs) + 1) if cs[i - 1].get("scale") == "object" and str(cs[i - 1].get("job_cue", "")).strip()
            and not urgent.search(str(cs[i - 1].get("job_cue", ""))) and i not in exclude]
def roll_object(cs, key, exclude=()):
    ok = eligible(cs, exclude) or eligible(cs)
    return [sorted(ok, key=lambda i: H(key, i))[0]]
def shortlist_icon(cs, key, exclude=()):
    rest = sorted([i for i in range(2, len(cs) + 1) if i not in exclude], key=lambda i: H(key, i))[:2]
    return [1] + rest

def shortlist(cs, key, exclude=()):
    ok = [i for i in range(2, len(cs) + 1) if str(cs[i - 1].get("job_cue", "")).strip() and i not in exclude]
    if len(ok) < 3: fail(f"only {len(ok)} of your candidates #2..#{len(cs)} have a job_cue; give at least 3 of them a cue that does a job on the page (rule:job-cue)")
    return sorted(ok, key=lambda i: H(key, i))[:3]

def weighted(dist, key):
    items = sorted(dist.items()); tot = sum(v for _, v in items) or 1
    x = (H(key) % 10000) / 10000 * tot
    for k, v in items:
        x -= v
        if x < 0: return k
    return items[-1][0]

PLACE = {   # rule:colour-level: where the colour goes, by page kind and drawn level
 "app": {"neutral": ["colour only in the content (charts, tags, status) and the primary action; white or black chrome"],
         "accent": ["a slim coloured header bar (48-72px)", "a coloured side rail", "coloured category tags and chart series on neutral chrome", "one tinted panel (filters or summary) beside white content"],
         "strong": ["a coloured header block holding the page title and key numbers (25-35% of the first screen)", "a coloured side rail plus a tinted summary strip"]},
 # V4.15 rule:shop-colour-place: real shop and booking homepages almost never open on a flat colour band (2 of 74 in the
 # reference library, both travel search sites); their first screen is a large picture. Colour lives in pictures and in small parts.
 "transact": {"neutral": ["colour from the products themselves: a large product or scene picture on the first screen, white or black chrome"],
              "accent": ["a large product or scene picture leads the first screen; the hue appears in the primary button, the selected filter and one slim promo line (one text line, at most 40px)",
                         "coloured category tiles or a coloured filter rail beside the catalogue; the first screen opens on pictures, not on a colour band"],
              "strong": ["product tiles on grounds tinted from the hue, chrome neutral", "one full-colour editorial block further down the page (a featured collection with its pictures), never a band above the catalogue"]},
 "show": {"neutral": ["the iconic image carries all colour on a white or black page"],
          "accent": ["the iconic image in colour plus one coloured band or block", "a coloured headline area beside a neutral image area"],
          "strong": ["a coloured ground across the first screen", "a full-bleed coloured image or data field"]}}
IMG_CATS = {"hardware", "travel", "hospitality", "food", "restaurants", "furniture", "fashion", "beauty", "real_estate", "museum", "film", "photography", "pets", "bookstores", "architecture"}
LOUD = {"games", "food", "studio", "type_foundry", "museum", "creative_tech"}
GROUND = {"white": ("white", "pure or near-white page; colour lives in content, actions and at most one field"),
          "dark": ("black", "near-black page (or --scene deep for a deep navy, forest or plum ground when the tone calls for it)"),
          "tinted": ("light", "a light ground with a hue cast from the direction"),
          "colour": ("light", "a saturated field carries the frame: --strategy committed or drenched")}
APP_GROUND = {"white": 0.75, "dark": 0.2, "tinted": 0.05}   # app interiors, not marketing homepages
ALL_CLASS = {"sans": 0.78, "serif": 0.19, "mono": 0.03}
def draw_type_corners(key, cat, S, F, R, mode="persuade", flow=False):
    p = R.get(cat)
    if not p: fail(f"unknown category {cat}; one of {sorted(R)}")
    p = dict(p)
    if p.get("n", 9) < 5:   # small samples: blend with all sites (rule:real-type)
        p["display_class"] = {k: round(0.5 * p["display_class"].get(k, 0) + 0.5 * v, 3) for k, v in ALL_CLASS.items()}
    if mode in ("operate", "read"):   # app screens: half category, half app-interior mix
        p["ground"] = {k: round(0.5 * p["ground"].get(k, 0) + 0.5 * APP_GROUND.get(k, 0), 3) for k in set(p["ground"]) | set(APP_GROUND)}
    cls = weighted(p["display_class"], (key, "class"))
    loud = cat in LOUD   # only categories whose real sites use display faces get one
    sub = {"sans": {"sans": 0.7, "display_sans": 0.3} if loud else {"sans": 1}, "serif": {"serif_sans": 0.85, "all_serif": 0.15}, "mono": {"mono_accent": 1}}[cls]
    g = weighted(p["ground"], (key, "ground"))
    level = weighted(p["colour_level"], (key, "level"))
    hue = weighted(p["hue"], (key, "hue"))
    if g in ("dark", "colour") and level == "neutral": level = "accent"
    place = PLACE[("app" if mode in ("operate", "read") or flow else mode if mode == "transact" else "show")][level]
    place = place[H(key, "place") % len(place)]
    st = {"ground": g, "colour_level": level, "hue_family": hue, "colour_place": place, "typeclass": weighted(sub, (key, "sub")),
          "containers": weighted(p["containers"], (key, "cont")), "controls": weighted(p["controls"], (key, "ctrl"))}
    for i in range(6):
        if any(all(st[q.split("=")[0]] == q.split("=")[1] for q in pr) for pr in S["forbidden_pairs"]):
            st["controls"] = weighted({k: v for k, v in p["controls"].items() if k != st["controls"]} or {"small": 1}, (key, "ctrl", i))
    pools = {"sans": ("sans_display", "sans_text"), "serif_sans": ("display_serif", "sans_text"), "slab_sans": ("slab", "sans_text"),
             "display_sans": ("display", "sans_text"), "all_serif": ("display_serif", "text_serif"), "mono_accent": ("sans_display", "sans_text")}
    dp, bp = pools[st["typeclass"]]
    st["fonts"] = {"display": F["pools"][dp][H(key, "fd") % len(F["pools"][dp])], "body": F["pools"][bp][H(key, "fb") % len(F["pools"][bp])]}
    if st["typeclass"] == "mono_accent": st["fonts"]["mono"] = F["pools"]["mono"][H(key, "fm") % len(F["pools"]["mono"])]
    st["premium"] = premium(mode, flow)
    if st["premium"]:   # V4.16 rule:premium-type: refined display faces (Hallmark fonts.md classes), not the workhorse pools
        pd = PREMIUM_DISPLAY[st["typeclass"]]; pb = PREMIUM_BODY["serif" if st["typeclass"] == "all_serif" else "sans"]
        st["fonts"] = {"display": pd[H(key, "pfd") % len(pd)], "body": pb[H(key, "pfb") % len(pb)]}
        if st["fonts"]["body"] == st["fonts"]["display"]: st["fonts"]["body"] = pb[(H(key, "pfb") + 1) % len(pb)]
        post = POSTURES["transact" if mode == "transact" else "show"]
        st["posture"] = post[H(key, "posture") % len(post)]
        st["photo_treatment"] = TREATMENTS[H(key, "treat") % len(TREATMENTS)]
    return st

def premium(mode, flow):
    return mode in ("persuade", "experience") or (mode == "transact" and not flow)
# V4.16: faces from Hallmark references/fonts.md (classes the catalog does not over-use); (FS) = Fontshare, loaded from api.fontshare.com
PREMIUM_DISPLAY = {
    "sans": ["Rethink Sans", "Albert Sans", "Reddit Sans", "Satoshi (FS)", "General Sans (FS)", "Supreme (FS)", "Afacad", "Switzer (FS)"],
    "display_sans": ["Clash Display (FS)", "Clash Grotesk (FS)", "Antonio", "Big Shoulders Display", "League Spartan", "Tektur"],
    "serif_sans": ["EB Garamond", "Gloock", "Libre Bodoni", "Castoro", "Cardo", "Besley", "Gambetta (FS)", "Erode (FS)", "Marcellus"],
    "all_serif": ["EB Garamond", "Libre Bodoni", "Castoro", "Cardo", "Gambetta (FS)", "Piazzolla"],
    "slab_sans": ["Hepta Slab", "Solway", "Domine", "Bespoke Slab (FS)"],
    "mono_accent": ["Rethink Sans", "Albert Sans", "Satoshi (FS)", "General Sans (FS)"],
}
PREMIUM_BODY = {"sans": ["Hanken Grotesk", "Figtree", "Onest", "Sofia Sans", "Golos Text", "Karla", "Albert Sans", "Switzer (FS)", "General Sans (FS)", "Satoshi (FS)"],
                "serif": ["Newsreader", "Source Serif 4", "Literata", "Spectral"]}
POSTURES = {"show": ["Poster", "Stage", "Ledge", "Corridor", "Poster", "Stage"], "transact": ["Stage", "Counter", "Poster", "Index", "Stage"]}
POSTURE_TXT = {
    "Poster": "a full-bleed photograph or key-art canvas filling 92-100% of the screen; the head on its calmest part, low-left or centred, over a scrim from the ink (35-65%, behind the text side only)",
    "Stage": "text on five columns, one big visual on seven at 60-75% of the screen tall (it may bleed off the outer edge); text and visual centred on each other",
    "Ledge": "a tall picture field above, the head resting large at its base, the lead and action beside it",
    "Corridor": "one centred column of 44ch or less with the head larger than usual (110-140px), a single full-width picture starting just under the fold edge",
    "Counter": "the buy box or booking control is the visual: the product photograph large with its options, price and action beside it, under a shorter head",
    "Index": "the list is the visual: the lead products/rooms/dates set large as the first screen with the head small above it",
}
TREATMENTS = ["natural", "warm", "muted", "mono", "duotone"]
TREAT_CSS = {"natural": "filter: contrast(1.03) saturate(.95)", "warm": "filter: sepia(.12) saturate(.9) contrast(1.04) brightness(1.01)",
             "muted": "filter: saturate(.7) contrast(.96) brightness(1.03)", "mono": "filter: grayscale(1) contrast(1.08)",
             "duotone": "filter: grayscale(1) contrast(1.1); mix-blend-mode: multiply over a slot background in your hue (or a ::after overlay in the hue at 40-60% with mix-blend-mode: screen on dark grounds)"}

NAV_SURF = {"light_plain": "the page ground with no bottom line or shadow (separation by space only)",
            "light_line": "the page ground with one hairline under it",
            "dark": "a dark bar (near-black or the deep end of your hue), light text",
            "colour": "a bar in your field colour, text in its on-colour",
            "over_image": "transparent, laid over the opening image or colour field; text in the field's on-colour (turn solid only after scrolling past the hero)"}
NAV_LAY = {"links_right": "logo left, 4-7 links grouped at the right before any action",
           "links_left": "logo left with the links right after it (left-aligned group); actions alone at the far right",
           "links_centre": "logo left, links centred in the bar, actions right",
           "logo_centre": "logo centred; links split or on the left, utilities (search, account, bag) on the right",
           "logo_and_menu": "logo and a single Menu control (word, not just an icon) plus at most one action; the rest of the navigation opens in a full panel"}
NAV_H = {"compact": "about 48-56px", "regular": "about 60-80px", "tall": "about 90-120px, or two rows (main row plus a row of sections)"}
def draw_nav(key, cat, mode, views=None, records=None, search=None):
    N = json.load(open(os.path.join(ROOT, "config", "nav_profiles.json")))
    p = json.loads(json.dumps(N.get(cat) or N["_all"]))
    # V4.16.1 rule:nav-scale: options the content cannot use do not enter the draw
    dropped = []
    if views is not None and views <= 5:
        if p["layout"].pop("logo_and_menu", None): dropped.append("menu-button layout (needs 6+ destinations)")
        if p["height"].pop("tall", None): dropped.append("tall or two-row bar (needs a row of sections)")
    if search is False or (search is None and records is not None and records < 50):
        p["search_box"] = 0; dropped.append("visible search field (" + ("no free-text lookup in the brief" if search is False else f"only about {records} records") + ")")
    if views is not None and views <= 5: p["links_median"] = min(p["links_median"], views)
    d = {"surface": weighted(p["surface"], (key, "nav_s")), "layout": weighted(p["layout"], (key, "nav_l")),
         "height": weighted(p["height"], (key, "nav_h")), "case": weighted(p["case"], (key, "nav_c")),
         "promo_bar": (H(key, "nav_p") % 100) < 60 * p["promo_bar"], "search_box": (H(key, "nav_q") % 100) < 100 * p["search_box"],
         "cta_button": (H(key, "nav_b") % 100) < 100 * p["cta_button"], "links": int(p["links_median"]), "link_px": int(p["link_px"])}
    if mode not in ("persuade", "experience") and d["surface"] == "over_image": d["surface"] = "light_plain"
    if search is True: d["search_box"] = True
    d["dropped"] = dropped
    return d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates"); ap.add_argument("--task"); ap.add_argument("--mode"); ap.add_argument("--seed"); ap.add_argument("--category")
    ap.add_argument("--type", choices=["landing", "app"]); ap.add_argument("--state", default="assign_state.json")
    ap.add_argument("--flow", action="store_true", help="transact page whose main job is a multi-step form or booking"); ap.add_argument("--veto"); ap.add_argument("--check-name"); ap.add_argument("--brief", help="brief text or file, for the reference picker")
    # V4.16.1 rule:nav-scale: the content's scale, so the navigation draw only offers what this page can use
    ap.add_argument("--views", type=int, help="how many top-level views or sections the page has")
    ap.add_argument("--records", type=int, help="about how many records or items a user scans (orders, products, notes)")
    ap.add_argument("--search", choices=["yes", "no"], help="does the user need free-text search?")
    a = ap.parse_args()
    S, F, U, R = cfg("config/structure.json"), cfg("config/fonts.json"), cfg("config/used.json"), cfg("config/real_profiles.json")
    if a.check_name:
        hit = used_hit(a.check_name, U["names"])
        print(f'name "{a.check_name}": ' + (f'REFUSED, already used for another page ("{hit}"). Pick another.' if hit else "ok")); return
    if a.task:
        T = cfg("evals/tasks.json")["tasks"]
        if a.task not in T: fail(f"unknown task {a.task}")
        x = T[a.task]; mode, typ, cat, key = x["mode"], x["type"], x["category"], "task|" + a.task; flow = bool(x.get("flow"))
    else:
        if not (a.mode and a.seed and a.category): fail("give --task, or --mode, --category and --seed")
        mode, typ, cat, key = a.mode, a.type or ("app" if a.mode == "operate" else "landing"), a.category, "seed|" + a.seed; flow = a.flow
    if mode not in S["modes"]: fail(f"mode must be one of {list(S['modes'])}")
    flow = flow or (mode == "transact" and cat == "government")   # rule:no-object-in-flows (V4.12)
    noobj = mode == "operate" or flow
    if not a.candidates and not noobj: fail("give --candidates")
    flow = flow or (mode == "transact" and cat == "government")
    st = draw_type_corners(key, cat, S, F, R, mode, flow)
    st["nav"] = draw_nav(key, cat, mode, a.views, a.records, None if a.search is None else a.search == "yes")
    brief = a.brief or (os.path.join(HERE, "..", "evals", "briefs", f"{a.task}.txt") if a.task else "")
    brief = open(brief).read() if brief and os.path.exists(brief) else (brief or "")
    try:
        import refs as RF
        rr, types = RF.pick(mode, cat, brief, key, 4, flow=flow)
    except Exception:
        RF, rr, types = None, [], []
    anchor = rr[0] if (mode == "operate" and rr and rr[0].get("is_anchor")) else None
    need_live = (mode == "operate" and not anchor) and ((rr[0].get("need_live") if rr else None) or (types[0] if types else "tool"))
    rr = [x for x in rr if x.get("img")]
    if anchor:   # rule:anchor: the app screen sets the ground and where colour sits; the hue family stays drawn
        st["ground"] = {"white": "white", "light": "white", "dark": "dark"}.get(anchor["ground"], st["ground"])
        if st["ground"] == "dark" and st["colour_level"] == "neutral": st["colour_level"] = "accent"
        st["colour_place"] = f"where the anchor screen ({anchor['host']}) puts it: the same rail, header, tabs, chips or charts, at about the same amount"
        st["anchor"] = anchor["img"]
    if noobj:   # rule:no-object-in-tools (V4.11), rule:no-object-in-flows (V4.12): no metaphor object
        cs, sl = [], []
        json.dump({"mode": mode, "category": cat, "assigned": st, "object": None}, open(a.state, "w"), indent=2)
    else:
        d, sha = check_candidates(a.candidates, typ == "app", U, osr=mode in OSR)
        cs = d["candidates"]
        state = json.load(open(a.state)) if os.path.exists(a.state) else None
        if state and state["candidates_sha256"] != sha: fail("candidates changed after the shortlist was revealed")
        pick = roll_object if mode in OSR else shortlist_icon
        if state and a.veto:
            if state.get("vetoed"): fail("only one veto")
            sl = pick(cs, key + "|veto", exclude=tuple(state["shortlist"]) if mode in OSR else tuple(state["shortlist"][1:]))
            state["vetoed"] = {"shortlist": state["shortlist"], "reason": a.veto}
        elif a.veto: fail("veto only after a first run")
        else: sl = state["shortlist"] if state else pick(cs, key + "|" + sha[:12])
        if state and state.get("vetoed") and not a.veto: sl = state["shortlist"]
        json.dump({"candidates_sha256": sha, "shortlist": sl, "mode": mode, "category": cat, "assigned": st,
                   **({"vetoed": state["vetoed"]} if state and state.get("vetoed") else {})}, open(a.state, "w"), indent=2)
    M = S["modes"][mode]; A = S["assigned"]; p = R[cat]
    out = {"mode": mode, "mode_for": M["for"], "category": cat,
           "shortlist": [{"rank": i, **{k: cs[i - 1][k] for k in ("id", "name", "job_cue", "audience_sees")}} for i in sl],
           "assigned": {**st, "containers_px": A["containers"]["px"][st["containers"]], "controls_px": A["controls"]["px"][st["controls"]]},
           "ground_from_real_sites": {"drawn": st["ground"], "scene": GROUND[st["ground"]][0], "means": GROUND[st["ground"]][1], "category_mix": p["ground"]},
           "type_size_from_real_sites": {"display_px": p["display_px"], "body_px": max(16, p["body_px"])},
           "you_choose": {"scene": ["white", "light", "mid", "black", "deep", "dark"], "colour_strategy": {k: S["colour_strategies"][k] for k in M["colour"]},
                          "headline": {k: S["headlines"][k] for k in M["headline"]}}}
    osr = mode in OSR
    big = min(120, round(p["display_px"] * 2.2)) if not osr else p["display_px"]
    out["type_size"] = {"display_px": big, "body_px": max(16, p["body_px"]), "note": "real-site median" if osr else "2-3x the real-site median: brand and story pages open big"}
    del out["type_size_from_real_sites"]
    if noobj: out.pop("shortlist"); out["built"] = ("the standard working screen of the best real product of this kind; no metaphor object (rule:no-object-in-tools)" if mode == "operate" else "the standard flow of the best real service of this kind; no metaphor object (rule:no-object-in-flows)")
    else: out["built" if osr else "shortlist"] = out.pop("shortlist") if not osr else out.pop("shortlist")[0]
    print(json.dumps(out, indent=2, ensure_ascii=False))
    f = st["fonts"]; Rt = ROOT
    if mode == "operate":
        head = f"""BUILD the standard working screen of the best real product of this kind (rule:no-object-in-tools).
        NO METAPHOR OBJECT: no stamps, slips, tags, tickets, lanyards, pins, postmarks or other props borrowed from another
        world, and no costume. Real products of this kind do not have them. The page is memorable through what real
        products do well: the right panes and density, real-looking content, clear states, good keyboard and empty states,
        and the type and colour drawn below. A mark is allowed only if real products of this kind use it (a label chip, a
        status dot, a progress ring, an avatar) and only in its ordinary form.
        IMAGES AS DATA (rule:image-as-data): the ban is on decoration, not on pictures. A picture of what a record IS (the
        cake on an order, the photo in a library, the dish on a menu, the room in a booking, the product in stock) is
        content: show it small on rows and larger in the detail view. A picture that stands for nothing in the data
        (a scene, an illustration, a prop) is decoration and stays out.
NEXT 1  write the contract into meta.json (direction.md step 5, with STRUCTURE and BORROW from categories.md "{cat}";
        OBJECT: none). Name the page and run: python3 {HERE}/assign.py --check-name '<name>'"""
    elif osr and not flow:
        c = cs[sl[0] - 1]
        head = f"""BUILD candidate #{sl[0]}: "{c['name']}" (scale object). Its object lives where it really exists on that component (a label, tag, base, edge or receipt line; rule:object-host):
        "{c['job_cue']}".
        OBJECT RULES (V4.14): never float it over a product picture or cover the product; on cards that repeat it is quiet
        (ink or neutral colour, no accent, a small strip or corner, at most about 1/12 of the card) and shows decision
        facts (material, size, origin, condition, time), never a stock or urgency count; the accent stays for the primary
        action; it must be true for every kind of item on the page; text on it is 12px+, never on a curved path.
        It may be full-size and coloured in one place only: the detail view or the selected state (rule:object-quiet). The structure, navigation and main controls stay the category's standard (modes.md "{mode}").
        Keep it unless it factually cannot do that job; then run once more with --veto "reason" (taste is not a reason).
NEXT 1  write the contract into meta.json (direction.md step 5, with STRUCTURE and BORROW from categories.md "{cat}").
        Name the page and run: python3 {HERE}/assign.py --check-name '<name>'"""
    elif flow:
        head = f"""BUILD the standard flow of the best real service of this kind (rule:no-object-in-flows, modes.md "Flows").
        NO METAPHOR OBJECT: no stamps, slips, tickets, coded step tiles or props. Brand or official bar, breadcrumbs or a
        back link, the form in one calm column (560-720px), an aside with what you need and how to get help. Progress as
        text ("Step 2 of 6 · Your details") with a thin bar; step names in plain words. On a phone the step row fits or
        shows only the current step.
NEXT 1  write the contract into meta.json (direction.md step 5, with STRUCTURE and BORROW from categories.md "{cat}";
        OBJECT: none). Name the page and run: python3 {HERE}/assign.py --check-name '<name>'"""
    else:
        head = f"""SHORTLIST #{', #'.join(map(str, sl))} (your #1, the most recognisable image, is included on purpose).
NEXT 1  direction.md step 4: three-line contract for each, score icon, atmosphere, fit 1-3, build the highest (person present: they pick).
        Record "shortlist" and "picked" in meta.json. Then the full contract (step 5, with STRUCTURE and BORROW from
        categories.md "{cat}"). Name the page and run: python3 {HERE}/assign.py --check-name '<name>'"""
    refs_txt = ("\n".join(f"        {RF.LIB}/{x['img']}  {x['host']} ({'ANCHOR, ' if anchor and x is anchor else ''}{'homepage' if x['lib'] == 'home' else 'app screen: ' + x['key']})" for x in rr)
                if rr else "        (no local library here; use categories.md alone)")
    anchor_txt = (f"""
        ANCHOR (rule:anchor): the first screen is the structure model for this tool. Follow its skeleton closely: which panes
        exist and their rough widths, where navigation and the main action sit, how dense rows and cells are, and where colour
        sits and how much of it (the ground above already follows it). Write what you took into STRUCTURE.
        BORROW LAYERS (rule:borrow-layers): take STRUCTURE from the anchor (panes, widths, where navigation and actions sit,
        row density, how much colour). Take nothing of its SURFACE: its selected-state treatment (an edge bar, a pill, an
        underline), tag and label colours, icon set, brand hue, wordmark and copy are that product's own language. Derive
        SURFACE from the subject's own world (the business's sign, packaging, materials, its own states) and write it in
        the contract's SURFACE line, separately from STRUCTURE.
        FIT CHECK (rule:anchor-fit, rule:ref-fit), before you follow it: open it and write meta.json "ref_fit":
        {"ref": file or URL, "page_kind": working_ui | marketing | article | obstructed | logged_out,
         "same_user": yes/no + why, "same_task": yes/no + why, "same_data": yes/no + why}. It passes only as a working
        screen with same_task and same_data both yes. Would a regular user of the brief's product say "yes, this is the
        same kind of product", not merely the same broad family? It FAILS when it is a marketing, pricing, checkout or docs
        page instead of the working screen; when it does a different job (a spreadsheet for a photo organiser, a code editor
        for a household app); or when it is a generic template (an admin kit, a UI demo) while products of this kind have a
        layout of their own. If it fails, do not follow it: run NEXT 1c below (live search) and use the screen you capture there as ANCHOR; write `anchor_fit: fail` and why in meta.json.""" if anchor else "")
    head += f"""
NEXT 1b real references (rule:refs): open each with the Read tool before the contract, and write what you took into BORROW.
{refs_txt}{anchor_txt}
        Take conventions only: where navigation and the main controls sit, density, where colour sits, corner and border
        habits, how much imagery. Never a logo, copy text, exact colours or a whole layout.
        SAMPLE CONTENT (rule:honest-sample): fill the page with what a real user would have on an ordinary day. Alarm states
        (a clash, an overdue card, an error) appear once or twice, never staged, and never over text."""
    if osr and not noobj:
        head += """
        OBJECT ON THE FIRST SCREEN (rule:object-visible): the object must be seen without scrolling. If it belongs to a repeated
        item (a card, row, event, post), every item carries it in its ordinary state; do not hide it in one column or one view."""
    if need_live or anchor:
        live_kind = need_live or (anchor.get("key") if anchor else "tool")
        head += f"""
NEXT 1c {"NO ANCHOR in the library" if need_live else "ONLY IF the FIT CHECK failed: no fitting anchor"} for a "{live_kind}" screen (rule:live-anchor). Find one on the web before the contract:
        WebSearch for 3-5 real, current products of this kind whose working screen is public without logging in (a public
        board, a public feed, a public profile, a demo instance; not a marketing homepage, not a login wall). Screenshot the 2-3
        best with: python3 {Rt}/scripts/shoot_ref.py <url> {live_kind}
        It refuses blank, blocked and login pages and saves usable ones into the library. Read them, pick the one closest to
        the job as ANCHOR (follow its skeleton as in rule:anchor), and record `anchor` and `live_refs` in meta.json. If none
        is usable after 5 tries, build from categories.md and say so in meta.json.
        shoot_ref.py prints the PAGE KIND; only a working_ui capture can be the anchor, and it still needs meta.json "ref_fit"
        {{"ref", "page_kind", "same_user", "same_task", "same_data"}} (rule:ref-fit): anchor only with same_task and same_data yes.
        Do not fill the slot with a different kind of product to have something to follow.
        FALLBACK (rule:ref-fallback): when the real products of this kind need a login (order back offices, POS, booking
        books, clinic systems, internal tools) and no public working screen passes ref_fit, stop searching: build the
        STRUCTURE from categories.md "{cat}" and modes.md "{mode}" alone, write "ref_fallback": "<why>" in meta.json,
        and say it in the final report (NEXT 6)."""
    IMG = ("""
        PICTURES: see NEXT 3c PREMIUM below (photos.py library, one treatment, big or not at all).""" if st.get("premium") else "") + ("""
        PICTURES (rule:atmospheric-imagery, rule:photo-library): """ + ("first look in the photo library (python3 " + HERE + "/photos.py '<subject>'; it lists file, author, licence, source) and use real photographs that fit your items, embedded as data URIs and credited in one footer line; " if mode == "transact" else "") + """where no photo fits, each item's picture is its own drawn scene (SVG or canvas) with light, depth and 3+
        colours from its setting, different per item; never one pictogram or line icon repeated across cards.""" if cat in IMG_CATS and mode != "operate" and not st.get("premium") else "")
    PREM = ""
    if st.get("premium"):
        PREM = f"""
        (FS) faces load from Fontshare: <link href="https://api.fontshare.com/v2/css?f[]=<name-lowercase-hyphenated>@400,500,700&display=swap" rel="stylesheet">; the rest from Google Fonts.
NEXT 3c PREMIUM (rule:premium, V4.16; adapted from Hallmark layout.md, imagery.md, review-hero.md). This page is judged on how made it looks.
        HERO posture: {st['posture']} = {POSTURE_TXT[st['posture']]}.
          The first screen holds the nav, the head (7 words or fewer), ONE lead sentence, one or two actions, and the visual. Nothing else:
          no label or pill above the head, no stat row, no chips, no filters, no badges, no second paragraph. The object (if any) may
          appear on the visual or just under the fold, not as extra chrome.
        SCALE at 1440: hero head 84-120px (a long head 64px), section heads 48-60px, item titles 24-28px, lead 20-22px, body 16-18px.
          Display letter-spacing -0.01 to -0.03em, line-height 0.95-1.1. A section head under 40px is the commonest reason a page looks unfinished.
        CANVAS and RHYTHM: one centred container 1312px wide (64px gutters) on 12 columns; sections 120-176px apart, mixed;
          6-9 sections; every screen holds ONE idea at the right size. A dense section (grid, table) is followed by a quiet one
          (a statement, a single big picture). Never the same composition twice in a row; never head-then-three-cards three times.
        RESTRAINT: separate by space, not boxes; hairlines over borders; no card shadows; at most two button looks; at most one
          accent colour, used on under 5% of the page (a full field of colour at most once, as a band or poster).
        PICTURES: big or not at all: a picture spans 6+ of 12 columns and stands 440px+ tall, or runs full-bleed; at thumbnail size it reads
          as clip art (a set of 4+ products may run smaller, each with its facts). Delete-test: remove the hero picture in your head; if the
          screen still says the same thing, the picture is too weak or too small.
          Source: python3 {HERE}/photos.py "<subject words>" [--tone light|dark] [--temp warm|cool|neutral] [--n 8] ranks the offline library
          (755 Wikimedia photos from Hallmark, tagged, licensed). View candidates with Read, keep only on-subject ones, all from the
          same temperature and tone, and embed them as data URIs. Credit each in one footer line (author, licence).
          Treatment for EVERY photo on the page: {st['photo_treatment']} ({TREAT_CSS[st['photo_treatment']]}). One treatment, the whole page.
          Drawn pictures: only when the subject is fictional (a game world, a film's world, a dream) and then as full-bleed key art with
          light, depth and atmosphere; never a small drawn object, plant, product or person as a card picture (Hallmark rule 80).
          No product pictures in the library? Set the product large in type and real data (name, notes, price) over a treated scene
          photograph of its material or place, rather than a weak or off-subject picture.
        SERIF and ITALIC: a serif display face and one italic phrase in the head are allowed here when the display face has a real
          italic; never on a cream ground with a rust accent (defaults.md 1).
        FIRST SCREEN CHECK: on these pages run check.py with --primary "<the hero's main action>" --premium (no --core): the
          catalogue, the form or the schedule may start under the fold, as on the best real sites."""
    print(f"""
{head}
NEXT 2  colour (drawn from real {cat} sites; rule:colour-level): ground {st['ground']} -> --scene {GROUND[st['ground']][0]};
        colour level {st['colour_level']}; hue family {st['hue_family']}; placement: {st['colour_place']}.
        Find the hue inside the {st['hue_family']} family in your direction's materials (or its nearest neighbour) and name
        the source in HUE. Use --strategy restrained for neutral, committed for accent and strong. You may change one of
        these once if the brief clearly calls for it (write why in FORM).
        tokens: python3 {HERE}/palette.py --brand <hue from the direction that fits the tone> --scene <scene> --strategy <{'|'.join(M['colour'])}>
        Use its output as CSS variables; if it prints a WARNING, change the hue or scene and run it again,
        or keep it and write the HUE source in the contract (a hue with a named source is allowed).
        COLOUR AREA (rule:colour-area): {"no flat colour block over about a third of the first screen; colour beyond that comes from the content." if osr else "the confident ground is allowed here (persuade / experience)."}{" SHOPS (rule:shop-colour-place): no full-width flat colour band holding only a headline and a button; a band, if any, holds pictures or products. The accent colour of the primary button is not also the colour of a large block." if mode == "transact" else ""}{IMG}
NEXT 3  faces: display {f['display']} / body {f['body']}{(' / mono ' + f['mono']) if f.get('mono') else ''} ({'Google Fonts; (FS) = Fontshare' if st.get('premium') else 'Google Fonts'}). Navigation, buttons and labels
        use the body face; the display face is for headlines and may letter the wordmark.
        Corners: containers {st['containers']} ({out['assigned']['containers_px']}), controls {st['controls']} ({out['assigned']['controls_px']}); media square unless containers are large.
        Type size: {"see SCALE in NEXT 3c (premium page)" if st.get("premium") else f"display about {big}px over body {max(16, p['body_px'])}px ({out['type_size']['note']})"}.{PREM}
NEXT 3b navigation (rule:real-nav, rule:nav-scale; {'APP BAR, not a website nav: copy the ANCHOR screen (or, with no anchor, the standard structure in categories.md). One slim row with the product name and the tool controls the job needs (search, primary action, account, at most one segmented view switch); NO row of text links in the bar at all, not even links to the app’s own views. Views and sections live in a side rail or a tab row inside the work area, as on the anchor.' if (anchor or mode == 'operate') else 'drawn from real ' + cat + ' sites'}):
        {'' if (anchor or mode == 'operate') else 'surface: ' + NAV_SURF[st['nav']['surface']] + '. layout: ' + NAV_LAY[st['nav']['layout']] + '. height: ' + NAV_H[st['nav']['height']] + '.'}
        {'' if (anchor or mode == 'operate') else ('links: inside the menu panel; in the bar at ' if st['nav']['layout'] == 'logo_and_menu' else 'links: about ' + str(st['nav']['links']) + ' at ') + str(st['nav']['link_px']) + 'px, ' + ('UPPERCASE, tracked' if st['nav']['case'] == 'upper' else 'normal case') + '; ' + ('a thin promo or notice strip above it' if st['nav']['promo_bar'] else 'no strip above it') + '; ' + ('a visible search field' if st['nav']['search_box'] else 'search as one control or none') + '; ' + ('one filled action button' if st['nav']['cta_button'] else 'no filled button in the bar') + '.'}
        {('Dropped before the draw for this content scale: ' + '; '.join(st['nav']['dropped']) + '.') if st['nav'].get('dropped') else ''}
        SCALE (rule:nav-scale): {'' if (a.views is not None or a.records is not None or a.search) else 'you did not pass --views/--records/--search, so: '}a Menu button needs 6+ destinations, a visible search field needs
        50+ records or real free-text lookup, a tall or two-row bar needs a row of sections. If the draw gives you one of these and
        the page cannot use it, leave it out and list it in meta.json "nav_dropped" (one line, no essay); better, rerun with
        --views N --records N --search yes|no before you build.
        Wordmark: lettered through the face itself (weight, width, case, spacing, a ligature or a cut), not a generic app
        icon in a rounded square next to plain text, and with no ornament stuck on: no coloured dot or full stop after the
        name, no tick, bar, dashed perforation, superscript box, and no split: the whole name in ONE weight and ONE colour
        (not Kettle Lane + bold Books, not Stripe + italic by + Stripe) (defaults.md 11). Bans (defaults.md 11): count badges that show 0, a grey
        descriptor after the name ("Name  Short tagline"), an outlined + filled button pair, a "sample data / saved in this
        browser" note in the bar, and the stock 64px white bar with a 1px grey line unless that is what was drawn.
NEXT 4  build with {Rt}/references/craft.md. One dominant move; everything else quiet. Separate by space and ground, not by boxes and lines.
NEXT 5  check pass, only now: read {Rt}/references/review.md and {Rt}/references/defaults.md, screenshot 1440x900 and 375x812
        with REAL FONTS (rule:real-fonts-in-shots: import sys; sys.path.insert(0, "{HERE}"); import fontroute; fontroute.attach(context)
        or await fontroute.attach_async(context) before page.goto; never abort font requests),
        run python3 {HERE}/check.py <index.html>, and list up to 8 fixes ordered by harm, including deletions (review.md section 2).
        Make them in your one fix pass, then run check.py once more (script only, no new screenshots) and fix anything it still prints.
        check.py also checks the default looks it can measure (accent edge bars on any block, identical card rows, dotted meta
        strings, tracked caps labels above heads); fix those like any other finding. Pages that need a server: run the app and
        pass --url http://localhost:PORT/... instead of a file. Real data from the brief (not invented): add --real-data.
NEXT 6  final report in the chat (rule:final-report), not only in meta.json. End your last message with:
        - References: each file or URL you used, its page kind, and ref_fit (same user / task / data); or "none: fallback, <why>".
        - Structure from the reference / surface from the subject: one line each.
        - Deviations: every drawn value or printed rule you did not follow (ground, faces, corners, nav items, colour place,
          a check.py finding left in place), each with its reason in a few words. "None" if none.
        - check.py: what it still prints, or "nothing found".""")

if __name__ == "__main__": main()
