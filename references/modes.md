# Page modes: two ways of building <!-- rule:page-modes -->

The mode comes from what a visitor does on **this page**, not from the product: a tool's launch page is persuade, its docs are read. Read only your mode's section.

**Colour** <!-- rule:colour-level -->: `assign.py` draws how much colour the page carries (neutral, accent or strong), the hue family and where the colour goes, with the frequencies of real sites of your category. Real sites differ: about a quarter keep the page itself neutral and let the content carry colour, half use colour as an accent, a quarter use a strong field. Build the placement you are given, so different pages get different arrangements (not always a full-width band on top). A neutral page still needs colour somewhere visible: the drawn products, the chart, the covers. A white page with thin line drawings and one accent button is never the answer.

Pages people keep choosing come in two kinds, and they are built in opposite ways:
- **Tools** (operate) look like the best real product of their kind and carry **no object**: no stamps, slips, tags, tickets or other props from another world (rule:no-object-in-tools, V4.11). Real products don't have them, and across many pages they read as a formula. A mark appears only if real products of this kind use it (label chip, status dot, progress ring), in its ordinary form. Character comes from the right panes and density, real content, clear states, type and colour. Pictures of what a record is (the cake on an order, the photo in a library, the product in stock) are content, not decoration, and belong on tool pages: small on rows, larger in the detail view (rule:image-as-data, V4.16.1).
- **Forms, applications and bookings** (transact pages whose main job is filling in a multi-step form, and every government or public-service page) also carry **no object** (rule:no-object-in-flows, V4.12). They are built like the best real service of their kind: an official or brand bar, breadcrumbs, one calm column for the form, a help or "what you need" aside, plain step names ("Your details", not "ACPL 2 YOU"). A visitor trusts a form that looks like every good form.
- **Lessons and shops** (read, transact) look like the best real product of their kind. Their structure is completely standard; character comes from type, colour and **one small object from the subject sitting on one component**: paint-chip strips on budget categories, a due-date slip and stamp on each book, a price tag on each piece of furniture. The object never replaces the main control. <!-- rule:object-on-structure -->
- **Brand and story pages** (persuade, experience) open on **the subject's most recognisable image, large**: the warming stripes, the coat, the building, the highlighted page of a paper. Big type, a confident ground, one dominant move. Mechanisms and interaction come second. <!-- rule:icon-first -->

## operate
Tools, dashboards, editors, forms. The visitor comes back daily and wants speed.
- **Structure is the category's standard** <!-- rule:standard-structure -->: a dashboard is key numbers, a trend chart and a breakdown table with filters; a form builder is field palette, canvas and settings in three panes; a calendar is a week grid with a mini-month; a vocabulary app is a lesson list, a card and a progress view. The primary control is the control people already know (a date range picker, a list, a chart), never a metaphor.
- The direction lends **type, palette and density**; no object since V4.11 (rule:no-object-in-tools), and pictures only as data (rule:image-as-data). The reference lends structure only, never its surface (rule:borrow-layers). Never costume the screen as the tool the user operates or as another machine (a departure board, an answer sheet, a terminal).
- Ground and colour: as drawn (rule:colour-level). Colour does jobs: a header bar or rail, state colours, category colours, chart series.
- Density: compact spacing base 4px, body 15–16px, tables and numbers in tabular figures. Headline: plain or quiet, real-site size. Motion: feedback only.
- Start honest: empty states and real defaults, no invented progress or history for a new user.

## read
Docs, articles, lessons, reference.
- Structure is a real lesson or article: a navigation rail, a calm reading column (60–75ch, body 17–19px, line-height 1.55–1.7), worked examples and exercises in working form.
- The direction owns the **frame** (masthead, rail, ground, how figures and examples are set) and one object; the reading column stays calm.
- Monospace only for code, data and labels that are data. Headline: plain, quiet or condensed.

## transact
Stores, booking, course catalogues, pricing.
- Structure is a real store: search, filters, a product grid or list, product detail, bag. **The products are visible on the first screen** (covers, garments, pieces), never wrapped, hidden or replaced by a diagram. <!-- rule:products-visible -->
- The object sits on the product card or the buy control (a tag, a slip, a label) and carries real information (price, state, size).
- The hero is an editorial moment (a big headline, search or one large product) above a working catalogue; its colour follows the drawn placement.
- Headline: any; oversized only for one or two words.
- **Colour area (rule:colour-area, V4.12).** No single block of flat colour covers more than about a third of the first screen. A coloured hero sits above the catalogue, never across it, and the catalogue stays on the page ground. Beyond that, colour comes from the products and pictures themselves.
- **Pictures with atmosphere (rule:atmospheric-imagery, V4.12).** Where the thing sold is a place, a stay, food, an object to live with or a trip, each item's picture is a drawn scene of that item in its setting, with light, depth and several colours (the street, the room, the sky, the material), and every item's picture differs. Never a one-colour pictogram or line icon repeated across cards; a card of icons reads as a template, a card of scenes reads as the place.

### Flows: forms, applications, bookings (rule:no-object-in-flows, V4.12)
- Structure of the best real service: brand or official bar, breadcrumbs or a back link, the form in one calm column of 560-720px, a narrow aside with what you need, help and contact. On a phone the aside folds below the form.
- Progress: "Step 2 of 6 · Your details" as text with a thin bar, or a vertical list on desktop. Step names are plain words a visitor would use. Never codes, numbered tiles or stamps.
- A step row on a phone either fits the width or collapses to the current step; it never runs off the edge (check.py flags it).
- Colour: the brand or official colour on the bar and the primary button; the form sits on white or the page ground.

## persuade
Launches, product sites, campaigns, events, studios.
- **Open on the iconic image** of the subject, large: what a visitor would draw if asked to sketch the subject (the highlighted paper for a research tool, the building for an architect, the garment for a label). It may be the same image other good pages of this subject use; that is fine. <!-- rule:icon-first -->
- Display type may be 2–3 times the real-site median of the category (about 80–120px on desktop), one emphasised word (italic or colour) is allowed in the headline. The ground is confident: a colour field, deep or black, or white only when the iconic image itself fills the first screen with colour.
- The opening shows the product's real action in working form where there is one (a demo, a sample answer), but it sits inside the image, not instead of it.
- A split hero (text left, image right) or a centred headline over three cards is the template whatever colours it wears. One dominant move; busy is louder, not bolder.
- Claims are proved on the page, never invented (no fake logos, metrics or testimonials).

## experience
Stories, data stories, art, games, interactive essays.
- **Open on the iconic image**: for data, the data itself drawn large (the stripes, the curve, the map); for art and games, the one picture that is the piece. The chart is the hero; do not add navigation gadgets (rails, dials) that take space from it. <!-- rule:chart-is-hero -->
- Display type may be large (as persuade). The ground is confident (colour field, deep or black) unless the drawn data or picture already fills the first screen with colour.
- The direction owns everything, including navigation, as long as a first-time visitor knows what to do within five seconds.
- One authored motion moment; everything else still. Always offer a plain, still version (reduced motion, plain text).
- Text that animates must stay readable at every frame.


## Operate: the anchor screen and honest sample content (V4.6)
- **Anchor (rule:anchor).** assign.py marks one app screenshot as ANCHOR. Build the tool's skeleton like it: the same panes at roughly the same widths, navigation and the main action in the same places, similar row and cell density, and colour in the same places at about the same amount. Take nothing of its brand. The object goes on one component of that skeleton.
- **Honest sample (rule:honest-sample).** Fill the tool the way a real person's account looks on an ordinary day: a normal number of events, cards or rows, with one or two showing the object's special state. Never add overlaps, errors or overdue items so the object has more to do.


## The object is seen on the first screen (V4.10; read and transact only since V4.11)
The object must be visible without scrolling. When it belongs to a repeated item (a card, row, event or post), every item carries it in its ordinary state. A Done-only stamp or a single highlighted card hides the idea. rule:honest-sample limits only alarm states (a clash, an overdue card, an error), not the object.
