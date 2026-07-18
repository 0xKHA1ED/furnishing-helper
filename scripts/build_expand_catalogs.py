"""Build expanded fridge + washer catalogs from B.TECH scrape (all colors).

Hard rules (still applied):
  Fridge: ≤35k EGP, ≥360 L, NoFrost (no manual defrost), has freezer, no dispenser, no minibar
  Washer: top-load, full auto, 7–15 kg (main 7–9, adjacent 11–13, oversized 15 tagged)
Color is NOT hard — stored for UI \"black only\" filter.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRAPE = ROOT / "data/appliances/_btech_expand_scrape.json"
FR_OUT = ROOT / "data/appliances/fridge_catalog.json"
WM_OUT = ROOT / "data/appliances/washer_catalog.json"

# Live JSON-LD verified overrides (2026-07-17 second expand pass)
VERIFIED = {
    "https://btech.com/en/p/beko-no-frost-refrigerator-406-liters-inverter-black-rdne455m20xbidegb": {
        "priceEGP": 30299, "inverter": True, "freezerL": None, "dims": "665x1850x700",
        "notes": "A+; 4 shelves; InStock",
    },
    "https://btech.com/en/p/beko-no-frost-refrigerator-406-liters-inverter-silver-rdne455m20xbids": {
        "priceEGP": 25499, "inverter": True, "notes": "Same platform as black IDEGB; electronic display; ~4.8k cheaper than black",
    },
    "https://btech.com/en/p/66b8a615-4c65-42e0-8453-ff9f23e64f3c": {
        "priceEGP": 28139, "inverter": True,
        "notes": "ProSmart + NeoFrost Dual Cooling + HarvestFresh; black 455L marketing",
    },
    "https://btech.com/en/p/tornado-no-frost-refrigerator-450l-inverter-black-rf-580tvbk": {
        "priceEGP": 28949, "inverter": True, "freezerL": 112,
        "notes": "112 L freezer verified on B.TECH description",
    },
    "https://btech.com/en/p/520c3ef1-24bd-4ea5-b5f3-b37bb91adf2e": {
        "priceEGP": 25999, "inverter": True, "notes": "10y inverter motor warranty claim; dark inox",
    },
    "https://btech.com/en/p/ariston-no-frost-refrigerator-408l-inverter-inox-art70f1452xdi": {
        "priceEGP": 28199, "inverter": True, "notes": "Listing 455 gross / ~408 net class; 10y inv motor",
    },
    "https://btech.com/en/p/lg-no-frost-refrigerator-401-liters-inveter-black-gtf402sban": {
        "priceEGP": 31300, "inverter": False, "notes": "Title/URL 'inveter' misleading — description has no Smart Inverter",
    },
    "https://btech.com/en/p/lg-no-frost-refrigerator-401liters-inveter-silver-gtf402svan": {
        "priceEGP": 30290, "inverter": False, "notes": "Multi Air Flow + exterior display; not inverter",
    },
    "https://btech.com/en/p/58c35fa6-31bc-4940-a771-33f1afd8a8ca": {
        "priceEGP": 29440, "inverter": True, "notes": "Toshiba inverter; humidity + cooling zone claims",
    },
    "https://btech.com/en/p/midea-no-frost-refrigerator-535-liters-inverter-stainless-rt723mtn46d": {
        "priceEGP": 32625, "inverter": True, "notes": "Biggest total under 35k class; mid-tier brand",
    },
    "https://btech.com/en/p/6d28e4f4-e913-4ef9-9508-07ba95ef9027": {
        "priceEGP": 34899, "inverter": True, "notes": "LG 450L silver inverter; near ceiling",
    },
    "https://btech.com/en/p/sharp-topload-auto-washingmachine-9kg-estn09gdsp": {
        "priceEGP": 13549, "inverter": False,
        "features": ["drain pump", "digital touch", "hot and cold inlets", "lint filter", "8 programs"],
    },
    "https://btech.com/en/p/fresh-top-load-washing-machine-9kg-ftm-09f12b": {
        "priceEGP": 12999, "inverter": False, "features": ["drain pump", "quick wash"],
    },
    "https://btech.com/en/p/lg-13kg-inverter-washing-machine-t1388nehgb-abmpeec": {
        "priceEGP": 19490, "inverter": True, "features": ["inverter", "800 RPM"],
    },
    "https://btech.com/en/p/toshiba-tl-wm-9kg-aw-j900dupeg": {
        "priceEGP": 12439, "inverter": False,
    },
    "https://btech.com/en/p/sharp-washing-mashine-tn09gslp": {
        "priceEGP": 17499, "inverter": False,
        "features": ["digital touch", "drain pump", "antibacterial fan", "8 programs"],
    },
    "https://btech.com/en/p/toshiba-washingmachine-13kg-inverter-dk1300kupeg": {
        "priceEGP": 18249, "inverter": True, "features": ["great waves", "quick wash 15", "soft close"],
    },
    "https://btech.com/en/p/sharp-invrtr-wm-11kg-es-td11gbkp": {
        "priceEGP": 22931, "inverter": True, "features": ["DDM inverter", "digital touch", "antibacterial fan"],
    },
}

# Manual injects missing from category scroll
EXTRA_FRIDGES = [
    {
        "name": "Tornado NoFrost Top Freezer Refrigerator , 450 Liter Inverter Motor , Black - RF-580TV-BK",
        "price": 28949,
        "href": "https://btech.com/en/p/tornado-no-frost-refrigerator-450l-inverter-black-rf-580tvbk",
        "liters": 450,
        "color": "black",
        "inverter": True,
        "bottom": False,
        "top": True,
        "dispenser": False,
        "brand": "Tornado",
        "defrost": False,
        "nofrost": True,
        "imageUrl": "https://dwecxxryy5p59.cloudfront.net/catalogs/7/b/c/8/7bc8eec73715d5037c8a43d0921eab1aea77ff41_6087137acd9567bc4ff3e7127886bd5e4153fefb58adc863364588f82c92c652.jpeg",
    },
]
EXTRA_WASHERS = [
    {
        "name": "Sharp ES-TN09GDSP Top Load washing Machine , 9 kg , Black",
        "price": 13549,
        "href": "https://btech.com/en/p/sharp-topload-auto-washingmachine-9kg-estn09gdsp",
        "kg": 9,
        "color": "black",
        "inverter": False,
        "brand": "Sharp",
        "imageUrl": "https://dwecxxryy5p59.cloudfront.net/catalogs/d/f/8/2/df8296ed9788cf1f3d8bac7ac7008dd2b3b4f724_studio_session_228.jpeg",
    },
]

BRAND_TRUST = {
    "LG": 9.0,
    "Samsung": 8.8,
    "Toshiba": 8.5,
    "Beko": 8.4,
    "Ariston": 8.2,
    "Bosch": 8.6,
    "Sharp": 8.0,
    "Zanussi": 7.4,
    "Indesit": 7.2,
    "Haier": 7.3,
    "Tornado": 7.0,
    "Midea": 6.9,
    "Fresh": 6.8,
    "Unionaire": 6.5,
    "White Point": 6.4,
    "White": 6.4,
}


def slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_").lower()
    return s[:48]


def model_token(name: str) -> str:
    m = re.search(r"([A-Z]{1,6}[-]?[A-Z0-9]{3,}[A-Z0-9\-/]*)", name)
    return m.group(1) if m else slug(name)[:20]


def fridge_pros_cons(it: dict, v: dict | None) -> tuple[list[str], list[str], str, float]:
    brand = it.get("brand") or "Unknown"
    inv = bool(it.get("inverter") if not v else v.get("inverter", it.get("inverter")))
    color = it.get("color") or "other"
    L = it.get("liters") or 0
    price = it.get("price") or 0
    bottom = bool(it.get("bottom"))
    trust = BRAND_TRUST.get(brand, 6.5)
    freezer_l = (v or {}).get("freezerL")

    pros: list[str] = []
    cons: list[str] = []

    if inv:
        pros.append("Inverter motor claimed/confirmed — better odds for quieter run and lower cycling wear")
    else:
        cons.append("Non-inverter (fixed-speed) — more start/stop noise and bill risk vs inverter peers")

    if L >= 450:
        pros.append(f"Large total capacity (~{L} L) — strong for weekly Friday meal-prep containers")
    elif L >= 400:
        pros.append(f"Solid capacity (~{L} L) for couple weekly shop + leftovers")
    elif L >= 360:
        pros.append(f"Meets min size floor (~{L} L) — tight but acceptable if organized")
        cons.append("Near the 360 L floor — can feel small if hosting or bulk shopping spikes")

    if freezer_l:
        pros.append(f"Freezer volume listed ~{freezer_l} L — good headroom for batch freeze")
    elif bottom:
        pros.append("Bottom freezer: fridge at eye level for daily prep containers")
        cons.append("Bottom freezers trade bulk freezer volume for organization — use flat packs")
    else:
        pros.append("Top freezer layout — classic max-fridge-shelf geometry for meal-prep trays")

    if color == "black":
        pros.append("Black finish matches partner aesthetics preference")
    elif color == "dark_inox":
        pros.append("Dark Inox finish reads modern/premium without pure black")
        cons.append("Not pure black — may fail hard aesthetics filter if partner insists")
    else:
        cons.append("Non-black finish — use gallery Black-only filter if aesthetics stay hard")

    if trust >= 8.2:
        pros.append(f"{brand} has a relatively strong Egypt service/warranty footprint via big chains")
    elif trust >= 7.0:
        pros.append(f"{brand} is common on B.TECH — keep invoice and register warranty")
    else:
        cons.append(f"{brand} mid/value-tier — reliability variance higher; buy authorized + written warranty")

    if price <= 25000:
        pros.append(f"Price ~{price:,} EGP leaves budget headroom under the 35k ceiling")
    elif price <= 30000:
        pros.append(f"Priced ~{price:,} EGP — under hard 35k with some room")
    else:
        cons.append(f"Near ceiling at ~{price:,} EGP — little promo headroom")

    pros.append("No water/ice dispenser (fewer leak/failure points)")
    pros.append("NoFrost — no manual defrost chore")

    if brand == "LG" and not inv:
        cons.append("Do not trust 'inveter' in URL/title — B.TECH description does not list Smart Inverter")
    if brand == "Unionaire":
        cons.append("Bluetooth/speaker gimmicks on Signature lines are optional noise — not a reliability plus")
    if brand == "Ariston" and inv:
        pros.append("10-year inverter motor warranty claim on B.TECH listing (confirm on invoice)")
    if brand == "Beko" and inv:
        pros.append("Beko inverter NeoFrost/HarvestFresh family is the best-documented noise/efficiency path in this budget")

    # Fit score (color is soft bonus only; reliability + inverter + value dominate)
    score = 5.0
    score += 1.8 if inv else 0.0
    score += min(1.2, max(0, (L - 360) / 150))
    score += (trust - 6.5) * 0.55  # brand network / reliability weight
    score += 0.25 if color == "black" else (0.15 if color == "dark_inox" else 0.0)
    score += 0.45 if freezer_l and freezer_l >= 105 else 0.0
    score += 0.55 if inv and price <= 27000 else (0.25 if price <= 29000 else 0.0)
    score -= 0.5 if bottom and not inv else 0.0
    score -= 0.55 if brand in ("Unionaire",) else 0.0  # soft-penalize vs Beko/LG/Toshiba
    score -= 0.25 if brand in ("Fresh", "Midea") and not inv else 0.0
    # verified platform bonus
    if "RDNE455" in (it.get("name") or "") and inv:
        score += 0.35
    if "ART70" in (it.get("name") or "") and inv:
        score += 0.2
    if freezer_l and freezer_l >= 110:
        score += 0.2
    score = round(min(9.7, max(5.0, score)), 1)

    # Summary
    layout = "bottom freezer" if bottom else "top freezer"
    inv_s = "inverter" if inv else "non-inverter"
    summary = f"{brand} ~{L}L {color} {layout}, {inv_s}, ~{price:,} EGP — fit {score}/10 for meal-prep couple under 35k."

    # Deduplicate preserve order
    def uniq(xs: list[str]) -> list[str]:
        seen = set()
        out = []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    return uniq(pros)[:7], uniq(cons)[:6], summary, score


def washer_pros_cons(it: dict, v: dict | None) -> tuple[list[str], list[str], str, float]:
    brand = it.get("brand") or "Unknown"
    kg = it.get("kg") or 0
    inv = bool(it.get("inverter") if not v else v.get("inverter", it.get("inverter")))
    color = it.get("color") or "other"
    price = it.get("price") or 0
    feats = (v or {}).get("features") or []
    trust = BRAND_TRUST.get(brand, 6.5)

    pros, cons = [], []
    if 7 <= kg <= 9:
        pros.append(f"Couple-size {kg} kg — enough for weekly loads without oversized bulk")
    elif 11 <= kg <= 13:
        pros.append(f"{kg} kg capacity buffer for bedding / occasional big loads")
        cons.append("Larger than couple need — more water/energy per half-load if not filled")
    elif kg >= 15:
        pros.append(f"Oversized {kg} kg — only if you want future family/bedding headroom")
        cons.append("Overkill for two people; footprint and water use rise")

    if inv:
        pros.append("Inverter motor — quieter spin/start and usually better longevity marketing")
    else:
        cons.append("Non-inverter motor — louder on spin vs inverter models")

    if color == "black":
        pros.append("Black finish matches kitchen/laundry aesthetic preference")
    elif color in ("dark_grey", "other"):
        pros.append("Dark grey/silver-dark can still look modern if pure black not required")
        cons.append("Not pure black — filter out if aesthetics stay strict")
    else:
        cons.append("Silver/light finish — fails black aesthetic preference")

    if "drain pump" in " ".join(feats).lower() or brand in ("Sharp", "Fresh", "LG"):
        pros.append("Drain pump class machines are easier to install (no low floor drain only)")
    if any("hot and cold" in f.lower() or "hot" in f.lower() for f in feats):
        pros.append("Hot + cold inlets — useful if you have hot water feed")
    if "digital" in " ".join(feats).lower() or brand == "Sharp":
        pros.append("Digital controls / modern program set vs bare mechanical dials")

    if trust >= 8.0:
        pros.append(f"{brand} service network is familiar in Egypt via major chains")
    else:
        cons.append(f"{brand} is value-tier — insist on B.TECH invoice + warranty registration")

    if price <= 14000:
        pros.append(f"Affordable ~{price:,} EGP — leaves budget for fridge/kitchen")
    elif price >= 22000:
        cons.append(f"Pricey ~{price:,} EGP for a washer — only if inverter/size flex is worth it")

    score = 5.5
    if 7 <= kg <= 9:
        score += 1.8
    elif 11 <= kg <= 13:
        score += 1.0
    else:
        score += 0.3
    score += 1.2 if inv else 0.0
    score += 0.5 if color == "black" else (0.15 if color == "dark_grey" else 0.0)
    score += (trust - 6.5) * 0.3
    score += 0.3 if price <= 14000 and 7 <= kg <= 9 else 0.0
    score = round(min(9.5, max(5.0, score)), 1)

    band = "main" if 7 <= kg <= 9 else ("adjacent" if 11 <= kg <= 13 else "oversized")
    summary = f"{brand} {kg}kg {color} top-load {'inverter' if inv else 'standard'}, ~{price:,} EGP — {band} band, fit {score}/10."
    return pros[:7], cons[:5], summary, score


def build_fridges(rows: list[dict]) -> list[dict]:
    by_href = {r["href"]: r for r in rows}
    for e in EXTRA_FRIDGES:
        by_href[e["href"]] = e
    items = []
    for href, r in by_href.items():
        if r.get("dispenser") or r.get("defrost"):
            continue
        if not r.get("price") or r["price"] > 35000:
            continue
        if not r.get("liters") or r["liters"] < 360:
            continue
        v = VERIFIED.get(href)
        price = (v or {}).get("priceEGP") or r["price"]
        inv = (v or {}).get("inverter") if v and "inverter" in v else r.get("inverter")
        r2 = {**r, "price": price, "inverter": inv}
        pros, cons, summary, score = fridge_pros_cons(r2, v)
        layout = "bottom_freezer" if r.get("bottom") else "top_freezer"
        mid = model_token(r["name"])
        items.append(
            {
                "id": f"fr_{slug(mid)}",
                "category": "fridge",
                "name": r["name"],
                "brand": r.get("brand") or "Unknown",
                "priceEGP": price,
                "currency": "EGP",
                "retailer": "B.TECH",
                "url": href,
                "scrapedAt": "2026-07-17",
                "color": r.get("color") or "other",
                "capacity": r["liters"],
                "capacityUnit": "L",
                "capacityL": r["liters"],
                "specs": {
                    "capacityL": r["liters"],
                    "layout": layout,
                    "inverter": bool(inv),
                    "nofrost": True,
                    "dispenser": False,
                    "hasFreezer": True,
                    "freezerL": (v or {}).get("freezerL"),
                },
                "imageUrl": r.get("imageUrl"),
                "imageGallery": [r["imageUrl"]] if r.get("imageUrl") else [],
                "pros": pros,
                "cons": cons,
                "summary": summary,
                "researchFitScore": score,
                "lifestyleFitScore": score,
                "hasDeepResearch": href in VERIFIED or bool((v or {}).get("notes")),
                "verifyNote": (v or {}).get("notes"),
                "status": "catalog",
                "tags": [
                    r.get("color") or "other",
                    "under_35k",
                    layout,
                    "inverter" if inv else "non_inverter",
                    "nofrost",
                ],
            }
        )
    items.sort(key=lambda x: (-x["researchFitScore"], x["priceEGP"]))
    for i, it in enumerate(items, 1):
        it["rank"] = i
        if i <= 8:
            it["status"] = "shortlist"
    return items


def build_washers(rows: list[dict]) -> list[dict]:
    by_href = {r["href"]: r for r in rows}
    for e in EXTRA_WASHERS:
        by_href[e["href"]] = e
    items = []
    for href, r in by_href.items():
        kg = r.get("kg")
        if not kg or kg < 7 or kg > 15:
            continue
        if not r.get("price") or r["price"] > 40000:
            continue
        v = VERIFIED.get(href)
        price = (v or {}).get("priceEGP") or r["price"]
        inv = (v or {}).get("inverter") if v and "inverter" in v else r.get("inverter")
        r2 = {**r, "price": price, "inverter": inv}
        pros, cons, summary, score = washer_pros_cons(r2, v)
        if 7 <= kg <= 9:
            band = "main"
        elif 11 <= kg <= 13:
            band = "adjacent"
        else:
            band = "oversized"
        mid = model_token(r["name"])
        items.append(
            {
                "id": f"wm_{slug(mid)}_{kg}",
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
                    "inverter": bool(inv),
                    "featuresClaimed": (v or {}).get("features") or [],
                },
                "imageUrl": r.get("imageUrl"),
                "imageGallery": [r["imageUrl"]] if r.get("imageUrl") else [],
                "pros": pros,
                "cons": cons,
                "summary": summary,
                "researchFitScore": score,
                "hasDeepResearch": href in VERIFIED,
                "status": "shortlist" if band == "main" else "catalog",
                "tags": [
                    "top_load",
                    "full_auto",
                    r.get("color") or "other",
                    f"{kg}kg",
                    band + "_band",
                    "inverter" if inv else "non_inverter",
                ],
            }
        )
    # rank within band priority: main first, then adjacent, then oversized; score desc
    band_order = {"main": 0, "adjacent": 1, "oversized": 2}
    items.sort(key=lambda x: (band_order.get(x["band"], 9), -x["researchFitScore"], x["priceEGP"]))
    for i, it in enumerate(items, 1):
        it["rank"] = i
    return items


def main() -> None:
    data = json.loads(SCRAPE.read_text(encoding="utf-8"))
    fridges = build_fridges(data.get("fridgeKeptList") or [])
    washers = build_washers(data.get("washers") or [])

    fr_doc = {
        "version": 2,
        "title": "Fridge catalog — all colors · hard rules · black filter in UI",
        "lastUpdated": "2026-07-17",
        "currency": "EGP",
        "retailerPrimary": "B.TECH",
        "filtersApplied": {
            "maxPriceEGP": 35000,
            "minCapacityL": 360,
            "mustHaveFreezer": True,
            "nofrostRequired": True,
            "excludeDispenser": True,
            "excludeMinibar": True,
            "color": "all colors included; use UI Black only filter",
        },
        "householdContext": {
            "city": "6th of October City",
            "mealPrep": "Friday weekly batch",
            "freezeLoad": "about half a normal freezer weekly",
            "layoutPreference": "top_freezer preferred for space; bottom still listed",
            "aesthetics": "black preferred not hard — filter available",
        },
        "counts": {
            "included": len(fridges),
            "black": sum(1 for x in fridges if x["color"] == "black"),
            "inverter": sum(1 for x in fridges if x["specs"]["inverter"]),
            "topFreezer": sum(1 for x in fridges if x["specs"]["layout"] == "top_freezer"),
            "bottomFreezer": sum(1 for x in fridges if x["specs"]["layout"] == "bottom_freezer"),
        },
        "rankingNote": "Rank = lifestyle fit: inverter + capacity + brand trust + freeze notes + slight black bonus. Re-verify prices on B.TECH before buy.",
        "disclaimer": "Prices from B.TECH product listing/JSON-LD 2026-07-17. Photos hotlinked from retailer CDN.",
        "items": fridges,
        "excludedExamples": [
            {"reason": "price > 35000"},
            {"reason": "capacity < 360 L"},
            {"reason": "minibar / manual defrost / dispenser"},
            {"reason": "non-B.TECH retailers (out of scope this pass)"},
        ],
    }

    wm_doc = {
        "version": 2,
        "title": "Washer catalog — top-load full auto · all colors · black filter in UI",
        "lastUpdated": "2026-07-17",
        "currency": "EGP",
        "retailerPrimary": "B.TECH",
        "filtersApplied": {
            "loading": "top_load only",
            "automation": "fully automatic only",
            "capacityKg": "7–15 kg listed; main 7–9, adjacent 11–13, oversized 15",
            "color": "all colors included; use UI Black only filter",
            "excluded": ["front_load", "half_automatic", "twin_tub"],
        },
        "marketNote": "B.TECH top-load full-auto inventory is wider in silver/grey than pure black. Black 7–9 kg still scarce.",
        "householdContext": {
            "size": "couple, no kids",
            "ironOwned": True,
            "note": "7–9 kg enough for two; 9 kg buffer for bedding",
        },
        "counts": {
            "main": sum(1 for x in washers if x["band"] == "main"),
            "adjacent": sum(1 for x in washers if x["band"] == "adjacent"),
            "oversized": sum(1 for x in washers if x["band"] == "oversized"),
            "black": sum(1 for x in washers if x["color"] == "black"),
            "inverter": sum(1 for x in washers if x["specs"]["inverter"]),
            "total": len(washers),
        },
        "disclaimer": "Prices from B.TECH 2026-07-17. Re-verify before buy.",
        "items": washers,
    }

    FR_OUT.write_text(json.dumps(fr_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    WM_OUT.write_text(json.dumps(wm_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"fridge {len(fridges)} (black {fr_doc['counts']['black']}, inv {fr_doc['counts']['inverter']}) → {FR_OUT.name}"
    )
    print(
        f"washer {len(washers)} (main {wm_doc['counts']['main']}, black {wm_doc['counts']['black']}) → {WM_OUT.name}"
    )
    print("Top 10 fridges:")
    for it in fridges[:10]:
        print(f"  #{it['rank']} {it['researchFitScore']} {it['priceEGP']:>6} {it['color']:10} {it['name'][:70]}")
    print("Top washers (main then adjacent):")
    for it in washers[:12]:
        print(f"  #{it['rank']} {it['band']:9} {it['researchFitScore']} {it['priceEGP']:>6} {it['color']:10} {it['name'][:65]}")


if __name__ == "__main__":
    main()
