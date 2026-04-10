// ─────────────────────────────────────────────
// DesignGrab — HTTP server
// Serves the frontend and exposes POST /api/grab
// ─────────────────────────────────────────────

import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { readFile } from "node:fs/promises";
import { join, extname } from "node:path";
import { capture } from "./layer1/capture.js";
import { normalize } from "./layer2/normalize.js";
import { classify } from "./layer3/classify.js";
import { narrate } from "./layer4/narrate.js";
import { render } from "./layer5/render.js";
import type { LLMConfig } from "./types/index.js";

const PORT = parseInt(process.env.PORT ?? "3000");
const ROOT = join(import.meta.dirname, "..");

const MIME: Record<string, string> = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "application/javascript",
  ".json": "application/json",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
};

function json(res: ServerResponse, status: number, data: unknown) {
  res.writeHead(status, {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
  });
  res.end(JSON.stringify(data));
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => resolve(Buffer.concat(chunks).toString()));
    req.on("error", reject);
  });
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", `http://localhost:${PORT}`);
  const method = req.method ?? "GET";

  // ── CORS preflight ──
  if (method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    });
    res.end();
    return;
  }

  // ── API: POST /api/grab ──
  if (method === "POST" && url.pathname === "/api/grab") {
    try {
      const body = JSON.parse(await readBody(req));
      const targetUrl: string = body.url;
      if (!targetUrl?.startsWith("http")) {
        json(res, 400, { error: "URL must start with http:// or https://" });
        return;
      }

      // Build LLM config from request (optional)
      let llmConfig: LLMConfig | null = null;
      if (body.apiKey && body.provider) {
        llmConfig = {
          provider: body.provider,
          apiKey: body.apiKey,
          model: body.model ?? "claude-haiku-4-5-20251001",
          endpoint: body.endpoint,
        };
      }
      const mode = llmConfig ? "polished" : "fast";

      console.log(`[API] Grabbing ${targetUrl} (${mode} mode)`);

      // Layer 1
      const raw = await capture(targetUrl);
      console.log(`[L1] ${raw.elements.length} elements`);

      // Layer 2
      const normalized = normalize(raw);
      console.log(`[L2] ${normalized.colors.length} colors, ${normalized.fonts.length} fonts`);

      // Layer 3
      const tokens = classify(normalized, raw);
      console.log(`[L3] theme=${tokens.theme} monochrome=${tokens.meta.monochrome}`);

      // Layer 4
      const narrateResult = await narrate(tokens, raw.screenshot, llmConfig);
      console.log(`[L4] source=${narrateResult.source}`);

      // Layer 5
      const markdown = render(tokens, narrateResult);

      // Respond
      json(res, 200, {
        markdown,
        tokens,
        narrative: narrateResult,
        screenshot: raw.screenshot.toString("base64"),
        stats: {
          elements: raw.elements.length,
          colors: normalized.colors.length,
          fonts: normalized.fonts.length,
          spacings: normalized.spacings.length,
        },
      });
    } catch (err) {
      console.error("[API] Error:", err);
      const msg = err instanceof Error ? err.message : String(err);
      json(res, 500, { error: msg });
    }
    return;
  }

  // ── API: POST /api/rerender ──
  // Re-generates DESIGN.md from modified tokens (no re-crawl)
  if (method === "POST" && url.pathname === "/api/rerender") {
    try {
      const body = JSON.parse(await readBody(req));
      const tokens = body.tokens;
      if (!tokens) {
        json(res, 400, { error: "Missing tokens" });
        return;
      }

      // Re-run Layer 4 (template) + Layer 5 (render)
      const narrateResult = await narrate(tokens, Buffer.alloc(0), null);
      const markdown = render(tokens, narrateResult);
      json(res, 200, { markdown });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      json(res, 500, { error: msg });
    }
    return;
  }

  // ── API: GET /api/examples ──
  if (method === "GET" && url.pathname === "/api/examples") {
    try {
      const content = await readFile(join(ROOT, "examples.json"), "utf-8");
      json(res, 200, JSON.parse(content));
    } catch {
      json(res, 200, []); // no examples yet
    }
    return;
  }

  // ── Static files ──
  let filePath = url.pathname === "/" ? "/designgrab.html" : url.pathname;
  const fullPath = join(ROOT, filePath);
  const ext = extname(fullPath);

  try {
    const content = await readFile(fullPath);
    res.writeHead(200, { "Content-Type": MIME[ext] ?? "application/octet-stream" });
    res.end(content);
  } catch {
    res.writeHead(404);
    res.end("Not found");
  }
});

server.listen(PORT, () => {
  console.log(`\n🎨 DesignGrab server running at http://localhost:${PORT}\n`);
});
