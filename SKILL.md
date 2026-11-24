---
name: design-director
description: Use when building or redesigning a web page, landing page, store, dashboard, lesson or app screen with no strict brand spec. Builds tools, forms and bookings as the best real product or service of their kind with no decoration borrowed from another world, lessons and shops with one small, quiet object from the subject where it really sits on one component, and brand and story pages around the subject's most recognisable image, large; real-site data sets ground, type and corners; colour tokens by script; copy written first, a craft check (first-screen task, sample labels, button family, focus, 320px) and a deletion pass. Not for one-line CSS fixes.
---

# Design Director V4.16.1

Goal: usable first, then memorable and fitting. Every rule has an id; why each exists is in CHANGELOG.md (for maintainers; you do not need to read it).

| Who decides | What |
|---|---|
| Mode (`references/modes.md`) | which of the two ways of building applies, the standard structure, how large type and colour may go |
| Category (`references/categories.md`) | how real sites of this kind are built: ground, colour tone, corners, type, conventions worth borrowing |
| Scene rules (`references/scenes.md`, `locale.md`) | behaviour and states |
| `scripts/assign.py` | which direction is built (tools, lessons, shops) or a shortlist of three (brand and story pages); ground, faces and corners |
| `scripts/palette.py` | every colour token, contrast, and warnings for known default palettes |
| You | the inventory, the candidates, the pick on brand and story pages, colour strategy, headline, imagery, copy, the build |

## Steps
1. **Brief** (into meta.json): page, users and context, one primary task, ≤3 secondary tasks, market, scene section. **Mode** <!-- rule:page-modes -->: what does a visitor do on this page? operate · read · transact · persuade · experience. **Category** <!-- rule:category -->: the nearest section of `references/categories.md`.
2. **Mode and scene**: read your section of `references/modes.md`, the matching section of `references/scenes.md`, and `locale.md` for the market.
3. **Category**: read only your section of `references/categories.md`. Note what to borrow and what not to borrow.
4. **Direction**: follow `references/direction.md` steps 1–3: the subject inventory, the rut, 5–7 ranked candidates with job cue and scale into `candidates.json`. **operate pages and flows skip this step** (rule:no-object-in-tools, rule:no-object-in-flows): tools, forms, applications, bookings and government services get no candidates and no object; run step 5 without `--candidates` (add `--flow` for a form or booking).
5. **Choose**: `python3 scripts/assign.py --candidates candidates.json --mode <mode> --category <key> --seed <any word>` (or `--task SLUG` in the benchmark). Then follow `references/direction.md` step 4 and **the NEXT lines the script prints**. <!-- rule:engine-prints-next --> On tool pages also pass the content's scale, so the navigation draw only offers what the page can use: `--views <top-level views> --records <about how many records> --search yes|no` (rule:nav-scale).
   **References** (rule:ref-kind, rule:ref-fit, rule:ref-fallback): `shoot_ref.py` prints each capture's page kind; only a `working_ui` screen can be the structure model, and only after you answer same user / same task / same data in meta.json `ref_fit`. When the real products need a login and nothing passes, build from `categories.md` alone and say so. Take STRUCTURE from a reference, never its SURFACE (rule:borrow-layers).

Method examples: `references/examples.md`. Copy the method, never their looks.
6. **Copy, build, check**: write the copy first (`references/craft.md`, rule:copy-first), build to `references/craft.md`, then at the check pass read `references/review.md` and run `python3 scripts/check.py index.html --primary "<css of the control that starts the primary task>" --core "<css of the working area>"` (premium pages: `--primary "<hero action>" --premium`). <!-- rule:first-screen-task --> An app that needs its server: run it and pass `--url http://localhost:PORT/...` instead of a file. Figures from the brief or a real source: add `--real-data`. check.py now also flags the measurable default looks (accent edge bars on any block, tracked caps labels above heads, dotted meta lines, identical icon card rows).
7. **Report** <!-- rule:final-report -->: end your last message in the chat (not only meta.json) with the references you used, their page kind and fit (or the fallback and why), one line each for structure-from-reference and surface-from-subject, every deviation from what assign.py drew or printed with its reason, and what check.py still prints.
