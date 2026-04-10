// ─────────────────────────────────────────────
// DesignGrab — Shared types for the 5-layer pipeline
// ─────────────────────────────────────────────

// ═══════════════════════════════════════════════
// Layer 1 — CAPTURE output
// ═══════════════════════════════════════════════

export interface ElementObservation {
  uid: string;
  tagName: string;
  role: string | null;
  classNames: string[];
  styles: Record<string, string>; // subset of computed styles we care about
  boundingRect: { x: number; y: number; width: number; height: number };
  isVisible: boolean;
  textContent: string; // first 200 chars
  isInteractive: boolean; // button, a, input, [role=button], etc.
}

export interface FontFaceInfo {
  family: string;
  src: string;
  weight: string;
  style: string;
}

export interface RawObservations {
  url: string;
  documentTitle: string;
  metaViewport: string | null;
  elements: ElementObservation[];
  cssVariables: Record<string, string>; // all --xxx on :root
  fontFaces: FontFaceInfo[];
  screenshot: Buffer; // 1440x900 PNG
  capturedAt: string; // ISO timestamp
  viewportWidth: number;
  viewportHeight: number;
}

// ═══════════════════════════════════════════════
// Layer 2 — NORMALIZE output
// ═══════════════════════════════════════════════

export type ColorRole =
  | "background"
  | "text"
  | "border"
  | "shadow"
  | "fill"
  | "stroke"
  | "outline";

export interface ColorUsage {
  role: ColorRole;
  tagName: string;
  count: number;
  areaPx: number; // total pixel area of elements using this color in this role
  isInteractive: boolean;
}

export interface NormalizedColor {
  hex: string; // 6-digit lowercase: #rrggbb
  rgb: [number, number, number];
  hsl: [number, number, number]; // h: 0-360, s: 0-100, l: 0-100
  alpha: number; // 0-1
  usages: ColorUsage[];
  totalCount: number;
  totalArea: number;
}

export interface FontUsage {
  tagName: string;
  fontSize: number; // px
  fontWeight: number;
  count: number;
}

export interface NormalizedFont {
  family: string; // primary family name, cleaned
  fallbacks: string[];
  usages: FontUsage[];
  totalCount: number;
}

export interface NormalizedBorder {
  width: number;
  style: string;
  color: string;
  count: number;
}

export interface NormalizedTokens {
  colors: NormalizedColor[];
  fonts: NormalizedFont[];
  spacings: number[]; // deduplicated, sorted ascending
  radii: number[]; // deduplicated, sorted ascending
  shadows: string[]; // deduplicated normalized box-shadow strings
  borders: NormalizedBorder[];
  gradients: string[]; // deduplicated CSS gradient strings
  cssVariables: Record<string, string>; // resolved final values
}

// ═══════════════════════════════════════════════
// Layer 3 — CLASSIFY output
// ═══════════════════════════════════════════════

export interface FontSpec {
  family: string;
  fallbacks: string[];
  weight: number;
}

export interface TypeScaleEntry {
  fontSize: number;
  lineHeight?: number;
}

export interface TypeScale {
  xs?: TypeScaleEntry;
  sm?: TypeScaleEntry;
  base: TypeScaleEntry;
  md?: TypeScaleEntry;
  lg?: TypeScaleEntry;
  xl?: TypeScaleEntry;
  "2xl"?: TypeScaleEntry;
  "3xl"?: TypeScaleEntry;
  "4xl"?: TypeScaleEntry;
}

export interface ComponentSpec {
  backgroundColor: string | null;
  textColor: string | null;
  borderRadius: number;
  paddingX: number;
  paddingY: number;
  fontSize: number;
  fontWeight: number;
  border: string | null; // "1px solid #xxx" or null
}

export interface SemanticTokens {
  meta: {
    url: string;
    siteName: string;
    capturedAt: string;
    monochrome: boolean; // accent === ink (e.g. ElevenLabs)
  };
  theme: "light" | "dark";
  palette: {
    "bg-base": string;
    "bg-surface-1": string | null;
    "bg-surface-2": string | null;
    "bg-surface-3": string | null;
    "ink-primary": string;
    "ink-secondary": string | null;
    "ink-tertiary": string | null;
    "ink-disabled": string | null;
    "line-subtle": string | null;
    "line-default": string | null;
    "line-strong": string | null;
    "accent-primary": string | null;
    "accent-secondary": string | null;
    "status-error": string | null;
    "status-success": string | null;
    "status-warning": string | null;
  };
  typography: {
    display: FontSpec;
    body: FontSpec;
    mono: FontSpec | null;
    scale: TypeScale;
  };
  spacing: {
    base: number; // inferred base unit (usually 4 or 8)
    scale: number[]; // e.g. [4, 8, 12, 16, 24, 32, 48, 64]
  };
  radii: {
    sm: number;
    md: number;
    lg: number;
    full: number; // 999 or 9999
  };
  shadows: string[];
  gradients: string[]; // extracted CSS gradient values
  components: {
    primaryButton: ComponentSpec | null;
    secondaryButton: ComponentSpec | null;
    card: ComponentSpec | null;
    input: ComponentSpec | null;
  };
}

// ═══════════════════════════════════════════════
// Layer 4 — NARRATE output
// ═══════════════════════════════════════════════

export interface Guideline {
  rule: string;
  reason?: string;
}

export interface ReadyPrompt {
  title: string;
  prompt: string;
  tokenRefs: string[]; // which token keys this prompt references
}

export interface SemanticName {
  token: string; // key in palette, e.g. "accent-primary"
  name: string; // human-friendly, e.g. "scanline-green"
  rationale: string;
}

export interface Narrative {
  mood: {
    summary: string; // 3-4 sentences
    keywords: string[]; // 3-8 mood keywords
  };
  semanticNames: SemanticName[];
  guidelines: {
    dos: Guideline[];
    donts: Guideline[];
  };
  readyPrompts: ReadyPrompt[];
}

export interface NarrateResult {
  narrative: Narrative;
  source: "llm" | "template";
  warnings: string[];
  usage?: {
    inputTokens: number;
    outputTokens: number;
    costUsd: number;
  };
}

// ═══════════════════════════════════════════════
// Layer 5 — RENDER output (just a string)
// ═══════════════════════════════════════════════

// render() returns a plain markdown string — no special type needed.

// ═══════════════════════════════════════════════
// Pipeline config
// ═══════════════════════════════════════════════

export type LLMProvider = "anthropic" | "openai" | "custom";

export interface LLMConfig {
  provider: LLMProvider;
  apiKey: string;
  endpoint?: string; // override base URL
  model: string;
}

export type GrabMode = "fast" | "polished";

export interface GrabOptions {
  url: string;
  mode: GrabMode;
  llm: LLMConfig | null; // null = template-only
  viewports?: { width: number; height: number }[];
  pages?: string[]; // additional paths to scrape, e.g. ["/pricing", "/docs"]
  outputDir?: string;
}

export interface GrabResult {
  markdown: string;
  tokens: SemanticTokens;
  narrative: NarrateResult;
  screenshot: Buffer;
}
