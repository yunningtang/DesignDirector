# Design Director V4.16 (Claude skill)

A Claude skill for building or redesigning a web page with no strict brand spec. You give it a brief (a landing page, a shop, a dashboard, a lesson, a booking flow), and it works through a fixed method:

1. Decide the page's **mode**. What does a visitor do here: operate, read, transact, persuade or experience?
2. Pick the nearest **category** of real sites.
3. Let a script set the ground, faces, corners, navigation and colour level from data on real sites.
4. Write the copy first, then build the page.
5. Run one check pass with a screenshot-based checker, then a deletion pass.

V4.16 adds a **premium tier** for brand, story, experience and shop landing pages. It uses Hallmark's scale and rhythm, hero postures, a tagged photo library, refined faces and a first-screen check, so those pages read as made rather than templated. Tool, form and flow pages are unchanged from V4.15.

Use `SKILL.md` as the entry point, and see `CHANGELOG.md` for why each rule exists.

## Install

Copy this folder into your skills folder, for example `~/.claude/skills/design-director/`, or upload it as a skill in Claude.

The scripts need:

- Python 3.10+
- `pip install pillow playwright`, then `playwright install chromium`
- `curl`
- Node/npm, if you want real Google Fonts in screenshots. `scripts/fontroute.py` installs `@fontsource` packages on demand into `~/.cache/dd-fontkit`; set `FONTKIT` to change that location.

## Layout

```
SKILL.md                 entry point (steps, who decides what)
references/              modes, categories (real-site profiles), scenes, locale, direction, craft, review, defaults
config/                  real-site profiles, faces, nav profiles, structure, used-direction pool
scripts/assign.py        draws mode-specific ground/faces/corners/nav and prints the NEXT steps
scripts/palette.py       colour tokens with contrast checks
scripts/check.py         screenshot checks (first-screen task, overflow, focus, 320px, --premium scale checks)
scripts/photos.py        ranks the offline photo library for a subject
scripts/fetch_photos.py  builds the offline photo library (see below)
scripts/fontroute.py     serves Google Fonts to Playwright from @fontsource
scripts/refs.py          picks real reference screenshots from a local library (optional)
evals/                   the 70 benchmark tasks (tasks.json + briefs/)
data/                    Hallmark photo list (metadata only) and its MIT licence
```

## Photo library (optional, recommended)

The premium tier works best with real photographs. To build the library, run:

```bash
python3 scripts/fetch_photos.py              # all 755 photos, about 40 MB, slow because of Wikimedia rate limits
python3 scripts/fetch_photos.py coffee bread # photos matching your subjects first
```

The script writes to `data/photolib2/`, which git ignores. Every photo keeps its own Wikimedia licence: CC0, public domain, CC BY or CC BY-SA. `photos.py` prints the credit line to put in the page footer.

## Reference screenshots (optional)

`scripts/refs.py` can show 3–5 real-site screenshots per page from a local library in `data/refimg/` (or `$DD_REFS`). The library isn't included because the screenshots are of other people's sites. Without it, `assign.py` says so and the skill works from `references/categories.md` alone.

## Benchmark use

`assign.py --task <slug>` reads the matching brief in `evals/briefs/`. For your own pages, use:

```bash
python3 scripts/assign.py --candidates candidates.json --mode persuade --category food --seed my-page
```

## Credits

The premium tier is adapted from **Hallmark** (MIT, see `data/HALLMARK_LICENSE`). That covers its layout scale and hero postures, the imagery rules and photo list, the font classes, and the hero review questions.
