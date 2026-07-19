"""
Merge official-site washer scrapes into washer_catalog.json.
Sources: Fresh.com.eg, Elaraby Group (Sharp/Tornado/Hoover/Candy/Hitachi/Toshiba…).
Keeps existing B.TECH items; adds new official SKUs (dedupe by model slug).
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/appliances/washer_catalog.json"
SCRAPE = ROOT / "data/appliances/_official_scrape_raw.json"
OUT = CATALOG


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s.lower()).strip("_")
    return s[:80]


def color_from_text(text: str) -> str:
    t = text.lower()
    if re.search(r"\bblack\b|obsidian", t):
        return "black"
    if re.search(r"dark\s*grey|dark\s*gray|dark\s*silver|graphite", t):
        return "dark_grey"
    if re.search(r"silver|steel|stainless|inox", t):
        return "silver"
    if re.search(r"gold|champagne", t):
        return "gold"
    if re.search(r"white|light\s*grey|light\s*gray", t):
        return "white"
    if re.search(r"blue|ocean", t):
        return "blue"
    if re.search(r"red|burgundy", t):
        return "red"
    return "other"


def band_for_kg(kg: float | None) -> str:
    if kg is None:
        return "unknown"
    if 7 <= kg <= 9:
        return "main"
    if 10 <= kg <= 13:
        return "adjacent"
    if 14 <= kg <= 17:
        return "oversized"
    if kg < 7:
        return "compact"
    return "oversized"


def brand_from_text(text: str, url: str = "") -> str:
    hay = f"{text} {url}".lower()
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
        ("ariston", "Ariston"),
        ("indesit", "Indesit"),
    ]
    for key, name in brands:
        if key in hay:
            return name
    return "Unknown"


def parse_kg_from_slug_or_name(text: str) -> float | None:
    # 14-kg, 9kg, 8-5-kg, 11-kg-7-kg dryer
    m = re.search(r"(\d{1,2})(?:-(\d))?-?kg", text.lower())
    if m:
        whole = float(m.group(1))
        if m.group(2):
            return whole + float(m.group(2)) / 10
        return whole
    m = re.search(r"(\d{1,2})\s*k\.?\s*g", text.lower())
    if m:
        return float(m.group(1))
    return None


def load_type_flags(name: str, url: str, explicit: dict | None = None) -> dict:
    hay = f"{name} {url}".lower()
    top = bool(explicit and explicit.get("topLoad")) or bool(
        re.search(r"top[-\s]?load|top[-\s]?automatic|top automatic", hay)
    )
    front = bool(explicit and explicit.get("frontLoad")) or bool(
        re.search(r"front[-\s]?load|direct\s*drive", hay)
    )
    # El Araby "fully automatic" without top often front-load
    if "top-automatic" in hay or "top_automatic" in hay or "top automatic" in hay:
        top = True
        front = False
    if re.search(r"washer.?dryer|washing.?dryer|\d+-\d+-kg-dryer|\d+/\d+\s*kg", hay):
        washer_dryer = True
    else:
        washer_dryer = bool(explicit and explicit.get("washerDryer"))
    # half-auto / twin
    half = bool(re.search(r"half[-\s]?auto|twin[-\s]?tub|manual|single\s*tub", hay))
    if top and not front:
        wtype = "top_load"
    elif front and not top:
        wtype = "front_load"
    elif top:
        wtype = "top_load"
    elif "fully-automatic" in hay or "full-automatic" in hay or "fully automatic" in hay:
        # default fully auto without top keyword → front on El Araby often
        wtype = "front_load" if "elaraby" in hay or "hoover" in hay or "candy" in hay else "top_load"
    else:
        wtype = "unknown"
    return {
        "type": wtype,
        "top": top,
        "front": front,
        "washerDryer": washer_dryer,
        "half": half,
        "inverter": bool(explicit and explicit.get("inverter")) or "inverter" in hay or "ddm" in hay,
    }


def clean_name(name: str) -> str:
    name = re.sub(r"^OFF\s*\d+%\s*Cash\s*", "", name, flags=re.I)
    name = re.sub(r"\s*Add to cart\s*$", "", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip()
    # drop trailing price fragments
    name = re.split(r"\d[\d,]*\.?\d*\s*EGP", name)[0].strip()
    return name[:160]


def make_item(raw: dict, retailer: str, source_label: str) -> dict | None:
    name = clean_name(raw.get("name") or raw.get("slug") or "")
    url = raw.get("url") or ""
    if not url or not name:
        return None
    if re.search(r"spare|part|accessory|hose|stand", f"{name} {url}", re.I):
        return None

    flags = load_type_flags(name, url, raw)
    if flags["half"]:
        return None

    kg = raw.get("capacityKg")
    if kg is None:
        kg = parse_kg_from_slug_or_name(f"{name} {raw.get('slug','')} {url}")
    if kg is not None:
        kg = float(kg)

    # Keep useful range: 6–17 kg (slightly wider than before to include official 6kg)
    if kg is not None and (kg < 6 or kg > 17):
        # allow washer-dryer up to 14 wash
        if not flags["washerDryer"]:
            return None

    brand = brand_from_text(name, url)
    color = color_from_text(f"{name} {url}")
    band = band_for_kg(kg)
    price = raw.get("priceEGP")
    if price is not None:
        try:
            price = int(round(float(price)))
        except Exception:
            price = None
    if price is not None and (price < 2000 or price > 120000):
        price = None

    inverter = flags["inverter"]
    wtype = flags["type"]
    if wtype == "unknown":
        return None

    id_base = slugify(f"wm_{retailer}_{brand}_{kg or 'x'}_{raw.get('slug') or name}")
    image = raw.get("imageUrl") or ""
    if image and "cache/" in image:
        # prefer larger-ish fresh/elaraby images as-is
        pass

    pros = [
        f"Official {source_label} listing — brand channel / warranty path",
        f"{'Top-load' if wtype == 'top_load' else 'Front-load'} · {int(kg) if kg and kg == int(kg) else kg or '?'} kg"
        if True
        else "",
    ]
    if inverter:
        pros.append("Inverter / efficient motor claimed on listing")
    if not raw.get("oos"):
        pros.append("Listed in stock (or not marked OOS) at scrape time")
    pros = [p for p in pros if p]

    cons = []
    if raw.get("oos"):
        cons.append("Marked out of stock on official site at scrape time")
    if price is None:
        cons.append("Confirm live price on product page")
    if flags["washerDryer"]:
        cons.append("Washer-dryer combo — higher price/energy; only if you need dryer")
    if wtype == "front_load" and kg and kg <= 9:
        cons.append("Front-load install needs drainage/leveling — check apartment plumbing")

    summary_bits = [
        brand,
        f"{int(kg) if kg and kg == int(kg) else kg}kg" if kg else None,
        wtype.replace("_", " "),
        f"~{price:,} EGP" if price else "price TBA",
        source_label,
    ]
    summary = " · ".join(x for x in summary_bits if x)

    # research fit: couple top-load 7-9 preferred
    score = 6.0
    if wtype == "top_load" and kg and 7 <= kg <= 9:
        score = 8.2
    elif wtype == "top_load" and kg and 10 <= kg <= 13:
        score = 7.4
    elif wtype == "front_load" and inverter and kg and 7 <= kg <= 10:
        score = 7.6
    if color == "black":
        score += 0.3
    if raw.get("oos"):
        score -= 0.8
    if flags["washerDryer"]:
        score -= 0.5
    score = round(min(9.5, max(4.0, score)), 1)

    tags = [wtype, "full_auto" if not flags["half"] else "half", color, f"{int(kg)}kg" if kg else "kg_unk"]
    if inverter:
        tags.append("inverter")
    if flags["washerDryer"]:
        tags.append("washer_dryer")
    tags.append(slugify(retailer))
    tags.append("official_site")

    return {
        "id": id_base,
        "category": "washer",
        "band": band,
        "name": name if brand.lower() in name.lower() else f"{brand} {name}",
        "brand": brand,
        "priceEGP": price,
        "url": url,
        "scrapedAt": date.today().isoformat(),
        "retailer": retailer,
        "sourceLabel": source_label,
        "color": color,
        "capacity": kg,
        "capacityUnit": "kg",
        "capacityKg": kg,
        "specs": {
            "capacityKg": kg,
            "type": wtype,
            "automation": "full_auto",
            "inverter": inverter,
            "washerDryer": flags["washerDryer"],
            "featuresClaimed": [],
        },
        "imageUrl": image or None,
        "imageGallery": [image] if image else [],
        "pros": pros,
        "cons": cons or ["Verify warranty registration on official site"],
        "summary": summary,
        "researchFitScore": score,
        "hasDeepResearch": False,
        "status": "catalog",
        "tags": tags,
        "oos": bool(raw.get("oos")),
        "rank": 50,
    }


def model_key(it: dict) -> str:
    """Dedupe key across retailers."""
    name = re.sub(r"[^a-z0-9]", "", (it.get("name") or "").lower())
    # extract model codes
    m = re.search(r"(es[a-z0-9\-]+|ftm\d+\w+|twt[a-z0-9\-]+|h3[a-z0-9]+|bd[a-z0-9\-]+|hw\d+\w+)", name)
    if m:
        return m.group(1)[:40]
    return f"{(it.get('brand') or '').lower()}_{it.get('capacityKg')}_{it.get('color')}_{name[-24:]}"


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    scrape = json.loads(SCRAPE.read_text(encoding="utf-8"))

    existing = catalog.get("items") or []
    for it in existing:
        it.setdefault("retailer", "B.TECH")
        it.setdefault("sourceLabel", "B.TECH")
        it.setdefault("specs", {})
        it["specs"].setdefault("type", "top_load")

    existing_keys = {model_key(it) for it in existing}
    existing_urls = {it.get("url") for it in existing if it.get("url")}

    added: list[dict] = []

    # Fresh top-load preferred + all Fresh (front DD too)
    for raw in (scrape.get("freshTop") or []) + (scrape.get("freshAll") or []):
        if raw.get("error"):
            continue
        item = make_item(raw, "Fresh Official", "Fresh.com.eg")
        if not item:
            continue
        if item["url"] in existing_urls:
            continue
        mk = model_key(item)
        if mk in existing_keys and item["specs"]["type"] == "top_load":
            # still add official if different URL (official path)
            pass
        if item["url"] in existing_urls:
            continue
        existing_urls.add(item["url"])
        existing_keys.add(mk)
        added.append(item)

    for raw in scrape.get("elaraby") or []:
        if raw.get("error") or not raw.get("url"):
            continue
        item = make_item(raw, "Elaraby Group", "ElarabyGroup.com")
        if not item:
            continue
        if item["url"] in existing_urls:
            continue
        existing_urls.add(item["url"])
        existing_keys.add(model_key(item))
        added.append(item)

    # Re-rank: official top-load main band first-ish after deep research B.TECH
    all_items = existing + added
    all_items.sort(
        key=lambda x: (
            0 if x.get("hasDeepResearch") else 1,
            0 if x.get("specs", {}).get("type") == "top_load" else 1,
            0 if x.get("band") == "main" else 1 if x.get("band") == "adjacent" else 2,
            -(x.get("researchFitScore") or 0),
            x.get("priceEGP") or 999999,
        )
    )
    for i, it in enumerate(all_items, 1):
        it["rank"] = i

    def count_where(pred):
        return sum(1 for x in all_items if pred(x))

    catalog.update(
        {
            "version": 4,
            "title": "Washer catalog — top + front load · B.TECH + official brands",
            "lastUpdated": date.today().isoformat(),
            "currency": "EGP",
            "retailerPrimary": "multi",
            "filtersApplied": {
                "loading": "top_load + front_load (filter in UI)",
                "automation": "fully automatic only",
                "capacityKg": "6–17 kg",
                "sources": ["B.TECH", "Fresh.com.eg", "ElarabyGroup.com (Sharp/Tornado/Hoover/Candy/Hitachi/…)"],
                "excluded": ["half_automatic", "twin_tub", "manual", "accessories", "spare_parts"],
            },
            "marketNote": (
                f"Merged official-site scrape {date.today().isoformat()}: "
                f"+{len(added)} models from Fresh.com.eg and Elaraby Group. "
                f"Total {len(all_items)}. Re-verify prices/stock before buy."
            ),
            "counts": {
                "total": len(all_items),
                "btech": count_where(lambda x: x.get("retailer") == "B.TECH"),
                "official": count_where(lambda x: x.get("retailer") != "B.TECH"),
                "top_load": count_where(lambda x: x.get("specs", {}).get("type") == "top_load"),
                "front_load": count_where(lambda x: x.get("specs", {}).get("type") == "front_load"),
                "main": count_where(lambda x: x.get("band") == "main"),
                "adjacent": count_where(lambda x: x.get("band") == "adjacent"),
                "oversized": count_where(lambda x: x.get("band") == "oversized"),
                "black": count_where(lambda x: x.get("color") == "black"),
                "inverter": count_where(lambda x: x.get("specs", {}).get("inverter") is True),
                "fresh_official": count_where(lambda x: x.get("retailer") == "Fresh Official"),
                "elaraby_official": count_where(lambda x: x.get("retailer") == "Elaraby Group"),
            },
            "disclaimer": (
                "Prices mixed B.TECH deep scrape (2026-07-17) + official Fresh/Elaraby scrape "
                f"({date.today().isoformat()}). Official prices/stock change — open product link before buying."
            ),
            "items": all_items,
            "addedOfficial": {
                "count": len(added),
                "date": date.today().isoformat(),
                "sources": ["https://fresh.com.eg/en/categories/washing-machines", "https://www.elarabygroup.com/en/electric-home-appliances/large-home-appliances/washing-machines"],
            },
        }
    )

    OUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Existing B.TECH-ish: {len(existing)} · Added official: {len(added)} · Total: {len(all_items)}")
    print("Counts:", catalog["counts"])
    brands: dict[str, int] = {}
    for it in all_items:
        brands[it.get("brand") or "?"] = brands.get(it.get("brand") or "?", 0) + 1
    print("Brands:", sorted(brands.items(), key=lambda x: -x[1])[:15])


if __name__ == "__main__":
    main()
