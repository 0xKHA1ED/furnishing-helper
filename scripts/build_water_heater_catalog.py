# -*- coding: utf-8 -*-
"""Electric water heaters for 2-person Egypt apartment — prefer 50–80 L storage."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "data" / "appliances"

SCRAPES = [
    "_wh_btech_cat.json",
    "_wh_btech.json",
    "_wh_amazon.json",
    "_wh_amazon80.json",
    "_wh_jumia.json",
]

BRANDS = [
    "Ariston",
    "Fresh",
    "Olympic",
    "Unionaire",
    "Tornado",
    "Beko",
    "Toshiba",
    "GMC",
    "Universal",
    "Ocean",
    "Venus",
    "Electrolux",
    "Bosch",
    "Zanussi",
    "White Whale",
    "Kiriazi",
]


def load_cards():
    cards = []
    for name in SCRAPES:
        p = APP / name
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for c in d.get("cards") or []:
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


def fix_price(p, source: str):
    if p is None:
        return None
    try:
        p = int(p)
    except (TypeError, ValueError):
        return None
    # Jumia sometimes concatenates without separator → 305000 means 3050
    if p >= 80000:
        if p % 100 == 0 and 1500 <= p // 100 <= 50000:
            p = p // 100
        elif p % 10 == 0 and 1500 <= p // 10 <= 50000:
            p = p // 10
    if p < 1500 or p > 60000:
        return None
    return p


def parse_liters(blob: str):
    b = blob
    m = re.search(r"(\d{2,3})\s*(?:Liter|Liters|Litre|Litres|L\b|لتر)", b, re.I)
    if m:
        n = int(m.group(1))
        if 10 <= n <= 200:
            return n
    m2 = re.search(r"\b(30|40|50|60|70|80|100|120|150)\b", b)
    if m2 and re.search(r"heater|water|سخان", b, re.I):
        return int(m2.group(1))
    return None


def is_gas(blob: str) -> bool:
    return bool(re.search(r"\bgas\b|غاز|LPG|natural gas", blob, re.I))


def is_space_heater(blob: str) -> bool:
    if re.search(r"water\s*heater|سخان\s*مياه|electric water", blob, re.I):
        return False
    return bool(
        re.search(
            r"space heater|fan heater|oil (filled )?heater|radiator heater|دفاية|heater fan",
            blob,
            re.I,
        )
    )


def is_instant(blob: str) -> bool:
    return bool(re.search(r"instant|tankless|فوري|بدون خزان|inline", blob, re.I))


def brand_of(name: str) -> str:
    for b in BRANDS:
        if re.search(rf"\b{re.escape(b)}\b", name, re.I):
            return b
    return name.split()[0] if name else "Unknown"


def mount(blob: str) -> str:
    b = blob.lower()
    if "horizontal" in b:
        return "horizontal"
    if "vertical" in b:
        return "vertical"
    return "unspecified"


def size_band(liters) -> str:
    if liters is None:
        return "unknown"
    if liters < 40:
        return "small_under_40"
    if liters == 40:
        return "adjacent_40"
    if liters == 50:
        return "main_50"
    if 50 < liters <= 80:
        return "main_80"
    if liters <= 100:
        return "large_100"
    return "oversized"


def score(liters, price, brand, instant, source, blob: str):
    s = 50
    pros, cons = [], []
    band = size_band(liters)

    if band == "main_50":
        s -= 18
        pros.append("50 L — classic size for a couple (one bathroom + kitchen)")
    elif band == "main_80":
        s -= 16
        pros.append("80 L — comfortable if two showers back-to-back or more hot water buffer")
    elif band == "adjacent_40":
        s += 4
        cons.append("40 L is tight for two showers close together — adjacent option only")
        pros.append("Smaller footprint / lower price than 50–80 L")
    elif band == "small_under_40":
        s += 8
        cons.append("Under 40 L can feel tight for two people showering close together")
        pros.append("OK as kitchen-only / tight install space")
    elif band == "large_100":
        s += 6
        cons.append("100 L is more than most couples need — bigger standby heat loss")
    elif band == "oversized":
        s += 15
        cons.append("Oversized for two people")
    else:
        s += 10
        cons.append("Capacity unclear from title — verify liters")

    if instant:
        s += 4
        pros.append("Instant/tankless — endless flow if electrical supply allows")
        cons.append("Needs correct high-power circuit; electrician must confirm amps")
    else:
        s -= 4
        pros.append("Storage tank — common Egypt apartment install, simpler wiring than high-power instant")

    tier_a = {"Ariston", "Beko", "Electrolux", "Bosch", "Toshiba"}
    tier_b = {"Fresh", "Olympic", "Unionaire", "Tornado", "Universal", "Venus"}
    if brand in tier_a:
        s -= 8
        pros.append(f"{brand} — stronger brand/service recognition")
    elif brand in tier_b:
        s -= 5
        pros.append(f"{brand} — common Egypt retail brand")
    else:
        s += 2
        cons.append("Lesser-known brand — confirm warranty years on tank/element")

    if price:
        if price <= 3500:
            s -= 4
            pros.append("Budget-friendly under ~3.5k")
        elif price <= 5000:
            s -= 2
        elif price >= 10000:
            s += 3
            cons.append("Premium price — justify with warranty/efficiency")

    if "b.tech" in source.lower() or "btech" in source.lower():
        s -= 2
        pros.append("B.TECH path for delivery/install inquiry")
    elif "amazon" in source.lower() or "jumia" in source.lower():
        s += 2
        cons.append("Marketplace — verify seller and official warranty stamp")

    if "enamel" in blob.lower() or "glass" in blob.lower() or "titanium" in blob.lower():
        s -= 2
        pros.append("Lined tank mention (enamel/glass) — better longevity vs bare steel")

    if not pros:
        pros.append("Electric water heater option available in Egypt retail")
    if not cons:
        cons.append("Confirm wall strength, vertical vs horizontal mount, and dedicated breaker")

    return max(1, s), pros[:6], cons[:5], band


def build():
    raw = load_cards()
    by = {}
    for c in raw:
        u = clean_url(c.get("url") or "")
        if not u:
            continue
        name = re.sub(r"\s+", " ", (c.get("name") or "").strip())
        blob = f"{name} {c.get('text','')}"
        if is_space_heater(blob):
            continue
        if is_gas(blob):
            continue
        price = fix_price(c.get("priceEGP"), c.get("source") or "")
        liters = parse_liters(blob)
        prev = by.get(u)
        if not prev or (price and (not prev.get("priceEGP") or price < prev["priceEGP"])):
            img = c.get("imageUrl") or ""
            if prev and not img:
                img = prev.get("imageUrl") or ""
            by[u] = {
                "name": name[:200],
                "url": u,
                "imageUrl": img,
                "priceEGP": price or prev.get("priceEGP") if prev else price,
                "source": c.get("source") or "",
                "text": (c.get("text") or "")[:300],
                "liters": liters,
            }
            if prev and price is None and prev.get("priceEGP"):
                by[u]["priceEGP"] = prev["priceEGP"]

    items = []
    excluded_examples = []
    for c in by.values():
        name = c["name"]
        blob = f"{name} {c.get('text','')}"
        liters = c.get("liters") or parse_liters(blob)
        price = c.get("priceEGP")
        brand = brand_of(name)
        instant = is_instant(blob)
        source = c.get("source") or ""
        mnt = mount(blob)

        band = size_band(liters)
        excluded = False
        reasons = []

        # Main: 50–80 L electric storage (or instant in that power class)
        # Keep 40 as adjacent, exclude gas already, exclude tiny <30, exclude non-water
        if liters is not None and liters < 30:
            excluded = True
            reasons.append(f"{liters} L too small for household hot water")
        if liters is not None and liters > 100:
            excluded = True
            reasons.append(f"{liters} L oversized for two people")
        if price is None:
            reasons.append("Price missing on scrape")
        if not re.search(r"water|heater|سخان|liter|litre", name, re.I):
            excluded = True
            reasons.append("Not clearly a water heater")

        # main list: 40–80 included; mark 40 as adjacent via tags not exclude
        sc, pros, cons, band = score(liters, price, brand, instant, source, blob)
        if reasons:
            cons = reasons + cons

        # Prefer main band in ranking later
        if not excluded and band in ("main_50", "main_80"):
            sc = max(1, sc - 5)
        if not excluded and band == "small_under_40" and liters and liters >= 40:
            sc = max(1, sc - 2)

        slug = re.sub(r"[^a-z0-9]+", "_", (c["url"].split("/")[-1] or name).lower())[:48]
        item = {
            "id": f"wh_{slug}",
            "rank": sc,
            "name": name,
            "brand": brand,
            "priceEGP": price,
            "capacityL": liters,
            "sizeBand": band,
            "type": "instant" if instant else "storage",
            "fuel": "electric",
            "mount": mnt,
            "url": c["url"],
            "imageUrl": c.get("imageUrl") or "",
            "source": source,
            "summary": (
                f"{liters or '?'} L electric {'instant' if instant else 'storage'} · "
                f"for couple apartment · band {band.replace('_', ' ')}"
            ),
            "pros": pros,
            "cons": cons,
            "tags": [
                t
                for t in [
                    band,
                    "electric",
                    "instant" if instant else "storage",
                    f"{liters}l" if liters else None,
                    brand.lower(),
                ]
                if t
            ],
            "excluded": excluded,
            "householdFit": (
                "Primary pick band for 2 people"
                if band in ("main_50", "main_80")
                else "Adjacent / verify need"
                if band in ("adjacent_40", "small_under_40", "large_100")
                else "Check capacity"
            ),
            "installNote": "Electrician: dedicated breaker, earth, pressure relief, wall anchors for full tank weight",
            "scrapeNote": "Playwright PLP 2026-07-17 — re-verify price/stock/warranty",
        }
        if excluded and len(excluded_examples) < 15:
            excluded_examples.append(
                {
                    "name": name[:100],
                    "price": price,
                    "capacityL": liters,
                    "reason": "; ".join(reasons) if reasons else "filtered",
                }
            )
        items.append(item)

    main = [i for i in items if not i["excluded"]]
    out = [i for i in items if i["excluded"]]

    # Collapse near-duplicates (same brand + liters + similar title)
    def norm_key(it):
        n = re.sub(r"[^a-z0-9]+", " ", (it["name"] or "").lower())
        n = re.sub(r"\b(white|black|digital|electric|water|heater|liter|litre|liters|litres|l)\b", " ", n)
        n = re.sub(r"\s+", " ", n).strip()[:40]
        return (it.get("brand") or "", it.get("capacityL"), it.get("type"), n)

    main.sort(key=lambda x: (x.get("priceEGP") is None, x.get("priceEGP") or 10**9, not x.get("imageUrl")))
    deduped = []
    seen_k = set()
    for it in main:
        k = norm_key(it)
        if k in seen_k:
            continue
        seen_k.add(k)
        deduped.append(it)
    main = deduped

    def sk(x):
        band_ord = {
            "main_50": 0,
            "main_80": 1,
            "adjacent_40": 2,
            "small_under_40": 3,
            "large_100": 4,
            "unknown": 5,
            "oversized": 6,
        }.get(x["sizeBand"], 5)
        type_ord = 0 if x["type"] == "storage" else 1
        brand_ord = 0 if x["brand"] in {"Ariston", "Fresh", "Olympic", "Beko", "Unionaire", "Tornado"} else 1
        return (
            band_ord,
            type_ord,
            brand_ord,
            x.get("priceEGP") is None,
            x.get("priceEGP") or 10**9,
            x["name"],
        )

    main.sort(key=sk)
    for i, it in enumerate(main, 1):
        it["rank"] = i
    for i, it in enumerate(out, 1):
        it["rank"] = 800 + i

    final = main + out
    rec = [
        it["id"]
        for it in main
        if it["sizeBand"] in ("main_50", "main_80") and it["type"] == "storage"
    ][:10]

    catalog = {
        "version": 1,
        "title": "Electric water heater — couple (prefer 50–80 L storage)",
        "lastUpdated": "2026-07-17",
        "currency": "EGP",
        "filtersApplied": {
            "fuel": "electric only",
            "household": "2 adults, Egypt apartment",
            "preferredCapacityL": [50, 80],
            "adjacentCapacityL": [40, 100],
            "typePrefer": "storage tank (simpler install); instant listed with wiring caveat",
            "exclude": ["gas", "space heaters", "<30 L household", ">100 L"],
        },
        "sizeGuide": {
            "40L": "Tight for two if simultaneous shower + kitchen — adjacent only",
            "50L": "Recommended default for couple, one main bathroom",
            "80L": "Recommended if you want buffer / two showers in a row",
            "100L": "Usually more than needed for two — only if long baths or multi-point",
        },
        "counts": {
            "included": len(main),
            "excludedListed": len(out),
            "total": len(final),
            "withImage": len([i for i in final if i.get("imageUrl")]),
            "byBand": {},
            "bySource": {},
        },
        "recommendedIds": rec,
        "shoppingRoute": [
            "Filter Main 50 L or Main 80 L first",
            "Prefer storage electric (Ariston / Fresh / Olympic / Unionaire) with clear tank warranty",
            "Confirm vertical vs horizontal for your wall space",
            "Budget electrician install — never hang a full tank on weak fixings",
            "If considering instant: electrician must size cable/breaker before purchase",
            "Re-check B.TECH/Amazon price day of buy",
        ],
        "kits": [
            {
                "id": "kit_50_default",
                "name": "Default couple kit — 50 L storage",
                "note": "Best balance of cost, heat-up, and space for 2 people",
                "items": ["50 L electric storage", "install + safety valve", "dedicated breaker"],
            },
            {
                "id": "kit_80_buffer",
                "name": "Buffer kit — 80 L storage",
                "note": "When two showers often run close together",
                "items": ["80 L electric storage", "install", "timer/eco use to cut bills"],
            },
        ],
        "excludedExamples": excluded_examples,
        "disclaimer": (
            "Scraped B.TECH water heaters category, Amazon.eg 50/80 L electric water heater searches, "
            "Jumia Egypt. Gas and room heaters excluded. Capacity for two people: main band 50–80 L. "
            "Prices PLP 2026-07-17 — re-verify. Install must meet Egyptian electrical safety practice."
        ),
        "items": final,
    }

    bands, src = {}, {}
    for it in final:
        src[it.get("source") or "?"] = src.get(it.get("source") or "?", 0) + 1
        if not it["excluded"]:
            bands[it["sizeBand"]] = bands.get(it["sizeBand"], 0) + 1
    catalog["counts"]["byBand"] = bands
    catalog["counts"]["bySource"] = src

    path = APP / "water_heater_catalog.json"
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", path, "included", len(main), "excluded", len(out))
    for it in main[:12]:
        print(
            f"  #{it['rank']} {it.get('capacityL')}L {it['brand']} {it.get('priceEGP')} {it['name'][:50]}"
        )


if __name__ == "__main__":
    build()
