# V4.16.1 (2026-11-23)
From a user's report after building a bakery order board with V4.16: the problems were in how the layers hand over, not in single rules.
- **Reference layer.** "Same kind" was undefined and shoot_ref.py kept whatever it captured (a Todoist template gallery, Linear's changelog, a Trello board under a pop-up). rule:ref-kind: shoot_ref.py classifies each capture as working_ui / marketing / article / obstructed / logged_out and only working_ui can anchor (refs.py also ignores non-working captures as anchors). rule:ref-fit: before following a reference, answer same_user / same_task / same_data in meta.json. rule:ref-fallback: when the real products need a login (order back offices, POS, booking books), stop searching, build from categories.md and say so. New category smallbiz_ops (orders, bookings, inventory of one small business) instead of forcing such briefs into productivity; new app kind "orders".
- **Borrow layer.** Structure and surface were borrowed together (GitHub's rail-and-list structure arrived with its selected-item bar and coloured labels). rule:borrow-layers: STRUCTURE from the reference, SURFACE from the subject's own world, two separate contract lines.
- **Rule layer.** Bans written per object ("a stripe down one side of cards") were narrowed ("a nav item is not a card"). rule:pattern-not-element: defaults.md 8 rewritten as visual patterns on any element (the accent edge bar includes the selected nav item). rule:image-as-data: the tool-page ban is on decoration; pictures of what a record is (the cake on an order) are content.
- **Draw layer.** The nav draw offered a tall bar, a Menu button and a search field to an app with 3 views and a few dozen records. rule:nav-scale: assign.py --views / --records / --search drop options the content cannot use before drawing; tool pages without an anchor now also get the app-bar instruction, not a website nav.
- **Check layer.** check.py checked craft only, so the edge bar passed. It now measures the default looks it can (accent edge bar on any block, tracked caps label above a head, dotted meta lines, identical icon + heading + text rows; --no-style turns them off for benchmark scoring). False positives fixed: short labels ("Fits", "(2 h)") are no longer "squeezed" (a word must actually not fit its box); real figures can be declared with --real-data. --url checks a served app; the page's own origin and localhost now load (before, every non-file request was aborted, so apps with a backend always failed).
- **Report layer.** Deviations and failed references lived only in meta.json. rule:final-report: the last chat message lists references and their fit (or the fallback), structure/surface lines, every deviation from the draws, and check.py's remaining output.
- **Bugs:** shoot_ref.py crashed when data/refimg/index.json did not exist (fresh install); it now creates the library. modes.md still said operate pages carry "one object on one component" (stale since V4.11); fixed.

# V4.16 (2026-11-21)
From the user's question "why does it look conventional but not premium?" and a side-by-side with Hallmark:
- Diagnosis: V4.15 draws faces, grounds and colour place from real-site frequencies (the median site), its default-looks bans removed the usual premium devices with the AI ones, rule:first-screen-task packed persuade first screens with controls, faces were workhorse sans, pictures were small drawn scenes or mixed photos. Measured on 17: hero head 46px, section heads 31px, largest picture 8% of the first screen (baseline and Hallmark pass the same check).
- Also found: check.py and our measure.py aborted every font request, so every screenshot (ours and the comparison pages) showed fallback fonts.
- rule:premium (persuade, experience, shop/booking landing): Hallmark scale, canvas and rhythm; drawn hero posture; first-screen content budget; restraint.
- rule:premium-type: display/body faces from Hallmark's refined classes (incl. Fontshare).
- rule:premium-pictures: Hallmark's 755-photo tagged library offline (scripts/photos.py), one drawn treatment per page, big or not at all, no small drawn illustrations.
- check.py --premium: hero head size, section head size, largest first-screen picture share (not radar features).
- rule:real-fonts-in-shots: scripts/fontroute.py serves Google Fonts from npm @fontsource; check.py lets Fontshare through.

# V4.15 (2026-11-19)
From the user's question about the coloured band at the top of every V4.14 shop page (08 12 17 21 24):
- Cause: the transact colour placements were hand-written and both "accent" options asked for a band; rule:colour-area plus rule:first-screen-task squeezed the hero into a short band; no pictures were available (Wikimedia 429), so the band held only text.
- Evidence: 2 of 74 real shop/booking homepages in the reference library open on a flat colour band (trip.com, momondo); the rest open on pictures.
- rule:shop-colour-place: transact placements rewritten to real-shop practice (picture-led first screen; colour in the primary button, selected filter, category tiles or filter rail, one slim promo line; strong = tinted product tiles or one editorial block further down). No headline-only colour band; button accent not reused as a large block.
- rule:photo-library: an offline Wikimedia photo library (index with author/licence/source) is read before any live search; hardware added to the picture categories.
- No new check.py rule (on purpose: fewer rules, not more).

# V4.14 (2026-11-19)
From the user's review of V4.13 task 12 (Kiln & Loom: a red firing-batch stamp floating on every product picture, saying "9 left") compared with tasks 21 (care label under the name) and 22 (veneer chip on the picture edge):
- rule:object-host: the object sits where it really exists (label, tag, edge, base, receipt line); never over the product picture.
- rule:object-quiet: on repeated cards it is small, neutral or the item's own colour, never the accent; full-size only in the detail view or selected state.
- rule:object-decides: it shows decision facts (ideally the filter values), never a stock or urgency count; assign.py skips candidates whose job cue is a count ("left", "in stock", "sells out"...).
- object true for every kind of item; text on it 12px+, never on a curved path.
- check.py v6: flags an object repeated on 4+ cards that is laid over a picture in a saturated colour.

# V4.13 (2026-11-19)
Borrowed from the external skills run on tasks 01-50 (Taste Skill, Impeccable, Hallmark; see the external-skills comparison):
- rule:first-screen-task (Impeccable first-viewport): primary control on the first screen and half the working area on the phone; check.py --primary/--core. Answers the V4.11 loss on task 11 (steps clipped on the phone).
- rule:sample-label (Impeccable): invented figures carry a "Sample data" tag; check.py flags many bare figures with no label.
- rule:copy-first (Taste copy-lint): copy before layout; headings name content; check.py flags slot-name headings and filler words.
- rule:button-family, rule:focus-visible, 44px phone controls, 320px overflow (Taste consistency checks); check.py counts button looks, tabs for a focus ring, and tests 320px.
- rule:real-photos, rule:photo-decode (Taste photo pipeline): licensed Wikimedia photos allowed on image-led categories, contact sheet, embedded, credited; check.py lists images that fail to decode (Taste's own fetch wrote broken WebP files on 2 of 50 pages).
- fonts: Host Grotesk and Mona Sans added to the sans pools.
Not taken: Impeccable's AI-tell detector rules (23 of them were tested against judge scores in V4.4 and only overlapping words held up; cream ground and fonts stay with the radar, rule:eval-separation); Taste's random hero/section dealing and marketing-page structure on apps.

# Changelog
## V4.12 (2026-11-19)
Rebuilt: the V4.11 workspace was lost. SKILL.md, modes.md, direction.md, assign.py, refs.py (V4.11), categories.md, craft.md, review.md, defaults.md and real_profiles.json (V4.10b) are the originals. palette.py (white, black and deep scenes), check.py (legibility, top-bar and drag checks), fonts.json, nav_profiles.json (all-sites shares only), used.json, evals/tasks.json, shoot_ref.py and the reference library (497 screens from the Review Desk copy; no anchor marks, so tools go to live search) were rebuilt from the changelog and V3. Compare V4.12 with V4.11 with that in mind.

From the user's blind picks (11 of 60: latest beat baseline 8 to 2; the two losses were 08 ryokan booking and 11 library-card application):
- **rule:no-object-in-flows.** Transact pages whose main job is a multi-step form or booking, and every government page, get no object (11 had coded "ACPL 1 ELIG" step tiles). Built like the best real service: official or brand bar, breadcrumbs, one calm form column, a help aside, plain step names. assign.py `--flow`; tasks.json `flow`.
- **rule:colour-area.** On operate, read and transact pages no flat colour block covers more than about a third of the first screen; the transact "strong" placement is capped (08 had a full-width rust block over the catalogue).
- **rule:atmospheric-imagery.** On place, food, room, object and trip pages each item's picture is its own drawn scene with light, depth and several colours, different per item; never one repeated pictogram (08's ryokans were one-colour line icons; the baseline's sunset-and-pagoda scenes won). defaults.md 12.
- **check.py: cut-off rows.** A step or progress row that runs off the phone edge is flagged (11's step tiles), as is any non-scrolling row of tabs or chips.

## V4.11 (2026-11-18)
Problems found while reviewing V4.10:
- **The fit check was written against this benchmark.** Its four examples (checkout page for a form builder, admin template for esports, diagram editor for video, calculator for a language course) were the exact failures from the 50 tasks, so the gains on 25/29/32 partly came from the answers being in the rule.
- **The single metaphor object had become the new AI tell.** Across a round, nearly every tool carried a prop: rubber stamps on 07, 25, 26 and 40, plus lanyards, postage stamps, slates, luggage tags and push pins. Each is clever on its own; together they read as a formula, and real tools don't have them.

Changes:
- **rule:anchor-fit rewritten as a general test.** The anchor must be the same kind of product, not just the same broad family. It fails when it is a marketing, pricing, checkout or docs page instead of the working screen, when it does a different job, or when it is a generic template while products of this kind have their own layout. The examples no longer come from the benchmark.
- **rule:no-object-in-tools.** operate pages get no candidates and no object; assign.py no longer needs `--candidates` for them. A mark is allowed only if real products of this kind use it, in its ordinary form. Lessons and shops (read, transact) keep the object.
- **Validation.** Check on 10 new tasks that are not in the 50.

## V4.10 (2026-11-18)
Why the to-do board (07) and community feed (09) got worse in V4.9:
- 09 matched "kanban" on its keywords and took a Trello board as its anchor, so a discover feed became a three-column board.
- 07 took Kanboard's dated homepage as its anchor and came out generic.
- Stacked restraint rules hid the object: the stamp appeared only on Done cards.

What changed:
- **Anchor threshold (rule:anchor).** Only screens marked anchor-worthy can anchor: working interiors of current products, reviewed by eye. There are now 87 of them, including 15 community feeds and profiles, 5 bookings, todo apps and real kanban boards. The kind must be one of the brief's top two. Marketing homepages and Kanboard are out, and cal.com moved to booking.
- **New kinds.** feed (Dribbble, Mastodon, Lobsters, dev.to, Hacker News, Flickr, Instructables, Hackaday...), profile, todo (TodoMVC), booking (Airbnb search, Resy, cal.com, Tablet). Community briefs map to feed first.
- **Live fallback (rule:live-anchor).** With no anchor-worthy screen, NEXT 1c tells the builder to WebSearch for real public product screens and capture 2-3 with scripts/shoot_ref.py. The script refuses blank, error, bot-check and login pages and saves usable ones into the library, so the library grows.
- **Anchor fit check (rule:anchor-fit).** The builder first checks that the anchor is the same kind of product as the brief, for example not a checkout page for a form builder. If it isn't, it switches to live search (NEXT 1c) instead.
- **Course and lesson screens.** 35 hand-picked screens in three new kinds: lesson (Odin Project, Go Tour, SQLBolt, RegexOne, Flexbox Froggy, CSS Grid Garden, musictheory.net, Exercism...), course (Codecademy and Scrimba syllabi, MIT OCW, CS50, Coursera, lichess learn) and vocab (SpanishDict, Jisho, Real Kana, LanguageGuide, Cambridge). Bot-checked sites (Quizlet, LeetCode, Forvo, WordReference) stay out.
- **shoot_ref.py parallel fix.** It now uses its own temp files, so captures running in parallel no longer swap images.
- **Object on the first screen (rule:object-visible).** The object must be visible without scrolling, and on repeated items every item carries it. honest-sample now limits only alarm states (clash, overdue, error).

## V4.9 (2026-11-18)
- **Tool app bar has no text links at all.** Not even links to the app's own views. Views go in a rail or a tab row inside the work area; at most one segmented switch sits in the bar. V4.8 still put 7 view links in the bar on language learning and coding school.
- **Wordmark: whole name in one weight and one colour.** V4.8 had 3 of 20 split it ("KettleLane**Books**", "Stripe*by*Stripe", "**Harbour** Notices"). check.py flags a split wordmark in the top bar.

## V4.8 (2026-11-18)
- **Wordmark ornaments are a default look.** A lettered name with a dot, tick, bar, dashed perforation, half underline, superscript box or two-colour split stuck on. V4.7 had 6 of 20 ("kept•", "grainline•", "dock|et", "Link'light"). Letter the name through the face only.
- **Tool pages get an app bar, not a website nav.** One slim row (product name plus tool controls), copied from the anchor screen. Sections go in the rail or tabs. V4.7 put 6-8 marketing links on finance, Wi-Fi, esports and coding.
- **Promo strip drawn at 0.6 of the measured rate.** V4.7 drew it on 7 of 20 pages; real sites have it on 16%.
- **Dragging never selects text (craft.md, check.py).** Draggable surfaces get user-select:none, and pointerdown and dialog open clear the selection. Found when V4.7's calendar painted the selection colour over every label after a drag-to-create. check.py flags grab/move/crosshair surfaces that still allow selection; it caught the calendar and stayed silent on a shop page.

## V4.7 (2026-11-18)
In V4.6, 11 of 20 pages had the same top bar: a 64px white bar with a 1px grey line, an icon in front of the name, 3-5 links on the right, an outlined + filled button pair, and "Bag 0" counters. App pages added a coloured strip with a grey tagline. This was the strongest source of the "AI look".
- **rule:real-nav.** The top bars of 783 sampled homepages were measured (491 usable). Across them:
  - Surface: 48% plain light with no line, 18% dark, 15% laid over the opening image, 13% light with a line, 4% colour.
  - Layout: 40% links on the right, 23% links on the left, 14% links centred, 14% logo + Menu, 10% centred logo.
  - Other: 14% uppercase links, 16% with a promo strip, 75% with a lettered or image wordmark.
  - assign.py draws the surface, layout, height, case, strip, search and action per category (shrunk toward all sites). It prints them as NEXT 3b.
  - Operate pages follow the ANCHOR's app bar, with the same bans.
- **defaults.md 11 "Stock top bar".** Covers the icon + plain name, the grey tagline, the outlined + filled pair, count badges at 0 and the stock 64px white bar with a line. The wordmark is lettered and may use the display face.
- **check.py.** Flags count badges showing 0 in the top bar.

## V4.6 (2026-11-18)
Fixes from V4.5's calendar and mind map, where the object staged the content: a dozen clashes, unreadable 30px event blocks, a map shrunk to 59%. V4.5 also changed little from V4.4, because every draw is seeded by the task.
- **rule:anchor (operate).** The first app reference is chosen as the tool's structure model. A curated list prefers real working screens: calendar.com and FullCalendar for calendars, mermaid.live and Excalidraw for canvases, admin demos for dashboards. The anchor sets the ground and where colour sits, replacing the drawn placement; the hue family stays drawn. The builder follows its panes, nav position, density and colour placement, and writes what it took into STRUCTURE.
- **rule:honest-sample.** Sample content is an ordinary day of real use. The object's special state (clash, overdue, error) appears once or twice, never covers or shrinks the text it sits on, and the content is never multiplied to show it off.
- **check.py v3 (legibility).** Flags first-screen text that is covered by another element, cut off without an ellipsis, or squeezed into a box too narrow to read. It caught V4.5's calendar (8 covered labels, 5 crushed event blocks) and stayed silent on 6 other V4.5 pages.
- **review.md.** The legibility check is a blocking fix, not a note.

## V4.5 (2026-11-17)
- **Real references per page (rule:refs).** assign.py now prints 3-5 real screenshots from a local library and the builder reads them before the contract. No live scraping.
  - Homepage library: 1216 production homepages in 49 categories (every category now has at least 15 measured sites, most 20-35).
  - App-screen library: 378 logged-out app screens in 18 kinds (dashboard, analytics, table, form/checkout, canvas, design tools, code, docs, kanban, calendar, map, chat, media, commerce, learning, games, pricing, design shots).
  - Which library: persuade/experience 4 homepages of the category; transact 3 homepages + 1 shop/checkout screen; read 3 homepages + 1 docs/learning screen; operate 3 app screens matched to the brief's job + 1 category homepage.
  - Picks are seeded and spread across grounds and hues. References give conventions only (navigation, density, colour placement, corners); never logos, copy, exact colours or whole layouts, and never the direction.
- **Category profiles re-measured on 1194 sites** (was 767): config/real_profiles.json.


Rule ids are the `rule:` tags in the files; RULES.md lists each with its evidence. Finding ids (F1–F13) refer to FINDINGS.md.

## V3 (2026-11-05)
Rebuilt from seven benchmark rounds (470 pages) and a reading of the impeccable skill (Apache-2.0).
- **Fewer forced axes.** Only faces and corners per role are assigned (rule:assign-type-corners). Ground, colour strategy and headline are chosen inside the page mode (rule:mode-limits). Reason: V1–V2 lost 0.5–1.0 looks points to Style Director V2 across every forced axis (F11–F12).
- **Page modes** operate · read · transact · persuade · experience replace the three tiers (rule:page-modes; impeccable mode files).
- **Rank-offset roll** replaces "first idea out, model picks": the script builds one of the model's ranked #3..#n (rule:rank-offset-roll; impeccable concept-seed). Plus **name the rut** (rule:name-the-rut) and a **used pool** of directions and names that recurred (rule:used-pool; F7, F12).
- **Direction contract** before code, reviewed against at the check pass (rule:direction-contract).
- **palette.py v3:** four colour strategies (restrained, committed, full, drenched), ink ≥ 7:1, no muddy fills, yellow lift, frame-only colour, warnings for cream, cool-grey shell, khaki, cobalt/navy, violet, forest-on-cream (rule:ink-7, rule:no-muddy, rule:attractor-warnings).
- **Default looks v3:** + poster headline (third generation), side stripe and icon-card rows in template chrome, decorative grid and halos in effects, the warm-subject prior (rule:defaults-block).
- **Craft floor** with impeccable's numbers; one dominant move; no invented claims (rule:craft-budget, rule:one-move, rule:no-invented-claims).
- **Review:** GROUND / TYPE / MATERIAL drift rows, ≤ 8 ordered fixes, a derived disposition word; check.py v2 (+ overlapping words) and one script-only re-check after the fix pass (rule:recheck-after-fix).
- RULES.md registry with evidence and a "tried and dropped" table; tests check every listed rule is still tagged.

## V2 (2026-11-04)
From round 6 (F11) and a review of another open-source design skill.
- rule:audience-world — candidates must come from the subject or a world the audience lives in; each carries `audience_sees`; beats the competitor test. (round 6: synth panel for a maths class, fluorescent pink for climate)
- rule:frame-ground — midtone and color_ground grounds are frame-only; body text, cards, forms, charts sit on a near-white --surface. palette.py emits --ground / --on-ground; midtone chroma raised (0.075 → 0.11). (round 6: all 4 coloured-ground pages called murky / loud)
- rule:engine-prints-next — assign.py prints the remaining steps with exact commands; SKILL.md stops at the reveal. (scripts are followed more reliably than file references, F2)
- rule:checklist-at-review — the usability checklist and default-looks block are read only at self-review. (examples and references pull the design toward them, F5)
- rule:mechanical-check — scripts/check.py lists craft defects (overflow and culprits, low contrast, tiny text, gradient text, hard shadows, stray empty fixed boxes, small tap targets). It does not measure the AI-ness features the radar scores, so the radar stays a clean evaluation. (round 6: hidden toasts showing as blobs on 3 pages)

## V1 (2026-11-02)
Merge of Style Director V2 and seeded V3.
- rule:tier, rule:commit-before-reveal, rule:direction-definition, rule:competitor-test, rule:fit-sentence, rule:hue-source, rule:craft-budget, rule:cues-do-jobs, rule:short-examples, rule:defaults-block
- From Style Director V2: scene rules, locale, checklist, token-first build, three-way self-review. (best overall in round 5, F8)
- From seeded V3: first idea out, 5–7 candidates with ≥2 graphic, structure decided outside the model, hue from the direction. (most distinct in round 5, F6, F7)
- New: restraint tier limits bold options (restrained 0, balanced ≤1, expressive ≥1).
- New: structure for the 10 benchmark tasks comes from a balanced assignment (evals/tasks.json), not a hash.
- New: palette.py takes the structural value; warns when a light ground falls into cream. (F3)
- Font pools: Archivo and Archivo Black retired (F3).
- Removed presets.md and the single long example (F5); three short contrasting examples instead.

## V4 (2026-11-12)
Built from three inputs: the user's 19 favourite pages (claude/USER_PICKS_analysis.md), a design-practice note on "pages without AI flavour", and measurements of 175 real sites (claude/REAL_SITES_seed_library.md).
- New rule:subject-inventory. Before style words, list what the subject already has that can be drawn (data, the work, paper and objects, tools and places) and what job each could do. Ten of the 19 favourites took one real object from the subject and made it do a job (a stamp is the add-to-cart, a paint chip darkens as budget is spent).
- New rule:job-cue. Each candidate names the cue that does a job and the inventory item it grows from; candidates without one are never shortlisted. Replaces the blind rank-offset roll, which sometimes built themes that only decorate.
- New rule:shortlist-pick. The script shortlists three of #2..#n (never #1); the model writes three short contracts and picks by job, memory and fit, or a person picks. Generating several options and choosing beats one-shot.
- New rule:category and references/categories.md: how real sites of 21 kinds are built, what to borrow and what not to. Contract gains BORROW. Real industry conventions (project index, product grid with no card chrome, exhibition-and-dates block) were the main source of "looks like a real brand" in the favourites.
- New rule:real-profile. Type class and corners are drawn with the frequencies measured on real sites of the category instead of uniformly.
- Craft: media square unless containers are large (90% of real sites); display size starts from the category median; real content shape and imagery drawn from the content (rule:real-content); separate by space and ground, not boxes (real median 3 bordered boxes in three screens vs 11-19 on model pages).
- Review: new deletion pass (rule:deletion-pass): every element on the first two screens names its job or is removed.
- Defaults v4: a combination is not a hit when the contract traces it to the subject (named hue source, stated reason for a face). Habit typefaces is now about the habit, not a ban list. Colour is bounded by provenance, not banned.
- Kept: modes, scenes, palette.py, check.py, fit sentence, hue source, one move, cues do jobs, budget (1 check, 1 fix, one script-only recheck).

## V4.1 (2026-11-12)
After round 12 (V4): 19 of 20 pages sat on a tinted or coloured ground (real sites: 55% white, 24% dark) and 40% used serif or slab headlines (real: 19%). User: grounds may be white or black; colour tone should fit the kind of site (esports: deep navy or black), without a fixed style.
- palette.py: new scenes white and black (no hue cast, near-black / near-white text, neutral hairline) and deep (deep navy, forest or plum ground). rule:neutral-grounds. Navy warning only for a lone accent on a light restrained page.
- assign.py draws the ground (white, dark, tinted, colour field) from the category's real-site mix (70% category, 30% all sites); one change allowed with a stated reason. rule:real-profile.
- categories.md: a TONE line per category (where colour lives, what grounds are normal); contract gains GROUND; HUE must sit inside the tone. rule:category-tone.
- Type: sans headlines no longer split into slab; display novelty faces only for games, food, studios, type foundries, museums, creative tech. Font pools swapped toward faces real sites use (Inter Tight, Geist, DM Sans, Inter...). craft rule:real-type.
- Defaults item 4 clarified: a white or black page whose colour comes from content is not the neutral app shell.

## V4.2 (2026-11-12)
After round 13 (V4.1) and a comparison with the user's favourite pages for the same briefs (claude/ROUND13_analysis.md):
- Favourites built by DD V3 came from ranks 5-7 of 7 (small concrete objects: competition boards, due-date slip, paint chips). V4 and V4.1 mostly built rank #2 (8/20 in V4.1): whole-page costumes (answer sheet, departure board, warming stripes as the date filter, parcels hiding the books).
- Favourite brand and story pages open on the subject's most recognisable image, large (warming stripes, a coat, a building, a highlighted paper), with big type and a confident ground. V4/V4.1 refused those images (used-pool, never #1) and calibrated every page to real-site medians.
- New: two ways of building (modes.md, rule:object-on-structure, rule:icon-first). operate/read/transact: standard structure of the category, one object on one component, the script builds an "object" candidate from #3..#n (rule:mode-choice, rule:scale), products always visible (rule:products-visible). persuade/experience: shortlist includes #1, scored on icon, atmosphere, fit; display 2-3x the real median; one emphasised word allowed; the chart is the hero on data stories (rule:chart-is-hero).
- used-pool no longer refuses directions, only page names.
- Ground: app-interior mix for operate/read (white 75%, dark 20%, tinted 5%); colour field boosted for persuade/experience.
- Type: navigation, buttons and wordmark in the body face; categories with fewer than 5 measured sites blend 50/50 with all sites before drawing the face class.
- palette.py: cream and green-on-cream warnings no longer fire on white or black scenes.

## V4.3 (2026-11-12)
After round 14 (V4.2): 15 of 20 first screens were white (real sites 55%; the user's favourites about half strong colour or dark). Real white sites look colourful because full-bleed photos carry the colour; these pages have no photos.
- rule:colour-coverage: every first screen has one large area of colour (30-60%): a header band or rail, a hero block, a coloured ground, or drawn content full of colour. Checked in review.
- operate/read: white content with a coloured header band or rail (like the user's favourite finance page) by default; transact: a coloured hero block above a white catalogue; persuade/experience: confident ground unless the iconic image fills the screen with colour.
- assign.py: white share capped (0.6 for tools and shops, 0.35 for brand and story pages), the rest moved to colour field and dark; the "it looks plain is not a reason" line removed.

## V4.4 (2026-11-12)
Inputs: 767 measured real sites in 49 kinds (claude/REAL_SITES_800_analysis.md) and rounds 12-15.
- V4.2 was too white (56% of first screens near-neutral, real 26-33%); V4.3 overshot (2% neutral, every tool page a full-width colour band, green 16% and teal 12% vs real 7% and 11%).
- rule:colour-level replaces rule:colour-coverage: assign.py draws colour level (neutral / accent / strong), hue family and placement per category from real sites; placements vary by page kind (header bar, side rail, coloured tags and charts, tinted panel, hero block, coloured ground...).
- Hue family drawn first, then the direction supplies a source inside it (green drops to its real share; government gets blue, kids get strong colour, restaurants orange, film dark with orange/red).
- Categories: 49 kinds with measured colour, type and corners; 30 benchmark briefs remapped to closer kinds (bookshops, climate, kids, government, transit, news, community, open-source apps, events, film, travel, web toys, design systems, pets).
- Operate/read ground: half category, half app-interior mix (instead of V4.3's white cap).
