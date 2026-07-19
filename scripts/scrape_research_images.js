/**
 * Scrape product images for research catalogs via Playwright.
 * Run: node scripts/scrape_research_images.js
 * Requires: playwright (npx playwright or local)
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const RESEARCH = path.join(ROOT, "data", "research");

async function main() {
  let chromium;
  try {
    ({ chromium } = require("playwright"));
  } catch {
    console.error("Install playwright: npm i playwright");
    process.exit(1);
  }

  const files = fs.readdirSync(RESEARCH).filter((f) => f.endsWith(".json"));
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    locale: "en-US"
  });
  const page = await context.newPage();
  page.setDefaultTimeout(25000);

  for (const file of files) {
    const fp = path.join(RESEARCH, file);
    const data = JSON.parse(fs.readFileSync(fp, "utf8"));
    console.log("\n==", file, data.items.length, "items ==");
    for (const item of data.items) {
      if (item.imageUrl && !process.env.FORCE) {
        console.log("  skip (has image)", item.id);
        continue;
      }
      if (!item.url) {
        console.log("  skip (no url)", item.id);
        continue;
      }
      try {
        const img = await scrapeImage(page, item.url);
        if (img) {
          item.imageUrl = img;
          console.log("  ok", item.id, img.slice(0, 80));
        } else {
          console.log("  no img", item.id);
        }
      } catch (e) {
        console.log("  err", item.id, e.message.slice(0, 80));
      }
      // small delay
      await page.waitForTimeout(400);
    }
    fs.writeFileSync(fp, JSON.stringify(data, null, 2) + "\n", "utf8");
  }

  await browser.close();
  console.log("\nDone.");
}

async function scrapeImage(page, url) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForTimeout(1500);

  // Jumia product page
  if (url.includes("jumia.com.eg") && url.includes(".html") && !url.includes("/catalog/")) {
    const src = await page.evaluate(() => {
      const candidates = [
        ...document.querySelectorAll("img[data-src], img.src, img[src]"),
        ...document.querySelectorAll(".itm img, .-fh img, .sldr img, picture img")
      ];
      for (const img of candidates) {
        const s = img.getAttribute("data-src") || img.currentSrc || img.src || "";
        if (!s || s.startsWith("data:")) continue;
        if (/logo|icon|sprite|placeholder|badge|flag|avatar/i.test(s)) continue;
        if (/\.(jpg|jpeg|png|webp)/i.test(s) || s.includes("jumia")) return s.split("?")[0];
      }
      // og:image
      const og = document.querySelector('meta[property="og:image"]');
      if (og?.content) return og.content;
      return null;
    });
    return normalize(src);
  }

  // Jumia search
  if (url.includes("jumia.com.eg")) {
    const src = await page.evaluate(() => {
      const a = document.querySelector("a.core img");
      if (!a) return null;
      return a.getAttribute("data-src") || a.src || null;
    });
    return normalize(src);
  }

  // Amazon search or product
  if (url.includes("amazon.eg") || url.includes("amazon.com")) {
    const src = await page.evaluate(() => {
      const og = document.querySelector('meta[property="og:image"]');
      if (og?.content && !/sprite|//g.test(og.content) === false) {
        /* noop */
      }
      if (og?.content && !/sprite|icon/i.test(og.content)) return og.content;

      // product page main image
      const landing = document.querySelector("#landingImage, #imgTagWrapperId img, #main-image-container img");
      if (landing) {
        const s = landing.getAttribute("data-old-hires") || landing.currentSrc || landing.src;
        if (s && !s.startsWith("data:")) return s;
      }

      // search results
      const result = document.querySelector(
        '[data-component-type="s-search-result"] img.s-image, .s-main-slot img.s-image'
      );
      if (result) {
        const s = result.currentSrc || result.src;
        if (s && !s.startsWith("data:")) return s;
      }
      return null;
    });
    return normalize(src);
  }

  // generic og:image
  const src = await page.evaluate(() => {
    const og = document.querySelector('meta[property="og:image"]');
    return og?.content || null;
  });
  return normalize(src);
}

function normalize(src) {
  if (!src) return null;
  if (src.startsWith("//")) src = "https:" + src;
  // prefer larger jumia images if path has size tokens
  src = src.replace(/\/\d+x\d+\//, "/680x680/");
  return src;
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
