#!/usr/bin/env node
// ─────────────────────────────────────────────
// DesignGrab CLI
//
// Usage:
//   designgrab <url>                       (fast mode, no LLM)
//   designgrab <url> --polished            (LLM-enhanced)
//   designgrab <url> --polished --provider anthropic --model claude-haiku-4-5-20251001 --key sk-ant-xxx
//
// Output:
//   ./output/<hostname>/DESIGN.md
//   ./output/<hostname>/tokens.json
//   ./output/<hostname>/screenshot.png
// ─────────────────────────────────────────────

import { writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import { grab } from "./pipeline.js";
import type { GrabMode, LLMConfig, LLMProvider } from "./types/index.js";

function usage(): never {
  console.log(`
DesignGrab — Extract design systems from any website

Usage:
  designgrab <url> [options]

Options:
  --polished                Use LLM for richer narrative (requires API key)
  --provider <name>         LLM provider: anthropic | openai | custom  [default: anthropic]
  --model <id>              Model ID                                    [default: claude-haiku-4-5-20251001]
  --key <api-key>           API key (or set DESIGNGRAB_API_KEY env var)
  --endpoint <url>          Custom API endpoint
  --output <dir>            Output directory                            [default: ./output]

Examples:
  designgrab https://stripe.com
  designgrab https://kraken.com --polished --key sk-ant-api03-xxx
  DESIGNGRAB_API_KEY=sk-xxx designgrab https://linear.app --polished
`);
  process.exit(1);
}

function parseArgs(argv: string[]): {
  url: string;
  mode: GrabMode;
  llm: LLMConfig | null;
  outputDir: string;
} {
  const args = argv.slice(2);
  if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
    usage();
  }

  const url = args[0];
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    console.error(`Error: URL must start with http:// or https://\n`);
    usage();
  }

  let mode: GrabMode = "fast";
  let provider: LLMProvider = "anthropic";
  let model = "claude-haiku-4-5-20251001";
  let apiKey = process.env.DESIGNGRAB_API_KEY ?? "";
  let endpoint: string | undefined;
  let outputDir = "./output";

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case "--polished":
        mode = "polished";
        break;
      case "--provider":
        provider = args[++i] as LLMProvider;
        break;
      case "--model":
        model = args[++i];
        break;
      case "--key":
        apiKey = args[++i];
        break;
      case "--endpoint":
        endpoint = args[++i];
        break;
      case "--output":
        outputDir = args[++i];
        break;
    }
  }

  let llm: LLMConfig | null = null;
  if (mode === "polished") {
    if (!apiKey) {
      console.error(
        "Error: --polished mode requires an API key. Use --key or set DESIGNGRAB_API_KEY.\n"
      );
      usage();
    }
    llm = { provider, apiKey, model, ...(endpoint ? { endpoint } : {}) };
  }

  return { url, mode, llm, outputDir };
}

async function main() {
  const { url, mode, llm, outputDir } = parseArgs(process.argv);

  console.log(`\n🎨 DesignGrab — ${mode} mode\n`);

  const result = await grab({ url, mode, llm });

  // Write output
  const hostname = new URL(url).hostname.replace(/^www\./, "");
  const outDir = join(outputDir, hostname);
  await mkdir(outDir, { recursive: true });

  const mdPath = join(outDir, "DESIGN.md");
  const tokensPath = join(outDir, "tokens.json");
  const screenshotPath = join(outDir, "screenshot.png");

  await Promise.all([
    writeFile(mdPath, result.markdown, "utf-8"),
    writeFile(tokensPath, JSON.stringify(result.tokens, null, 2), "utf-8"),
    writeFile(screenshotPath, result.screenshot),
  ]);

  console.log(`\n✅ Output written to ${outDir}/`);
  console.log(`   ${mdPath}`);
  console.log(`   ${tokensPath}`);
  console.log(`   ${screenshotPath}`);

  if (result.narrative.usage) {
    const u = result.narrative.usage;
    console.log(
      `\n💰 LLM usage: ${u.inputTokens} in + ${u.outputTokens} out ≈ $${u.costUsd.toFixed(4)}`
    );
  }
}

main().catch((err) => {
  console.error("\n❌ Fatal error:", err.message ?? err);
  process.exit(1);
});
