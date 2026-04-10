// ─────────────────────────────────────────────
// Layer 4 — Zod schema for LLM structured output
// ─────────────────────────────────────────────

import { z } from "zod";

export const GuidelineSchema = z.object({
  rule: z.string().min(10).max(150),
  reason: z.string().max(100).optional(),
});

export const ReadyPromptSchema = z.object({
  title: z.string().max(60),
  prompt: z.string().min(80).max(500),
  tokenRefs: z.array(z.string()),
});

export const SemanticNameSchema = z.object({
  token: z.string(), // key in palette, e.g. "accent-primary"
  name: z
    .string()
    .regex(/^[a-z][a-z0-9-]{2,30}$/, "Must be lowercase kebab-case, 3-31 chars"),
  rationale: z.string().max(120),
});

export const NarrativeSchema = z.object({
  mood: z.object({
    summary: z.string().min(50).max(400),
    keywords: z.array(z.string()).min(3).max(8),
  }),
  semanticNames: z.array(SemanticNameSchema).max(10),
  guidelines: z.object({
    dos: z.array(GuidelineSchema).min(3).max(6),
    donts: z.array(GuidelineSchema).min(3).max(6),
  }),
  readyPrompts: z.array(ReadyPromptSchema).min(2).max(4),
});

export type NarrativeFromSchema = z.infer<typeof NarrativeSchema>;

/**
 * Convert NarrativeSchema to a plain JSON Schema object
 * for use in LLM tool_use / structured output calls.
 */
export function narrativeJsonSchema(): Record<string, unknown> {
  return zodToJsonSchema(NarrativeSchema);
}

// Minimal zod-to-json-schema converter (avoids extra dependency)
function zodToJsonSchema(schema: z.ZodTypeAny): Record<string, unknown> {
  if (schema instanceof z.ZodObject) {
    const shape = schema.shape;
    const properties: Record<string, unknown> = {};
    const required: string[] = [];
    for (const [key, val] of Object.entries(shape)) {
      properties[key] = zodToJsonSchema(val as z.ZodTypeAny);
      if (!(val instanceof z.ZodOptional)) {
        required.push(key);
      }
    }
    return { type: "object", properties, required };
  }
  if (schema instanceof z.ZodArray) {
    return { type: "array", items: zodToJsonSchema(schema.element) };
  }
  if (schema instanceof z.ZodString) {
    return { type: "string" };
  }
  if (schema instanceof z.ZodNumber) {
    return { type: "number" };
  }
  if (schema instanceof z.ZodOptional) {
    return zodToJsonSchema(schema.unwrap());
  }
  return {};
}
