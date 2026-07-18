"""Merge images + research notes into catalog.json for the gallery UI."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/appliances/catalog.json"
IMAGES = ROOT / "data/appliances/images_partial.json"
OUT = ROOT / "data/appliances/catalog.json"

# Research enrichment keyed by substring match on name or url
RESEARCH: list[dict] = [
    {
        "match": ["GTF402SBAN", "gtf402sban"],
        "status": "shortlist",
        "color": "black",
        "pros": [
            "Strong black finish (aesthetics partner)",
            "LG service network widely available in Egypt",
            "Documented ~97 L freezer — enough for half-box weekly freeze",
            "~401 L total, meal-prep couple size",
            "No water/ice dispenser",
        ],
        "cons": [
            "NOT inverter despite some page titles — fixed-speed recipro (LG + B.TECH specs)",
            "Likely more compressor cycling noise than true inverter peers",
            "Priced near 31k while non-inverter",
        ],
        "summary": "Black top-freezer look/brand pick. Accept non-inverter before buying.",
        "researchFitScore": 7.8,
        "rankNote": "Black shortlist #2",
    },
    {
        "match": ["ZRT41204BA", "zrt41204ba", "406 Liter , Black - ZRT"],
        "status": "shortlist",
        "color": "black",
        "pros": [
            "True black top-freezer under 35k",
            "Best value among black shortlist (~25k)",
            "~406 L class for weekly prep",
            "Electrolux-group Zanussi presence in Egypt",
        ],
        "cons": [
            "No inverter — more cycling noise risk",
            "Less 'premium' brand weight than LG/Samsung",
            "Mechanical controls on many listings",
        ],
        "summary": "Budget black top-freezer if inverter is optional.",
        "researchFitScore": 7.5,
        "rankNote": "Black shortlist #3 value",
    },
    {
        "match": ["FNT-BR470BMB", "fnt-br470bmb", "397 Liter , Black - FNT-BR"],
        "status": "backup",
        "color": "black",
        "pros": ["Cheapest black no-frost in catalog band", "Local Fresh service density"],
        "cons": ["No inverter", "Budget build perception", "QC/noise variance risk"],
        "summary": "Emergency budget black only.",
        "researchFitScore": 6.5,
    },
    {
        "match": ["RDNE455M20XBIDS", "rdne455m20xbids"],
        "status": "shortlist",
        "color": "silver",
        "pros": [
            "Confirmed ProSmart inverter",
            "~406 L NoFrost top freezer",
            "Strong value under 35k",
            "Good noise odds vs fixed-speed",
        ],
        "cons": ["Silver — fails hard black requirement", "Freezer L not always listed (~90–95 class)"],
        "summary": "Best silver inverter value; reopen if black softens.",
        "researchFitScore": 8.1,
    },
    {
        "match": ["ART70 F1422D", "ART70F1422", "520c3ef1-24bd-4ea5"],
        "status": "research",
        "color": "dark_inox",
        "pros": [
            "Inverter + official ~41 dB(A)",
            "Dark Inox looks modern",
            "~26k leaves budget headroom",
            "No dispenser",
        ],
        "cons": [
            "Net ~367 L / freezer ~93 L",
            "Not black",
            "Thin model-specific reviews",
        ],
        "summary": "Strong dark metal inverter pick if black not required.",
        "researchFitScore": 7.0,
    },
    {
        "match": ["ART70F1452", "art70f1452", "408l-inverter-inox-art70"],
        "status": "research",
        "color": "dark_inox",
        "pros": [
            "Taller ~185 cm chassis — more fridge height",
            "Inverter NoFrost ~406–408 L net",
            "Dark Inox under 30k",
        ],
        "cons": ["Freezer still ~90 L class", "Not black", "455 L is gross marketing"],
        "summary": "Better Ariston sibling for 'not too small' if dark metal OK.",
        "researchFitScore": 7.5,
    },
    {
        "match": ["RT723MTN46D", "rt723mtn46d", "535-liters-inverter-stainless-rt723"],
        "status": "research",
        "color": "stainless",
        "pros": ["535 L capacity king under 35k", "Inverter NoFrost", "Stainless look"],
        "cons": ["Midea mid-tier reliability perception", "Noise unverified", "Freezer split unclear"],
        "summary": "Space-first if brand risk acceptable.",
        "researchFitScore": 7.0,
    },
    {
        "match": ["RB34C672EB1", "rb34c672eb1"],
        "status": "research",
        "color": "black",
        "pros": [
            "Black bottom-freezer Samsung",
            "Digital inverter ~39 dB class",
            "Eye-level fridge for prep containers",
            "Power Freeze for Friday loads",
        ],
        "cons": [
            "Only ~340 L total — tight for bulk",
            "Freezer ~112 L with drawer height limits",
            "You preferred top-freezer space story",
        ],
        "summary": "Best black if you flip back to bottom-freezer ergonomics.",
        "researchFitScore": 7.5,
    },
    {
        "match": ["RB34C671ES9", "rb34c671es9"],
        "status": "research",
        "color": "silver",
        "pros": ["Same Samsung platform as black, better value", "Inverter quiet class"],
        "cons": ["Silver", "Bottom freezer ~344 L"],
        "summary": "Bottom-freezer silver value Samsung.",
        "researchFitScore": 8.0,
    },
    {
        "match": ["GR-RT558WE-PMN", "gr-rt558we-pmn", "58c35fa6-31bc-4940"],
        "status": "research",
        "color": "silver",
        "pros": ["~105 L freezer listed — best freeze-first top", "Inverter", "Tropical positioning"],
        "cons": ["Not black", "Slightly shorter cabinet"],
        "summary": "Freeze-first top freezer if color flexible.",
        "researchFitScore": 8.0,
    },
]


def color_guess(name: str) -> str | None:
    n = name.lower()
    if "black" in n:
        return "black"
    if "dark inox" in n or "dark grey" in n or "dark gray" in n:
        return "dark_metal"
    if "stainless" in n or "inox" in n or "silver" in n:
        return "silver"
    if "white" in n:
        return "white"
    if "grey" in n or "gray" in n:
        return "grey"
    return None


def apply_research(item: dict) -> None:
    blob = (item.get("name") or "") + " " + (item.get("url") or "")
    for r in RESEARCH:
        if any(m.lower() in blob.lower() for m in r["match"]):
            item["pros"] = r.get("pros", [])
            item["cons"] = r.get("cons", [])
            item["summary"] = r.get("summary", "")
            item["researchFitScore"] = r.get("researchFitScore")
            if r.get("status"):
                item["status"] = r["status"]
            if r.get("rankNote"):
                item["rankNote"] = r["rankNote"]
            if r.get("color"):
                item["color"] = r["color"]
            item["hasDeepResearch"] = True
            return
    item.setdefault("pros", [])
    item.setdefault("cons", [])
    item.setdefault("summary", "")
    item.setdefault("hasDeepResearch", False)


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    images = {}
    if IMAGES.exists():
        images = json.loads(IMAGES.read_text(encoding="utf-8"))

    for item in catalog["items"]:
        url = item.get("url") or ""
        img = images.get(url) or {}
        item["imageUrl"] = img.get("og")
        item["imageGallery"] = img.get("gallery") or ([] if not img.get("og") else [img["og"]])
        if not item.get("color"):
            item["color"] = color_guess(item.get("name") or "")
        apply_research(item)
        # capacity helper for filters
        s = item.get("specs") or {}
        item["capacity"] = s.get("capacityL") or s.get("capacityKg")
        item["capacityUnit"] = "L" if s.get("capacityL") is not None else ("kg" if s.get("capacityKg") is not None else "")

    with_img = sum(1 for i in catalog["items"] if i.get("imageUrl"))
    deep = sum(1 for i in catalog["items"] if i.get("hasDeepResearch"))
    catalog["version"] = 2
    catalog["ui"] = {
        "imageCoverage": with_img,
        "deepResearchCount": deep,
        "note": "Images from B.TECH product pages (CloudFront). Hotlink may need network. Pros/cons filled for researched fridge shortlist first.",
    }
    catalog["lastUpdated"] = "2026-07-17"
    OUT.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"items={len(catalog['items'])} images={with_img} deep={deep}")


if __name__ == "__main__":
    main()
