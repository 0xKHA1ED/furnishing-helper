"""
Scrape official Egypt manufacturer sites for:
  9kg + black (or dark silver near-black) + top-load + full-automatic washers.
Uses Playwright sync API if available; otherwise prints targets for MCP.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/appliances/_9kg_black_top_scrape.json"

# Official manufacturer / brand storefronts in Egypt
TARGETS = [
    {
        "source": "Elaraby Group",
        "brand_hint": None,
        "urls": [
            "https://www.elarabygroup.com/en/electric-home-appliances/large-home-appliances/washing-machines/top-automatic-washing-machines",
            "https://www.elarabygroup.com/en/electric-home-appliances/large-home-appliances/washing-machines/top-automatic-washing-machines?p=2",
            "https://www.elarabygroup.com/en/catalogsearch/result/?q=9+kg+top+automatic+black",
            "https://www.elarabygroup.com/en/shop-elaraby-brands/sharp-products/sharp-washing-machines",
            "https://www.elarabygroup.com/en/shop-elaraby-brands/tornado-products/tornado-washing-machines",
            "https://www.elarabygroup.com/en/shop-elaraby-brands/hoover-products/hoover-washing-machines",
            "https://www.elarabygroup.com/en/shop-elaraby-brands/hitachi-products/hitachi-washing-machines",
            "https://www.elarabygroup.com/en/shop-elaraby-brands/toshiba-products/toshiba-washing-machines",
            "https://www.elarabygroup.com/en/shop-elaraby-brands/candy-products/candy-washing-machines",
        ],
    },
    {
        "source": "Fresh Official",
        "brand_hint": "Fresh",
        "urls": [
            "https://fresh.com.eg/en/categories/washing-machines",
            "https://fresh.com.eg/en/products/fresh-washing-machine-top-loading-9-k-g-new-touch-silver",
            "https://fresh.com.eg/en/products/fresh-washing-machine-top-loading-9-k-g-new-silver",
            "https://fresh.com.eg/en/products/fresh-washing-machine-top-loading-9-k-g-silver-n",
        ],
    },
    {
        "source": "Samsung Egypt",
        "brand_hint": "Samsung",
        "urls": [
            "https://www.samsung.com/eg/washers-and-dryers/all-washers-and-dryers/",
            "https://www.samsung.com/eg/washers-and-dryers/top-load-washer/",
            "https://www.samsung.com/eg/search/?searchvalue=top%20load%20washer%209kg",
        ],
    },
    {
        "source": "LG Egypt",
        "brand_hint": "LG",
        "urls": [
            "https://www.lg.com/eg_en/washing-machines/",
            "https://www.lg.com/eg_en/washing-machines/top-load/",
            "https://www.lg.com/eg/washing-machines/",
        ],
    },
    {
        "source": "White Point Elabd",
        "brand_hint": "White Point",
        "urls": [
            "https://whitepointelabd.com/product-category/full-automatic-washing-machine/",
            "https://whitepointelabd.com/?s=top+load+9",
            "https://whitepointegypt.com/laundry/washing-machines/",
        ],
    },
    {
        "source": "Kiriazi Official",
        "brand_hint": "Kiriazi",
        "urls": [
            "https://kiriazi.com/",
            "https://kiriazi.com/ar/products/washing-machines",
        ],
    },
    {
        "source": "Unionaire Official",
        "brand_hint": "Unionaire",
        "urls": [
            "https://www.unionaire.com/",
            "https://www.unionaire.com/products/washing-machines",
        ],
    },
    {
        "source": "Zanussi Egypt",
        "brand_hint": "Zanussi",
        "urls": [
            "https://www.zanussi.com.eg/en/laundry/washing-machines.html",
            "https://www.zanussi.com.eg/en/laundry.html",
        ],
    },
    {
        "source": "Toshiba Lifestyle Egypt",
        "brand_hint": "Toshiba",
        "urls": [
            "https://www.toshiba-lifestyle.com/eg-en/laundry/top-load-washer/",
            "https://www.toshiba-lifestyle.com/eg-en/laundry/",
        ],
    },
    {
        "source": "Beko Egypt",
        "brand_hint": "Beko",
        "urls": [
            "https://www.beko.com/eg-ar",
            "https://www.beko.com/eg-en",
            "https://www.beko.com/eg-en/washing-machines",
        ],
    },
    {
        "source": "Haier Egypt",
        "brand_hint": "Haier",
        "urls": [
            "https://www.haier.com/eg_en/",
            "https://www.haier.com/eg_en/washing-machines/",
        ],
    },
]


def parse_kg(text: str):
    t = text.lower()
    m = re.search(r"(\d{1,2})\s*(?:/|\-)\s*(\d)\s*kg", t)  # washer-dryer
    if m and int(m.group(1)) >= 7:
        # treat as wash capacity
        return float(m.group(1))
    m = re.search(r"(\d{1,2})(?:\.(\d))?\s*k\.?\s*g", t)
    if m:
        whole = float(m.group(1))
        if m.group(2):
            return whole + float(m.group(2)) / 10
        return whole
    m = re.search(r"(\d{1,2})-?kg", t)
    if m:
        return float(m.group(1))
    return None


def color_from_text(text: str) -> str:
    t = text.lower()
    if re.search(r"\bblack\b|obsidian|onyx", t):
        return "black"
    if re.search(r"dark\s*silver|dark\s*grey|dark\s*gray|graphite|anthracite", t):
        return "dark_silver"
    if re.search(r"\bsilver\b|stainless|steel", t):
        return "silver"
    if re.search(r"\bwhite\b", t):
        return "white"
    if re.search(r"gold|champagne", t):
        return "gold"
    return "unknown"


def is_top_load(text: str, url: str = "") -> bool:
    hay = f"{text} {url}".lower()
    if re.search(r"front[-\s]?load|front[-\s]?automatic|تحميل\s*أمام", hay):
        if not re.search(r"top[-\s]?load|top[-\s]?automatic|تحميل\s*علو", hay):
            return False
    return bool(
        re.search(
            r"top[-\s]?load|top[-\s]?automatic|top\s*loading|تحميل\s*علو|top automatic",
            hay,
        )
    )


def is_full_auto(text: str) -> bool:
    t = text.lower()
    if re.search(r"half[-\s]?auto|twin[-\s]?tub|semi[-\s]?auto|manual|spin\s*tub|twin tub", t):
        return False
    return True


def brand_from_text(text: str, hint: str | None = None) -> str:
    if hint:
        return hint
    hay = text.lower()
    brands = [
        ("white point", "White Point"),
        ("hitachi", "Hitachi"),
        ("toshiba", "Toshiba"),
        ("tornado", "Tornado"),
        ("hoover", "Hoover"),
        ("candy", "Candy"),
        ("sharp", "Sharp"),
        ("fresh", "Fresh"),
        ("beko", "Beko"),
        ("samsung", "Samsung"),
        ("zanussi", "Zanussi"),
        ("haier", "Haier"),
        ("lg", "LG"),
        ("kiriazi", "Kiriazi"),
        ("unionaire", "Unionaire"),
        ("ariston", "Ariston"),
        ("indesit", "Indesit"),
    ]
    for key, name in brands:
        if key in hay:
            return name
    return "Unknown"


EXTRACT_JS = """
() => {
  const items = [];
  const push = (name, url, imageUrl, price, oos, raw) => {
    if (!name || name.length < 6) return;
    if (!url) return;
    items.push({
      name: name.replace(/\\s+/g, ' ').trim().slice(0, 200),
      url,
      imageUrl: imageUrl || '',
      priceEGP: price,
      oos: !!oos,
      raw: (raw || name).replace(/\\s+/g, ' ').trim().slice(0, 300)
    });
  };

  // Generic product cards
  const cards = document.querySelectorAll(
    '.product-item, li.item.product, .product-item-info, .product-card, .product, [data-product], .product-tile, .c-product, article.product'
  );
  cards.forEach(card => {
    const a = card.querySelector('a[href]');
    if (!a) return;
    const nameEl = card.querySelector(
      '.product-item-link, .product-name a, a.product-item-link, strong a, h2 a, h3 a, .product-title, .name, [class*="title"]'
    ) || a;
    let name = (nameEl.innerText || nameEl.textContent || a.getAttribute('title') || '').trim();
    if (!name) name = (a.getAttribute('aria-label') || '').trim();
    const img = card.querySelector('img');
    let price = null;
    const priceEl = card.querySelector('[data-price-amount], .price, .price-wrapper, [class*="price"]');
    if (priceEl) {
      const amt = priceEl.getAttribute('data-price-amount');
      if (amt) price = parseFloat(amt);
      else {
        const m = (priceEl.innerText || '').replace(/,/g, '').match(/(\\d+(?:\\.\\d+)?)/);
        if (m) price = parseFloat(m[1]);
      }
    }
    const stock = card.innerText || '';
    push(name, a.href, img ? (img.src || img.getAttribute('data-src') || '') : '', price,
      /out of stock|غير متوفر|sold out|نفدت|not available/i.test(stock), stock);
  });

  // Link fallback for laundry pages
  if (items.length < 3) {
    document.querySelectorAll('a[href]').forEach(a => {
      const t = (a.innerText || a.getAttribute('title') || a.getAttribute('aria-label') || '').replace(/\\s+/g, ' ').trim();
      const href = a.href || '';
      if (!/wash|washer|laundry|غسال|top.?load/i.test(t + href)) return;
      if (t.length < 12 || t.length > 180) return;
      if (/category|filter|login|cart|wishlist|compare|share/i.test(t)) return;
      const img = a.querySelector('img') || a.parentElement?.querySelector('img');
      const parent = a.closest('div,li,article,section') || a.parentElement;
      const raw = (parent ? parent.innerText : t).replace(/\\s+/g, ' ').trim().slice(0, 300);
      let price = null;
      const m = raw.replace(/,/g, '').match(/(\\d{3,6}(?:\\.\\d+)?)\\s*(?:EGP|جنيه|LE)?/i);
      if (m) price = parseFloat(m[1]);
      push(t, href, img ? (img.src || '') : '', price,
        /out of stock|غير متوفر|sold out/i.test(raw), raw);
    });
  }

  // Product detail page
  const h1 = document.querySelector('h1');
  if (h1 && /wash|غسال/i.test(h1.innerText || '')) {
    const img = document.querySelector('.gallery-placeholder img, .fotorama img, .product-image-main img, img.product, [class*="gallery"] img');
    let price = null;
    const pe = document.querySelector('[data-price-amount], .price-final_price .price, .price');
    if (pe) {
      const amt = pe.getAttribute('data-price-amount');
      if (amt) price = parseFloat(amt);
      else {
        const m = (pe.innerText || '').replace(/,/g, '').match(/(\\d+(?:\\.\\d+)?)/);
        if (m) price = parseFloat(m[1]);
      }
    }
    const body = document.body.innerText.slice(0, 2000);
    push(h1.innerText.trim(), location.href, img ? img.src : '', price,
      /out of stock|غير متوفر|sold out/i.test(body), body.slice(0, 300));
  }

  const seen = new Set();
  return items.filter(i => {
    const k = (i.url || '').split('?')[0] + '|' + i.name.slice(0, 40);
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}
"""


def match_criteria(item: dict, strict_black: bool = False) -> bool:
    hay = f"{item.get('name','')} {item.get('raw','')} {item.get('url','')}"
    kg = parse_kg(hay)
    item["capacityKg"] = kg
    item["color"] = color_from_text(hay)
    item["topLoad"] = is_top_load(hay, item.get("url", ""))
    item["fullAuto"] = is_full_auto(hay)

    if kg != 9:
        return False
    if not item["topLoad"]:
        # if page is top-automatic category, trust name without front-load
        if "top-automatic" in (item.get("url") or "") or "top-load" in (item.get("url") or ""):
            item["topLoad"] = True
        else:
            return False
    if not item["fullAuto"]:
        return False
    if strict_black:
        return item["color"] == "black"
    # allow black + dark_silver (near-black common on Egypt SKUs)
    return item["color"] in ("black", "dark_silver")


def scrape_with_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed", file=sys.stderr)
        return None

    all_raw = []
    matches_strict = []
    matches_near = []
    errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="en-EG",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.set_default_timeout(45000)

        for target in TARGETS:
            source = target["source"]
            for url in target["urls"]:
                print(f"[{source}] {url}", flush=True)
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(2000)
                    for _ in range(6):
                        page.evaluate("window.scrollBy(0, 1400)")
                        page.wait_for_timeout(350)
                    # load more
                    for _ in range(5):
                        try:
                            btn = page.locator("text=/load more|show more|عرض المزيد/i").first
                            if btn.is_visible(timeout=800):
                                btn.click()
                                page.wait_for_timeout(1500)
                            else:
                                break
                        except Exception:
                            break
                    items = page.evaluate(EXTRACT_JS)
                    for it in items:
                        it["source"] = source
                        it["brand"] = brand_from_text(
                            f"{it.get('name','')} {it.get('url','')}", target.get("brand_hint")
                        )
                        it["listingUrl"] = url
                        all_raw.append(it)
                        if match_criteria(it, strict_black=True):
                            matches_strict.append(it)
                        elif match_criteria(dict(it), strict_black=False):
                            matches_near.append(it)
                    print(f"  -> {len(items)} items", flush=True)
                except Exception as e:
                    errors.append({"source": source, "url": url, "error": str(e)})
                    print(f"  ERROR: {e}", flush=True)

        browser.close()

    # dedupe matches by model-ish key
    def dedupe(rows):
        seen = set()
        out = []
        for r in rows:
            key = re.sub(r"[^a-z0-9]+", "", (r.get("name") or "").lower())[:60]
            if key in seen:
                continue
            seen.add(key)
            out.append(r)
        return out

    result = {
        "scrapedAt": date.today().isoformat(),
        "criteria": {
            "capacityKg": 9,
            "color": "black (strict) + dark_silver (near-black)",
            "type": "top_load",
            "automation": "full_auto",
            "channel": "official manufacturer sites only",
        },
        "matchesStrictBlack": dedupe(matches_strict),
        "matchesNearBlack": dedupe(matches_near),
        "rawCount": len(all_raw),
        "errors": errors,
        "allRaw": all_raw,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"\nSaved {OUT}\nstrict black: {len(result['matchesStrictBlack'])}, "
        f"near black: {len(result['matchesNearBlack'])}, raw: {len(all_raw)}"
    )
    return result


if __name__ == "__main__":
    scrape_with_playwright()
