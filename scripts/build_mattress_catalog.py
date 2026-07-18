# -*- coding: utf-8 -*-
"""Build mattress_catalog.json — master 180×200, ≤25k, pocket/hybrid, cool, medium-firm default."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "data" / "appliances"
MAX_PRICE = 25000
SIZE = (180, 200)

SCRAPES = [
    "_mattress_ikea_all.json",
    "_mattress_ikea.json",
    "_mattress_ikea_spring.json",
    "_mattress_amazon_pocket.json",
    "_mattress_amazon.json",
    "_mattress_jumia_ar.json",
    "_mattress_jumia.json",
]


def load_cards():
    out = []
    for name in SCRAPES:
        p = APP / name
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        out.extend(d.get("cards") or [])
    return out


def clean_url(u: str) -> str:
    if not u:
        return ""
    u = u.split("?")[0].rstrip("/")
    m = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", u, re.I)
    if m:
        return f"https://www.amazon.eg/dp/{m.group(1).upper()}"
    return u


def is_junk(blob: str) -> bool:
    b = blob.lower()
    junk = [
        "protector",
        "fitted sheet",
        "bed sheet",
        "pillow case",
        "pillow protector",
        "waterproof cover",
        "ملاءة",
        "واقي",
        "غطاء مرتب",
        "topper only",
        "floor mattress",
        "folding floor",
        "camping mat",
        "yoga",
        "pet bed",
    ]
    # toppers allowed only if clearly mattress-adjacent under budget later
    if any(j in b for j in junk):
        if "mattress topper" in b or "topper mattress" in b:
            return False  # keep toppers as accessory/out
        if "protector" in b or "sheet" in b or "cover" in b:
            return True
        if "floor mattress" in b or "folding floor" in b:
            return True
    return False


def parse_size(blob: str):
    m = re.search(r"(\d{2,3})\s*[x×*]\s*(\d{2,3})", blob.replace(" ", ""))
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a > b:
            a, b = b, a
        return [a, b]
    if "180" in blob and "200" in blob:
        return [180, 200]
    if "king" in blob.lower() and "super" not in blob.lower():
        return [180, 200]  # EU king often 180
    return None


def detect_type(blob: str) -> str:
    b = blob.lower()
    if "hybrid" in b:
        return "hybrid"
    if "pocket" in b or "pocket-sprung" in b or "pocket sprung" in b or "individually" in b:
        return "pocket_spring"
    if "innerspring" in b or "inner spring" in b or "spring" in b or "سوست" in b:
        return "spring"
    if "latex" in b:
        return "latex"
    if "memory foam" in b or "memo" in b:
        return "memory_foam"
    if "foam" in b or "سفنج" in b:
        return "foam"
    return "unknown"


def detect_firmness(blob: str) -> str:
    b = blob.lower()
    if "extra firm" in b or "extra-firm" in b or "xfirm" in b:
        return "extra_firm"
    if "medium firm" in b or "medium-firm" in b or "med firm" in b:
        return "medium_firm"
    if re.search(r"\bfirm\b", b) and "soft" not in b:
        return "firm"
    if "medium" in b or "mid" in b:
        return "medium"
    if "soft" in b or "plush" in b or "pillow top" in b or "pillowtop" in b:
        return "soft_or_pillowtop"
    return "unspecified"


def brand_of(name: str, source: str) -> str:
    if "ikea" in source.lower():
        m = re.match(r"^([A-ZÄÖÅÉÜa-zäöåéü\\-]+)", name.strip())
        return f"IKEA / {(m.group(1) if m else 'IKEA')}"
    for b in [
        "Habitat",
        "Janssen",
        "Restonic",
        "Serta",
        "Simmons",
        "Dunlopillo",
        "Lady Americana",
        "Spring Air",
        "Sealy",
        "Hilding",
        "Emma",
        "Dorelan",
        "Taki",
        "High Point",
        "Mobica",
        "Ikea",
    ]:
        if re.search(rf"\b{re.escape(b)}\b", name, re.I):
            return b
    return name.split()[0] if name else source


def score(item_type, firmness, price, size, source, blob: str):
    s = 50
    pros, cons = [], []
    # type preference pocket/hybrid
    if item_type in ("pocket_spring", "hybrid"):
        s -= 15
        pros.append("Pocket spring / hybrid — airflow + motion isolation (matches heat + couple brief)")
    elif item_type == "spring":
        s -= 6
        pros.append("Spring core — cooler than dense foam-only")
        cons.append("Confirm pocket vs open coil if motion isolation matters")
    elif item_type == "memory_foam":
        s += 8
        cons.append("Memory foam can sleep warmer (heat is high priority for you)")
    elif item_type == "foam":
        s += 4
        cons.append("Foam-only — OK if budget, less ideal for Egypt heat vs pocket spring")
    elif item_type == "latex":
        s -= 8
        pros.append("Latex often resilient and cooler than memory foam")

    # firmness: default medium-firm for unknown preference + mixed sleep
    if firmness in ("medium_firm", "medium", "firm"):
        s -= 8
        pros.append(f"Firmness band “{firmness.replace('_',' ')}” suits mixed sleepers when you said “no idea”")
    elif firmness == "extra_firm":
        s -= 2
        pros.append("Extra firm — good if you like support; may feel hard for side sleep segments")
        cons.append("If you later prefer plush, this may feel too firm")
    elif firmness == "soft_or_pillowtop":
        s += 3
        cons.append("Softer/pillow-top — can sleep warmer; still list for choice")
    else:
        s += 1
        cons.append("Firmness not clear on listing — test in store or check return policy")

    # size
    if size == [180, 200]:
        s -= 12
        pros.append("Exact 180×200 for your bed")
    elif size and size[0] >= 180:
        s -= 4
        pros.append(f"Size {size[0]}×{size[1]} — verify fits 180 frame")
    elif size and size[0] < 180:
        s += 20
        cons.append(f"Size {size[0]}×{size[1]} — narrower than 180 bed")

    # price
    if price is not None:
        if price <= MAX_PRICE:
            head = MAX_PRICE - price
            if head >= 8000:
                s -= 5
                pros.append(f"Leaves ~{head:,} EGP under 25k (protector later)")
            elif head >= 0:
                s -= 2
        else:
            s += 30

    if "ikea" in source.lower():
        s -= 6
        pros.append("IKEA Egypt — clear size variants, delivery, returns path")
        pros.append("Works on slatted bases when slat gap meets IKEA guidance")
    elif "amazon" in source.lower() or "jumia" in source.lower():
        s += 4
        cons.append("Marketplace — verify true size, spring type, and warranty stamp")

    if "breath" in blob.lower() or "airflow" in blob.lower() or "ventil" in blob.lower():
        s -= 3
        pros.append("Listing mentions breathability/airflow")

    if not pros:
        pros.append("Candidate for master bed shortlist under your filters")
    if not cons:
        cons.append("Lie on it 10–15 min in store if possible; firmness is personal")

    return max(1, s), pros[:6], cons[:5]


def build():
    raw = load_cards()
    by = {}
    for c in raw:
        u = clean_url(c.get("url") or "")
        if not u:
            continue
        name = re.sub(r"\s+", " ", (c.get("name") or "").strip())
        name = re.sub(r"^(Compare|Top seller|New|Limited edition)\s+", "", name, flags=re.I)
        blob = f"{name} {c.get('text','')}"
        if is_junk(blob):
            continue
        # skip pure toppers as main? keep as accessory
        price = c.get("priceEGP")
        if isinstance(price, float):
            price = int(price)
        size = parse_size(blob)
        # Prefer 180x200 in name for IKEA variants without size in alt
        if size is None and "ikea.com" in u:
            # many IKEA PLP cards are multi-size; keep if price and mattress
            if re.search(r"180\s*[x×]\s*200|180x200", blob, re.I):
                size = [180, 200]
        key = u
        prev = by.get(key)
        if not prev or (price and (not prev.get("priceEGP") or price < prev["priceEGP"])):
            by[key] = {
                "name": name[:200],
                "url": u,
                "imageUrl": (c.get("imageUrl") or "").replace("f=xxs", "f=s"),
                "priceEGP": price,
                "source": c.get("source") or "",
                "text": (c.get("text") or "")[:300],
                "sizeCm": size,
            }

    items = []
    excluded_examples = []
    for c in by.values():
        name = c["name"]
        blob = f"{name} {c.get('text','')}"
        size = c.get("sizeCm")
        price = c.get("priceEGP")
        source = c.get("source") or ""
        mtype = detect_type(blob)
        firmness = detect_firmness(blob)
        brand = brand_of(name, source)

        is_topper = bool(re.search(r"\btopper\b", blob, re.I))
        is_main_mattress = not is_topper and re.search(
            r"mattress|مرتب|sprung|innerspring|pocket", blob, re.I
        )

        reasons = []
        excluded = False
        category = "mattress"

        if is_topper:
            category = "topper"
            excluded = True
            reasons.append("Topper — not full mattress (you said mattress only now)")
        if not is_main_mattress and not is_topper:
            excluded = True
            reasons.append("Not clearly a full mattress")

        if size and size[0] < 160:
            excluded = True
            reasons.append(f"Too narrow ({size[0]} cm) for 180 bed")
        elif size and size[0] == 160:
            excluded = True
            reasons.append("160×200 — narrower than 180 bed")
        elif size and size[0] >= 180 and size[1] and size[1] < 195:
            excluded = True
            reasons.append(f"Length {size[1]} cm short of 200 — wrong for standard 180×200 sheets/frame")
        elif size and size[0] not in (180,) and size[0] < 180:
            excluded = True
            reasons.append(f"Size {size} not 180×200")
        elif size is None:
            # allow if amazon/jumia claim 180x200 in search context
            if re.search(r"180|king", blob, re.I):
                size = [180, 200]
                reasons.append("Size assumed 180×200 from title keywords — verify")
            else:
                excluded = True
                reasons.append("Size not 180×200 / unclear")

        if price is None:
            reasons.append("Price missing — re-check")
        elif price > MAX_PRICE:
            excluded = True
            reasons.append(f"{price:,} EGP over 25k budget")
        elif price < 3000 and not is_topper:
            excluded = True
            reasons.append("Price too low for real 180×200 mattress — likely accessory/error")

        sc, pros, cons = score(mtype, firmness, price or 999999, size, source, blob)
        if reasons:
            cons = reasons + cons

        # boost medium-firm default path
        if not excluded and mtype in ("pocket_spring", "hybrid", "spring") and firmness in (
            "firm",
            "medium_firm",
            "medium",
            "unspecified",
            "extra_firm",
        ):
            sc = max(1, sc - 3)

        slug = re.sub(r"[^a-z0-9]+", "_", (c["url"].split("/")[-1] or name).lower())[:48]
        item = {
            "id": f"mat_{slug}",
            "rank": sc,
            "name": name,
            "brand": brand,
            "priceEGP": price,
            "sizeCm": size,
            "type": mtype,
            "firmness": firmness,
            "category": category,
            "url": c["url"],
            "imageUrl": c.get("imageUrl") or "",
            "source": source,
            "summary": (
                f"{(size[0] if size else '?')}×{(size[1] if size else '?')} cm · {mtype.replace('_',' ')} · "
                f"{firmness.replace('_',' ')}. "
                f"Master bedroom only · ≤{MAX_PRICE:,} EGP · heat-friendly lean · slatted base."
            ),
            "pros": pros,
            "cons": cons,
            "tags": [
                t
                for t in [
                    mtype,
                    firmness,
                    "180x200" if size == [180, 200] else None,
                    "under_25k" if price and price <= MAX_PRICE else "over_budget",
                    "cool_lean" if mtype in ("pocket_spring", "hybrid", "spring", "latex") else "foam",
                ]
                if t
            ],
            "excluded": excluded,
            "baseNote": "Use on slatted base; check max slat gap (often ≤3–6 cm depending on brand warranty)",
            "scrapeNote": "Playwright PLP 2026-07-17 — re-verify size variant, firmness, stock",
        }
        if excluded and len(excluded_examples) < 20:
            excluded_examples.append(
                {
                    "name": name[:100],
                    "price": price,
                    "sizeCm": size,
                    "reason": "; ".join(reasons) if reasons else "filtered",
                }
            )
        items.append(item)

    main = [i for i in items if not i["excluded"]]
    out = [i for i in items if i["excluded"]]

    def sk(x):
        type_pref = {"pocket_spring": 0, "hybrid": 0, "spring": 1, "latex": 2, "foam": 3, "memory_foam": 4, "unknown": 5}.get(
            x["type"], 5
        )
        firm_pref = {"medium_firm": 0, "firm": 0, "medium": 1, "extra_firm": 2, "unspecified": 3, "soft_or_pillowtop": 4}.get(
            x["firmness"], 3
        )
        ikea = 0 if "ikea" in (x.get("source") or "").lower() else 1
        return (
            type_pref,
            firm_pref,
            ikea,
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
    rec = [it["id"] for it in main if it["type"] in ("pocket_spring", "hybrid", "spring")][:8]

    catalog = {
        "version": 1,
        "title": "Mattress shortlist — master 180×200 · ≤25,000 EGP · pocket/hybrid · cool lean",
        "lastUpdated": "2026-07-17",
        "currency": "EGP",
        "filtersApplied": {
            "room": "master_bedroom_only",
            "sizeCm": [180, 200],
            "maxPriceEGP": MAX_PRICE,
            "typePrefer": ["pocket_spring", "hybrid"],
            "firmnessDefault": "medium_firm (user had no idea)",
            "heat": "high_priority_breathable",
            "motion": "medium",
            "base": "slatted",
            "extras": "mattress_only",
        },
        "answers": json.loads((ROOT / "data" / "mattress-brief.json").read_text(encoding="utf-8")).get(
            "answers", {}
        ),
        "counts": {
            "included": len(main),
            "excludedListed": len(out),
            "total": len(final),
            "withImage": len([i for i in final if i.get("imageUrl")]),
            "bySource": {},
            "byType": {},
        },
        "recommendedIds": rec,
        "shoppingRoute": [
            "Filter Main (180×200 ≤25k)",
            "Prefer pocket spring / hybrid for Egypt heat + medium motion isolation",
            "Because firmness was “no idea”: start with firm / medium-firm; avoid ultra-soft first buy",
            "Lie-test 10–15 minutes (back + side) at IKEA or a local mattress hall if possible",
            "Confirm slatted base gap for warranty",
            "Mattress only now — add waterproof breathable protector next trip",
            "Re-check price/stock day of purchase",
        ],
        "kits": [
            {
                "id": "kit_ikea_pocket",
                "name": "IKEA pocket path",
                "note": "VESTERÖY / VALEVÅG 180×200 firm under 25k when in stock",
                "items": ["180×200 pocket sprung firm", "slatted bed base compatible", "protector later"],
            },
            {
                "id": "kit_local_value",
                "name": "Local value pocket spring",
                "note": "Amazon/Jumia Habitat, Janssen etc. — verify 180×200 and warranty",
                "items": ["Pocket spring 180×200 ≤25k", "check return window"],
            },
        ],
        "excludedExamples": excluded_examples,
        "disclaimer": (
            "Scraped IKEA Egypt mattresses (incl. 180×200 spring filter), Amazon.eg pocket spring / 180×200, "
            "Jumia مرتبة 180×200. B.TECH search returned no mattress hits. "
            "Prices 2026-07-17 PLP — re-verify. Main list: full mattresses ~180×200 ≤25k. "
            "Firmness defaulted to medium-firm/firm because user selected “no idea”."
        ),
        "items": final,
    }

    src, types = {}, {}
    for it in final:
        src[it.get("source") or "?"] = src.get(it.get("source") or "?", 0) + 1
        if not it["excluded"]:
            types[it["type"]] = types.get(it["type"], 0) + 1
    catalog["counts"]["bySource"] = src
    catalog["counts"]["byType"] = types

    path = APP / "mattress_catalog.json"
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", path, "included", len(main), "excluded", len(out))
    for it in main[:12]:
        print(f"  #{it['rank']} {it.get('priceEGP')} {it['type']} {it['firmness']} {it['name'][:55]}")


if __name__ == "__main__":
    build()
