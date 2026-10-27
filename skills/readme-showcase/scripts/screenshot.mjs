#!/usr/bin/env node
// Usage: node screenshot.mjs <url> <out.png> [--width 1440] [--height 900] [--dark] [--full] [--wait 1500]
// Needs Playwright: npx --yes playwright install chromium (once)
const args = process.argv.slice(2);
const [url, out] = args;
if (!url || !out) { console.error('usage: screenshot.mjs <url> <out.png> [--width N --height N --dark --full --wait ms]'); process.exit(1); }
const opt = (k, d) => { const i = args.indexOf(k); return i > -1 ? Number(args[i + 1]) : d; };
let chromium;
try { ({ chromium } = await import('playwright')); }
catch { try {
  // Fall back to the Playwright installed in the project being documented (cwd).
  const { createRequire } = await import('node:module');
  ({ chromium } = createRequire(process.cwd() + '/')('playwright'));
} catch { console.error('Playwright not found. Run: npm i -D playwright && npx playwright install chromium'); process.exit(1); } }
const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: opt('--width', 1440), height: opt('--height', 900) },
  deviceScaleFactor: 2,
  colorScheme: args.includes('--dark') ? 'dark' : 'light',
});
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForTimeout(opt('--wait', 1500));
await page.screenshot({ path: out, fullPage: args.includes('--full') });
await browser.close();
console.log(`saved ${out}`);
