// ─────────────────────────────────────────────
// OpenAI adapter (also works for OpenAI-compatible APIs)
// ─────────────────────────────────────────────

import type { LLMConfig, SemanticTokens } from "../../types/index.js";
import { SYSTEM_PROMPT, assembleUserPrompt } from "../prompts.js";
import { narrativeJsonSchema } from "../schema.js";
import type { LLMCallResult } from "./anthropic.js";

export async function callOpenAI(
  tokens: SemanticTokens,
  screenshot: Buffer,
  config: LLMConfig,
  prevErrors?: string[]
): Promise<LLMCallResult> {
  const endpoint = config.endpoint ?? "https://api.openai.com/v1";

  const body = {
    model: config.model,
    max_tokens: 4096,
    response_format: {
      type: "json_schema",
      json_schema: {
        name: "narrative",
        schema: narrativeJsonSchema(),
        strict: true,
      },
    },
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      {
        role: "user",
        content: [
          {
            type: "image_url",
            image_url: {
              url: `data:image/png;base64,${screenshot.toString("base64")}`,
            },
          },
          {
            type: "text",
            text: assembleUserPrompt(tokens, prevErrors),
          },
        ],
      },
    ],
  };

  const response = await fetch(`${endpoint}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${config.apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`OpenAI API error ${response.status}: ${text}`);
  }

  const data = (await response.json()) as any;
  const content = data.choices?.[0]?.message?.content;
  if (!content) throw new Error("OpenAI response had no content");

  const output = JSON.parse(content);

  return {
    output,
    usage: {
      inputTokens: data.usage?.prompt_tokens ?? 0,
      outputTokens: data.usage?.completion_tokens ?? 0,
    },
  };
}
