# -*- coding: utf-8 -*-
"""Build carpet_catalog.json from Playwright scrapes (IKEA EG + Amazon.eg + Jumia)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "data" / "appliances"

SCRAPE_FILES = [
    "_ikea_rugs_raw.json",
    "_ikea_rugs_p2.json",
    "_ikea_rugs_p3.json",
    "_ikea_underlay.json",
    "_amazon_rugs.json",
    "_amazon_mac.json",
    "_amazon_kitchen.json",
    "_amazon_ow.json",
    "_jumia_rugs.json",
]

SIZE_RE = re.compile(
    r"(\d{2,3})\s*[x×X]\s*(\d{2,3})\s*cm|(\d{2,3})\s*cm\s*[x×X]\s*(\d{2,3})|(\d{2,3})\s*x\s*(\d{2,3})",
    re.I,
)
ROUND_RE = re.compile(r"\b(\d{2,3})\s*cm\b", re.I)


def load_cards():
    cards = []
    for name in SCRAPE_FILES:
        p = APP / name
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        raw = d.get("cards", d if isinstance(d, list) else [])
        for c in raw:
            c = dict(c)
            c["_src_file"] = name
            cards.append(c)
    return cards


def clean_url(u: str) -> str:
    if not u:
        return ""
    u = u.split("?")[0].rstrip("/")
    # normalize amazon
    m = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", u, re.I)
    if m:
        return f"https://www.amazon.eg/dp/{m.group(1).upper()}"
    return u


def parse_size(text: str):
    if not text:
        return None
    m = SIZE_RE.search(text.replace("×", "x"))
    if m:
        a = m.group(1) or m.group(3) or m.group(5)
        b = m.group(2) or m.group(4) or m.group(6)
        w, l = int(a), int(b)
        if w > l:
            w, l = l, w
        return [w, l]
    # round diameter only if explicit round
    if re.search(r"\bround\b|دائري", text, re.I):
        m2 = ROUND_RE.search(text)
        if m2:
            d = int(m2.group(1))
            if 50 <= d <= 250:
                return [d, d]
    return None


def name_from_ikea_url(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    # tiphede-rug-flatwoven-natural-black-40456757
    parts = slug.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        slug = parts[0]
    return slug.replace("-", " ").title()


def clean_name(c: dict) -> str:
    t = (c.get("name") or "").strip()
    text = c.get("text") or ""
    # Prefer Option: line
    m = re.search(
        r"Option:\s*([A-ZÄÖÅÉÜa-zäöåéü0-9\- ]+,\s*(?:Rug|Door mat|Mat|Carpet|underlay|Anti-slip)[^,]*(?:,[^,]*){0,4})",
        text,
        re.I,
    )
    if m:
        t = m.group(1).strip()
    t = re.sub(r"^(Compare|Top seller|New|Limited edition|Best Seller)\s+", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) < 12 or t.lower().startswith("option:"):
        if "ikea.com" in (c.get("url") or ""):
            t = name_from_ikea_url(c.get("url") or "")
    # truncate noise
    t = re.split(r"\s+EGP\s*|\s+Price\s+", t)[0].strip()
    if len(t) > 160:
        t = t[:157] + "..."
    return t


def detect_pile(blob: str) -> str:
    b = blob.lower()
    if "underlay" in b or "anti-slip" in b or "anti slip" in b:
        return "underlay"
    if "high pile" in b or "shaggy" in b or "shag" in b or "faux fur" in b:
        return "high_pile"
    if "flatwoven" in b or "flat-woven" in b or "flat weave" in b or "flatweave" in b:
        return "flatwoven"
    if "low pile" in b or "short pile" in b:
        return "low_pile"
    if "door mat" in b or "doormat" in b:
        return "doormat"
    if "coir" in b:
        return "doormat"
    return "unknown"


def detect_color(blob: str) -> str:
    b = blob.lower()
    colors = []
    mapping = [
        ("dark green", "dark green"),
        ("pale green", "pale green"),
        ("green", "green"),
        ("orange", "orange/terracotta"),
        ("terracotta", "terracotta"),
        ("navy", "navy"),
        ("blue", "blue"),
        ("grey", "grey"),
        ("gray", "grey"),
        ("black", "black"),
        ("brown", "brown"),
        ("beige", "beige"),
        ("off-white", "off-white"),
        ("white", "white"),
        ("cream", "cream"),
        ("natural", "natural"),
        ("multicolour", "multicolour"),
        ("multicolor", "multicolour"),
        ("pink", "pink"),
        ("yellow", "yellow"),
        ("red", "red"),
    ]
    for k, v in mapping:
        if k in b:
            colors.append(v)
            break
    return colors[0] if colors else "see listing"


def detect_material(blob: str) -> str:
    b = blob.lower()
    if "wool" in b:
        return "wool (check composition)"
    if "jute" in b and "poly" in b:
        return "jute/poly blend"
    if "jute" in b:
        return "jute"
    if "coir" in b:
        return "coir"
    if "cotton" in b:
        return "cotton"
    if "polypropylene" in b or "polyprop" in b or "pp " in b:
        return "polypropylene"
    if "polyester" in b:
        return "polyester"
    if "in/outdoor" in b or "in-outdoor" in b:
        return "polypropylene (in/outdoor)"
    if "underlay" in b or "anti-slip" in b:
        return "anti-slip underlay"
    return "see listing"


def is_junk(blob: str) -> bool:
    b = blob.lower()
    junk = [
        "bath mat",
        "bath set",
        "bathroom",
        "toilet",
        "car mat",
        "car carpet",
        "mouse pad",
        "desk mat",
        "yoga",
        "prayer",
        "سجاد صلاة",
        "chandelier",
        "curtain",
        "pillow",
        "cushion",
        "blanket",
        "throw",
        "sheet set",
        "bamboo wood mat",
        "sitting behind",
        "rabbit fur",
        "bath rug",
    ]
    return any(j in b for j in junk)


def classify_room(name: str, pile: str, size, blob: str) -> str:
    b = blob.lower()
    if pile == "underlay":
        return "accessory"
    if pile == "doormat" or "door mat" in b or "doormat" in b:
        return "entry"
    if "مطبخ" in b or "kitchen" in b:
        if size and size[0] <= 100:
            return "kitchen"
        if "مطبخ" in b:
            return "kitchen"
    if size:
        w, l = size
        # runners
        if w <= 100 and l >= 140:
            if "kitchen" in b or w <= 90:
                return "kitchen"
            return "kitchen" if "runner" in b or "hallway" in b else "kitchen"
        if w <= 60 and l <= 100:
            return "entry"
        if w >= 160 and l >= 220:
            # large living/bedroom
            if "bed" in b:
                return "master_bedroom"
            return "living"
        if w >= 120 and l >= 160:
            return "living"
        if w <= 100 and l <= 160:
            return "kitchen"
    if "kitchen" in b:
        return "kitchen"
    if "bed" in b:
        return "master_bedroom"
    if "kids" in b or "children" in b or "barndr" in b:
        return "second_bedroom"
    return "living"


def fit_score(room: str, size, pile: str, color: str, blob: str) -> tuple[int, list, list, bool]:
    """Return rank_boost (lower better), pros, cons, excluded."""
    pros, cons = [], []
    excluded = False
    boost = 50
    b = blob.lower()

    # Hard style exclusions (still list but flag)
    if pile == "high_pile":
        cons.append("High pile / shaggy — traps Cairo dust; against preferred flatweave/low pile")
        boost += 40
        excluded = True
    if color in ("white", "cream", "off-white") and room in ("living", "master_bedroom", "kitchen"):
        cons.append("Very light / cream-white — shows dust; you preferred deeper tones")
        boost += 25
        if "pure" in b or color in ("white", "cream"):
            if room != "accessory":
                excluded = True
                boost += 20
    if any(x in b for x in ("cartoon", "unicorn", "princess", "kids print")):
        cons.append("Kids/cartoon vibe — not for main rooms")
        excluded = True
        boost += 50

    # Size fit living 375x450 → prefer 200x300 or 160x230
    if room == "living" and size:
        w, l = size
        if (w, l) in ((200, 300), (160, 230), (170, 240), (160, 235)):
            pros.append(f"Size {w}×{l} fits medium front-of-sofa plan for 375×450 living")
            boost -= 15
        elif w >= 180 and l >= 250:
            pros.append("Large enough for living seating zone")
            boost -= 8
        elif w < 120:
            cons.append("Small for living room seating zone")
            boost += 15

    if room == "master_bedroom" and size:
        w, l = size
        if w >= 200 and l >= 280:
            pros.append("Large enough to frame 180 cm bed (sides + foot)")
            boost -= 12
        elif w < 160:
            cons.append("Small under a 180 bed — more side-only use")
            boost += 10

    if room == "kitchen" and size:
        w, l = size
        if w <= 100 and 140 <= l <= 220:
            pros.append("Runner proportions suit 250×215 kitchen")
            boost -= 10

    if pile == "flatwoven":
        pros.append("Flatweave — easier dust control / shake-clean")
        boost -= 12
    if pile == "low_pile":
        pros.append("Low pile — better than shag for dust")
        boost -= 8
    if "in/outdoor" in b or "in-outdoor" in b:
        pros.append("In/outdoor grade — practical for spills and vacuuming")
        boost -= 6
    if "dark green" in b or "orange" in b or "brown" in b or "grey" in b or "navy" in b:
        if color not in ("white", "cream", "off-white", "pale green"):
            pros.append("Deeper / practical tone family")
            boost -= 5
    if "wool" in b:
        pros.append("Wool mentioned — good for bedroom soft foot feel (verify %)")
        boost -= 5
        if room == "master_bedroom":
            boost -= 8
    if pile == "doormat":
        pros.append("Entry mat — traps street dust before it hits floors")
        boost -= 5
    if pile == "underlay":
        pros.append("Anti-slip underlay — stops rugs sliding on tile")
        boost -= 5

    if "amazon" in b or "jumia" in b:
        cons.append("Marketplace listing — check seller rating, return policy, true size")
        boost += 5
    if "ikea" in b:
        pros.append("IKEA Egypt stock path / returns")
        boost -= 8
    # Prefer named rug lines over generic marketplace
    if re.search(r"\b(morum|tiphede|stoense|onsevig|järnväg|jaernvaeg|lydersholm|stopp|sindal|betal)\b", b, re.I):
        boost -= 10

    if not pros:
        pros.append("Available online in Egypt — verify in person if color critical")
    if not cons:
        cons.append("Confirm exact size, pile height, and colour under your lighting")

    return max(1, boost), pros[:6], cons[:5], excluded


def brand_of(c: dict, name: str) -> str:
    src = c.get("source") or ""
    if "IKEA" in src or "ikea.com" in (c.get("url") or ""):
        # first word often product line
        m = re.match(r"^([A-ZÄÖÅÉÜa-zäöåéü\-]+)", name)
        line = m.group(1) if m else "IKEA"
        return f"IKEA / {line}"
    n = name.lower()
    if "mac carpet" in n or "mac-carpet" in n:
        return "Mac Carpet"
    if "oriental weavers" in n or "oriental-weavers" in n:
        return "Oriental Weavers"
    if "prado" in n:
        return "Prado"
    if "amazon" in src.lower():
        return "Amazon.eg"
    if "jumia" in src.lower():
        return "Jumia"
    return src or "Egypt retail"


def build():
    raw = load_cards()
    by_url = {}
    for c in raw:
        u = clean_url(c.get("url") or "")
        if not u:
            continue
        # skip non-rug junk on underlay search
        blob0 = " ".join(
            [
                c.get("name") or "",
                c.get("text") or "",
                u,
            ]
        )
        if "ikea.com" in u and not re.search(
            r"rug|mat|carpet|underlay|anti-slip|doormat|gaser|filt", blob0, re.I
        ):
            continue
        prev = by_url.get(u)
        if not prev:
            by_url[u] = c
        else:
            # prefer with price and better image
            if c.get("priceEGP") and not prev.get("priceEGP"):
                by_url[u] = c
            elif c.get("imageUrl") and (
                not prev.get("imageUrl") or "xxs" in (prev.get("imageUrl") or "")
            ):
                if not c.get("priceEGP") and prev.get("priceEGP"):
                    c = dict(c)
                    c["priceEGP"] = prev["priceEGP"]
                by_url[u] = c

    items = []
    for u, c in by_url.items():
        name = clean_name(c)
        text = c.get("text") or ""
        blob = f"{name} {text} {u} {c.get('source','')}"
        if is_junk(blob):
            continue
        size = parse_size(name) or parse_size(text) or parse_size(u)
        pile = detect_pile(blob)
        color = detect_color(blob)
        material = detect_material(blob)
        room = classify_room(name, pile, size, blob)
        img = c.get("imageUrl") or ""
        if "ikea.com" in img:
            img = re.sub(r"f=(xxs|xu|u|xs)\b", "f=s", img)
        if "amazon" in img:
            img = re.sub(r"\._AC_UL\d+_\.", "._AC_SL500_.", img)

        boost, pros, cons, excluded = fit_score(room, size, pile, color, blob)
        brand = brand_of(c, name)
        slug = re.sub(r"[^a-z0-9]+", "_", (u.split("/")[-1] or name).lower())[:48]
        item_id = f"rug_{slug}"

        price = c.get("priceEGP")
        if isinstance(price, float):
            price = int(price)

        summary_bits = []
        if size:
            summary_bits.append(f"{size[0]}×{size[1]} cm")
        summary_bits.append(pile.replace("_", " "))
        summary_bits.append(color)
        summary = (
            f"{' · '.join(summary_bits)}. "
            f"Scraped from {c.get('source') or 'web'} for Egypt delivery. "
            f"Mapped to room: {room}."
        )

        tags = [room, pile, color.split("/")[0]]
        if size:
            tags.append(f"{size[0]}x{size[1]}")
        if "in/outdoor" in blob.lower() or "in-outdoor" in blob.lower():
            tags.append("easy_clean")
        if excluded:
            tags.append("flagged")

        items.append(
            {
                "id": item_id,
                "room": room,
                "rank": boost,  # temp; re-rank later
                "name": name,
                "brand": brand,
                "priceEGP": price,
                "sizeCm": size,
                "material": material,
                "pile": pile,
                "color": color,
                "url": u if u.startswith("http") else c.get("url"),
                "imageUrl": img,
                "summary": summary,
                "pros": pros,
                "cons": cons,
                "tags": tags,
                "excluded": excluded,
                "source": c.get("source") or "",
                "scrapeNote": "Playwright PLP scrape 2026-07-17 — re-verify price/stock",
            }
        )

    # Deduplicate near-identical names+size keep cheapest
    items.sort(key=lambda x: (x["name"].lower(), x.get("priceEGP") or 10**9))
    deduped = []
    seen_key = set()
    for it in items:
        key = (it["name"].lower()[:60], tuple(it["sizeCm"] or []), it["source"])
        if key in seen_key:
            continue
        seen_key.add(key)
        deduped.append(it)
    items = deduped

    # Rank within room: lower rank number = better
    by_room: dict[str, list] = {}
    for it in items:
        by_room.setdefault(it["room"], []).append(it)

    rank_counter = 1
    final = []
    # Order rooms for display ranking
    room_order = [
        "living",
        "master_bedroom",
        "kitchen",
        "entry",
        "accessory",
        "second_bedroom",
    ]
    for room in room_order:
        group = by_room.get(room, [])
        group.sort(
            key=lambda x: (
                x["excluded"],
                x["rank"],
                x.get("priceEGP") is None,
                x.get("priceEGP") or 10**9,
            )
        )
        for i, it in enumerate(group, 1):
            # global rank for non-excluded first
            if not it["excluded"]:
                it["rank"] = rank_counter
                rank_counter += 1
            else:
                it["rank"] = 900 + i
            final.append(it)

    # Any leftover rooms
    for room, group in by_room.items():
        if room in room_order:
            continue
        for it in group:
            it["rank"] = rank_counter
            rank_counter += 1
            final.append(it)

    # Ensure at least 50 included
    included = [i for i in final if not i["excluded"]]
    if len(included) < 50:
        # un-exclude borderline low_pile light colors to fill
        for it in final:
            if it["excluded"] and it["pile"] in ("low_pile", "flatwoven", "unknown", "doormat"):
                it["excluded"] = False
                it["cons"] = (it.get("cons") or []) + ["Was borderline — kept for choice width"]
                included.append(it)
            if len(included) >= 50:
                break

    # Re-number ranks for included only
    def quality_key(x):
        # Prefer IKEA + size-known + flat/low + priced
        src = (x.get("source") or "").lower()
        ikea = 0 if "ikea" in src else 1
        sized = 0 if x.get("sizeCm") else 1
        pile_pref = {"flatwoven": 0, "low_pile": 1, "doormat": 2, "underlay": 2, "unknown": 3, "high_pile": 9}.get(
            x.get("pile") or "unknown", 4
        )
        room_i = room_order.index(x["room"]) if x["room"] in room_order else 99
        return (
            room_i,
            ikea,
            pile_pref,
            sized,
            x.get("priceEGP") is None,
            x.get("priceEGP") or 10**9,
            x["name"],
        )

    included_sorted = sorted(
        [i for i in final if not i["excluded"]],
        key=quality_key,
    )
    for i, it in enumerate(included_sorted, 1):
        it["rank"] = i
    for it in final:
        if it["excluded"]:
            it["rank"] = 900 + (it.get("rank") or 0) % 100

    catalog = {
        "version": 3,
        "title": "Rugs & carpets — 50+ Egypt options (IKEA + Amazon.eg + Jumia)",
        "lastUpdated": "2026-07-17",
        "currency": "EGP",
        "disclaimer": (
            "Bulk Playwright scrape of IKEA Egypt rugs category (pages 1–3 + underlays), "
            "Amazon.eg (area rugs, Mac Carpet, kitchen/doormat, Oriental Weavers), and Jumia Egypt. "
            "Prices/images from listing cards 2026-07-17 — re-verify stock, size variants, and true colour. "
            "Homzmart blocked (TLS). High-pile and pure cream large rugs flagged excluded where possible."
        ),
        "filters": {
            "include": [
                "low_pile",
                "flatweave",
                "deeper_tones",
                "easy_clean_living",
                "doormats",
                "runners",
                "underlays",
            ],
            "exclude_flagged": ["high_pile_shaggy", "pure_white_cream_large", "kids_cartoon"],
            "rooms": {
                "living_cm": [375, 450],
                "bedroom_cm": [330, 475],
                "second_room_cm": [380, 330],
                "kitchen_cm": [250, 215],
            },
        },
        "sizePlanSummary": {
            "living_375x450": "Medium rug in front of L-sofa: prefer 200×300 cm (alt 160×230 / 170×240)",
            "bedroom_330x475_bed180": "Under bed: 200×300 practical; 240×300 better side margins; wool preferred",
            "kitchen_250x215": "Runner ~80×150–200 (or 70–100 wide)",
            "entry": "Doormat 40×60 to 60×90",
            "accessory": "STOPP / anti-slip underlay under large rugs on tile",
        },
        "counts": {
            "totalScrapedUnique": len(final),
            "included": len([i for i in final if not i["excluded"]]),
            "excluded": len([i for i in final if i["excluded"]]),
            "withImage": len([i for i in final if i.get("imageUrl")]),
            "bySource": {},
            "byRoom": {},
        },
        "kits": [
            {
                "id": "kit_ikea_core",
                "name": "IKEA-first practical set",
                "note": "Living MORUM dark green 200×300 + kitchen MORUM runner + doormat + STOPP underlay; bedroom wool still showroom/Amazon wool search",
                "items": [
                    "Living: MORUM or ONSEVIG/JÄRNVÄG 200×300 deeper tones",
                    "Kitchen: MORUM or TIPHEDE runner ~80×200",
                    "Entry: SINDAL / BETALVÄG / FRIKTION",
                    "Accessory: STOPP FILT underlay",
                ],
            },
            {
                "id": "kit_local_value",
                "name": "Local value (Amazon/Jumia + Mac / Oriental Weavers)",
                "note": "Often cheaper large sizes; quality varies — order with returns where possible",
                "items": [
                    "Living/bedroom: Mac Carpet or Oriental Weavers ~160×220–200×300",
                    "Kitchen: washable runner listings",
                    "Entry: rubber/coir doormat",
                ],
            },
        ],
        "shoppingRoute": [
            "Filter gallery by room (Living / Bedroom / Kitchen / Entry / Accessory)",
            "Star 2–3 per room; open product links and confirm exact size variant",
            "IKEA Egypt: flatweave living + mats + underlay in one delivery",
            "Amazon.eg / Jumia: Mac Carpet, Oriental Weavers, wool claims — check fibre % and reviews",
            "For true wool bedroom: measure under bed (200×300 min for 180 bed) and visit a showroom if online photos look too light",
            "Second room: still deferred — do not buy yet unless you change plan",
        ],
        "items": final,
    }

    # counts
    src_counts: dict[str, int] = {}
    room_counts: dict[str, int] = {}
    for it in final:
        src_counts[it.get("source") or "?"] = src_counts.get(it.get("source") or "?", 0) + 1
        room_counts[it["room"]] = room_counts.get(it["room"], 0) + 1
    catalog["counts"]["bySource"] = src_counts
    catalog["counts"]["byRoom"] = room_counts

    out = APP / "carpet_catalog.json"
    out.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "Wrote",
        out,
        "total",
        len(final),
        "included",
        catalog["counts"]["included"],
        "excluded",
        catalog["counts"]["excluded"],
        "images",
        catalog["counts"]["withImage"],
    )
    print("byRoom", room_counts)
    print("bySource", src_counts)


if __name__ == "__main__":
    build()
