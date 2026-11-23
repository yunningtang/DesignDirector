# Direction: inventory the subject, name the rut, rank candidates, let the mode decide how one is chosen

A direction is a visual world this audience already knows, which can carry the primary task. <!-- rule:direction-definition --> The pages people remember take one real thing from the subject (a due-date slip, a paint chip, a cyanotype, a warming-stripe chart, an exhibition board) and make it do a job on the page: the stamp is the add-to-cart, the chip darkens as the budget is spent, the stripe is the chart. A theme that only decorates is forgettable however bold it looks.

1. **Subject inventory** <!-- rule:subject-inventory -->. Before any style word, list 6–10 things the subject already has that can be drawn in code (SVG, canvas, CSS), in four groups:
   - **its data**: numbers, series, schedules, scores, measurements it produces;
   - **its work or goods**: the products, projects, books, garments, artworks themselves (drawn, not photographed);
   - **its paper and objects**: tickets, slips, labels, receipts, forms, stamps, tags, packaging, signage;
   - **its tools and places**: instruments, workbenches, counters, rooms, maps.
   Mark each with `can_do`: which job on the page it could carry (show state, show progress, filter, group, prove a claim, be the navigation). Items with no job are fine to list; they can only decorate.
2. **Name the rut** <!-- rule:name-the-rut -->. Write the category's default page (what most sites in this category look like; `categories.md` describes it) and its predictable opposite (the obvious "different" version). Both are excluded.
3. **Candidates.** Write 5–7 directions and rank them by how strongly this audience would recognise them, #1 first.
   - **Audience test** <!-- rule:audience-world -->: each comes from the subject itself or from a world this audience already lives in. `audience_sees` is what a typical visitor would call it in a second.
   - **Job cue** <!-- rule:job-cue -->: each names `job_cue`, the one cue that does a job on this page ("each book carries a due-date slip; adding to the bag stamps it"), and `from_inventory`, the inventory item it grows from. A candidate whose cues only decorate gets an empty `job_cue`; the script will not choose it. The job is a fact the visitor decides with (material, size, origin, condition, time, route), never a stock or urgency count ("9 left"): the script will not choose those (rule:object-decides). The object must be true for every kind of item on the page (a kiln stamp does not belong on candles and linen).
   - **Scale** <!-- rule:scale -->: each is `"scale": "object"` (one small concrete thing that sits on one component of a standard page: a slip, a stamp, a chip, a tag, a label, a sticker) or `"scale": "page"` (a whole-page genre or picture: a departure board, an exercise book, an answer sheet, a poster wall, the warming stripes). On operate, read and transact pages only `object` candidates can be chosen, so write at least 3 of them; their job cue sits on a component and never replaces the main control. On persuade and experience pages rank the subject's most recognisable image as #1.
   - at least 3 material families; at least 2 of kind `graphic` (a notation, typographic system, signage or map language, data-graphics convention, printing technique); at most one literal reading of the brief.
   - operate pages: no candidate may be the tool the user operates (a terminal for a code tool).
   - Directions that recurred in earlier runs are refused by the script (`config/used.json`, rule:used-pool). Do not try to guess them; if one is refused, replace it.
   Write `candidates.json` and run `scripts/assign.py` once.

```json
{"inventory": [{"item": "due-date slip", "group": "paper", "can_do": "show that a book is in the bag"}],
 "rut": {"category_default": "...", "predictable_opposite": "..."},
 "candidates": [{"id": "c1", "name": "...", "family": "library circulation", "kind": "graphic",
   "looks": "three concrete visual cues", "serves": "how it carries the primary task",
   "job_cue": "the cue that does a job", "from_inventory": "due-date slip", "scale": "object",
   "audience_sees": "what a visitor would call it", "literal": false, "operated_tool": false}]}
```

4. **How one is chosen** <!-- rule:mode-choice -->. The script prints it; follow it.
   - **operate**: no candidates since V4.11 (rule:no-object-in-tools); run assign.py without `--candidates`.
   - **read, transact**: the script builds one `object` candidate from your #3..#n (the small, specific objects at the bottom of the list are the ones that become good cues; the top of the list is usually a whole-page costume). Keep it unless it factually cannot carry its job; then run once more with `--veto "reason"`.
   - **persuade, experience**: the script prints a shortlist of three that includes your #1. For each, write three lines into meta.json `shortlist`: THESIS, the first screen in one sentence, the memory test. Score each 1–3 on *icon* (would a visitor recognise the subject from the first screen alone), *atmosphere* (would the first screen work as a poster), *fit* (does this audience trust it). Build the highest total; on a tie, the one listed first. When a person is present, show the three as cards and let them pick.
5. **Contract** <!-- rule:direction-contract --> (about 120 words, into meta.json before any code, never into the page):
   - THESIS: "[direction] serves [primary task] because [mechanism on the page]." <!-- rule:fit-sentence -->
   - WORLD: three cues you will actually build, and what the audience calls the world. At least one is the job cue.
   - FIRST SCREEN: what is on it, including the primary task in working form.
   - STRUCTURE: operate, read and transact: the standard structure you are using (name its parts) and the one component the object sits on. persuade and experience: the iconic image and how large it is on the first screen.
   - BORROW: one or two conventions from your category section you keep on purpose (a project index, a product grid without card chrome, an exhibition-and-dates block), and why.
   - FORM: mode, scene, colour strategy, headline, faces, corners.
   - HUE: where the hue comes from in the direction (its inks, signage, materials, data colours), and how it sits inside your category's TONE line (`categories.md`). <!-- rule:hue-source --> <!-- rule:category-tone --> Of the hues the direction offers, pick the one this kind of site would plausibly wear (esports: deep navy or black with team colours; a diagnostic tool: a neutral ground with state colours). A hue that fights the tone is used as an accent, not as the ground. A hue with a named source may cover a whole band; that is not a default look.
   - GROUND: the ground the script drew from real sites of the category (white, black, tinted or a colour field), or the one change you made and why.
   - ONE MOVE: the single dominant move; everything else stays quiet. Memory test: what would a visitor remember tomorrow?
