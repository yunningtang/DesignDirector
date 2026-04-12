// ─────────────────────────────────────────────
// Layer 2 — NORMALIZE
// Pure functions. Converts raw observations into
// deduplicated, unit-normalized tokens.
// ─────────────────────────────────────────────

import type {
  RawObservations,
  NormalizedTokens,
  NormalizedColor,
  NormalizedFont,
  NormalizedBorder,
  ColorUsage,
  ColorRole,
  FontUsage,
} from "../types/index.js";

// ─── Color parsing ───────────────────────────

/** Parse any CSS color string to [r, g, b, a]. Returns null if unparseable. */
export function parseColor(raw: string): [number, number, number, number] | null {
  const s = raw.trim().toLowerCase();
  if (!s || s === "transparent" || s === "rgba(0, 0, 0, 0)") return null;

  // #rgb
  const hex3 = s.match(/^#([0-9a-f])([0-9a-f])([0-9a-f])$/);
  if (hex3) {
    return [
      parseInt(hex3[1] + hex3[1], 16),
      parseInt(hex3[2] + hex3[2], 16),
      parseInt(hex3[3] + hex3[3], 16),
      1,
    ];
  }

  // #rrggbb
  const hex6 = s.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/);
  if (hex6) {
    return [parseInt(hex6[1], 16), parseInt(hex6[2], 16), parseInt(hex6[3], 16), 1];
  }

  // #rrggbbaa
  const hex8 = s.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/);
  if (hex8) {
    return [
      parseInt(hex8[1], 16),
      parseInt(hex8[2], 16),
      parseInt(hex8[3], 16),
      parseInt(hex8[4], 16) / 255,
    ];
  }

  // rgb(r, g, b) or rgba(r, g, b, a)
  const rgbMatch = s.match(
    /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)$/
  );
  if (rgbMatch) {
    return [
      parseInt(rgbMatch[1]),
      parseInt(rgbMatch[2]),
      parseInt(rgbMatch[3]),
      rgbMatch[4] !== undefined ? parseFloat(rgbMatch[4]) : 1,
    ];
  }

  return null;
}

/** Convert RGB to HSL. Returns [h (0-360), s (0-100), l (0-100)]. */
export function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;

  if (max === min) return [0, 0, Math.round(l * 100)];

  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

  let h = 0;
  if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
  else if (max === g) h = ((b - r) / d + 2) / 6;
  else h = ((r - g) / d + 4) / 6;

  return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
}

/** Convert RGBA to canonical 6-digit hex (ignoring alpha for the hex). */
export function rgbToHex(r: number, g: number, b: number): string {
  const toHex = (n: number) => n.toString(16).padStart(2, "0");
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

// ─── CSS value parsing ───────────────────────

/** Parse a CSS pixel value like "16px" to a number. Returns null for non-px. */
export function parsePx(raw: string): number | null {
  const match = raw.trim().match(/^([\d.]+)px$/);
  return match ? parseFloat(match[1]) : null;
}

/** Parse font-weight string to a number. */
export function parseFontWeight(raw: string): number {
  const n = parseInt(raw);
  if (!isNaN(n)) return n;
  const map: Record<string, number> = {
    normal: 400,
    bold: 700,
    lighter: 300,
    bolder: 700,
  };
  return map[raw.toLowerCase()] ?? 400;
}

/** Extract primary font family from a font-family string. */
export function parseFontFamily(raw: string): { family: string; fallbacks: string[] } {
  const parts = raw
    .split(",")
    .map((s) => s.trim().replace(/^["']|["']$/g, ""))
    .filter(Boolean);

  return {
    family: parts[0] ?? "sans-serif",
    fallbacks: parts.slice(1),
  };
}

// ─── Determine color role from CSS property ──

function colorRoleFromProperty(property: string): ColorRole {
  if (property === "background-color") return "background";
  if (property === "color") return "text";
  if (property.includes("border")) return "border";
  if (property === "box-shadow") return "shadow";
  if (property === "outline-color") return "outline";
  return "fill";
}

// ─── Main normalize function ─────────────────

/** Pick the most frequently used radius from a count map, or null if empty. */
function getMostCommonRadius(map: Map<number, number>): number | null {
  if (map.size === 0) return null;
  let best: number | null = null;
  let bestCount = 0;
  for (const [r, count] of map) {
    if (count > bestCount) { best = r; bestCount = count; }
  }
  return best;
}

export function normalize(raw: RawObservations): NormalizedTokens {
  // Accumulators
  const colorMap = new Map<string, NormalizedColor>();
  const fontMap = new Map<string, NormalizedFont>();
  const spacingSet = new Set<number>();
  const radiiSet = new Set<number>();
  const radiiByComponent = {
    button: new Map<number, number>(),
    input: new Map<number, number>(),
    card: new Map<number, number>(),
  };
  const shadowSet = new Set<string>();
  const borderMap = new Map<string, NormalizedBorder>();
  const gradientSet = new Set<string>();

  // Keys match the camelCase names from STYLE_KEYS in capture.ts
  const colorProperties: Array<{ prop: string; role: ColorRole }> = [
    { prop: "backgroundColor", role: "background" },
    { prop: "color", role: "text" },
    { prop: "borderTopColor", role: "border" },
  ];

  const spacingProperties = [
    "paddingTop",
    "paddingRight",
    "paddingBottom",
    "paddingLeft",
    "marginTop",
    "marginRight",
    "marginBottom",
    "marginLeft",
    "gap",
  ];

  for (const el of raw.elements) {
    const area = el.boundingRect.width * el.boundingRect.height;

    // ── Colors ──
    for (const { prop, role } of colorProperties) {
      const rawValue = el.styles[prop];
      if (!rawValue) continue;

      const parsed = parseColor(rawValue);
      if (!parsed) continue;

      const [r, g, b, a] = parsed;
      if (a < 0.05) continue; // skip fully transparent

      const hex = rgbToHex(r, g, b);
      const hsl = rgbToHsl(r, g, b);

      if (!colorMap.has(hex)) {
        colorMap.set(hex, {
          hex,
          rgb: [r, g, b],
          hsl,
          alpha: a,
          usages: [],
          totalCount: 0,
          totalArea: 0,
        });
      }

      const entry = colorMap.get(hex)!;
      entry.totalCount++;
      entry.totalArea += area;
      // Solid-fill usage proves this color is a real token, not just a gradient stop
      entry.fromGradient = false;

      // Merge into existing usage or create new
      const existing = entry.usages.find(
        (u) => u.role === role && u.tagName === el.tagName
      );
      if (existing) {
        existing.count++;
        existing.areaPx += area;
        existing.isInteractive = existing.isInteractive || el.isInteractive;
      } else {
        entry.usages.push({
          role,
          tagName: el.tagName,
          count: 1,
          areaPx: area,
          isInteractive: el.isInteractive,
        });
      }
    }

    // ── Gradient colors ──
    // Extract individual colors from CSS gradients like linear-gradient(135deg, #635BFF, #0073E6)
    const bgImage = el.styles["backgroundImage"];
    if (bgImage && bgImage !== "none" && bgImage.includes("gradient")) {
      // Store the raw gradient string (deduplicated)
      gradientSet.add(bgImage);
      // Pull all rgb/rgba/hex color stops out of the gradient string
      const rgbMatches = bgImage.matchAll(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)/g);
      for (const m of rgbMatches) {
        const [r, g, b] = [parseInt(m[1]), parseInt(m[2]), parseInt(m[3])];
        const a = m[4] !== undefined ? parseFloat(m[4]) : 1;
        if (a < 0.05) continue;
        const hex = rgbToHex(r, g, b);
        const hsl = rgbToHsl(r, g, b);
        const isNew = !colorMap.has(hex);
        if (isNew) {
          colorMap.set(hex, { hex, rgb: [r, g, b], hsl, alpha: a, usages: [], totalCount: 0, totalArea: 0, fromGradient: true });
        }
        const entry = colorMap.get(hex)!;
        entry.totalCount++;
        entry.totalArea += area;
        const existing = entry.usages.find(u => u.role === "background" && u.tagName === el.tagName);
        if (existing) { existing.count++; existing.areaPx += area; }
        else { entry.usages.push({ role: "background", tagName: el.tagName, count: 1, areaPx: area, isInteractive: el.isInteractive }); }
      }
    }

    // ── Fonts ──
    const rawFamily = el.styles["fontFamily"];
    if (rawFamily) {
      const { family, fallbacks } = parseFontFamily(rawFamily);
      if (!fontMap.has(family)) {
        fontMap.set(family, {
          family,
          fallbacks,
          usages: [],
          totalCount: 0,
        });
      }
      const fontEntry = fontMap.get(family)!;
      fontEntry.totalCount++;

      const fontSize = parsePx(el.styles["fontSize"] ?? "") ?? 16;
      const fontWeight = parseFontWeight(el.styles["fontWeight"] ?? "400");

      fontEntry.usages.push({
        tagName: el.tagName,
        fontSize,
        fontWeight,
        count: 1,
      });
    }

    // ── Spacings ──
    for (const prop of spacingProperties) {
      const val = parsePx(el.styles[prop] ?? "");
      if (val !== null && val > 0 && val <= 200) {
        spacingSet.add(Math.round(val));
      }
    }

    // ── Radii ──
    const radius = parsePx(el.styles["borderRadius"] ?? "");
    if (radius !== null && radius > 0) {
      radiiSet.add(Math.round(radius));
    }

    // ── Radii by component type ──
    if (radius !== null && radius > 0) {
      const r = Math.round(radius);
      if (el.isInteractive || el.tagName === "BUTTON" || el.tagName === "A") {
        if (!radiiByComponent.button.has(r)) radiiByComponent.button.set(r, 0);
        radiiByComponent.button.set(r, radiiByComponent.button.get(r)! + 1);
      }
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA" || el.tagName === "SELECT") {
        if (!radiiByComponent.input.has(r)) radiiByComponent.input.set(r, 0);
        radiiByComponent.input.set(r, radiiByComponent.input.get(r)! + 1);
      }
      // Larger elements with radius are likely cards/containers
      const w = el.boundingRect?.width ?? 0;
      const h = el.boundingRect?.height ?? 0;
      if (w > 150 && h > 80 && !el.isInteractive) {
        if (!radiiByComponent.card.has(r)) radiiByComponent.card.set(r, 0);
        radiiByComponent.card.set(r, radiiByComponent.card.get(r)! + 1);
      }
    }

    // ── Shadows ──
    const shadow = el.styles["boxShadow"];
    if (shadow && shadow !== "none") {
      shadowSet.add(shadow);
    }

    // ── Borders ──
    const borderWidth = parsePx(el.styles["borderTopWidth"] ?? "");
    const borderStyle = el.styles["borderTopStyle"];
    const borderColor = el.styles["borderTopColor"];
    if (borderWidth && borderWidth > 0 && borderStyle && borderStyle !== "none" && borderColor) {
      const key = `${borderWidth}|${borderStyle}|${borderColor}`;
      if (borderMap.has(key)) {
        borderMap.get(key)!.count++;
      } else {
        borderMap.set(key, {
          width: borderWidth,
          style: borderStyle,
          color: borderColor,
          count: 1,
        });
      }
    }
  }

  // Resolve CSS variables to final values
  const resolvedVars: Record<string, string> = {};
  for (const [key, value] of Object.entries(raw.cssVariables)) {
    // Already resolved by getComputedStyle in the browser, but strip whitespace
    resolvedVars[key] = value.trim();
  }

  return {
    colors: Array.from(colorMap.values()).sort((a, b) => b.totalArea - a.totalArea),
    fonts: Array.from(fontMap.values()).sort((a, b) => b.totalCount - a.totalCount),
    spacings: Array.from(spacingSet).sort((a, b) => a - b),
    radii: Array.from(radiiSet).sort((a, b) => a - b),
    radiiByComponent: {
      button: getMostCommonRadius(radiiByComponent.button),
      input: getMostCommonRadius(radiiByComponent.input),
      card: getMostCommonRadius(radiiByComponent.card),
    },
    shadows: Array.from(shadowSet),
    borders: Array.from(borderMap.values()).sort((a, b) => b.count - a.count),
    gradients: Array.from(gradientSet).slice(0, 8),
    cssVariables: resolvedVars,
  };
}
