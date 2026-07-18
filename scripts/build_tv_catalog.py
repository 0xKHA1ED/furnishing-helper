# -*- coding: utf-8 -*-
"""Build tv_catalog.json — 50\"+ TVs under 26k EGP, no 4K/gimmick priority."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "data" / "appliances"
MAX_PRICE = 26000
MIN_INCH = 50

SCRAPES = [
    "_tv_btech_v2.json",  # good LE price parse
    # skip _tv_btech_50.json — bad price fragments from model numbers
    "_tv_amazon.json",
    "_tv_jumia.json",
]

INCH_RE = re.compile(r"(\d{2})\s*(?:Inch|inch|\"|''|بوصة)", re.I)
BRANDS = [
    "Samsung",
    "LG",
    "Hisense",
    "Sharp",
    "Toshiba",
    "Sony",
    "TCL",
    "Haier",
    "Fresh",
    "Unionaire",
    "Tornado",
    "ATA",
    "Ultra",
    "Grouhy",
    "Armadillo",
    "Elc",
    "Evolve",
    "Toshiba",
    "Panasonic",
    "Philips",
]


def load_cards():
    cards = []
    for name in SCRAPES:
        p = APP / name
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for c in d.get("cards", []):
            cards.append(c)
    return cards


def clean_url(u: str) -> str:
    if not u:
        return ""
    u = u.split("?")[0].rstrip("/")
    m = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", u, re.I)
    if m:
        return f"https://www.amazon.eg/dp/{m.group(1).upper()}"
    return u


def parse_inch(text: str):
    if not text:
        return None
    m = INCH_RE.search(text)
    if m:
        return int(m.group(1))
    # model prefixes 50U8000, 55A6N
    m2 = re.search(r"\b([456][0-9])[A-Z0-9]{2,}", text)
    if m2:
        n = int(m2.group(1))
        if 32 <= n <= 85:
            return n
    return None


def price_plausible(price: int | None, inch: int | None) -> bool:
    if price is None:
        return False
    if price < 8000 or price > 200000:
        return False
    if inch:
        # reject model-number fragments (e.g. UA98DU9000 → 9000)
        floors = [
            (85, 45000),
            (75, 35000),
            (70, 28000),
            (65, 16000),
            (58, 14000),
            (55, 12000),
            (50, 11000),
        ]
        for min_inch, floor in floors:
            if inch >= min_inch and price < floor:
                return False
    return True


def parse_price(c: dict, inch: int | None = None):
    p = c.get("priceEGP")
    candidates = []
    if isinstance(p, (int, float)) and p > 0:
        candidates.append(int(p))
    text = f"{c.get('name','')} {c.get('text','')}"
    text = re.sub(r"From.*?LE/mo", " ", text, flags=re.I)
    for m in re.finditer(r"(\d{1,3}(?:,\d{3})+)\s*LE", text, re.I):
        n = int(m.group(1).replace(",", ""))
        if 8000 <= n <= 200000:
            candidates.append(n)
    # prefer plausible; among those, lowest (sale)
    ok = [n for n in candidates if price_plausible(n, inch)]
    if ok:
        return min(ok)
    return None


def brand_of(name: str) -> str:
    for b in BRANDS:
        if re.search(rf"\b{re.escape(b)}\b", name, re.I):
            return b
    return name.split()[0] if name else "Unknown"


def panel_res(blob: str) -> tuple[str, str]:
    b = blob.lower()
    if "oled" in b:
        panel = "OLED"
    elif "nanocell" in b or "nano cell" in b or "nano 4k" in b:
        panel = "NanoCell"
    elif "qled" in b or "neo qled" in b:
        panel = "QLED"
    elif "mini-led" in b or "miniled" in b:
        panel = "Mini-LED"
    else:
        panel = "LED"

    if "8k" in b:
        res = "8K"
    elif "4k" in b or "uhd" in b or "ultra hd" in b:
        res = "4K UHD"
    elif "fhd" in b or "full hd" in b or "1080" in b:
        res = "FHD"
    elif re.search(r"\bhd\b", b) and "uhd" not in b:
        res = "HD"
    else:
        res = "unspecified"
    return panel, res


def is_bundle_junk(blob: str) -> bool:
    b = blob.lower()
    junk = [
        "soundbar only",
        "wall mount only",
        "remote only",
        "tv stand only",
        "bracket only",
        "cover for tv",
        "screen protector",
        "fire stick only",
    ]
    return any(j in b for j in junk)


def score_item(inch, price, brand, panel, res, blob: str, source: str):
    """Lower is better. 4K/gimmicks do NOT get bonus."""
    s = 50
    pros, cons = [], []

    # Size
    if inch >= 65:
        s -= 18
        pros.append(f"{inch}\" — large for living room distance")
    elif inch >= 55:
        s -= 14
        pros.append(f"{inch}\" — solid living-room size under budget")
    elif inch >= 50:
        s -= 8
        pros.append(f"{inch}\" meets your 50\" minimum")

    # Price headroom under 26k
    if price is not None:
        headroom = MAX_PRICE - price
        if headroom >= 8000:
            s -= 6
            pros.append(f"Leaves ~{headroom:,} EGP under 26k ceiling")
        elif headroom >= 3000:
            s -= 3
            pros.append(f"Under budget by ~{headroom:,} EGP")
        elif headroom < 500:
            cons.append("Near the 26k ceiling — little room for stand/mount")
            s += 2

    # Brand reliability (service in Egypt)
    tier_a = {"Samsung", "LG", "Sony", "Hisense", "Sharp", "Toshiba", "Panasonic"}
    tier_b = {"TCL", "Haier", "Philips", "Fresh"}
    if brand in tier_a:
        s -= 12
        pros.append(f"{brand} — wider Egypt service / spare parts path")
    elif brand in tier_b:
        s -= 5
        pros.append(f"{brand} — common retail brand; check warranty card")
    else:
        s += 4
        cons.append("Lesser-known brand — confirm warranty length and service centres")

    # User said 4K not important — do not boost 4K. Slight preference for simple LED.
    if panel in ("OLED", "Mini-LED"):
        s += 2
        cons.append(f"{panel} is a premium panel family — may be overkill vs your no-gimmick brief")
    if panel in ("NanoCell", "QLED"):
        # not bad, just not a ranking reason
        cons.append(f"{panel} marketing layer — fine if price is right, not a must")
    if panel == "LED" and res in ("FHD", "HD", "unspecified"):
        s -= 4
        pros.append("Simple LED panel — matches ‘gimmicks not important’ brief")
    if res == "FHD":
        s -= 2
        pros.append("FHD is fine for 50–55\" at normal living distance (you said 4K not required)")
    if res == "4K UHD":
        # neutral: common at this size, no bonus
        pros.append("4K available but not required for your brief")

    # Egypt practical
    if "built-in receiver" in blob.lower() or "built in receiver" in blob.lower() or "receiver" in blob.lower():
        s -= 5
        pros.append("Built-in receiver — useful for Egyptian satellite setups")

    if "frameless" in blob.lower():
        # aesthetic only
        pass

    if "b.tech" in source.lower() or "btech" in source.lower():
        s -= 3
        pros.append("B.TECH listing — installment/delivery path known for your area")
    elif "amazon" in source.lower() or "jumia" in source.lower():
        cons.append("Marketplace — verify seller, returns, and official warranty stamp")
        s += 3

    # Bundles with speakers can inflate price
    if "kisonli" in blob.lower() or "with soundbar" in blob.lower() or "with speaker" in blob.lower():
        cons.append("May be a TV+speaker bundle — compare bare TV price")
        s += 3

    if not pros:
        pros.append("In-budget 50\"+ option available online in Egypt")
    if not cons:
        cons.append("Confirm wall-mount VESA, actual depth, and HDR support only if you care later")

    return max(1, s), pros[:6], cons[:5]


def build():
    raw = load_cards()
    by = {}
    for c in raw:
        u = clean_url(c.get("url") or "")
        if not u:
            continue
        name = re.sub(r"\s+", " ", (c.get("name") or "").strip())
        if len(name) < 8:
            continue
        blob = f"{name} {c.get('text','')}"
        if is_bundle_junk(blob):
            continue
        inch = parse_inch(name) or parse_inch(blob)
        price = parse_price(c, inch)
        # keep candidates
        key = u
        prev = by.get(key)
        better = False
        if not prev:
            better = True
        elif price and price_plausible(price, inch):
            if not prev.get("priceEGP") or not price_plausible(prev.get("priceEGP"), prev.get("inch")):
                better = True
            elif price < prev["priceEGP"]:
                better = True
        if better:
            by[key] = {
                "name": name[:200],
                "url": u,
                "imageUrl": c.get("imageUrl") or "",
                "priceEGP": price,
                "source": c.get("source") or "",
                "text": (c.get("text") or "")[:300],
                "inch": inch,
            }

    items = []
    excluded_examples = []
    for c in by.values():
        inch = c.get("inch")
        price = c.get("priceEGP")
        name = c["name"]
        blob = f"{name} {c.get('text','')}"
        brand = brand_of(name)
        panel, res = panel_res(blob)

        reasons = []
        excluded = False
        if inch is None:
            # try keep if model looks like TV but size unknown
            if price and price <= MAX_PRICE and re.search(r"\bTV\b", name, re.I):
                reasons.append("size unclear from title — verify inches before buy")
            else:
                continue
        elif inch < MIN_INCH:
            excluded = True
            reasons.append(f"{inch}\" below 50\" minimum")
        if price is None or not price_plausible(price, inch):
            excluded = True
            reasons.append("price missing or implausible for size — re-check listing")
            price = c.get("priceEGP")  # keep raw for display if any
        elif price > MAX_PRICE:
            excluded = True
            reasons.append(f"{price:,} EGP over 26k budget")

        # still catalog adjacent excluded for transparency (under 50 or over budget)
        sc, pros, cons = score_item(
            inch or 0, price or MAX_PRICE + 1, brand, panel, res, blob, c.get("source") or ""
        )
        if reasons:
            cons = reasons + cons

        slug = re.sub(r"[^a-z0-9]+", "_", (c["url"].split("/")[-1] or name).lower())[:50]
        item = {
            "id": f"tv_{slug}",
            "rank": sc,
            "name": name,
            "brand": brand,
            "priceEGP": price,
            "sizeInches": inch,
            "panel": panel,
            "resolution": res,
            "url": c["url"],
            "imageUrl": c.get("imageUrl") or "",
            "source": c.get("source") or "",
            "summary": (
                f"{inch or '?'}″ {panel} {res}. "
                f"Budget filter ≤{MAX_PRICE:,} EGP; size ≥{MIN_INCH}″. "
                f"4K/gimmicks not prioritized per brief."
            ),
            "pros": pros,
            "cons": cons,
            "tags": [
                t
                for t in [
                    brand.lower(),
                    f"{inch}in" if inch else None,
                    panel.lower().replace(" ", "_"),
                    res.lower().replace(" ", "_"),
                    "under_26k" if price and price <= MAX_PRICE else "over_budget",
                    "main" if (not excluded and inch and inch >= MIN_INCH and price and price <= MAX_PRICE) else "out",
                ]
                if t
            ],
            "excluded": excluded,
            "scrapeNote": "Playwright PLP 2026-07-17 — re-verify price/stock/warranty",
        }

        if excluded:
            if len(excluded_examples) < 25:
                excluded_examples.append(
                    {
                        "name": name[:120],
                        "price": price,
                        "sizeInches": inch,
                        "reason": "; ".join(reasons) if reasons else "filtered",
                    }
                )
        items.append(item)

    # Main set ranking
    main = [i for i in items if not i["excluded"]]
    out_of = [i for i in items if i["excluded"]]

    def sort_key(x):
        brand_tier = 0 if x["brand"] in {"Samsung", "LG", "Hisense", "Sharp", "Toshiba", "Sony"} else 1
        size_pref = -(x.get("sizeInches") or 0)  # larger first within budget
        # de-prioritize gimmick panels slightly
        panel_pen = 1 if x.get("panel") in ("OLED", "NanoCell", "QLED", "Mini-LED") else 0
        return (
            brand_tier,
            panel_pen,
            size_pref,
            x.get("priceEGP") is None,
            x.get("priceEGP") or 10**9,
            x["name"],
        )

    main.sort(key=sort_key)
    for i, it in enumerate(main, 1):
        it["rank"] = i
    for i, it in enumerate(out_of, 1):
        it["rank"] = 800 + i

    final = main + out_of

    # Recommended picks (top practical)
    picks = []
    for it in main:
        if it["brand"] in {"Samsung", "LG", "Hisense", "Sharp", "Toshiba", "Haier"} and it.get(
            "sizeInches", 0
        ) >= 50:
            picks.append(it["id"])
        if len(picks) >= 8:
            break

    catalog = {
        "version": 1,
        "title": "TV shortlist — ≥50″ · ≤26,000 EGP · no 4K/gimmick priority",
        "lastUpdated": "2026-07-17",
        "currency": "EGP",
        "filtersApplied": {
            "maxPriceEGP": MAX_PRICE,
            "minSizeInches": MIN_INCH,
            "resolutionPriority": "none (4K not important)",
            "gimmicksPriority": "none (NanoCell/QLED/OLED not ranked higher)",
            "prefer": [
                "size for living room",
                "reliable brand service in Egypt",
                "built-in receiver when present",
                "simple LED",
                "B.TECH / clear warranty path",
            ],
        },
        "householdContext": {
            "city": "6th of October City",
            "roomHint": "Living 375×450 cm — 50–55″ typical; 65″ if seating distance allows",
            "budgetEGP": MAX_PRICE,
        },
        "counts": {
            "included": len(main),
            "excludedListed": len(out_of),
            "total": len(final),
            "withImage": len([i for i in final if i.get("imageUrl")]),
            "bySource": {},
            "byBrand": {},
            "bySize": {},
        },
        "recommendedIds": picks,
        "shoppingRoute": [
            "Filter gallery to Main (≥50″ & ≤26k)",
            "Prefer Samsung / LG / Hisense / Sharp if prices are close — service path",
            "Ignore 4K/QLED/Nano marketing unless two models are equal on size+price+warranty",
            "Confirm built-in receiver if you use satellite; otherwise a cheap external receiver is fine",
            "Budget leftover for wall mount or TV bench — do not blow full 26k on panel only if you need furniture",
            "Re-check B.TECH price the day you buy — TV promos move weekly",
        ],
        "kits": [
            {
                "id": "kit_value_55",
                "name": "Value 55″ under 26k",
                "note": "Biggest practical size still under ceiling; brand over gimmicks",
                "rule": "Pick cheapest 55″ from Samsung/LG/Hisense/Sharp with ≥1y warranty",
            },
            {
                "id": "kit_50_headroom",
                "name": "50″ + cash left",
                "note": "Take a solid 50″ ~15–19k and keep money for stand/mount",
                "rule": "50″ LED with built-in receiver; ignore 4K upsell",
            },
            {
                "id": "kit_65_if_fit",
                "name": "65″ only if seating distance OK",
                "note": "Several 65″ dip under 26k on promo — only if living seating is far enough",
                "rule": "Sit ≥2.2–2.5m from screen for 65″ FHD/4K mixed use",
            },
        ],
        "excludedExamples": excluded_examples,
        "disclaimer": (
            "Scraped B.TECH TV category, Amazon.eg 50″ search, Jumia 50″ smart TV search (2026-07-17). "
            "Prices from listing cards — re-verify. Hard filters: size ≥50″ and price ≤26,000 EGP for main list. "
            "4K and marketing panels are listed but not ranked as upgrades."
        ),
        "items": final,
    }

    src, br, sz = {}, {}, {}
    for it in final:
        src[it.get("source") or "?"] = src.get(it.get("source") or "?", 0) + 1
        if not it["excluded"]:
            br[it["brand"]] = br.get(it["brand"], 0) + 1
            k = str(it.get("sizeInches") or "?")
            sz[k] = sz.get(k, 0) + 1
    catalog["counts"]["bySource"] = src
    catalog["counts"]["byBrand"] = br
    catalog["counts"]["bySize"] = sz

    out = APP / "tv_catalog.json"
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "Wrote",
        out,
        "included",
        len(main),
        "excluded",
        len(out_of),
        "images",
        catalog["counts"]["withImage"],
    )
    print("bySize", sz)
    print("top:")
    for it in main[:12]:
        print(
            f"  #{it['rank']} {it.get('sizeInches')}\" {it['brand']} {it.get('priceEGP')} {it['name'][:55]}"
        )


if __name__ == "__main__":
    build()
