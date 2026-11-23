# Review (read only at the check pass) <!-- rule:checklist-at-review -->

Look at your two screenshots and `check.py` output, and write down at most 8 fixes ordered by harm. Fix them in your one pass; then run `check.py` once more. <!-- rule:recheck-after-fix -->

## 1. Drift (from your contract)
- **COLOUR:** does the page follow the drawn colour level, hue family and placement? Is the hue inside the family? A white page with thin drawings and one accent button fails at every level. <!-- rule:colour-level -->
- **GROUND:** is the page ground what the contract says? Drift toward warm cream, pale cool grey, or blue-black slate is the model prior pulling.
- **TYPE:** are the assigned faces on the headline and body, with the planned headline treatment?
- **MATERIAL:** are the three world cues on the first screen and still present in the second half?
- **ONE MOVE:** is there exactly one dominant move? Remove competing ones.

## 2. Delete <!-- rule:deletion-pass -->
Models add; good pages subtract. List every element on the first two screens (labels, icons, dividers, badges, cards, extra buttons, captions, background shapes). For each, write the job it does in a few words. Anything without a job is deleted or merged, and counts as one of your fixes. Typical ones: a small label above every heading, an icon per card, a second call to action that repeats the first, a divider between sections that already differ, a decorative shape behind the hero, a caption restating the heading.

## 3. Usable
- The primary task is the most prominent action on the first screen and works end to end.
- Every interactive element has hover, focus-visible, active, disabled; async actions show loading and prevent double submit; every action gives visible success or error feedback; destructive actions confirm or offer undo.
- Field errors say how to fix and keep the input; empty states explain the next action; no dead ends.
- Tabs, filters, search and open detail views are in the URL; Back returns to the previous state; links are `<a href>`, actions are `<button>`.
- Keyboard: Tab order follows the visual order, focus always visible, Esc closes overlays, focus moves into and back out of modals.
- Phone (375px): no sideways scroll; tap targets about 44px; inputs 16px+; navigation collapses; tables scroll in their box or become cards; nothing hidden behind a fixed bar or a toast.
- Contrast: 4.5:1 for text, 3:1 for large text and UI edges (`palette.py --check`); colour is never the only signal; one h1, ordered headings, labelled inputs; `prefers-reduced-motion` respected.

## 4. Refuse list (unless the brief names it)
Identical icon + heading + text card rows; a hero metric row as decoration; nested cards; a centred headline + two buttons + three cards; logo walls, fake stats, invented testimonials; filler copy ("revolutionize", "unlock", "seamless", "supercharge"); every section fading up on scroll; pulsing calls to action; plus the combinations in `defaults.md`.

## 5. Disposition
After fixing, write one word in meta.json `disposition`: **ship** (nothing harmful left), **fix** (known issues remain, listed), or **rebuild** (the direction did not carry the task; say why). Derive it from the list above, not from how the page feels.


## Legibility (V4.6, blocking)
After the fix pass, every label on the first screen must be readable. Nothing may be covered by a stamp, badge or another block, cut off, or crushed into a box narrower than its words. check.py lists these as "text covered", "text cut off" and "text squeezed". Fix every one. When the object is what covers text, shrink or move the object; do not shrink the text. When the sample data causes it (too many overlaps, too many items in one cell), make the data ordinary (rule:honest-sample).


## V4.12 rows (answer each with where on the page, or fix)
- **Flow pages:** no prop or code on the steps; step names in plain words; on the phone screenshot the step row fits or shows only the current step.
- **Colour area:** on the 1440 screenshot, the largest flat colour block is under about a third of the first screen (tools, shops, flows).
- **Pictures:** on shops and bookings of places, food, rooms or objects, each card's picture is a different drawn scene with light and several colours, not a repeated one-colour icon.


## V4.13 rows (answer each, or fix)
- **Copy:** every heading names its content; every button names its action; no filler (rule:copy-first).
- **First screen:** check.py was run with `--primary` and `--core` (premium pages: `--primary` and `--premium`, no `--core`); both pass at 1440 and 375 (rule:first-screen-task).
- **Sample:** blocks of invented figures carry a "Sample data" tag (rule:sample-label).
- **Buttons and focus:** at most three button looks; Tab shows a focus ring; phone controls about 44px; no sideways scroll at 320px.
- **Photos:** if you used photographs, every one decodes and is credited; none shows a brand name or logo (rule:real-photos).


## V4.14 rows (small objects)
- **Object host:** on the 1440 and 375 screenshots, the object sits on a label, tag, edge or line, not over the product picture.
- **Quiet:** on repeated cards it is not the accent colour and is not the first thing you see on the card; the primary button is the strongest colour on the card.
- **Decides:** it shows a fact a buyer compares, not "N left".


## V4.15 rows (shops)
- **No empty band:** the first screen of a shop opens on pictures or products, not on a flat colour band with a headline and a button.


## V4.16 hero review (premium pages; from Hallmark review-hero.md)
Answer these from the 1440 screenshot before listing fixes:
- Does the head say something only this product could say, in seven words or fewer?
- Is the visual a real picture (a photograph, the product, the key art) and does it hold its half of the screen at 60% of the screen tall or more, or fill it?
- Does anything read as a template: a centred stack, a pill or label above the head, a gradient blob, an empty coloured box where a picture should be, a small drawn illustration, two filled buttons side by side, a row of stats?
- Delete the picture in your head: if the screen still says the same thing, the picture is too weak or too small.
- Squint: with the words blurred, does each section still have a shape and the page a rhythm of heavy and light?
