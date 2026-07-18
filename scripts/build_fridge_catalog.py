"""Build filtered black-fridge catalog under hard constraints."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRAPE = ROOT / "data/appliances/_fridge_scrape.json"
OUT = ROOT / "data/appliances/fridge_catalog.json"
IMAGES = ROOT / "data/appliances/images_partial.json"

# Hard filters (user 2026-07-17)
MAX_PRICE = 35000
MIN_CAPACITY_L = 360  # meal-prep couple; exclude "too small"
REQUIRE_BLACK = True
REQUIRE_FREEZER = True  # exclude minibar / no-freezer

# Manual research pros/cons + layout (not always in scrape name)
RESEARCH = {
    "RDNE455M20XBIDEGB": {
        "layout": "top_freezer",
        "inverter": True,
        "nofrost": True,
        "fit": 9.0,
        "rank": 1,
        "summary": "Best overall black top-freezer under 35k: true inverter + ~406 L + brand network.",
        "pros": [
            "True inverter motor (better noise/efficiency odds vs fixed-speed)",
            "Black finish matches hard aesthetics requirement",
            "~406 L NoFrost top freezer — solid for Friday meal-prep",
            "Under 35k with a little budget headroom (~30.3k)",
            "Beko widely sold via B.TECH; warranty path is straightforward if bought authorized",
            "No water/ice dispenser (fewer failure points)",
        ],
        "cons": [
            "Freezer is still a normal top-freezer (~90–100 L class) — organize flat packs",
            "Some global Beko noise complaints are install/defrost related — level unit, leave clearance",
            "Looks competent, not ultra-premium glass/design flagship",
        ],
    },
    "RDNE455M20XBIDTEWEG": {
        "layout": "top_freezer",
        "inverter": True,
        "nofrost": True,
        "fit": 8.8,
        "rank": 2,
        "summary": "Larger ~455 L black inverter Beko; strong space pick if price stays ≤35k.",
        "pros": [
            "Bigger total capacity (~455 L) for weekly prep containers",
            "Inverter + NoFrost + black",
            "Often priced under the 406 black sibling depending on promo",
            "Same family as researched Beko inverter line",
        ],
        "cons": [
            "Confirm exact net liters and freezer split on the energy label",
            "Larger unit needs height/door-swing measurement",
            "Model suffix variants are easy to confuse at checkout",
        ],
    },
    "RF-580TV-BK": {
        "layout": "top_freezer",
        "inverter": True,
        "nofrost": True,
        "fit": 8.3,
        "rank": 3,
        "summary": "450 L black inverter Tornado — capacity + inverter without leaving black.",
        "pros": [
            "~450 L marketing capacity — roomy for couple meal-prep",
            "Inverter claimed in product name",
            "Black finish",
            "Price in the high-20k band on scrape — under hard ceiling",
            "Tornado parts/service common in Egypt mid-market",
        ],
        "cons": [
            "Brand prestige/service consistency below LG/Samsung",
            "Verify inverter on sticker/invoice (titles can be marketing-heavy)",
            "Finish/QC less 'premium' than Korean brands",
            "Noise not independently verified for this SKU",
        ],
    },
    "FNT-DR540YGB": {
        "layout": "top_freezer",
        "inverter": False,
        "nofrost": True,
        "fit": 7.6,
        "rank": 4,
        "summary": "426 L black Fresh — max liters in black budget tier; non-inverter.",
        "pros": [
            "Large black top freezer (~426 L)",
            "NoFrost",
            "Local Fresh service density / parts culture in Egypt",
            "Fits black + capacity rules under 35k",
        ],
        "cons": [
            "No inverter — more start/stop noise and bill risk",
            "Build/reliability perception is value-tier (variance)",
            "Fewer premium features than Beko/Tornado inverter peers",
        ],
    },
    "GTF402SBAN": {
        "layout": "top_freezer",
        "inverter": False,
        "nofrost": True,
        "fit": 7.8,
        "rank": 5,
        "summary": "LG black 401 L — best brand/look among non-inverter blacks; title inverter is wrong.",
        "pros": [
            "Strong black exterior / modern look",
            "LG service network reputation in Egypt",
            "~401 L + documented ~97 L freezer class on this line",
            "Multi Air Flow / total NoFrost lineage",
            "No dispenser",
        ],
        "cons": [
            "NOT Smart Inverter — LG/B.TECH specs show recipro/fixed-speed (ignore 'inveter' URL)",
            "Paying ~31k without inverter is weak vs Beko black inverter ~30k",
            "More cycling noise risk than inverter models",
        ],
    },
    "ZRT41204BA": {
        "layout": "top_freezer",
        "inverter": False,
        "nofrost": True,
        "fit": 7.5,
        "rank": 6,
        "summary": "Zanussi 406 L black value workhorse — non-inverter.",
        "pros": [
            "Black + ~406 L NoFrost under ~25–26k",
            "Electrolux-group brand presence",
            "Good price/size if inverter not required",
            "No dispenser",
        ],
        "cons": [
            "No inverter",
            "Mechanical/simpler controls on many listings",
            "Energy class often average",
        ],
    },
    "URN-800CEPBLG1A-DXHIRBXXL": {
        "layout": "bottom_freezer",
        "inverter": True,
        "nofrost": True,
        "fit": 8.0,
        "rank": 7,
        "summary": "Huge 545 L black inverter bottom-freezer Unionaire Signature — space king in budget.",
        "pros": [
            "Very large ~545 L for bulk shop + prep",
            "Black + inverter claimed",
            "Bottom freezer: eye-level fridge for containers",
            "Stays under 35k on scrape (~32k)",
        ],
        "cons": [
            "Unionaire reliability/service variance vs LG/Samsung/Beko",
            "Large footprint — measure kitchen/elevator carefully",
            "Black glass/signature lines show fingerprints",
            "You leaned top-freezer space story; this is bottom layout",
        ],
    },
    "URN800CEPBLG1ADXHIRBXXLN": {
        "layout": "bottom_freezer",
        "inverter": False,
        "nofrost": True,
        "fit": 7.2,
        "rank": 8,
        "summary": "545 L black bottom-freezer Unionaire without inverter — capacity over tech.",
        "pros": [
            "Massive capacity in black under 35k",
            "Bottom freezer ergonomics",
            "NoFrost",
        ],
        "cons": [
            "No inverter",
            "Same brand/service caveats as other Unionaire",
            "Prefer Signature inverter sibling if price is close",
        ],
    },
    "URN600CEPBLG1ADXHRBLS": {
        "layout": "bottom_freezer",
        "inverter": False,
        "nofrost": True,
        "fit": 7.4,
        "rank": 9,
        "summary": "440 L black glass Unionaire Signature bottom-freezer — looks-first large box.",
        "pros": [
            "Black glass aesthetic (strong for looks gate)",
            "~440 L capacity",
            "Bottom freezer",
            "Aggressive price (~23k class) leaves money for other rooms",
        ],
        "cons": [
            "Glass shows smudges; careful cleaning",
            "No inverter on this SKU",
            "Unionaire mid-tier reliability perception",
        ],
    },
    "RDNE420K02DXIPEGB": {
        "layout": "top_freezer",
        "inverter": True,
        "nofrost": True,
        "fit": 7.7,
        "rank": 10,
        "summary": "Beko black inverter ~367 L — good tech, slightly tight capacity.",
        "pros": [
            "Inverter + black + NoFrost",
            "Strong price (~26k)",
            "Beko network",
        ],
        "cons": [
            "~367 L is the lower edge of 'not too small' for heavy weekly prep",
            "Prefer 400 L+ siblings if shelf Tetris is a fear",
        ],
    },
    "FNT-BR470BMB": {
        "layout": "top_freezer",
        "inverter": False,
        "nofrost": True,
        "fit": 6.8,
        "rank": 11,
        "summary": "Cheapest black NoFrost ~397 L Fresh — budget only.",
        "pros": [
            "Lowest price black NoFrost that still clears ~360 L",
            "Local service density",
        ],
        "cons": [
            "No inverter",
            "Value-tier QC/noise variance",
            "Weakest match if reliability/noise are hard hates",
        ],
    },
    "Crispo": {
        "layout": "top_freezer",
        "inverter": False,
        "nofrost": True,
        "fit": 7.0,
        "rank": 12,
        "summary": "Zanussi Crispo 370 L black — entry NoFrost black.",
        "pros": [
            "Black NoFrost under 25k",
            "Crisper/TasteLock-style marketing on Zanussi line",
        ],
        "cons": [
            "370 L is only slightly above min capacity",
            "No inverter",
            "Less capacity than 400 L peers for little savings vs Zanussi 406",
        ],
    },
}

# Models excluded with reasons (for transparency in catalog meta)
EXCLUDED = [
    {"name": "Samsung RB34C672EB1 black 340L", "price": 30999, "reason": "Below min capacity 360 L (too small for weekly prep rule)"},
    {"name": "Beko RDNE448M20B black 408L inv", "price": 35499, "reason": "Over hard ceiling 35,000 EGP"},
    {"name": "Beko RDNE455M20XBIDB black 455L inv", "price": 35399, "reason": "Over hard ceiling 35,000 EGP"},
    {"name": "Beko B3RDNE500LXBR black 477L inv", "price": 43449, "reason": "Over hard ceiling 35,000 EGP"},
    {"name": "LG GTF452SSAN black 450L inv", "price": 36729, "reason": "Over hard ceiling 35,000 EGP"},
    {"name": "Unionaire defrost 310L black", "price": 14300, "reason": "Too small + manual defrost"},
    {"name": "Unionaire 330L black NoFrost", "price": 17500, "reason": "Below min capacity 360 L"},
    {"name": "Any non-black (silver/inox/white)", "reason": "Hard aesthetics requirement: black only"},
    {"name": "Minibar / no real freezer", "reason": "Must have freezer for batch cooking"},
]


def pick_research(name: str) -> dict | None:
    for key, val in RESEARCH.items():
        if key.lower() in name.lower():
            return val
    return None


def main() -> None:
    scrape = json.loads(SCRAPE.read_text(encoding="utf-8"))
    images_all = {}
    if IMAGES.exists():
        images_all = json.loads(IMAGES.read_text(encoding="utf-8"))

    items = []
    skipped = []
    for row in scrape:
        if not row.get("ok"):
            continue
        name = row.get("name") or ""
        price = row.get("price")
        url = row.get("url") or ""
        if not name or price is None:
            continue
        if "black" not in name.lower() and "black" not in url.lower():
            # RDNE448 name has black
            if "Black" not in name:
                skipped.append({"name": name, "reason": "not black"})
                continue
        # capacity
        import re

        m = re.search(r"(\d{2,4})\s*Liter", name, re.I)
        cap = int(m.group(1)) if m else None
        if cap is not None and cap < MIN_CAPACITY_L:
            skipped.append({"name": name, "price": price, "reason": f"capacity {cap} < {MIN_CAPACITY_L}"})
            continue
        if price > MAX_PRICE:
            skipped.append({"name": name, "price": price, "reason": f"price {price} > {MAX_PRICE}"})
            continue
        if re.search(r"mini\s*bar", name, re.I):
            skipped.append({"name": name, "reason": "minibar"})
            continue

        research = pick_research(name) or {}
        layout = research.get("layout")
        if not layout:
            if re.search(r"bottom\s*freezer", name, re.I):
                layout = "bottom_freezer"
            elif re.search(r"top\s*freezer", name, re.I):
                layout = "top_freezer"
            elif re.search(r"french", name, re.I):
                layout = "french"
            else:
                layout = "top_freezer"

        inverter = research.get("inverter")
        if inverter is None:
            inverter = bool(row.get("hasInverterWord")) and "GTF402" not in name
        if "GTF402SBAN" in name:
            inverter = False  # confirmed non-inverter

        gallery = row.get("gallery") or []
        og = row.get("og") or (gallery[0] if gallery else None)
        # merge older image cache
        if url in images_all and images_all[url].get("og"):
            if not og:
                og = images_all[url]["og"]
            g2 = images_all[url].get("gallery") or []
            gallery = list(dict.fromkeys(gallery + g2))[:12]

        brand = name.split()[0]
        item_id = "fr_" + re.sub(r"[^a-zA-Z0-9]+", "_", name.split("-")[-1].strip() if "-" in name else name)[:40]

        items.append(
            {
                "id": item_id,
                "category": "fridge",
                "name": name,
                "brand": brand,
                "priceEGP": price,
                "currency": "EGP",
                "retailer": "B.TECH",
                "url": url.split("?")[0],
                "scrapedAt": "2026-07-17",
                "color": "black",
                "capacity": cap,
                "capacityUnit": "L",
                "capacityL": cap,
                "specs": {
                    "capacityL": cap,
                    "layout": layout,
                    "inverter": inverter,
                    "nofrost": research.get("nofrost", True),
                    "dispenser": False,
                    "hasFreezer": True,
                },
                "imageUrl": og,
                "imageGallery": gallery if gallery else ([og] if og else []),
                "pros": research.get("pros")
                or [
                    "Black finish",
                    f"Within hard budget (≤{MAX_PRICE:,} EGP)",
                    f"Capacity listed {cap} L with freezer compartment",
                ],
                "cons": research.get("cons")
                or [
                    "Deep research limited — verify warranty and noise in showroom",
                    "Re-check live price before purchase",
                ],
                "summary": research.get("summary") or "Meets hard filters: black, freezer, ≤35k, capacity ≥360 L.",
                "researchFitScore": research.get("fit"),
                "rank": research.get("rank"),
                "hasDeepResearch": bool(research.get("pros")),
                "status": "shortlist" if research.get("rank") and research["rank"] <= 5 else "catalog",
                "lifestyleFitScore": research.get("fit"),
                "tags": [
                    "black",
                    "under_35k",
                    layout,
                    "inverter" if inverter else "non_inverter",
                    "nofrost",
                ],
            }
        )

    # de-dupe by url
    seen = set()
    deduped = []
    for it in sorted(items, key=lambda x: (x.get("rank") or 99, x.get("priceEGP") or 0)):
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        deduped.append(it)

    catalog = {
        "version": 1,
        "title": "Fridge shortlist — hard filters applied",
        "lastUpdated": "2026-07-17",
        "currency": "EGP",
        "filtersApplied": {
            "color": "black only",
            "maxPriceEGP": MAX_PRICE,
            "minCapacityL": MIN_CAPACITY_L,
            "mustHaveFreezer": True,
            "excludeMinibar": True,
            "excludeNonBlack": True,
        },
        "householdContext": {
            "city": "6th of October City",
            "mealPrep": "Friday weekly batch",
            "freezeLoad": "about half a normal freezer weekly",
            "layoutPreference": "top_freezer_space_story (bottom freezers still listed if they pass hard filters)",
        },
        "counts": {"included": len(deduped), "scrapeRows": len(scrape)},
        "excludedExamples": EXCLUDED + skipped[:20],
        "disclaimer": "Prices from B.TECH product pages 2026-07-17. Re-verify before buy. Photos hotlinked from retailer CDN.",
        "items": deduped,
    }
    OUT.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    print("included", len(deduped))
    for it in deduped:
        print(it.get("rank"), it["priceEGP"], it["capacity"], it["name"][:60])


if __name__ == "__main__":
    main()
