// ─────────────────────────────────────────────
// Layer 4 — NARRATE entry point
// Tries LLM if configured, falls back to template.
// LLM output is schema-validated then semantically
// validated. Two retry attempts max.
// ─────────────────────────────────────────────

import type {
  LLMConfig,
  Narrative,
  NarrateResult,
  SemanticTokens,
} from "../types/index.js";
import { NarrativeSchema } from "./schema.js";
import { validateNarrative } from "./validation.js";
import { narrateWithTemplate } from "./template.js";
import { callLLM } from "./adapters/index.js";

const MAX_ATTEMPTS = 2;

async function narrateWithLLM(
  tokens: SemanticTokens,
  screenshot: Buffer,
  config: LLMConfig,
  attempt = 1,
  prevErrors: string[] = []
): Promise<{
  narrative: Narrative;
  usage: { inputTokens: number; outputTokens: number };
}> {
  const result = await callLLM(tokens, screenshot, config, prevErrors);

  // Layer 1: Schema validation (Zod)
  const schemaResult = NarrativeSchema.safeParse(result.output);
  if (!schemaResult.success) {
    const errors = schemaResult.error.errors.map(
      (e) => `${e.path.join(".")}: ${e.message}`
    );
    if (attempt < MAX_ATTEMPTS) {
      return narrateWithLLM(tokens, screenshot, config, attempt + 1, errors);
    }
    throw new Error(`Schema validation failed: ${errors.join("; ")}`);
  }

  // Map Zod output to our Narrative type (they're structurally identical)
  const narrative: Narrative = schemaResult.data;

  // Layer 2: Semantic validation
  const semanticResult = validateNarrative(narrative, tokens);
  if (!semanticResult.ok) {
    if (attempt < MAX_ATTEMPTS) {
      return narrateWithLLM(
        tokens,
        screenshot,
        config,
        attempt + 1,
        semanticResult.errors
      );
    }
    throw new Error(
      `Semantic validation failed: ${semanticResult.errors.join("; ")}`
    );
  }

  return { narrative: semanticResult.data, usage: result.usage };
}

/**
 * Main entry point for Layer 4.
 * If LLM config is provided, tries LLM with validation + retry.
 * Falls back to template on any failure.
 */
export async function narrate(
  tokens: SemanticTokens,
  screenshot: Buffer,
  config: LLMConfig | null
): Promise<NarrateResult> {
  // No config → template only
  if (!config) {
    return {
      narrative: narrateWithTemplate(tokens),
      source: "template",
      warnings: [],
    };
  }

  // Try LLM with fallback
  try {
    const { narrative, usage } = await narrateWithLLM(
      tokens,
      screenshot,
      config
    );
    const costUsd = estimateCost(config.model, usage.inputTokens, usage.outputTokens);
    return {
      narrative,
      source: "llm",
      warnings: [],
      usage: { ...usage, costUsd },
    };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return {
      narrative: narrateWithTemplate(tokens),
      source: "template",
      warnings: [`LLM narration failed: ${msg}. Using template fallback.`],
    };
  }
}

/** Rough cost estimation per model. */
function estimateCost(
  model: string,
  inputTokens: number,
  outputTokens: number
): number {
  // Prices per million tokens (approximate, as of 2025)
  const pricing: Record<string, { input: number; output: number }> = {
    "claude-haiku-4-5-20251001": { input: 0.8, output: 4 },
    "claude-sonnet-4-6": { input: 3, output: 15 },
    "claude-opus-4-6": { input: 15, output: 75 },
    "gpt-4o-mini": { input: 0.15, output: 0.6 },
    "gpt-4o": { input: 2.5, output: 10 },
  };

  const p = pricing[model] ?? { input: 3, output: 15 }; // default to ~sonnet
  return (inputTokens * p.input + outputTokens * p.output) / 1_000_000;
}
