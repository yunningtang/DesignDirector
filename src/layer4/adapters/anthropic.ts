// ─────────────────────────────────────────────
// Anthropic (Claude) adapter
// ─────────────────────────────────────────────

import Anthropic from "@anthropic-ai/sdk";
import type { LLMConfig, SemanticTokens } from "../../types/index.js";
import { SYSTEM_PROMPT, assembleUserPrompt } from "../prompts.js";
import { narrativeJsonSchema } from "../schema.js";

export interface LLMCallResult {
  output: unknown;
  usage: { inputTokens: number; outputTokens: number };
}

export async function callAnthropic(
  tokens: SemanticTokens,
  screenshot: Buffer,
  config: LLMConfig,
  prevErrors?: string[]
): Promise<LLMCallResult> {
  const client = new Anthropic({
    apiKey: config.apiKey,
    ...(config.endpoint ? { baseURL: config.endpoint } : {}),
  });

  const response = await client.messages.create({
    model: config.model,
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    tools: [
      {
        name: "write_narrative",
        description: "Output the complete narrative for the design system.",
        input_schema: narrativeJsonSchema() as Anthropic.Tool.InputSchema,
      },
    ],
    tool_choice: { type: "tool" as const, name: "write_narrative" },
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/png",
              data: screenshot.toString("base64"),
            },
          },
          {
            type: "text",
            text: assembleUserPrompt(tokens, prevErrors),
          },
        ],
      },
    ],
  });

  const toolUse = response.content.find(
    (b): b is Anthropic.ToolUseBlock => b.type === "tool_use"
  );

  if (!toolUse) {
    throw new Error("Anthropic response did not contain tool_use block");
  }

  return {
    output: toolUse.input,
    usage: {
      inputTokens: response.usage.input_tokens,
      outputTokens: response.usage.output_tokens,
    },
  };
}
