// ─────────────────────────────────────────────
// Layer 5 — RENDER
// Pure template. Combines SemanticTokens + Narrative
// into a DESIGN.md string.
//
// All factual values (hex, px, font names) come
// directly from SemanticTokens — never from Narrative.
// ─────────────────────────────────────────────

import type { SemanticTokens, NarrateResult } from "../types/index.js";

function componentBlock(
  name: string,
  spec: NonNullable<SemanticTokens["components"]["primaryButton"]>
): string {
  const lines = [
    `### ${name}`,
    "```css",
    spec.backgroundColor ? `background: ${spec.backgroundColor};` : null,
    spec.textColor ? `color: ${spec.textColor};` : null,
    spec.borderRadius ? `border-radius: ${spec.borderRadius}px;` : null,
    spec.paddingX || spec.paddingY
      ? `padding: ${spec.paddingY}px ${spec.paddingX}px;`
      : null,
    spec.fontSize ? `font-size: ${spec.fontSize}px;` : null,
    spec.fontWeight ? `font-weight: ${spec.fontWeight};` : null,
    spec.border ? `border: ${spec.border};` : null,
    "```",
  ].filter(Boolean);
  return lines.join("\n");
}

export function render(tokens: SemanticTokens, result: NarrateResult): string {
  const { narrative, source, warnings } = result;
  const t = tokens;
  const n = narrative;
  const s: string[] = [];

  const p = t.palette;
  const displayFont = t.typography.display.family;
  const bodyFont = t.typography.body.family;

  // ═══════════════════════════════════════════
  // Header
  // ═══════════════════════════════════════════
  s.push(`# DESIGN.md — ${t.meta.siteName}`);
  s.push("");
  s.push(`> Extracted from [${t.meta.url}](${t.meta.url}) on ${t.meta.capturedAt.slice(0, 10)}`);
  s.push(`> Theme: **${t.theme}**${t.meta.monochrome ? " · monochrome" : ""}`);
  s.push("");

  // ═══════════════════════════════════════════
  // 1. Mood & Atmosphere
  // ═══════════════════════════════════════════
  s.push("## 1. Mood & Atmosphere");
  s.push("");
  s.push(n.mood.summary);
  s.push("");
  s.push(`**Keywords:** ${n.mood.keywords.join(", ")}`);
  s.push("");

  // ═══════════════════════════════════════════
  // 2. Color Palette — full CSS custom properties
  // ═══════════════════════════════════════════
  s.push("## 2. Color Palette");
  s.push("");
  s.push("### CSS Custom Properties (copy-paste ready)");
  s.push("");
  s.push("```css");
  s.push(":root {");
  s.push("  /* Backgrounds */");
  if (p["bg-base"]) s.push(`  --bg-base: ${p["bg-base"]};`);
  if (p["bg-surface-1"]) s.push(`  --bg-surface-1: ${p["bg-surface-1"]};`);
  if (p["bg-surface-2"]) s.push(`  --bg-surface-2: ${p["bg-surface-2"]};`);
  if (p["bg-surface-3"]) s.push(`  --bg-surface-3: ${p["bg-surface-3"]};`);
  s.push("");
  s.push("  /* Text / Ink */");
  if (p["ink-primary"]) s.push(`  --ink-primary: ${p["ink-primary"]};`);
  if (p["ink-secondary"]) s.push(`  --ink-secondary: ${p["ink-secondary"]};`);
  if (p["ink-tertiary"]) s.push(`  --ink-tertiary: ${p["ink-tertiary"]};`);
  if (p["ink-disabled"]) s.push(`  --ink-disabled: ${p["ink-disabled"]};`);
  s.push("");
  s.push("  /* Lines / Borders */");
  if (p["line-subtle"]) s.push(`  --line-subtle: ${p["line-subtle"]};`);
  if (p["line-default"]) s.push(`  --line-default: ${p["line-default"]};`);
  if (p["line-strong"]) s.push(`  --line-strong: ${p["line-strong"]};`);
  s.push("");
  s.push("  /* Accent */");
  if (p["accent-primary"]) s.push(`  --accent-primary: ${p["accent-primary"]};`);
  if (p["accent-secondary"]) s.push(`  --accent-secondary: ${p["accent-secondary"]};`);
  s.push("");
  s.push("  /* Status */");
  if (p["status-error"]) s.push(`  --status-error: ${p["status-error"]};`);
  if (p["status-success"]) s.push(`  --status-success: ${p["status-success"]};`);
  if (p["status-warning"]) s.push(`  --status-warning: ${p["status-warning"]};`);
  s.push("}");
  s.push("```");
  s.push("");

  // Color role table
  s.push("### Color Roles");
  s.push("");
  s.push("| Role | Token | Value | Usage |");
  s.push("|------|-------|-------|-------|");
  if (p["bg-base"]) s.push(`| Page background | \`--bg-base\` | ${p["bg-base"]} | Default page/body background |`);
  if (p["bg-surface-1"]) s.push(`| Surface 1 | \`--bg-surface-1\` | ${p["bg-surface-1"]} | Cards, modals, popovers |`);
  if (p["bg-surface-2"]) s.push(`| Surface 2 | \`--bg-surface-2\` | ${p["bg-surface-2"]} | Nested containers, sidebars |`);
  if (p["ink-primary"]) s.push(`| Primary text | \`--ink-primary\` | ${p["ink-primary"]} | Headings, important labels |`);
  if (p["ink-secondary"]) s.push(`| Secondary text | \`--ink-secondary\` | ${p["ink-secondary"]} | Body text, descriptions |`);
  if (p["ink-tertiary"]) s.push(`| Tertiary text | \`--ink-tertiary\` | ${p["ink-tertiary"]} | Captions, metadata, timestamps |`);
  if (p["ink-disabled"]) s.push(`| Disabled text | \`--ink-disabled\` | ${p["ink-disabled"]} | Disabled inputs, placeholders |`);
  if (p["line-default"]) s.push(`| Default border | \`--line-default\` | ${p["line-default"]} | Card borders, dividers, table lines |`);
  if (p["accent-primary"]) s.push(`| Primary accent | \`--accent-primary\` | ${p["accent-primary"]} | CTAs, links, focus rings, active states |`);
  if (p["accent-secondary"]) s.push(`| Secondary accent | \`--accent-secondary\` | ${p["accent-secondary"]} | Secondary buttons, hover highlights |`);
  s.push("");

  // Semantic names
  if (n.semanticNames.length > 0) {
    s.push("### Semantic Naming Suggestions");
    s.push("");
    s.push("| Token | Suggested Name | Rationale |");
    s.push("|-------|----------------|-----------|");
    for (const sn of n.semanticNames) {
      s.push(`| \`--${sn.token}\` | \`--${sn.name}\` | ${sn.rationale} |`);
    }
    s.push("");
  }

  // ═══════════════════════════════════════════
  // 3. Typography
  // ═══════════════════════════════════════════
  s.push("## 3. Typography");
  s.push("");
  s.push("### Font Stack");
  s.push("");
  s.push("```css");
  s.push(`:root {`);
  const displayFallbacks = t.typography.display.fallbacks.join(", ") || "system-ui, sans-serif";
  const bodyFallbacks = t.typography.body.fallbacks.join(", ") || "system-ui, sans-serif";
  s.push(`  --font-display: '${displayFont}', ${displayFallbacks};`);
  if (displayFont !== bodyFont) {
    s.push(`  --font-body: '${bodyFont}', ${bodyFallbacks};`);
  }
  if (t.typography.mono) {
    const monoFallbacks = t.typography.mono.fallbacks.join(", ") || "ui-monospace, monospace";
    s.push(`  --font-mono: '${t.typography.mono.family}', ${monoFallbacks};`);
  }
  s.push("}");
  s.push("```");
  s.push("");

  s.push("### Type Scale");
  s.push("");
  s.push("| Token | Size | Usage |");
  s.push("|-------|------|-------|");
  const scaleUsage: Record<string, string> = {
    xs: "Fine print, badges",
    sm: "Captions, labels, nav links",
    base: "Body text (default)",
    md: "Subheadings, card titles",
    lg: "Section headings (h3)",
    xl: "Page headings (h2)",
    "2xl": "Hero subheading (h1)",
    "3xl": "Display heading",
    "4xl": "Display hero",
  };
  for (const [key, entry] of Object.entries(t.typography.scale)) {
    if (entry) {
      s.push(`| ${key} | ${entry.fontSize}px | ${scaleUsage[key] ?? ""} |`);
    }
  }
  s.push("");

  // ═══════════════════════════════════════════
  // 4. Spacing
  // ═══════════════════════════════════════════
  s.push("## 4. Spacing");
  s.push("");
  s.push(`Base unit: **${t.spacing.base}px**`);
  s.push("");
  s.push("```css");
  s.push(":root {");
  t.spacing.scale.forEach((v, i) => {
    s.push(`  --space-${i + 1}: ${v}px;`);
  });
  s.push("}");
  s.push("```");
  s.push("");
  s.push(`Scale: \`${t.spacing.scale.join(" · ")}\``);
  s.push("");

  // ═══════════════════════════════════════════
  // 5. Border Radius
  // ═══════════════════════════════════════════
  s.push("## 5. Border Radius");
  s.push("");
  s.push("```css");
  s.push(`:root {`);
  s.push(`  --radius-sm: ${t.radii.sm}px;    /* buttons, inputs, tags */`);
  s.push(`  --radius-md: ${t.radii.md}px;   /* cards, containers */`);
  s.push(`  --radius-lg: ${t.radii.lg}px;   /* modals, large surfaces */`);
  s.push(`  --radius-full: ${t.radii.full}px; /* pills, avatars */`);
  s.push("}");
  s.push("```");
  s.push("");

  // ═══════════════════════════════════════════
  // 6. Shadows
  // ═══════════════════════════════════════════
  if (t.shadows.length > 0) {
    s.push("## 6. Shadows");
    s.push("");
    s.push("```css");
    s.push(":root {");
    for (let i = 0; i < t.shadows.length; i++) {
      s.push(`  --shadow-${i + 1}: ${t.shadows[i]};`);
    }
    s.push("}");
    s.push("```");
    s.push("");
  }

  // ═══════════════════════════════════════════
  // 6b. Gradients
  // ═══════════════════════════════════════════
  if (t.gradients && t.gradients.length > 0) {
    s.push("### Gradients");
    s.push("");
    s.push("```css");
    for (let i = 0; i < t.gradients.length; i++) {
      s.push(`--gradient-${i + 1}: ${t.gradients[i]};`);
    }
    s.push("```");
    s.push("");
  }

  // ═══════════════════════════════════════════
  // 7. Components
  // ═══════════════════════════════════════════
  const comps = t.components;
  const hasComponents =
    comps.primaryButton || comps.secondaryButton || comps.card || comps.input;
  if (hasComponents) {
    s.push("## 7. Components");
    s.push("");
    if (comps.primaryButton) {
      s.push(componentBlock("Primary Button", comps.primaryButton));
      s.push("");
    }
    if (comps.secondaryButton) {
      s.push(componentBlock("Secondary Button", comps.secondaryButton));
      s.push("");
    }
    if (comps.card) {
      s.push(componentBlock("Card", comps.card));
      s.push("");
    }
    if (comps.input) {
      s.push(componentBlock("Input", comps.input));
      s.push("");
    }
  }

  // ═══════════════════════════════════════════
  // 8. Do's and Don'ts
  // ═══════════════════════════════════════════
  s.push("## 8. Do's and Don'ts");
  s.push("");
  s.push("### ✅ Do");
  s.push("");
  for (const d of n.guidelines.dos) {
    s.push(`- **${d.rule}**${d.reason ? ` — *${d.reason}*` : ""}`);
  }
  s.push("");
  s.push("### ❌ Don't");
  s.push("");
  for (const d of n.guidelines.donts) {
    s.push(`- **${d.rule}**${d.reason ? ` — *${d.reason}*` : ""}`);
  }
  s.push("");

  // ═══════════════════════════════════════════
  // 9. Ready-to-Use Prompts
  // ═══════════════════════════════════════════
  s.push("## 9. Ready-to-Use Prompts");
  s.push("");
  s.push("Copy-paste these into your AI coding assistant to generate matching UI:");
  s.push("");
  for (const pr of n.readyPrompts) {
    s.push(`### ${pr.title}`);
    s.push("```");
    s.push(pr.prompt);
    s.push("```");
    s.push("");
  }

  // ═══════════════════════════════════════════
  // 10. Quick-Start CSS Reset
  // ═══════════════════════════════════════════
  s.push("## 10. Quick-Start CSS Reset");
  s.push("");
  s.push("Paste this at the top of your stylesheet to match the extracted design:");
  s.push("");
  s.push("```css");
  s.push("*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }");
  s.push("");
  s.push(`html {`);
  s.push(`  font-family: '${bodyFont}', ${t.typography.body.fallbacks.join(", ") || "system-ui, sans-serif"};`);
  s.push(`  font-size: ${t.typography.scale.base.fontSize}px;`);
  s.push(`  line-height: 1.5;`);
  s.push(`  color: ${p["ink-primary"]};`);
  s.push(`  background: ${p["bg-base"]};`);
  s.push(`  -webkit-font-smoothing: antialiased;`);
  s.push(`}`);
  s.push("");
  s.push(`h1, h2, h3 {`);
  if (displayFont !== bodyFont) {
    s.push(`  font-family: '${displayFont}', ${t.typography.display.fallbacks.join(", ") || "system-ui, sans-serif"};`);
  }
  s.push(`  font-weight: ${t.typography.display.weight};`);
  s.push(`  letter-spacing: -0.02em;`);
  s.push(`  color: ${p["ink-primary"]};`);
  s.push(`}`);
  s.push("```");
  s.push("");

  // ═══════════════════════════════════════════
  // Footer
  // ═══════════════════════════════════════════
  const modeLabel = source === "llm" ? "AI-authored (LLM)" : "Template";
  s.push("---");
  s.push(`*Generated by DesignGrab · Mode: ${modeLabel} · ${t.meta.capturedAt.slice(0, 10)}*`);
  if (warnings.length > 0) {
    s.push("");
    for (const w of warnings) {
      s.push(`> ⚠️ ${w}`);
    }
  }

  return s.join("\n");
}
