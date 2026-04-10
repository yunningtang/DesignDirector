// ─────────────────────────────────────────────
// Layer 3 — CLASSIFY
// Heuristic rules that assign semantic meaning
// to normalized tokens. Pure functions, no I/O.
// ─────────────────────────────────────────────

import type {
  NormalizedTokens,
  NormalizedColor,
  NormalizedFont,
  SemanticTokens,
  FontSpec,
  TypeScale,
  ComponentSpec,
  RawObservations,
} from "../types/index.js";

// ─── Helpers ─────────────────────────────────

function isGrayscale(c: NormalizedColor): boolean {
  return c.hsl[1] < 15;
}

function isSaturated(c: NormalizedColor, threshold = 30): boolean {
  return c.hsl[1] >= threshold;
}

function isBackground(c: NormalizedColor): boolean {
  return c.usages.some((u) => u.role === "background");
}

function isText(c: NormalizedColor): boolean {
  return c.usages.some((u) => u.role === "text");
}

function bgArea(c: NormalizedColor): number {
  return c.usages
    .filter((u) => u.role === "background")
    .reduce((sum, u) => sum + u.areaPx, 0);
}

function textCount(c: NormalizedColor): number {
  return c.usages
    .filter((u) => u.role === "text")
    .reduce((sum, u) => sum + u.count, 0);
}

/** How "accenty" a color is on interactive elements. Count-based, not area-based. */
function interactiveWeight(c: NormalizedColor): number {
  return c.usages
    .filter((u) => u.isInteractive)
    .reduce((sum, u) => sum + u.count, 0);
}

function isMono(f: NormalizedFont): boolean {
  return /mono|code|menlo|consolas|courier|fira\s*code/i.test(f.family);
}

/** Find the closest value in a sorted array. */
function closest(arr: number[], target: number): number {
  let best = arr[0];
  let bestDist = Math.abs(target - best);
  for (const v of arr) {
    const d = Math.abs(target - v);
    if (d < bestDist) {
      best = v;
      bestDist = d;
    }
  }
  return best;
}

// ─── Theme detection ─────────────────────────

function detectTheme(colors: NormalizedColor[]): "light" | "dark" {
  const bgColors = colors.filter(isBackground);
  if (bgColors.length === 0) return "light";

  // Take the largest-area background
  bgColors.sort((a, b) => bgArea(b) - bgArea(a));
  const topBg = bgColors[0];
  return topBg.hsl[2] < 50 ? "dark" : "light";
}

// ─── Palette classification ──────────────────

/** Lightness distance between two colors. */
function lightnessDist(a: NormalizedColor, b: NormalizedColor): number {
  return Math.abs(a.hsl[2] - b.hsl[2]);
}

function classifyPalette(
  colors: NormalizedColor[],
  theme: "light" | "dark",
  totalPageArea: number
): SemanticTokens["palette"] {
  const palette: SemanticTokens["palette"] = {
    "bg-base": "#ffffff",
    "bg-surface-1": null,
    "bg-surface-2": null,
    "bg-surface-3": null,
    "ink-primary": "#000000",
    "ink-secondary": null,
    "ink-tertiary": null,
    "ink-disabled": null,
    "line-subtle": null,
    "line-default": null,
    "line-strong": null,
    "accent-primary": null,
    "accent-secondary": null,
    "status-error": null,
    "status-success": null,
    "status-warning": null,
  };

  // Track which hex values are already claimed so we don't double-assign
  const claimed = new Set<string>();

  // ── Background stack ──
  // Only grayscale backgrounds, sorted by lightness for layering
  const bgCandidates = colors
    .filter((c) => isBackground(c) && isGrayscale(c));

  const bgSorted =
    theme === "dark"
      ? [...bgCandidates].sort((a, b) => a.hsl[2] - b.hsl[2])
      : [...bgCandidates].sort((a, b) => b.hsl[2] - a.hsl[2]);

  if (bgSorted[0]) {
    palette["bg-base"] = bgSorted[0].hex;
    claimed.add(bgSorted[0].hex);
  }

  // Surfaces must be distinct from bg-base but on the same "side" of lightness.
  // On light themes, surfaces are light (lightness > 50).
  // On dark themes, surfaces are dark (lightness < 50).
  // This prevents dark hero sections on a light site from being classified as surfaces.
  const bgBase = bgSorted[0];
  const surfaceCandidates = bgBase
    ? bgSorted.filter((c) => {
        if (c.hex === bgBase.hex) return false;
        if (lightnessDist(c, bgBase) < 1) return false;
        // Must be on the same side as bg-base
        if (theme === "light" && c.hsl[2] < 50) return false;
        if (theme === "dark" && c.hsl[2] > 50) return false;
        return true;
      })
    : [];

  // Deduplicate: keep only distinct lightness steps (gap >= 2 between each)
  const surfaces: NormalizedColor[] = [];
  for (const c of surfaceCandidates) {
    if (surfaces.length >= 3) break;
    const tooClose = surfaces.some((s) => lightnessDist(s, c) < 2);
    if (!tooClose) {
      surfaces.push(c);
      claimed.add(c.hex);
    }
  }
  if (surfaces[0]) palette["bg-surface-1"] = surfaces[0].hex;
  if (surfaces[1]) palette["bg-surface-2"] = surfaces[1].hex;
  if (surfaces[2]) palette["bg-surface-3"] = surfaces[2].hex;

  // ── Ink (text colors) ──
  // Only grayscale or very low-saturation text colors for ink slots.
  // Saturated text colors (like Stripe's purple links) belong in accent, not ink.
  const inkCandidates = colors
    .filter((c) => isText(c) && isGrayscale(c))
    .sort((a, b) => textCount(b) - textCount(a));

  // Sort by contrast: highest contrast first
  const inkSorted =
    theme === "dark"
      ? [...inkCandidates].sort((a, b) => b.hsl[2] - a.hsl[2])
      : [...inkCandidates].sort((a, b) => a.hsl[2] - b.hsl[2]);

  // Only assign ink if it's not already claimed as a bg color,
  // EXCEPT ink-primary (black can be both bg-base in dark themes and ink)
  const inkSlots: (keyof typeof palette)[] = [
    "ink-primary",
    "ink-secondary",
    "ink-tertiary",
    "ink-disabled",
  ];
  let inkIdx = 0;
  for (const c of inkSorted) {
    if (inkIdx >= inkSlots.length) break;
    // ink-primary is allowed to overlap bg; others shouldn't
    if (inkIdx > 0 && claimed.has(c.hex)) continue;
    palette[inkSlots[inkIdx]] = c.hex;
    claimed.add(c.hex);
    inkIdx++;
  }

  // ── Lines / borders ──
  // Line colors should sit between bg and ink in lightness.
  // Exclude colors that are too close to pure white or pure black
  // (those are likely ink or bg reused as borders, not true "line" tokens).
  const bgBaseLightness = bgBase?.hsl[2] ?? (theme === "dark" ? 0 : 100);
  const inkPrimaryLightness = inkSorted[0]?.hsl[2] ?? (theme === "dark" ? 100 : 0);
  const midLightness = (bgBaseLightness + inkPrimaryLightness) / 2;

  const lineCandidates = colors
    .filter((c) => {
      if (!c.usages.some((u) => u.role === "border")) return false;
      if (!isGrayscale(c)) return false;
      // Must not be at either extreme — should be "in between"
      const distFromBg = Math.abs(c.hsl[2] - bgBaseLightness);
      const distFromInk = Math.abs(c.hsl[2] - inkPrimaryLightness);
      return distFromBg >= 5 && distFromInk >= 5;
    })
    .sort((a, b) => {
      // Prefer colors closer to the midpoint between bg and ink
      const aDist = Math.abs(a.hsl[2] - midLightness);
      const bDist = Math.abs(b.hsl[2] - midLightness);
      return aDist - bDist;
    });

  if (lineCandidates[0]) {
    palette["line-default"] = lineCandidates[0].hex;
    claimed.add(lineCandidates[0].hex);
  }
  if (lineCandidates.length >= 2) {
    // Among remaining, pick one closer to bg (subtle) and one closer to ink (strong)
    const rest = lineCandidates.slice(1);
    const subtle = rest.find((c) =>
      theme === "dark" ? c.hsl[2] < midLightness : c.hsl[2] > midLightness
    );
    const strong = rest.find((c) =>
      theme === "dark" ? c.hsl[2] >= midLightness : c.hsl[2] <= midLightness
    );
    if (subtle && subtle.hex !== palette["line-default"]) {
      palette["line-subtle"] = subtle.hex;
    }
    if (strong && strong.hex !== palette["line-default"] && strong.hex !== palette["line-subtle"]) {
      palette["line-strong"] = strong.hex;
    }
  }

  // ── Accent colors ──
  // Saturated colors that appear on interactive elements (as bg OR text).
  // Key insight: accent can be a text color on buttons/links (e.g. Stripe purple),
  // not just a background color.
  const accentCandidates = colors
    .filter((c) => {
      if (!isSaturated(c, 25)) return false;
      if (claimed.has(c.hex)) return false;
      // Exclude colors that are used as large backgrounds (full-page hero etc.)
      // Check max single-usage area, not total (many small buttons add up > viewport)
      const maxSingleBgArea = Math.max(
        0,
        ...c.usages
          .filter((u) => u.role === "background")
          .map((u) => u.areaPx / u.count) // average area per element
      );
      if (maxSingleBgArea / totalPageArea > 0.3) return false;
      return true;
    })
    .sort((a, b) => {
      // Score = interactive count * saturation multiplier
      // A vivid color (sat 90) on 100 buttons beats a pale color (sat 40) on 100 buttons
      const aSat = a.hsl[1] / 100; // 0..1
      const bSat = b.hsl[1] / 100;
      const aScore = interactiveWeight(a) * (0.5 + aSat) + a.hsl[1] * 3;
      const bScore = interactiveWeight(b) * (0.5 + bSat) + b.hsl[1] * 3;
      return bScore - aScore;
    });

  if (accentCandidates[0]) {
    palette["accent-primary"] = accentCandidates[0].hex;
    claimed.add(accentCandidates[0].hex);
  }
  if (accentCandidates[1]) {
    palette["accent-secondary"] = accentCandidates[1].hex;
    claimed.add(accentCandidates[1].hex);
  }

  // ── Status colors (heuristic by hue) ──
  // Only assign if not already claimed as accent
  const saturatedColors = colors.filter(
    (c) => isSaturated(c, 40) && !claimed.has(c.hex)
  );
  for (const c of saturatedColors) {
    const [h, s] = c.hsl;
    // Red/error: hue 340-360 or 0-20
    if (!palette["status-error"] && ((h >= 340 && s > 50) || (h <= 20 && s > 50))) {
      palette["status-error"] = c.hex;
    }
    // Green/success: hue 90-170
    if (!palette["status-success"] && h >= 90 && h <= 170 && s > 30) {
      palette["status-success"] = c.hex;
    }
    // Yellow-orange/warning: hue 30-55
    if (!palette["status-warning"] && h >= 30 && h <= 55 && s > 40) {
      palette["status-warning"] = c.hex;
    }
  }

  return palette;
}

// ─── Typography classification ───────────────

function classifyTypography(fonts: NormalizedFont[]): SemanticTokens["typography"] {
  const nonMono = fonts.filter((f) => !isMono(f));
  const mono = fonts.find((f) => isMono(f)) ?? null;

  // Display font: used at largest sizes (h1/h2 or fontSize > 36)
  const displayFont = nonMono.find((f) =>
    f.usages.some((u) => u.fontSize > 36 || u.tagName === "H1" || u.tagName === "H2")
  );

  // Body font: highest total count
  const bodyFont = nonMono.sort((a, b) => b.totalCount - a.totalCount)[0];

  const toSpec = (f: NormalizedFont | undefined | null): FontSpec => ({
    family: f?.family ?? "sans-serif",
    fallbacks: f?.fallbacks ?? [],
    weight: f?.usages[0]?.fontWeight ?? 400,
  });

  // Build type scale from all observed font sizes
  const allSizes = new Set<number>();
  for (const f of fonts) {
    for (const u of f.usages) {
      allSizes.add(Math.round(u.fontSize));
    }
  }
  const sortedSizes = Array.from(allSizes).sort((a, b) => a - b);

  const scale: TypeScale = {
    base: { fontSize: 16 },
  };

  if (sortedSizes.length >= 2) {
    // Find the most common size (likely body/base)
    const sizeFreq = new Map<number, number>();
    for (const f of fonts) {
      for (const u of f.usages) {
        const s = Math.round(u.fontSize);
        sizeFreq.set(s, (sizeFreq.get(s) ?? 0) + u.count);
      }
    }
    const baseFontSize = [...sizeFreq.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? 16;
    scale.base = { fontSize: baseFontSize };

    // Assign sizes relative to base
    const below = sortedSizes.filter((s) => s < baseFontSize);
    const above = sortedSizes.filter((s) => s > baseFontSize);

    if (below.length >= 2) scale.xs = { fontSize: below[0] };
    if (below.length >= 1) scale.sm = { fontSize: below[below.length - 1] };

    if (above.length >= 1) scale.md = { fontSize: above[0] };
    if (above.length >= 2) scale.lg = { fontSize: above[1] };
    if (above.length >= 3) scale.xl = { fontSize: above[2] };
    if (above.length >= 4) scale["2xl"] = { fontSize: above[3] };
    if (above.length >= 5) scale["3xl"] = { fontSize: above[4] };
    if (above.length >= 6) scale["4xl"] = { fontSize: above[5] };
  }

  return {
    display: toSpec(displayFont ?? bodyFont),
    body: toSpec(bodyFont),
    mono: mono ? toSpec(mono) : null,
    scale,
  };
}

// ─── Spacing classification ──────────────────

function classifySpacing(spacings: number[]): SemanticTokens["spacing"] {
  if (spacings.length === 0) return { base: 4, scale: [4, 8, 12, 16, 24, 32, 48, 64] };

  // Count how many values are multiples of 4 vs 8
  const mult4 = spacings.filter((s) => s % 4 === 0).length;
  const mult8 = spacings.filter((s) => s % 8 === 0).length;
  const base = mult8 / spacings.length > 0.6 ? 8 : 4;

  // Keep only multiples of base, take the top 8 by frequency
  const onGrid = spacings.filter((s) => s % base === 0);
  const scale = onGrid.length > 0 ? onGrid.slice(0, 10) : spacings.slice(0, 10);

  return { base, scale };
}

// ─── Radii classification ────────────────────

function classifyRadii(radii: number[]): SemanticTokens["radii"] {
  if (radii.length === 0) return { sm: 4, md: 8, lg: 16, full: 999 };

  const sorted = [...radii].sort((a, b) => a - b);
  const nonFull = sorted.filter((r) => r < 100);
  const full = sorted.find((r) => r >= 100) ?? 999;

  if (nonFull.length === 0) return { sm: 4, md: 8, lg: 16, full };
  if (nonFull.length === 1) return { sm: nonFull[0], md: nonFull[0], lg: nonFull[0], full };
  if (nonFull.length === 2) return { sm: nonFull[0], md: nonFull[1], lg: nonFull[1], full };

  // Pick 3 spread across the range
  const sm = nonFull[0];
  const lg = nonFull[nonFull.length - 1];
  const mid = nonFull[Math.floor(nonFull.length / 2)];

  return { sm, md: mid, lg, full };
}

// ─── Component extraction ────────────────────

function extractComponents(
  raw: RawObservations,
  palette: SemanticTokens["palette"],
  theme: "light" | "dark"
): SemanticTokens["components"] {
  // Only real button-like elements (not every <a> tag)
  const buttons = raw.elements.filter(
    (el) =>
      el.isInteractive &&
      (el.tagName === "BUTTON" ||
        el.classNames.some((c) => /btn|button|cta/i.test(c)) ||
        el.role === "button")
  );

  // Also include <a> tags that look like buttons (have padding + border-radius)
  const buttonishLinks = raw.elements.filter(
    (el) =>
      el.tagName === "A" &&
      el.isInteractive &&
      parsePxSimple(el.styles["paddingLeft"]) >= 8 &&
      parsePxSimple(el.styles["paddingTop"]) >= 4 &&
      parsePxSimple(el.styles["borderRadius"]) >= 2
  );

  const allButtons = [...buttons, ...buttonishLinks];
  const aboveFold = allButtons.filter((b) => b.boundingRect.y < 900);

  let primaryButton: ComponentSpec | null = null;
  let secondaryButton: ComponentSpec | null = null;

  // Score each button candidate
  const scored = aboveFold.map((btn) => {
    const bg = btn.styles["backgroundColor"] ?? "";
    const bgParsed = parseColorSimple(bg);
    const isOpaque = bgParsed !== null && !isTransparentColor(bg);
    const hasPadding = parsePxSimple(btn.styles["paddingLeft"]) >= 8;

    const spec: ComponentSpec = {
      backgroundColor: bg || null,
      textColor: btn.styles["color"] || null,
      borderRadius: parsePxSimple(btn.styles["borderRadius"]),
      paddingX: parsePxSimple(btn.styles["paddingLeft"] || btn.styles["paddingRight"]),
      paddingY: parsePxSimple(btn.styles["paddingTop"] || btn.styles["paddingBottom"]),
      fontSize: parsePxSimple(btn.styles["fontSize"]),
      fontWeight: parseInt(btn.styles["fontWeight"] ?? "400") || 400,
      border: formatBorder(btn.styles),
    };

    // Primary score: opaque bg + has padding + high saturation or contrast
    let primaryScore = 0;
    if (isOpaque && hasPadding) {
      primaryScore += 10;
      // Saturated bg (colored CTA) gets big bonus
      if (bgParsed && bgParsed[1] > 30) primaryScore += 20;
      // Dark bg on light theme or light bg on dark theme = high contrast
      if (bgParsed) {
        const contrasty = theme === "light" ? bgParsed[2] < 40 : bgParsed[2] > 60;
        if (contrasty) primaryScore += 15;
      }
      // Higher up on page = more likely hero CTA
      primaryScore += Math.max(0, 10 - btn.boundingRect.y / 100);
    }

    // Secondary score: transparent/light bg with visible border or ghost style
    let secondaryScore = 0;
    if (hasPadding && (!isOpaque || (bgParsed && bgParsed[2] > 80))) {
      secondaryScore += 10;
      if (spec.border) secondaryScore += 5;
    }

    return { spec, primaryScore, secondaryScore };
  });

  // Pick best primary
  const bestPrimary = scored
    .filter((s) => s.primaryScore > 0)
    .sort((a, b) => b.primaryScore - a.primaryScore)[0];
  if (bestPrimary) primaryButton = bestPrimary.spec;

  // Pick best secondary (must be different from primary)
  const bestSecondary = scored
    .filter(
      (s) =>
        s.secondaryScore > 0 &&
        s.spec.backgroundColor !== bestPrimary?.spec.backgroundColor
    )
    .sort((a, b) => b.secondaryScore - a.secondaryScore)[0];
  if (bestSecondary) secondaryButton = bestSecondary.spec;

  return {
    primaryButton,
    secondaryButton,
    card: null, // TODO: detect card patterns
    input: null, // TODO: detect input patterns
  };
}

/** Check if a CSS color value is effectively transparent. */
function isTransparentColor(raw: string): boolean {
  const s = raw.trim().toLowerCase();
  if (s === "transparent" || s === "rgba(0, 0, 0, 0)") return true;
  const alphaMatch = s.match(/rgba\([^)]+,\s*([\d.]+)\s*\)$/);
  if (alphaMatch && parseFloat(alphaMatch[1]) < 0.1) return true;
  return false;
}

function parseColorSimple(raw: string): [number, number, number] | null {
  // Lightweight: just get lightness for classification
  const s = raw.trim().toLowerCase();
  const rgbMatch = s.match(/rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
  if (rgbMatch) {
    const r = parseInt(rgbMatch[1]) / 255;
    const g = parseInt(rgbMatch[2]) / 255;
    const b = parseInt(rgbMatch[3]) / 255;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const l = ((max + min) / 2) * 100;
    const d = max - min;
    const sat = d === 0 ? 0 : (d / (1 - Math.abs(2 * (max + min) / 2 - 1))) * 100;
    const hue =
      d === 0
        ? 0
        : max === r
        ? (((g - b) / d + (g < b ? 6 : 0)) / 6) * 360
        : max === g
        ? (((b - r) / d + 2) / 6) * 360
        : (((r - g) / d + 4) / 6) * 360;
    return [Math.round(hue), Math.round(sat), Math.round(l)];
  }
  return null;
}

function parsePxSimple(raw: string | undefined): number {
  if (!raw) return 0;
  const m = raw.match(/([\d.]+)px/);
  return m ? parseFloat(m[1]) : 0;
}

function formatBorder(styles: Record<string, string>): string | null {
  const w = styles["borderTopWidth"];
  const s = styles["borderTopStyle"];
  const c = styles["borderTopColor"];
  if (!w || !s || s === "none") return null;
  return `${w} ${s} ${c}`;
}

// ─── Main classify function ──────────────────

export function classify(
  normalized: NormalizedTokens,
  raw: RawObservations
): SemanticTokens {
  const theme = detectTheme(normalized.colors);

  // Estimate total page area for accent detection
  const totalPageArea = raw.viewportWidth * raw.viewportHeight;

  const palette = classifyPalette(normalized.colors, theme, totalPageArea);
  const typography = classifyTypography(normalized.fonts);
  const spacing = classifySpacing(normalized.spacings);
  const radii = classifyRadii(normalized.radii);
  const components = extractComponents(raw, palette, theme);

  // Detect monochrome: accent is same as ink-primary
  const monochrome =
    !palette["accent-primary"] ||
    palette["accent-primary"] === palette["ink-primary"];

  if (monochrome && !palette["accent-primary"]) {
    palette["accent-primary"] = palette["ink-primary"];
  }

  // Extract site name from title
  const siteName = raw.documentTitle
    .replace(/\s*[-–—|·]\s*.+$/, "") // strip trailing " — Tagline"
    .trim() || new URL(raw.url).hostname;

  return {
    meta: {
      url: raw.url,
      siteName,
      capturedAt: raw.capturedAt,
      monochrome,
    },
    theme,
    palette,
    typography,
    spacing,
    radii,
    shadows: normalized.shadows.slice(0, 5),
    gradients: normalized.gradients.slice(0, 5),
    components,
  };
}
