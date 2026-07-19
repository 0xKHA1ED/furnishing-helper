"""
Fetch product/search page HTML and extract best product image URL.
Updates data/research/*.json with imageUrl fields.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "data" / "research"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

OG_RE = re.compile(
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.I,
)
OG_RE2 = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
    re.I,
)
# Amazon search result images
AMZ_IMG = re.compile(
    r'<img[^>]+class="[^"]*s-image[^"]*"[^>]+src="([^"]+)"',
    re.I,
)
AMZ_IMG2 = re.compile(
    r'src="(https://[^"]*media-amazon\.com/images/I/[^"]+)"',
    re.I,
)
# Jumia listing images
JUMIA_IMG = re.compile(
    r'data-src="(https://[^"]*jumia[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
    re.I,
)
JUMIA_IMG2 = re.compile(
    r'src="(https://[^"]*(?:jumia|jpmtuc)[^"]+\.(?:jpg|jpeg|png|webp)[^"]*)"',
    re.I,
)
LANDING = re.compile(
    r'data-old-hires="(https://[^"]+)"',
    re.I,
)


def fetch(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="replace")


def bad(url: str) -> bool:
    return bool(
        re.search(
            r"logo|icon|sprite|placeholder|badge|flag|avatar|pixel|1x1|spinner|transparent",
            url,
            re.I,
        )
    )


def normalize(url: str | None) -> str | None:
    if not url:
        return None
    url = unescape(url).strip()
    if url.startswith("//"):
        url = "https:" + url
    if bad(url) or url.startswith("data:"):
        return None
    # prefer larger jumia thumbs
    url = re.sub(r"/\d+x\d+/", "/680x680/", url)
    # amazon: strip size modifiers carefully — keep as-is if already good
    return url


def extract_image(html: str, page_url: str) -> str | None:
    # 1) og:image
    for rx in (OG_RE, OG_RE2):
        m = rx.search(html)
        if m:
            img = normalize(m.group(1))
            if img:
                return img

    # 2) amazon landing / product
    m = LANDING.search(html)
    if m:
        img = normalize(m.group(1))
        if img:
            return img

    # 3) amazon search images
    if "amazon." in page_url:
        m = AMZ_IMG.search(html)
        if m:
            img = normalize(m.group(1))
            if img:
                return img
        for m in AMZ_IMG2.finditer(html):
            img = normalize(m.group(1))
            if img and "._AC_" in img or "images/I/" in img:
                return img

    # 4) jumia
    if "jumia" in page_url:
        for rx in (JUMIA_IMG, JUMIA_IMG2):
            for m in rx.finditer(html):
                img = normalize(m.group(1))
                if img:
                    return img

    # 5) any large-ish product image host
    for m in re.finditer(
        r'(https://[^"\'\s]+(?:media-amazon|jumia|jpmtuc|ssl-images)[^"\'\s]+\.(?:jpg|jpeg|png|webp)[^"\'\s]*)',
        html,
        re.I,
    ):
        img = normalize(m.group(1))
        if img:
            return img

    return None


def main() -> None:
    stats = {"ok": 0, "fail": 0, "skip": 0}
    fails: list[str] = []

    for fp in sorted(RESEARCH.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        print(f"\n== {fp.name} ==")
        for item in data.get("items", []):
            iid = item.get("id", "?")
            url = item.get("url")
            if not url:
                stats["skip"] += 1
                print(f"  skip {iid} (no url)")
                continue
            try:
                html = fetch(url)
                img = extract_image(html, url)
                if img:
                    item["imageUrl"] = img
                    stats["ok"] += 1
                    print(f"  ok   {iid}")
                else:
                    stats["fail"] += 1
                    fails.append(f"{fp.name}:{iid}")
                    print(f"  fail {iid}")
            except Exception as e:
                stats["fail"] += 1
                fails.append(f"{fp.name}:{iid}:{type(e).__name__}")
                print(f"  err  {iid}: {type(e).__name__}: {e}")
            time.sleep(0.35)
        fp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\nSummary:", stats)
    if fails:
        print("Failures:")
        for f in fails:
            print(" ", f)


if __name__ == "__main__":
    main()
