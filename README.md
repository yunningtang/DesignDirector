# DesignGrab 🤚

**Grab the design system of any website.** Paste a URL, get a complete DESIGN.md with color palette, typography, spacing, components, do's & don'ts, and ready-to-use prompts.

![DesignGrab](https://img.shields.io/badge/sites-52-black) ![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue) ![Playwright](https://img.shields.io/badge/Playwright-1.52-green)

## How it works

DesignGrab runs a **5-layer pipeline**:

```
URL → Capture → Normalize → Classify → Narrate → DESIGN.md
      (Playwright)  (pure fn)   (heuristics) (LLM/template) (markdown)
```

1. **Layer 1 — Capture**: Headless Chromium loads the page, waits for hydration, reads `getComputedStyle()` on every visible element, extracts `@font-face`, CSS variables, gradients, and takes a screenshot.
2. **Layer 2 — Normalize**: Parses all color formats to hex/HSL, deduplicates, calculates area-weighted usage stats per color role (background/text/border).
3. **Layer 3 — Classify**: Heuristic rules assign semantic meaning — detects theme (light/dark), classifies bg/ink/accent/line colors, extracts type scale, spacing grid, border radii, button components.
4. **Layer 4 — Narrate**: Template mode (free, instant) or LLM mode (Claude/GPT, richer output). LLM output is schema-validated + semantically verified to prevent hallucinated colors.
5. **Layer 5 — Render**: Combines tokens + narrative into a 10-section DESIGN.md with copy-paste CSS variables, color role tables, and ready-to-use prompts.

## Quick start

```bash
git clone https://github.com/yunningtang/DesignGrab.git
cd DesignGrab
npm install
npx playwright install chromium
npm run build
```

### CLI

```bash
# Fast mode (free, no API key, ~3s)
npm run grab -- https://stripe.com

# Polished mode (LLM-enhanced narrative)
npm run grab -- https://stripe.com --polished --provider anthropic --key sk-ant-xxx
```

Output goes to `output/<hostname>/`:
- `DESIGN.md` — Full design system document
- `tokens.json` — Structured semantic tokens
- `screenshot.png` — Homepage screenshot

### Web UI

```bash
npm start
# → http://localhost:3000
```

Features:
- Paste any URL and grab in real-time
- **Editable token panel** — click any color to open custom color picker, edit fonts, spacing, radii
- **Live regeneration** — changes instantly update the DESIGN.md
- **3 view tabs** — DESIGN.md / tokens.json / Visual (screenshot + editor)
- **52 pre-grabbed examples** across 8 categories
- **Search & filter** gallery by name, font, category, theme
- **Save & Share** — bookmark grabs, copy share links
- **Multi-language** — EN, 中文, 日本語, 한국어, Español
- **Login system** — Google/GitHub/email (localStorage mock, ready for real OAuth)

## Pre-grabbed sites (52)

All grabbed with our own pipeline — real computed styles, not copied.

### AI (9)
Anthropic · Cohere · Mistral · Replicate · Together · Ollama · OpenCode · RunwayML · VoltAgent

### Dev Tools (12)
GitHub · Vercel · Supabase · Sentry · PostHog · Tailwind CSS · Warp · Expo · HashiCorp · MongoDB · Composio · Cursor

### SaaS (10)
Linear · Notion · Resend · Cal.com · Intercom · Mintlify · Raycast · Airtable · Clay · Arc

### Fintech (6)
Stripe · Coinbase · Wise · Revolut · Binance · Kraken

### Consumer (6)
Airbnb · Spotify · Nike · Pinterest · Meta · Shopify

### Enterprise (4)
Apple · Nvidia · Tesla · BMW

### Design (3)
Framer · Webflow · Miro

### Auto (2)
Lamborghini · Renault

## DESIGN.md output (10 sections)

Each grab produces a comprehensive design system document:

| Section | Content |
|---------|---------|
| 1. Mood & Atmosphere | Theme description, keywords |
| 2. Color Palette | CSS custom properties (grouped), color role table, semantic naming |
| 3. Typography | Font stack declarations, type scale with usage hints |
| 4. Spacing | Base unit, `--space-1` through `--space-10` |
| 5. Border Radius | sm/md/lg/full with usage comments |
| 6. Shadows & Gradients | Extracted box-shadows and CSS gradients |
| 7. Components | Primary/secondary button specs |
| 8. Do's and Don'ts | 6+ actionable rules with rationale |
| 9. Ready-to-Use Prompts | Hero, card, nav bar, form — copy-paste into AI |
| 10. Quick-Start CSS Reset | `html`, `h1-h3` reset matching the design |

## Architecture

```
src/
  types/index.ts          — Shared types (RawObservations → SemanticTokens → Narrative)
  layer1/capture.ts       — Playwright: DOM extraction + screenshot
  layer2/normalize.ts     — Color parsing, font cleaning, dedup, gradient extraction
  layer3/classify.ts      — Theme detection, palette/ink/accent heuristics, components
  layer4/
    schema.ts             — Zod schema for LLM structured output
    prompts.ts            — System + user prompts
    validation.ts         — Semantic validation (catches hallucinated colors)
    template.ts           — Rule-based narrator (no LLM fallback)
    narrate.ts            — Entry: LLM with retry → fallback to template
    adapters/             — Anthropic / OpenAI / custom provider adapters
  layer5/render.ts        — Markdown template renderer
  pipeline.ts             — Wires L1→L2→L3→L4→L5
  server.ts               — HTTP server (serves UI + API)
  cli.ts                  — CLI entry point

designgrab.html           — Single-file frontend (no build step)
batch-grab.js             — Batch grabber for multiple sites
examples.json             — 52 pre-grabbed sites with tokens + screenshots
```

## Key design decisions

- **Data flows strictly downward** — LLM (L4) only reads SemanticTokens, never raw CSS
- **LLM can't corrupt facts** — all hex/px/font values come from tokens, not LLM output
- **Double validation** — Zod schema + semantic checks on LLM responses
- **Graceful degradation** — LLM failure auto-falls back to template mode
- **Zero-config default** — fast mode needs no API key, works offline

## Batch grabbing

```bash
# Grab all sites from a list
node batch-grab.js
```

Edit `batch-grab.js` to add/remove URLs. Runs 2 concurrent browsers.

## LLM configuration

In the web UI, click **Settings** to configure:

| Mode | LLM | Cost | Speed |
|------|-----|------|-------|
| Fast | None (template) | Free | ~3s |
| Polished | Claude Haiku | ~$0.003 | ~5s |
| Polished | Claude Sonnet | ~$0.03 | ~8s |
| Polished | GPT-4o-mini | ~$0.002 | ~5s |

API keys are stored in localStorage, never sent to any server.

## Inspired by

- [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — curated list of DESIGN.md files
- [DESIGNmd.dev](https://designmd.dev) — design system marketplace

## License

MIT
