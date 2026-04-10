// ─────────────────────────────────────────────
// Adapter dispatcher — routes to the right provider
// ─────────────────────────────────────────────

import type { LLMConfig, SemanticTokens } from "../../types/index.js";
import { callAnthropic, type LLMCallResult } from "./anthropic.js";
import { callOpenAI } from "./openai.js";

export type { LLMCallResult };

export async function callLLM(
  tokens: SemanticTokens,
  screenshot: Buffer,
  config: LLMConfig,
  prevErrors?: string[]
): Promise<LLMCallResult> {
  switch (config.provider) {
    case "anthropic":
      return callAnthropic(tokens, screenshot, config, prevErrors);
    case "openai":
    case "custom":
      return callOpenAI(tokens, screenshot, config, prevErrors);
    default:
      throw new Error(`Unknown LLM provider: ${config.provider}`);
  }
}
