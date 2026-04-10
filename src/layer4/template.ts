// ─────────────────────────────────────────────
// Layer 4 — Template-based narrator (no LLM)
// Generates a correct but "dry" narrative from
// heuristic rules. Used as default / fallback.
// ─────────────────────────────────────────────

import type { Narrative, SemanticTokens } from "../types/index.js";

export function narrateWithTemplate(tokens: SemanticTokens): Narrative {
  const t = tokens;
  const theme = t.theme;
  const hasAccent = t.palette["accent-primary"] && !t.meta.monochrome;
  const displayFont = t.typography.display.family;
  const bodyFont = t.typography.body.family;
  const hasMono = !!t.typography.mono;
  const lineColor = t.palette["line-default"] ?? t.palette["line-subtle"];

  // ── Mood ──
  const surfaceDesc = theme === "dark"
    ? "Dark surfaces layered for depth with subtle elevation steps"
    : "Clean light surfaces with subtle layering and generous whitespace";
  const accentDesc = hasAccent
    ? `a single accent color (${t.palette["accent-primary"]}) used with restraint on CTAs and interactive elements`
    : "a monochrome palette where the primary ink color doubles as the accent";
  const fontDesc =
    displayFont === bodyFont
      ? `${bodyFont} as the sole typeface`
      : `${displayFont} for display headings and ${bodyFont} for body text`;

  const summary = `A ${theme}-themed interface built on ${fontDesc}. ${surfaceDesc}, with ${accentDesc}. The spacing system follows a strict ${t.spacing.base}px base grid. The overall aesthetic is ${theme === "dark" ? "technical, focused, and data-dense" : "clean, professional, and content-forward"}.`;

  const keywords: string[] = [
    theme,
    t.meta.monochrome ? "monochrome" : "accent-driven",
    t.spacing.base === 8 ? "8px-grid" : "4px-grid",
  ];
  if (theme === "dark") keywords.push("technical", "focused", "layered");
  else keywords.push("clean", "professional", "airy");
  if (displayFont !== bodyFont) keywords.push("dual-typeface");

  // ── Semantic names ──
  const semanticNames: Narrative["semanticNames"] = [];
  if (hasAccent && t.palette["accent-primary"]) {
    semanticNames.push({
      token: "accent-primary",
      name: "brand-accent",
      rationale: "Primary interactive color — CTAs, focus rings, active states.",
    });
  }
  if (t.palette["accent-secondary"]) {
    semanticNames.push({
      token: "accent-secondary",
      name: "brand-secondary",
      rationale: "Supporting accent for secondary actions, links, hover states.",
    });
  }
  if (lineColor) {
    semanticNames.push({
      token: "line-default",
      name: "divider",
      rationale: "Default border and separator color for cards, tables, and sections.",
    });
  }
  if (t.palette["bg-surface-1"]) {
    semanticNames.push({
      token: "bg-surface-1",
      name: "surface-raised",
      rationale: "First elevation layer — cards, dropdowns, popovers.",
    });
  }

  // ── Do's ──
  const dos: Narrative["guidelines"]["dos"] = [
    {
      rule: `Use ${displayFont} for all display headings (h1-h3), ${bodyFont} for body and UI text.`,
      reason: "Maintains the typographic hierarchy observed on the site.",
    },
    {
      rule: `Base all spacing on the ${t.spacing.base}px grid: ${t.spacing.scale.slice(0, 8).join(", ")}px.`,
      reason: "Keeps vertical rhythm and horizontal alignment consistent.",
    },
    {
      rule: `Use border-radius ${t.radii.md}px for cards and containers, ${t.radii.sm}px for buttons and inputs, ${t.radii.full}px for pills and avatars.`,
      reason: "Matches the three-tier radius scale observed in components.",
    },
  ];

  if (hasAccent) {
    dos.push({
      rule: `Reserve ${t.palette["accent-primary"]} for primary CTAs, focus rings, and active states only.`,
      reason: "The site uses accent color sparingly — overuse dilutes its impact.",
    });
  } else {
    dos.push({
      rule: "Stay monochrome — use font weight, size, and opacity to create hierarchy.",
      reason: "This design language intentionally avoids chromatic accents.",
    });
  }

  if (t.palette["bg-surface-1"]) {
    dos.push({
      rule: `Use ${t.palette["bg-surface-1"]} for elevated surfaces (cards, modals), not ${t.palette["bg-base"]}.`,
      reason: "Creates visual depth through surface layering.",
    });
  }

  if (lineColor) {
    dos.push({
      rule: `Use ${lineColor} for all borders and dividers — keep them 1px solid.`,
      reason: "Consistent, subtle lines maintain the design's restrained feel.",
    });
  }

  // ── Don'ts ──
  const donts: Narrative["guidelines"]["donts"] = [
    {
      rule: "Don't introduce colors outside the extracted palette.",
      reason: "Even one off-palette color breaks the visual system.",
    },
    {
      rule: `Don't use font sizes outside the type scale (base: ${t.typography.scale.base.fontSize}px).`,
      reason: "Ad-hoc sizes create visual noise and inconsistent hierarchy.",
    },
    {
      rule: "Don't mix border-radius values — stick to the sm/md/lg/full scale.",
      reason: "Inconsistent rounding is one of the most visible design bugs.",
    },
    {
      rule: `Don't use spacing values that aren't multiples of ${t.spacing.base}px.`,
      reason: "Off-grid spacing breaks alignment and looks unpolished.",
    },
  ];

  if (theme === "dark") {
    donts.push({
      rule: "Don't use pure white (#ffffff) for body text — use the extracted ink-primary instead.",
      reason: "Pure white on dark backgrounds causes eye strain and glare.",
    });
    donts.push({
      rule: "Don't use light shadows (rgba with white) — use inset borders or opacity layers.",
      reason: "Light shadows are invisible on dark surfaces.",
    });
  } else {
    donts.push({
      rule: "Don't use pure black (#000000) for large text blocks — use the extracted ink-primary.",
      reason: "The site uses a softer near-black for comfortable reading.",
    });
    donts.push({
      rule: "Don't use heavy drop shadows — prefer subtle elevation (opacity < 0.1).",
      reason: "The design uses light, diffused shadows for depth.",
    });
  }

  // ── Ready prompts ──
  const accent = t.palette["accent-primary"] ?? t.palette["ink-primary"];
  const bg1 = t.palette["bg-surface-1"] ?? t.palette["bg-base"];
  const ink2 = t.palette["ink-secondary"] ?? t.palette["ink-primary"];

  const readyPrompts: Narrative["readyPrompts"] = [
    {
      title: "Hero section",
      prompt: `Build a hero section matching ${t.meta.siteName}'s design system. Background: ${t.palette["bg-base"]}. Heading: ${displayFont}, ${t.typography.scale["3xl"]?.fontSize ?? t.typography.scale["2xl"]?.fontSize ?? 48}px, weight ${t.typography.display.weight}, color ${t.palette["ink-primary"]}, letter-spacing -0.035em. Subheading: ${bodyFont}, ${t.typography.scale.md?.fontSize ?? 18}px, color ${ink2}, line-height 1.5, max-width 540px. Primary CTA: background ${accent}, color ${theme === "dark" ? t.palette["bg-base"] : "#ffffff"}, padding ${t.spacing.scale[3] ?? 12}px ${t.spacing.scale[5] ?? 24}px, border-radius ${t.radii.sm}px, font-size ${t.typography.scale.sm?.fontSize ?? 14}px, weight 500. Section padding: ${t.spacing.scale[7] ?? 64}px vertical.`,
      tokenRefs: ["bg-base", "ink-primary", "accent-primary"],
    },
    {
      title: "Card component",
      prompt: `Create a card component for ${t.meta.siteName}: background ${bg1}, border-radius ${t.radii.md}px, padding ${t.spacing.scale[5] ?? 24}px. ${lineColor ? `Border: 1px solid ${lineColor}.` : "No border."} Card title: ${displayFont}, ${t.typography.scale.md?.fontSize ?? 18}px, weight ${t.typography.display.weight}, color ${t.palette["ink-primary"]}. Card body: ${bodyFont}, ${t.typography.scale.base.fontSize}px, color ${ink2}, line-height 1.6. If the card has a footer, separate with 1px ${lineColor ?? "border"} and ${t.spacing.scale[4] ?? 20}px top padding. Cards should stack in a grid with ${t.spacing.scale[4] ?? 20}px gap.`,
      tokenRefs: ["bg-surface-1", "ink-primary", "line-default"],
    },
    {
      title: "Navigation bar",
      prompt: `Build a sticky nav bar for ${t.meta.siteName}: height 64px, background ${t.palette["bg-base"]} with backdrop-filter blur(12px) and ${lineColor ? `border-bottom: 1px solid ${lineColor}` : "no border"}. Logo on the left: ${bodyFont}, 18px, weight 700, color ${t.palette["ink-primary"]}. Nav links: ${bodyFont}, ${t.typography.scale.sm?.fontSize ?? 14}px, weight 500, color ${ink2}, ${t.spacing.scale[5] ?? 32}px gap. Right side CTA button: background ${accent}, color ${theme === "dark" ? t.palette["bg-base"] : "#ffffff"}, padding 8px 20px, border-radius ${t.radii.full}px. Max-width 1440px, centered, horizontal padding ${t.spacing.scale[6] ?? 48}px.`,
      tokenRefs: ["bg-base", "ink-secondary", "accent-primary"],
    },
    {
      title: "Form / Input field",
      prompt: `Style form inputs for ${t.meta.siteName}: height 44px, background ${t.palette["bg-base"]}, border 1px solid ${lineColor ?? t.palette["ink-disabled"] ?? "#e0e0e0"}, border-radius ${t.radii.sm}px, padding 0 ${t.spacing.scale[3] ?? 14}px. Font: ${bodyFont}, ${t.typography.scale.base.fontSize}px, color ${t.palette["ink-primary"]}. Placeholder color: ${t.palette["ink-disabled"] ?? t.palette["ink-tertiary"] ?? "#999"}. Focus state: border-color ${accent}, box-shadow 0 0 0 3px ${accent}20. Labels: ${bodyFont}, ${t.typography.scale.sm?.fontSize ?? 13}px, weight 500, color ${ink2}, margin-bottom 6px.`,
      tokenRefs: ["bg-base", "ink-primary", "accent-primary", "line-default"],
    },
  ];

  return {
    mood: { summary, keywords },
    semanticNames,
    guidelines: { dos, donts },
    readyPrompts,
  };
}
