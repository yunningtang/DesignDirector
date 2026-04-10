// ─────────────────────────────────────────────
// Layer 1 — CAPTURE
// Playwright loads the page, collects raw observations.
// This is the only layer that touches the network.
// ─────────────────────────────────────────────

import { chromium, type Browser, type Page } from "playwright";
import type { RawObservations, ElementObservation, FontFaceInfo } from "../types/index.js";

const DEFAULT_VIEWPORT = { width: 1440, height: 900 };

// CSS properties we extract from computed styles
const STYLE_KEYS = [
  "color",
  "backgroundColor",
  "backgroundImage",  // captures gradients
  "borderTopColor",
  "borderTopWidth",
  "borderTopStyle",
  "borderRadius",
  "boxShadow",
  "fontFamily",
  "fontSize",
  "fontWeight",
  "lineHeight",
  "letterSpacing",
  "padding",
  "paddingTop",
  "paddingRight",
  "paddingBottom",
  "paddingLeft",
  "margin",
  "marginTop",
  "marginRight",
  "marginBottom",
  "marginLeft",
  "gap",
  "opacity",
  "textDecoration",
  "display",
  "position",
] as const;

/**
 * The extraction script that runs inside the browser page.
 * Returns serializable data — no DOM references leak out.
 */
function extractionScript(styleKeys: readonly string[]) {
  const INTERACTIVE_TAGS = new Set(["BUTTON", "A", "INPUT", "SELECT", "TEXTAREA"]);
  const INTERACTIVE_ROLES = new Set(["button", "link", "tab", "menuitem", "switch", "checkbox", "radio"]);

  // Collect all visible elements (limit to reasonable count)
  const allElements = document.querySelectorAll("body *");
  const elements: any[] = [];
  let uid = 0;

  for (const el of allElements) {
    if (elements.length >= 3000) break; // safety cap

    const htmlEl = el as HTMLElement;
    const rect = htmlEl.getBoundingClientRect();

    // Skip invisible elements
    if (rect.width === 0 || rect.height === 0) continue;
    const computed = getComputedStyle(htmlEl);
    if (computed.display === "none" || computed.visibility === "hidden") continue;
    if (parseFloat(computed.opacity) === 0) continue;

    const styles: Record<string, string> = {};
    for (const key of styleKeys) {
      // Use bracket notation — works with camelCase directly
      // and returns resolved values for all properties
      styles[key] = (computed as any)[key] ?? "";
    }

    const role = htmlEl.getAttribute("role");
    const tagName = htmlEl.tagName;
    const isInteractive =
      INTERACTIVE_TAGS.has(tagName) ||
      INTERACTIVE_ROLES.has(role ?? "") ||
      htmlEl.hasAttribute("onclick") ||
      htmlEl.closest("button, a") !== null;

    elements.push({
      uid: `el-${uid++}`,
      tagName,
      role,
      classNames: Array.from(htmlEl.classList),
      styles,
      boundingRect: {
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height,
      },
      isVisible: true,
      textContent: (htmlEl.textContent ?? "").trim().slice(0, 200),
      isInteractive,
    });
  }

  // Collect CSS custom properties from :root
  const cssVariables: Record<string, string> = {};
  const rootStyles = getComputedStyle(document.documentElement);
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (
          rule instanceof CSSStyleRule &&
          (rule.selectorText === ":root" || rule.selectorText === "html")
        ) {
          for (let i = 0; i < rule.style.length; i++) {
            const prop = rule.style[i];
            if (prop.startsWith("--")) {
              // Resolve to final computed value
              cssVariables[prop] = rootStyles.getPropertyValue(prop).trim();
            }
          }
        }
      }
    } catch {
      // Cross-origin stylesheet — skip
    }
  }

  // Collect @font-face declarations
  const fontFaces: any[] = [];
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule instanceof CSSFontFaceRule) {
          fontFaces.push({
            family: rule.style.getPropertyValue("font-family").replace(/['"]/g, "").trim(),
            src: rule.style.getPropertyValue("src") ?? "",
            weight: rule.style.getPropertyValue("font-weight") || "400",
            style: rule.style.getPropertyValue("font-style") || "normal",
          });
        }
      }
    } catch {
      // Cross-origin
    }
  }

  const metaViewport = document.querySelector('meta[name="viewport"]');

  return {
    documentTitle: document.title,
    metaViewport: metaViewport?.getAttribute("content") ?? null,
    elements,
    cssVariables,
    fontFaces,
  };
}

export interface CaptureOptions {
  viewport?: { width: number; height: number };
  waitMs?: number; // extra wait after networkidle
  timeout?: number; // navigation timeout
}

export async function capture(
  url: string,
  options: CaptureOptions = {}
): Promise<RawObservations> {
  const viewport = options.viewport ?? DEFAULT_VIEWPORT;
  const waitMs = options.waitMs ?? 1500;
  const timeout = options.timeout ?? 30_000;

  let browser: Browser | null = null;

  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      viewport,
      deviceScaleFactor: 2,
      userAgent:
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    });

    const page = await context.newPage();

    // Navigate and wait for content
    await page.goto(url, {
      waitUntil: "networkidle",
      timeout,
    });

    // Extra settle time for JS-rendered content
    await page.waitForTimeout(waitMs);

    // Run extraction script in-page
    const extracted = await page.evaluate(extractionScript, STYLE_KEYS);

    // Take screenshot
    const screenshot = await page.screenshot({
      fullPage: false,
      type: "png",
    });

    await context.close();

    return {
      url,
      documentTitle: extracted.documentTitle,
      metaViewport: extracted.metaViewport,
      elements: extracted.elements as ElementObservation[],
      cssVariables: extracted.cssVariables,
      fontFaces: extracted.fontFaces as FontFaceInfo[],
      screenshot: Buffer.from(screenshot),
      capturedAt: new Date().toISOString(),
      viewportWidth: viewport.width,
      viewportHeight: viewport.height,
    };
  } finally {
    await browser?.close();
  }
}
