"""Parse deep washer MCP scrape and rebuild washer_catalog.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP = Path(
    r"C:\Users\h\.grok\sessions\C%3A%5CUsers%5Ch%5CDesktop%5CNew%20folder%20%282%29"
    r"\019f70f2-353c-7362-95d5-0ad56442c7a3\mcp"
    r"\call-5d711e43-40ab-4baa-ae56-d2adf35fec7f-110.txt"
)
SCRAPE_OUT = ROOT / "data/appliances/_washer_deep_scrape.json"
WM_OUT = ROOT / "data/appliances/washer_catalog.json"

# Extra known SKU if missing from scroll
EXTRA = [
    {
        "name": "Sharp ES-TN09GDSP Top Load washing Machine , 9 kg , Black",
        "price": 13549,
        "href": "https://btech.com/en/p/sharp-topload-auto-washingmachine-9kg-estn09gdsp",
        "kg": 9,
        "top": True,
        "front": False,
        "half": False,
        "inverter": False,
        "color": "black",
        "brand": "Sharp",
        "imageUrl": "https://dwecxxryy5p59.cloudfront.net/catalogs/d/f/8/2/df8296ed9788cf1f3d8bac7ac7008dd2b3b4f724_studio_session_228.jpeg",
    },
]

BRAND_TRUST = {
    "LG": 9.0,
    "Samsung": 8.8,
    "Toshiba": 8.5,
    "Beko": 8.4,
    "Sharp": 8.0,
    "Haier": 7.3,
    "Tornado": 7.0,
    "Midea": 6.9,
    "Fresh": 6.8,
    "Unionaire": 6.5,
    "White Point": 6.4,
    "Zanussi": 7.4,
}


def slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()[:48]


def model_token(name: str) -> str:
    m = re.search(r"([A-Z]{1,6}[-]?[A-Z0-9]{3,}[A-Z0-9\-/]*)", name)
    return m.group(1) if m else slug(name)[:20]


def load_mcp() -> list[dict]:
    text = MCP.read_text(encoding="utf-8", errors="replace")
    raw = text.split("### Result", 1)[1].strip() if "### Result" in text else text[text.find("{") :]
    data = None
    for end in range(len(raw), max(2000, len(raw) - 30000), -1):
        try:
            data = json.loads(raw[:end])
            break
        except json.JSONDecodeError:
            continue
    if data is None:
        # salvage "kept" array
        i = raw.find('"kept"')
        if i < 0:
            raise SystemExit("cannot parse MCP")
        arr = raw[raw.find("[", i) :]
        for k in range(len(arr), max(0, len(arr) - 8000), -1):
            try:
                kept = json.loads(arr[:k])
                data = {"kept": kept}
                break
            except json.JSONDecodeError:
                continue
    kept = data.get("kept") or data.get("items") or []
    return kept


def pros_cons(it: dict) -> tuple[list[str], list[str], str, float]:
    brand = it.get("brand") or "Unknown"
    kg = it.get("kg") or 0
    inv = bool(it.get("inverter"))
    color = it.get("color") or "other"
    price = it.get("price") or 0
    trust = BRAND_TRUST.get(brand, 6.5)

    pros, cons = [], []
    if 7 <= kg <= 9:
        pros.append(f"Couple-size {kg:g} kg — weekly loads for two without oversized bulk")
    elif 10 <= kg <= 13:
        pros.append(f"{kg:g} kg buffer for bedding / occasional big loads")
        cons.append("Larger than couple need — fill the drum or you waste water/energy")
    else:
        pros.append(f"Large {kg:g} kg — only if you want future family/bedding headroom")
        cons.append("Overkill for two people; footprint and water use rise")

    if inv:
        pros.append("Inverter motor — quieter start/spin and better longevity odds")
    else:
        cons.append("Non-inverter motor — louder on spin vs inverter models")

    if color == "black":
        pros.append("Black finish matches aesthetics preference")
    elif color == "dark_grey":
        pros.append("Dark grey/silver-dark can still look modern if pure black not required")
        cons.append("Not pure black — filter out if aesthetics stay strict")
    elif color == "silver":
        cons.append("Silver/light finish — fails black aesthetic preference")
    else:
        cons.append(f"Finish ({color}) may not match black kitchen/laundry look")

    if trust >= 8.0:
        pros.append(f"{brand} service network is familiar in Egypt via major chains")
    elif trust >= 7.0:
        pros.append(f"{brand} is common on B.TECH — keep invoice and register warranty")
    else:
        cons.append(f"{brand} is value-tier — insist on B.TECH invoice + warranty registration")

    if price <= 14000 and 7 <= kg <= 9:
        pros.append(f"Affordable ~{price:,} EGP — leaves budget for fridge/kitchen")
    elif price >= 22000:
        cons.append(f"Pricey ~{price:,} EGP — only if inverter/size flex is worth it")

    if brand == "Sharp":
        pros.append("Sharp top-loads often include drain pump + digital controls (confirm SKU page)")
    if brand == "LG" and inv:
        pros.append("LG inverter top-load is a strong noise/reliability flex pick if size is OK")

    score = 5.5
    if 7 <= kg <= 9:
        score += 1.8
    elif 10 <= kg <= 13:
        score += 1.0
    else:
        score += 0.3
    score += 1.2 if inv else 0.0
    score += 0.5 if color == "black" else (0.15 if color == "dark_grey" else 0.0)
    score += (trust - 6.5) * 0.3
    score += 0.3 if price <= 14000 and 7 <= kg <= 9 else 0.0
    score = round(min(9.5, max(5.0, score)), 1)

    if 7 <= kg <= 9:
        band = "main"
    elif 10 <= kg <= 13:
        band = "adjacent"
    else:
        band = "oversized"
    summary = (
        f"{brand} {kg:g}kg {color} top-load {'inverter' if inv else 'standard'}, "
        f"~{price:,} EGP — {band} band, fit {score}/10."
    )
    return pros[:7], cons[:5], summary, score, band


def build(rows: list[dict]) -> list[dict]:
    by = {r["href"]: r for r in rows if r.get("href")}
    for e in EXTRA:
        by.setdefault(e["href"], e)

    items = []
    for href, r in by.items():
        kg = r.get("kg")
        if kg is None or kg < 7 or kg > 15:
            continue
        if r.get("front") or r.get("half"):
            continue
        if not r.get("top") and "top load" not in (r.get("name") or "").lower():
            continue
        price = r.get("price")
        if not price or price > 45000:
            continue
        # exclude manual if name says manual
        if re.search(r"\bmanual\b", r.get("name") or "", re.I):
            continue
        pros, cons, summary, score, band = pros_cons(r)
        mid = model_token(r["name"])
        items.append(
            {
                "id": f"wm_{slug(mid)}_{int(kg) if float(kg).is_integer() else kg}",
                "category": "washer",
                "band": band,
                "name": r["name"],
                "brand": r.get("brand") or "Unknown",
                "priceEGP": price,
                "url": href,
                "scrapedAt": "2026-07-17",
                "retailer": "B.TECH",
                "color": r.get("color") or "other",
                "capacity": kg,
                "capacityUnit": "kg",
                "capacityKg": kg,
                "specs": {
                    "capacityKg": kg,
                    "type": "top_load",
                    "automation": "full_auto",
                    "inverter": bool(r.get("inverter")),
                    "featuresClaimed": [],
                },
                "imageUrl": r.get("imageUrl"),
                "imageGallery": [r["imageUrl"]] if r.get("imageUrl") else [],
                "pros": pros,
                "cons": cons,
                "summary": summary,
                "researchFitScore": score,
                "hasDeepResearch": href in {e["href"] for e in EXTRA}
                or "TN09GDSP" in (r.get("name") or "")
                or "T1388" in (r.get("name") or ""),
                "status": "shortlist" if band == "main" else "catalog",
                "tags": [
                    "top_load",
                    "full_auto",
                    r.get("color") or "other",
                    f"{kg:g}kg",
                    f"{band}_band",
                    "inverter" if r.get("inverter") else "non_inverter",
                ],
            }
        )

    # dedupe ids
    seen_ids = {}
    for it in items:
        base = it["id"]
        if base in seen_ids:
            n = seen_ids[base] + 1
            seen_ids[base] = n
            it["id"] = f"{base}_{n}"
        else:
            seen_ids[base] = 0

    band_order = {"main": 0, "adjacent": 1, "oversized": 2}
    items.sort(key=lambda x: (band_order.get(x["band"], 9), -x["researchFitScore"], x["priceEGP"]))
    for i, it in enumerate(items, 1):
        it["rank"] = i
    return items


def main() -> None:
    kept = load_mcp()
    SCRAPE_OUT.write_text(
        json.dumps({"keptCount": len(kept), "kept": kept}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    items = build(kept)
    doc = {
        "version": 3,
        "title": "Washer catalog — top-load full auto · all colors · black filter in UI",
        "lastUpdated": "2026-07-17",
        "currency": "EGP",
        "retailerPrimary": "B.TECH",
        "filtersApplied": {
            "loading": "top_load only",
            "automation": "fully automatic only (half-auto / twin-tub / manual excluded)",
            "capacityKg": "7–15 kg (main 7–9, adjacent 10–13, oversized 14–15)",
            "color": "all colors included; use UI Black only filter",
            "excluded": ["front_load", "half_automatic", "twin_tub", "manual", "accessories"],
        },
        "marketNote": (
            f"Deep B.TECH scrape of top-load category (~138 listed sitewide). "
            f"Catalog has {len(items)} full-auto 7–15 kg models after filters. "
            "Default gallery view shows ALL — use Main 7–9 kg or Black only as needed."
        ),
        "householdContext": {
            "size": "couple, no kids",
            "ironOwned": True,
            "note": "7–9 kg enough for two; 9 kg buffer for bedding",
        },
        "counts": {
            "main": sum(1 for x in items if x["band"] == "main"),
            "adjacent": sum(1 for x in items if x["band"] == "adjacent"),
            "oversized": sum(1 for x in items if x["band"] == "oversized"),
            "black": sum(1 for x in items if x["color"] == "black"),
            "inverter": sum(1 for x in items if x["specs"]["inverter"]),
            "total": len(items),
        },
        "disclaimer": "Prices from B.TECH 2026-07-17 deep scrape. Re-verify before buy.",
        "items": items,
    }
    WM_OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"washers {len(items)} main={doc['counts']['main']} adj={doc['counts']['adjacent']} "
        f"over={doc['counts']['oversized']} black={doc['counts']['black']} inv={doc['counts']['inverter']}"
    )


if __name__ == "__main__":
    main()
