// Batch grab sites from awesome-design-md list
import { grab } from "./dist/pipeline.js";
import { writeFile, mkdir, readFile } from "node:fs/promises";
import { join } from "node:path";

const SITES = [
  // AI & ML
  { url: "https://anthropic.com", cat: "AI" },
  { url: "https://cohere.com", cat: "AI" },
  { url: "https://elevenlabs.com", cat: "AI" },
  { url: "https://mistral.ai", cat: "AI" },
  { url: "https://replicate.com", cat: "AI" },
  { url: "https://together.ai", cat: "AI" },
  { url: "https://x.ai", cat: "AI" },
  // Dev Tools
  { url: "https://cursor.so", cat: "Dev Tools" },
  { url: "https://vercel.com", cat: "Dev Tools" },
  { url: "https://warp.dev", cat: "Dev Tools" },
  { url: "https://supabase.com", cat: "Dev Tools" },
  { url: "https://sentry.io", cat: "Dev Tools" },
  { url: "https://posthog.com", cat: "Dev Tools" },
  { url: "https://hashicorp.com", cat: "Dev Tools" },
  { url: "https://expo.dev", cat: "Dev Tools" },
  { url: "https://clickhouse.com", cat: "Dev Tools" },
  // SaaS / Productivity
  { url: "https://linear.app", cat: "SaaS" },
  { url: "https://notion.so", cat: "SaaS" },
  { url: "https://resend.com", cat: "SaaS" },
  { url: "https://cal.com", cat: "SaaS" },
  { url: "https://zapier.com", cat: "SaaS" },
  { url: "https://intercom.com", cat: "SaaS" },
  { url: "https://mintlify.com", cat: "SaaS" },
  { url: "https://raycast.com", cat: "SaaS" },
  { url: "https://superhuman.com", cat: "SaaS" },
  // Design
  { url: "https://figma.com", cat: "Design" },
  { url: "https://framer.com", cat: "Design" },
  { url: "https://webflow.com", cat: "Design" },
  { url: "https://miro.com", cat: "Design" },
  // Fintech
  { url: "https://stripe.com", cat: "Fintech" },
  { url: "https://coinbase.com", cat: "Fintech" },
  { url: "https://wise.com", cat: "Fintech" },
  { url: "https://revolut.com", cat: "Fintech" },
  // Consumer
  { url: "https://airbnb.com", cat: "Consumer" },
  { url: "https://spotify.com", cat: "Consumer" },
  { url: "https://nike.com", cat: "Consumer" },
  { url: "https://uber.com", cat: "Consumer" },
  { url: "https://pinterest.com", cat: "Consumer" },
  // Enterprise
  { url: "https://apple.com", cat: "Enterprise" },
  { url: "https://nvidia.com", cat: "Enterprise" },
  { url: "https://spacex.com", cat: "Enterprise" },
  { url: "https://tesla.com", cat: "Enterprise" },
  { url: "https://bmw.com", cat: "Enterprise" },
];

const CONCURRENCY = 2;
const results = [];
let done = 0;

async function grabSite(site) {
  const hostname = new URL(site.url).hostname.replace(/^www\./, "");
  try {
    console.log(`[${++done}/${SITES.length}] Grabbing ${hostname}...`);
    const result = await grab({ url: site.url, mode: "fast", llm: null });
    const outDir = join("output", hostname);
    await mkdir(outDir, { recursive: true });
    await writeFile(join(outDir, "DESIGN.md"), result.markdown, "utf-8");
    await writeFile(join(outDir, "tokens.json"), JSON.stringify(result.tokens, null, 2), "utf-8");
    await writeFile(join(outDir, "screenshot.png"), result.screenshot);

    const name = result.tokens.meta.siteName.split(/[:|–—]/)[0].trim();
    results.push({
      hostname,
      category: site.cat,
      siteName: name,
      theme: result.tokens.theme,
      accentPrimary: result.tokens.palette["accent-primary"],
      bgBase: result.tokens.palette["bg-base"],
      inkPrimary: result.tokens.palette["ink-primary"],
      displayFont: result.tokens.typography.display.family,
      markdown: result.markdown,
      tokens: result.tokens,
      screenshot: result.screenshot.toString("base64"),
    });
    console.log(`  ✓ ${name} (${result.tokens.theme}, ${result.tokens.typography.display.family})`);
  } catch (err) {
    console.log(`  ✗ ${hostname}: ${err.message}`);
  }
}

async function main() {
  console.log(`Batch grabbing ${SITES.length} sites (concurrency: ${CONCURRENCY})...\n`);
  done = 0;

  // Process in chunks
  for (let i = 0; i < SITES.length; i += CONCURRENCY) {
    const chunk = SITES.slice(i, i + CONCURRENCY);
    await Promise.all(chunk.map(grabSite));
  }

  // Write examples.json
  await writeFile("examples.json", JSON.stringify(results));
  console.log(`\n✅ Done. ${results.length}/${SITES.length} sites saved to examples.json`);
}

main();
