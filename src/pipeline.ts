// ─────────────────────────────────────────────
// Pipeline — connects all 5 layers
//
//   URL → Capture → Normalize → Classify → Narrate → Render → DESIGN.md
//
// Data flows strictly downward. LLM (Layer 4)
// only sees SemanticTokens, never raw CSS.
// ─────────────────────────────────────────────

import type { GrabOptions, GrabResult } from "./types/index.js";
import { capture } from "./layer1/capture.js";
import { normalize } from "./layer2/normalize.js";
import { classify } from "./layer3/classify.js";
import { narrate } from "./layer4/narrate.js";
import { render } from "./layer5/render.js";

export async function grab(options: GrabOptions): Promise<GrabResult> {
  const { url, mode, llm } = options;
  const viewports = options.viewports ?? [{ width: 1440, height: 900 }];

  // ── Layer 1: Capture ──
  console.log(`[L1] Capturing ${url} …`);
  const raw = await capture(url, { viewport: viewports[0] });
  console.log(
    `[L1] Done. ${raw.elements.length} elements, ${Object.keys(raw.cssVariables).length} CSS vars.`
  );

  // ── Layer 2: Normalize ──
  console.log("[L2] Normalizing …");
  const normalized = normalize(raw);
  console.log(
    `[L2] Done. ${normalized.colors.length} colors, ${normalized.fonts.length} fonts, ${normalized.spacings.length} spacings.`
  );

  // ── Layer 3: Classify ──
  console.log("[L3] Classifying …");
  const tokens = classify(normalized, raw);
  console.log(
    `[L3] Done. Theme: ${tokens.theme}, monochrome: ${tokens.meta.monochrome}.`
  );

  // ── Layer 4: Narrate ──
  const llmConfig = mode === "polished" ? llm : null;
  console.log(`[L4] Narrating (${llmConfig ? "LLM" : "template"}) …`);
  const narrateResult = await narrate(tokens, raw.screenshot, llmConfig);
  console.log(`[L4] Done. Source: ${narrateResult.source}.`);
  if (narrateResult.warnings.length > 0) {
    for (const w of narrateResult.warnings) {
      console.warn(`[L4] ⚠️  ${w}`);
    }
  }

  // ── Layer 5: Render ──
  console.log("[L5] Rendering DESIGN.md …");
  const markdown = render(tokens, narrateResult);
  console.log("[L5] Done.");

  return {
    markdown,
    tokens,
    narrative: narrateResult,
    screenshot: raw.screenshot,
  };
}
