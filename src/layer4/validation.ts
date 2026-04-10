// ─────────────────────────────────────────────
// Layer 4 — Semantic validation
// Ensures LLM output doesn't hallucinate facts
// that contradict the extracted tokens.
// ─────────────────────────────────────────────

import type { Narrative, SemanticTokens } from "../types/index.js";

export interface ValidationOk {
  ok: true;
  data: Narrative;
}

export interface ValidationFail {
  ok: false;
  errors: string[];
}

export type ValidationResult = ValidationOk | ValidationFail;

const HEX_PATTERN = /#[0-9a-fA-F]{6,8}\b/g;

export function validateNarrative(
  narrative: Narrative,
  tokens: SemanticTokens
): ValidationResult {
  const errors: string[] = [];

  // Collect all known hex values from tokens
  const allTokenColors = new Set<string>();
  for (const val of Object.values(tokens.palette)) {
    if (val) allTokenColors.add(val.toLowerCase());
  }

  // Collect all known token keys
  const allTokenKeys = new Set<string>([
    ...Object.keys(tokens.palette),
    "display",
    "body",
    "mono",
    ...Object.keys(tokens.spacing),
    ...Object.keys(tokens.radii),
  ]);

  // Collect all font families
  const allFontFamilies = new Set<string>(
    [
      tokens.typography.display.family,
      tokens.typography.body.family,
      tokens.typography.mono?.family,
    ]
      .filter(Boolean)
      .map((f) => f!.toLowerCase())
  );

  // Gather all free-text fields
  const textFields: string[] = [
    narrative.mood.summary,
    ...narrative.guidelines.dos.map((d) => d.rule + " " + (d.reason ?? "")),
    ...narrative.guidelines.donts.map((d) => d.rule + " " + (d.reason ?? "")),
    ...narrative.readyPrompts.map((p) => p.prompt),
  ];

  // 1. Check for hallucinated hex colors
  for (const text of textFields) {
    const matches = text.match(HEX_PATTERN) ?? [];
    for (const hex of matches) {
      if (!allTokenColors.has(hex.toLowerCase())) {
        errors.push(`Hallucinated color: ${hex} not in extracted tokens`);
      }
    }
  }

  // 2. Check tokenRefs in readyPrompts
  for (const prompt of narrative.readyPrompts) {
    for (const ref of prompt.tokenRefs) {
      if (!allTokenKeys.has(ref)) {
        errors.push(`Hallucinated token reference: "${ref}" does not exist`);
      }
    }
  }

  // 3. Check semantic names reference real palette keys
  const paletteKeys = new Set(Object.keys(tokens.palette));
  for (const sn of narrative.semanticNames) {
    if (!paletteKeys.has(sn.token)) {
      errors.push(`Semantic name references non-existent token: "${sn.token}"`);
    }
  }

  // 4. Basic sanity checks
  if (narrative.mood.keywords.length < 3) {
    errors.push("Mood keywords must have at least 3 entries");
  }
  if (narrative.guidelines.dos.length < 3) {
    errors.push("Must have at least 3 do's");
  }
  if (narrative.guidelines.donts.length < 3) {
    errors.push("Must have at least 3 don'ts");
  }

  return errors.length === 0
    ? { ok: true, data: narrative }
    : { ok: false, errors };
}
