# -*- coding: utf-8 -*-
"""Build tv_catalog.json from official manufacturer scrapes (55–65″, <30k EGP)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "data" / "appliances"
MAX_PRICE = 30000
MIN_INCH = 55
MAX_INCH = 65


def el(name, brand, price, inch, url, img, oos, panel="LED", res="4K UHD", extra=None):
    return {
        "name": name,
        "brand": brand,
        "priceEGP": price,
        "sizeInches": inch,
        "panel": panel,
        "resolution": res,
        "url": url,
        "imageUrl": img,
        "source": "Elaraby Group official",
        "inStock": not oos,
        "features": extra or [],
    }


def main():
    raw = []

    # Samsung Egypt official
    raw += [
        {
            "name": "Samsung 55 Inch Mini LED M70H 4K Samsung Vision AI Smart TV (2026)",
            "brand": "Samsung",
            "priceEGP": 25999,
            "sizeInches": 55,
            "panel": "Mini-LED",
            "resolution": "4K UHD",
            "url": "https://www.samsung.com/eg/tvs/mini-led-tv/m70h-55-inch-4k-smart-tv-ua55m70hauxeg/",
            "imageUrl": "https://images.samsung.com/is/image/samsung/p6pim/eg/ua55m70hauxeg/gallery/eg-mini-led-m70h-ua55m70hauxeg-552250102?$1164_776_PNG$",
            "source": "Samsung Egypt official",
            "inStock": True,
            "features": [
                "Mini LED",
                "4K",
                "Samsung Vision AI",
                "Tizen smart TV",
                "Official Samsung EG store",
            ],
        },
        {
            "name": "Samsung 55 Inch QLED Q6F 4K Smart TV (2025)",
            "brand": "Samsung",
            "priceEGP": 28999,
            "sizeInches": 55,
            "panel": "QLED",
            "resolution": "4K UHD",
            "url": "https://www.samsung.com/eg/tvs/qled-tv/q6f-55-inch-qled-4k-smart-tv-qa55q6faauxeg/",
            "imageUrl": "https://images.samsung.com/is/image/samsung/p6pim/eg/qa55q6faauxeg/gallery/eg-qled-q6f-qa55q6faauxeg-552022552?$1164_776_PNG$",
            "source": "Samsung Egypt official",
            "inStock": True,
            "features": [
                "QLED",
                "4K",
                "2025 model",
                "Official Samsung EG store",
                "Add to cart available",
            ],
        },
        {
            "name": "Samsung 65 Inch Crystal UHD U8000H 4K Samsung Vision AI Smart TV (2026)",
            "brand": "Samsung",
            "priceEGP": 28999,
            "sizeInches": 65,
            "panel": "LED",
            "resolution": "4K UHD",
            "url": "https://www.samsung.com/eg/tvs/uhd-4k-tv/u8000h-65-inch-crystal-uhd-4k-smart-tv-ua65u8000huxeg/",
            "imageUrl": "https://images.samsung.com/is/image/samsung/p6pim/eg/ua65u8000huxeg/gallery/eg-uhd-u8000h-ua65u8000huxeg-552249641?$1164_776_PNG$",
            "source": "Samsung Egypt official",
            "inStock": True,
            "features": [
                "Crystal UHD",
                "4K",
                "65 inch large living-room size",
                "Samsung Vision AI",
                "In stock on official store",
            ],
        },
        {
            "name": "Samsung 55 Inch Crystal UHD U8000H 4K Samsung Vision AI Smart TV (2026)",
            "brand": "Samsung",
            "priceEGP": 22999,
            "sizeInches": 55,
            "panel": "LED",
            "resolution": "4K UHD",
            "url": "https://www.samsung.com/eg/tvs/uhd-4k-tv/u8000h-55-inch-crystal-uhd-4k-smart-tv-ua55u8000huxeg/",
            "imageUrl": "https://images.samsung.com/is/image/samsung/p6pim/eg/ua55u8000huxeg/gallery/eg-uhd-u8000h-ua55u8000huxeg-552249589?$1164_776_PNG$",
            "source": "Samsung Egypt official",
            "inStock": False,
            "features": [
                "Crystal UHD",
                "4K",
                "Best Samsung price in size band",
                "Listed but not available for cart on official site",
            ],
        },
    ]

    # LG Egypt official
    raw += [
        {
            "name": "55 inch LG NANO 4K AI NU84 Smart TV 2026",
            "brand": "LG",
            "priceEGP": 23499,
            "sizeInches": 55,
            "panel": "NanoCell",
            "resolution": "4K UHD",
            "url": "https://www.lg.com/eg_en/tv-soundbars/nano-4k-uhd/55nu840b6la/",
            "imageUrl": "https://www.lg.com/content/dam/channel/wcms/1-channel/portal/ms/lgcom/2026/tv-audio-video/tv/nano-4k-uhd/nu85/gp1/gallery/55-nu85/gallery/55-450.jpg",
            "source": "LG Egypt official",
            "inStock": True,
            "features": [
                "NanoCell / NANO 4K",
                "webOS",
                "AI Magic remote ecosystem",
                "Free delivery/installation offers",
                "Buy now on LG.com/eg",
            ],
        },
        {
            "name": "55 inch LG NANO 4K AI NU85 Smart TV 2026",
            "brand": "LG",
            "priceEGP": 23999,
            "sizeInches": 55,
            "panel": "NanoCell",
            "resolution": "4K UHD",
            "url": "https://www.lg.com/eg_en/tv-soundbars/nano-4k-uhd/55nu850b6la/",
            "imageUrl": "https://www.lg.com/content/dam/channel/wcms/1-channel/portal/ms/lgcom/2026/tv-audio-video/tv/nano-4k-uhd/nu85/gp1/gallery/55-nu85/gallery/55-450.jpg",
            "source": "LG Egypt official",
            "inStock": True,
            "features": [
                "NANO 4K AI NU85",
                "webOS",
                "In stock",
                "Official LG Egypt pricing",
            ],
        },
        {
            "name": "55 inch LG QNED AI QNED7E Mini LED 4K Smart TV 2026",
            "brand": "LG",
            "priceEGP": 24599,
            "sizeInches": 55,
            "panel": "Mini-LED",
            "resolution": "4K UHD",
            "url": "https://www.lg.com/eg_en/tv-soundbars/qned/55qned7eb6t/",
            "imageUrl": "https://www.lg.com/content/dam/channel/wcms/1-channel/eg_en/ms/lgcom/2026/tv-audio-video/tv/qned/qned70/gp1/gallery/55-qned70/gallery/55-450-1.jpg",
            "source": "LG Egypt official",
            "inStock": True,
            "features": [
                "QNED Mini LED",
                "LG Online Exclusive",
                "0% interest offers",
                "Buy now",
            ],
        },
        {
            "name": "65 inch LG NANO 4K UHD AI NU8E Smart TV 2026",
            "brand": "LG",
            "priceEGP": 24499,
            "sizeInches": 65,
            "panel": "NanoCell",
            "resolution": "4K UHD",
            "url": "https://www.lg.com/eg_en/tv-soundbars/nano-4k-uhd/65nu8e0b6la/",
            "imageUrl": "https://www.lg.com/content/dam/channel/wcms/1-channel/eg_en/ms/lgcom/2026/tv-audio-video/tv/nano-4k-uhd/nu85/gp1/gallery/65-nu85/gallery/new/450.jpg",
            "source": "LG Egypt official",
            "inStock": False,
            "features": [
                "65 inch NANO",
                "LG Online Exclusive pricing",
                "Stock alert shown on PDP",
            ],
        },
        {
            "name": "55 inch LG QNED AI QNED70 Mini LED 4K Smart TV 2026",
            "brand": "LG",
            "priceEGP": 27499,
            "sizeInches": 55,
            "panel": "Mini-LED",
            "resolution": "4K UHD",
            "url": "https://www.lg.com/eg_en/tv-soundbars/qned/55qned70b6t/",
            "imageUrl": "https://www.lg.com/content/dam/channel/wcms/1-channel/eg_en/ms/lgcom/2026/tv-audio-video/tv/qned/qned70/gp1/gallery/55-qned70/gallery/55-450.jpg",
            "source": "LG Egypt official",
            "inStock": True,
            "features": ["QNED70 Mini LED", "2026 model", "In stock on LG Egypt"],
        },
        {
            "name": "65 inch LG NANO 4K AI NU85 Smart TV 2026",
            "brand": "LG",
            "priceEGP": 28999,
            "sizeInches": 65,
            "panel": "NanoCell",
            "resolution": "4K UHD",
            "url": "https://www.lg.com/eg_en/tv-soundbars/nano-4k-uhd/65nu850b6la/",
            "imageUrl": "https://www.lg.com/content/dam/channel/wcms/1-channel/portal/ms/lgcom/2026/tv-audio-video/tv/nano-4k-uhd/nu85/gp1/gallery/65-nu85/gallery/65-450.jpg",
            "source": "LG Egypt official",
            "inStock": True,
            "features": ["65 inch", "NANO 4K AI", "In stock", "Official LG store"],
        },
        {
            "name": "65 inch LG QNED AI QNED7E Mini LED 4K Smart TV 2026",
            "brand": "LG",
            "priceEGP": 29899,
            "sizeInches": 65,
            "panel": "Mini-LED",
            "resolution": "4K UHD",
            "url": "https://www.lg.com/eg_en/tv-soundbars/qned/65qned7eb6t/",
            "imageUrl": "https://www.lg.com/content/dam/channel/wcms/1-channel/eg_en/ms/lgcom/2026/tv-audio-video/tv/qned/qned70/gp1/gallery/65-qned70/gallery/65-450-1.jpg",
            "source": "LG Egypt official",
            "inStock": True,
            "features": ["QNED Mini LED 65\"", "Just under 30k", "Buy now available"],
        },
    ]

    base = "https://www.elarabygroup.com/media/catalog/product/cache/3495d522e9ac8b580d54c7d730441906"
    el_img = {
        "58US1500E": f"{base}/t/o/tornado-4k-smart-dled-tv-58-inch-wifi-connection-58us1500e.jpg",
        "58US4600E": f"{base}/t/o/tornado-4k-smart-frameless-dled-tv-58-inch-58us4600e-front_new.jpg",
        "55UA5300E": f"{base}/t/o/tornado-4k-frameless-tv-55-inch-android-built-in-receiver-55ua5300e-new.jpg",
        "55US4600E": f"{base}/t/o/tornado-4k-smart-frameless-dled-tv-55-inch-55us4600e.jpg",
        "55US3500E": f"{base}/t/o/tornado-4k-smart-frameless-dled-tv-55-inch-built-in-receiver-55us3500e.jpg",
        "55UA1400E": f"{base}/t/o/tornado-4k-smart-frameless-led-tv-55-inch-android-system-built-in-receiver-3-hdmi-2-usb-inputs-55ua1400e.jpg",
        "55UA3400E": f"{base}/t/o/tornado-4k-smart-frameless-tv-55-inch-built-in-receiver-55ua3400e-new.jpg",
        "4T-C55FJ16EX": f"{base}/s/h/sharp-4k-smart-frameless-tv-55-inch-4t-c55fj16ex-lifestyle.jpg",
        "55P7K": f"{base}/t/c/tcl-4k-qled-smart-frameless-tv-55-inch-built-in-receiver-55p7k.jpg",
        "K55QA501D": f"{base}/k/a/kajito-4k-smart-frameless-tv-qled-55-inch-built-in-receiver-k55qa501d.jpg",
        "4T-C55FL6EX": f"{base}/s/h/sharp-4k-smart-frameless-tv-55-inch-built-in-receiver-4t-c55fl6ex.jpg",
        "55QA3400G": f"{base}/t/o/tornado-4k-smart-frameless-qled-tv-55-inch-built-in-receiver-55qa3400g.jpg",
        "4T-C65FJ16EX": f"{base}/s/h/sharp-4k-smart-frameless-tv-65-inch-4t-c65fj16ex-lifestyle.jpg",
        "55QS3500E": f"{base}/t/o/tornado-4k-smart-frameless-qled-tv-55-inch-built-in-receiver-55qs3500e-front_new.jpg",
        "65UA3400E": f"{base}/t/o/tornado-4k-smart-frameless-tv-65-inch-built-in-receiver-65ua3400e-new.jpg",
        "65UA5300E": f"{base}/t/o/tornado-4k-frameless-tornado-4k-frameless-tv-65-inch-android-built-in-receiver-65ua5300e-new.jpg",
        "65US1500E": f"{base}/t/o/tornado-4k-smart-dled-tv-65-inch-wifi-connection-65us1500e.jpg",
        "65UA1400E": f"{base}/t/o/tornado-4k-smart-frameless-led-tv-65-inch-android-system-built-in-receiver-3-hdmi-2-usb-inputs-65ua1400e.jpg",
        "55QA3400E": f"{base}/t/o/tornado-4k-smart-frameless-qled-tv-55-inch-built-in-receiver-55qa3400e.jpg",
        "65US3500E": f"{base}/t/o/tornado-4k-smart-frameless-dled-tv-65-inch-built-in-receiver-65us3500e-front_new.jpg",
        "55P8K": f"{base}/t/c/tcl-4k-smart-frameless-tv-qled-55-inch-built-in-receiver-55p8k-life_style.jpg",
        "55C6K": f"{base}/t/c/tcl-4k-smart-frameless-qd-mini-led-tv-55-inch-built-in-receiver-55c6k.jpg",
    }

    elaraby = [
        (
            "TORNADO 4K Smart DLED TV 58 Inch WiFi Connection 58US1500E",
            "Tornado",
            21299,
            58,
            "https://www.elarabygroup.com/en/tornado-4k-smart-dled-tv-58-inch-wifi-connection-58us1500e",
            "58US1500E",
            False,
            "LED",
            ["Built-in WiFi", "Local Tornado/Elaraby service", "Cheapest 58\" official listing"],
        ),
        (
            "TORNADO 4K Smart Frameless DLED TV 55 Inch 55US4600E",
            "Tornado",
            21299,
            55,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-dled-tv-55-inch-55us4600e",
            "55US4600E",
            True,
            "LED",
            ["Frameless DLED", "Out of stock on Elaraby"],
        ),
        (
            "TORNADO 4K Smart Frameless DLED TV 55 Inch Built-In Receiver 55US3500E",
            "Tornado",
            21619,
            55,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-dled-tv-55-inch-built-in-receiver-55us3500e",
            "55US3500E",
            True,
            "LED",
            ["Built-in receiver", "Out of stock"],
        ),
        (
            "TORNADO 4K Smart Frameless DLED TV 58 Inch 58US4600E",
            "Tornado",
            21729,
            58,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-dled-tv-58-inch-58us4600e",
            "58US4600E",
            False,
            "LED",
            ["Frameless", "58 inch mid-size", "In stock"],
        ),
        (
            "TORNADO 4K Frameless TV 55 Inch Android Built-In Receiver 55UA5300E",
            "Tornado",
            21939,
            55,
            "https://www.elarabygroup.com/en/tornado-4k-frameless-tv-55-inch-android-built-in-receiver-55ua5300e",
            "55UA5300E",
            False,
            "LED",
            ["Android TV", "Built-in receiver", "In stock"],
        ),
        (
            "TORNADO 4K Frameless TV 55 Inch Android Built-In Receiver 55UA1400E",
            "Tornado",
            22469,
            55,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-led-tv-55-inch-android-system-built-in-receiver-3-hdmi-2-usb-inputs-55ua1400e",
            "55UA1400E",
            True,
            "LED",
            ["Android", "Built-in receiver", "Out of stock"],
        ),
        (
            "TORNADO 4K Smart Frameless TV 55 Inch Built-In Receiver 55UA3400E",
            "Tornado",
            22629,
            55,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-tv-55-inch-built-in-receiver-55ua3400e",
            "55UA3400E",
            True,
            "LED",
            ["Built-in receiver", "Out of stock"],
        ),
        (
            "SHARP 4K Smart Frameless TV 55 Inch 4T-C55FJ16EX",
            "Sharp",
            23199,
            55,
            "https://www.elarabygroup.com/en/sharp-4k-smart-frameless-tv-55-inch-4t-c55fj16ex",
            "4T-C55FJ16EX",
            False,
            "LED",
            ["Sharp brand via Elaraby", "Frameless 4K", "In stock"],
        ),
        (
            "TCL 4K QLED Smart Frameless TV 55 Inch Built-In Receiver 55P7K",
            "TCL",
            25039,
            55,
            "https://www.elarabygroup.com/en/tcl-4k-qled-smart-frameless-tv-55-inch-built-in-receiver-55p7k",
            "55P7K",
            False,
            "QLED",
            ["QLED", "Built-in receiver", "TCL via official Elaraby"],
        ),
        (
            "KAJITO 4K Smart Frameless TV QLED 55 Inch Built-In Receiver K55QA501D",
            "Kajito",
            25499,
            55,
            "https://www.elarabygroup.com/en/kajito-4k-smart-frameless-tv-qled-55-inch-built-in-receiver-k55qa501d",
            "K55QA501D",
            True,
            "QLED",
            ["Elaraby house brand Kajito", "QLED", "Out of stock"],
        ),
        (
            "SHARP 4K Smart Frameless TV 55 Inch Built-In Receiver 4T-C55FL6EX",
            "Sharp",
            25699,
            55,
            "https://www.elarabygroup.com/en/sharp-4k-smart-frameless-tv-55-inch-built-in-receiver-4t-c55fl6ex",
            "4T-C55FL6EX",
            True,
            "LED",
            ["Built-in receiver", "Out of stock"],
        ),
        (
            "TORNADO 4K Smart Frameless QLED TV 55 Inch Built-In Receiver 55QA3400G",
            "Tornado",
            25699,
            55,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-qled-tv-55-inch-built-in-receiver-55qa3400g",
            "55QA3400G",
            True,
            "QLED",
            ["QLED", "Out of stock"],
        ),
        (
            "SHARP 4K Smart Frameless TV 65 Inch 4T-C65FJ16EX",
            "Sharp",
            27099,
            65,
            "https://www.elarabygroup.com/en/sharp-4k-smart-frameless-tv-65-inch-4t-c65fj16ex",
            "4T-C65FJ16EX",
            False,
            "LED",
            ["65 inch Sharp", "In stock", "Elaraby official"],
        ),
        (
            "TORNADO 4K Smart Frameless QLED TV 55 Inch Built-In Receiver 55QS3500E",
            "Tornado",
            27179,
            55,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-qled-tv-55-inch-built-in-receiver-55qs3500e",
            "55QS3500E",
            False,
            "QLED",
            ["QLED", "Built-in receiver", "In stock"],
        ),
        (
            "TORNADO 4K Smart Frameless TV 65 Inch Built-In Receiver 65UA3400E",
            "Tornado",
            27399,
            65,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-tv-65-inch-built-in-receiver-65ua3400e",
            "65UA3400E",
            False,
            "LED",
            ["65 inch", "Built-in receiver", "In stock"],
        ),
        (
            "TORNADO 4K Frameless TV 65 Inch Android Built-In Receiver 65UA5300E",
            "Tornado",
            27399,
            65,
            "https://www.elarabygroup.com/en/tornado-4k-frameless-tv-65-inch-android-built-in-receiver-65ua5300e",
            "65UA5300E",
            False,
            "LED",
            ["Android TV 65\"", "Built-in receiver", "In stock"],
        ),
        (
            "TORNADO 4K Smart DLED TV 65 Inch WiFi Connection 65US1500E",
            "Tornado",
            27399,
            65,
            "https://www.elarabygroup.com/en/tornado-4k-smart-dled-tv-65-inch-wifi-connection-65us1500e",
            "65US1500E",
            True,
            "LED",
            ["65 inch DLED", "Out of stock"],
        ),
        (
            "TORNADO 4K Frameless TV 65 Inch Android Built-In Receiver 65UA1400E",
            "Tornado",
            27499,
            65,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-led-tv-65-inch-android-system-built-in-receiver-3-hdmi-2-usb-inputs-65ua1400e",
            "65UA1400E",
            True,
            "LED",
            ["Android", "Out of stock"],
        ),
        (
            "TORNADO 4K Smart Frameless QLED TV 55 Inch Built-In Receiver 55QA3400E",
            "Tornado",
            27499,
            55,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-qled-tv-55-inch-built-in-receiver-55qa3400e",
            "55QA3400E",
            True,
            "QLED",
            ["QLED", "Out of stock"],
        ),
        (
            "TORNADO 4K Smart Frameless DLED TV 65 Inch Built-In Receiver 65US3500E",
            "Tornado",
            27719,
            65,
            "https://www.elarabygroup.com/en/tornado-4k-smart-frameless-dled-tv-65-inch-built-in-receiver-65us3500e",
            "65US3500E",
            False,
            "LED",
            ["65 inch DLED", "Built-in receiver", "In stock"],
        ),
        (
            "TCL 4K Smart Frameless TV QLED 55 Inch Built-In Receiver 55P8K",
            "TCL",
            27819,
            55,
            "https://www.elarabygroup.com/en/tcl-4k-smart-frameless-tv-qled-55-inch-built-in-receiver-55p8k",
            "55P8K",
            False,
            "QLED",
            ["QLED P8K", "Built-in receiver", "In stock"],
        ),
        (
            "TCL 4K Smart Frameless QD-Mini LED TV 55 Inch Built-In Receiver 55C6K",
            "TCL",
            34889,
            55,
            "https://www.elarabygroup.com/en/tcl-4k-smart-frameless-qd-mini-led-tv-55-inch-built-in-receiver-55c6k",
            "55C6K",
            False,
            "Mini-LED",
            ["QD-Mini LED", "PDP price above 30k"],
        ),
    ]

    for name, brand, price, inch, url, key, oos, panel, feats in elaraby:
        raw.append(
            el(
                name,
                brand,
                price,
                inch,
                url,
                el_img.get(key, ""),
                oos,
                panel,
                "4K UHD",
                feats + ["Elaraby Group official manufacturer channel"],
            )
        )

    # Fresh Egypt official
    raw.append(
        {
            "name": "Fresh Smart Google TV Monitor 60 Inch QLED UHD - 60MUQ433GT",
            "brand": "Fresh",
            "priceEGP": 25361,
            "sizeInches": 60,
            "panel": "QLED",
            "resolution": "4K UHD",
            "url": "https://fresh.com.eg/en/products/fresh-smart-google-tv-monitor-60-inch-qled-uhd-60muq433gt",
            "imageUrl": "https://be.fresh.com.eg/media/catalog/product/cache/74c1057f7991b4edb2bc7bdaa94de933/6/0/60muq433g.jpg",
            "source": "Fresh Egypt official",
            "inStock": True,
            "features": [
                "Google TV",
                "QLED UHD",
                "60 inch rare mid-size",
                "Egyptian brand Fresh official store",
            ],
        }
    )

    coverage = {
        "Samsung": "https://www.samsung.com/eg/tvs/all-tvs/ — e-commerce with prices",
        "LG": "https://www.lg.com/eg_en/tv-soundbars/all-tvs/ — e-commerce with prices",
        "Elaraby Group (Tornado, Sharp, TCL, Kajito)": "https://www.elarabygroup.com/en/tvs-and-electronics/televisions",
        "Fresh": "https://fresh.com.eg/en/categories/tv",
        "Beko": "https://www.beko.com/eg-en/products/televisions — only 43/50 inch (none 55–65)",
        "Haier": "https://www.haier.com/eg/tvs/ — catalog only, no Egypt e-commerce prices",
        "Hisense": "hisenseme.com timed out (522); no working EG shop at scrape time",
        "Unionaire": "unionaire.com shop — no TV category products found",
    }

    (APP / "_tv_official_scrape.json").write_text(
        json.dumps(
            {
                "scrapedAt": "2026-07-20",
                "criteria": {
                    "minInches": MIN_INCH,
                    "maxInches": MAX_INCH,
                    "maxPriceEGP": MAX_PRICE,
                    "sources": "official manufacturers only",
                },
                "products": raw,
                "manufacturerCoverage": coverage,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    def score(it):
        s = 50
        pros, cons = [], []
        inch, price, brand = it["sizeInches"], it["priceEGP"], it["brand"]
        panel = it["panel"]
        stock = it.get("inStock")
        blob = " ".join(it.get("features") or []) + " " + it["name"]

        if inch >= 65:
            s -= 16
            pros.append(f'{inch}" — large living-room size within 55–65 band')
        elif inch >= 60:
            s -= 14
            pros.append(f'{inch}" — generous size under 65"')
        elif inch >= 58:
            s -= 12
            pros.append(f'{inch}" — between common 55 and 65 sizes')
        else:
            s -= 10
            pros.append(f'{inch}" — solid living-room size under budget')

        if price is not None:
            head = MAX_PRICE - price
            if head >= 7000:
                s -= 8
                pros.append(f"Leaves ~{head:,} EGP under 30k ceiling")
            elif head >= 3000:
                s -= 4
                pros.append(f"Under budget by ~{head:,} EGP")
            elif head < 500:
                s += 2
                cons.append("Near the 30k ceiling — little room for stand/mount")

        tier_a = {"Samsung", "LG", "Sharp", "Toshiba", "Sony", "Hisense"}
        tier_b = {"TCL", "Tornado", "Fresh", "Haier", "Beko"}
        if brand in tier_a:
            s -= 12
            pros.append(f"{brand} — strong Egypt brand/service path")
        elif brand in tier_b:
            s -= 6
            pros.append(f"{brand} — common Egypt retail brand; confirm warranty card")
        else:
            s += 3
            cons.append("Lesser-known brand — confirm warranty and service centres")

        if "official" in it["source"].lower():
            s -= 8
            pros.append(f"Official manufacturer channel: {it['source']}")
        if "built-in receiver" in blob.lower() or "receiver" in it["name"].lower():
            s -= 5
            pros.append("Built-in receiver — useful for Egyptian satellite setups")
        if "android" in blob.lower() or "google tv" in blob.lower():
            s -= 2
            pros.append("Android/Google TV app ecosystem")

        if panel == "OLED":
            s += 1
            cons.append("OLED premium panel — often overkill for value brief")
        if panel in ("QLED", "NanoCell", "Mini-LED"):
            cons.append(f"{panel} marketing layer — fine if price is right")
        if panel == "LED":
            s -= 3
            pros.append("Simple LED panel — good value orientation")

        if stock is True:
            s -= 6
            pros.append("In stock on official site at scrape time")
        elif stock is False:
            s += 15
            cons.append("Out of stock / not available for cart on official site")

        pros = list(dict.fromkeys(pros))[:6]
        cons = list(dict.fromkeys(cons))[:5]
        if not cons:
            cons.append("Re-verify price, stock, and warranty the day you buy")
        return max(1, s), pros, cons

    items = []
    excluded_examples = []
    for it in raw:
        inch, price = it["sizeInches"], it["priceEGP"]
        excluded = False
        reasons = []
        if inch is None or inch < MIN_INCH or inch > MAX_INCH:
            excluded = True
            reasons.append(f'{inch}" outside 55–65" band')
        if price is None:
            excluded = True
            reasons.append("price missing")
        elif price >= MAX_PRICE:
            excluded = True
            reasons.append(f"{price:,} EGP over 30k budget")

        sc, pros, cons = score(it)
        if reasons:
            cons = reasons + cons

        slug = re.sub(
            r"[^a-z0-9]+",
            "_",
            (it["url"].rstrip("/").split("/")[-1] or it["name"]).lower(),
        )[:55]
        stock_status = (
            "in_stock"
            if it.get("inStock") is True
            else ("out_of_stock" if it.get("inStock") is False else "unknown")
        )
        item = {
            "id": f"tv_{slug}",
            "rank": sc,
            "name": it["name"],
            "brand": it["brand"],
            "priceEGP": int(round(price)) if price is not None else None,
            "sizeInches": inch,
            "panel": it["panel"],
            "resolution": it["resolution"],
            "url": it["url"],
            "imageUrl": it.get("imageUrl") or "",
            "source": it["source"],
            "inStock": it.get("inStock"),
            "availability": (
                "In stock"
                if it.get("inStock") is True
                else ("Out of stock" if it.get("inStock") is False else "Unknown")
            ),
            "stockStatus": stock_status,
            "summary": (
                f'{inch or "?"}″ {it["panel"]} {it["resolution"]}. '
                f"Official manufacturer channel. Filter: 55–65″ and <{MAX_PRICE:,} EGP. "
                f'Availability: {"in stock" if it.get("inStock") else "not in stock / unavailable"}.'
            ),
            "pros": pros,
            "cons": cons,
            "tags": [
                t
                for t in [
                    it["brand"].lower(),
                    f"{inch}in" if inch else None,
                    it["panel"].lower().replace(" ", "_").replace("-", "_"),
                    it["resolution"].lower().replace(" ", "_"),
                    "under_30k" if price and price < MAX_PRICE else "over_budget",
                    "in_stock" if it.get("inStock") else "oos",
                    "official",
                    "main" if not excluded else "out",
                ]
                if t
            ],
            "excluded": excluded,
            "scrapeNote": "Playwright official manufacturer scrape 2026-07-20 — re-verify price/stock/warranty",
        }
        if excluded and len(excluded_examples) < 20:
            excluded_examples.append(
                {
                    "name": it["name"][:120],
                    "price": item["priceEGP"],
                    "sizeInches": inch,
                    "reason": "; ".join(reasons) if reasons else "filtered",
                }
            )
        items.append(item)

    main_items = [i for i in items if not i["excluded"]]
    out_of = [i for i in items if i["excluded"]]

    def sort_key(x):
        stock_pen = 0 if x.get("inStock") else 1
        brand_tier = (
            0
            if x["brand"] in {"Samsung", "LG", "Sharp", "Toshiba", "Sony"}
            else (1 if x["brand"] in {"TCL", "Tornado", "Fresh", "Hisense"} else 2)
        )
        return (
            stock_pen,
            brand_tier,
            -(x.get("sizeInches") or 0),
            x.get("priceEGP") or 10**9,
            x["name"],
        )

    main_items.sort(key=sort_key)
    for i, it in enumerate(main_items, 1):
        it["rank"] = i
    for i, it in enumerate(out_of, 1):
        it["rank"] = 800 + i

    final = main_items + out_of

    picks = []
    for it in main_items:
        if it.get("inStock") and it["brand"] in {
            "Samsung",
            "LG",
            "Sharp",
            "TCL",
            "Tornado",
            "Fresh",
        }:
            picks.append(it["id"])
        if len(picks) >= 8:
            break

    by_source, by_brand, by_size = {}, {}, {}
    for it in final:
        by_source[it["source"]] = by_source.get(it["source"], 0) + 1
        by_brand[it["brand"]] = by_brand.get(it["brand"], 0) + 1
        k = str(it.get("sizeInches") or "?")
        by_size[k] = by_size.get(k, 0) + 1

    catalog = {
        "version": 2,
        "title": "TV shortlist — 55–65″ · under 30,000 EGP · official manufacturers only",
        "lastUpdated": "2026-07-20",
        "currency": "EGP",
        "filtersApplied": {
            "maxPriceEGP": MAX_PRICE,
            "minSizeInches": MIN_INCH,
            "maxSizeInches": MAX_INCH,
            "sources": "official manufacturer websites in Egypt only",
            "prefer": [
                "official manufacturer store / brand group",
                "in-stock models",
                "size 55–65 for living room",
                "reliable brand service in Egypt",
                "built-in receiver when present",
            ],
        },
        "householdContext": {
            "city": "6th of October City",
            "roomHint": "Living 375×450 cm — 55–65″ band",
            "budgetEGP": MAX_PRICE,
        },
        "counts": {
            "included": len(main_items),
            "excludedListed": len(out_of),
            "total": len(final),
            "withImage": len([i for i in final if i.get("imageUrl")]),
            "inStock": len([i for i in main_items if i.get("inStock")]),
            "bySource": by_source,
            "byBrand": by_brand,
            "bySize": by_size,
        },
        "recommendedIds": picks,
        "shoppingRoute": [
            "Filter gallery to Main (55–65″ & under 30k) and prefer In stock",
            "Start with Samsung / LG official stores for warranty clarity",
            "Compare Elaraby (Tornado / Sharp / TCL) for local value and built-in receivers",
            "Fresh 60″ is a rare mid-size official option under 30k",
            "Ignore marketplace listings — this catalog is official manufacturers only",
            "Re-check price and stock the day you buy — promos move weekly",
        ],
        "kits": [
            {
                "id": "kit_value_55",
                "name": "Value 55″ under 30k",
                "note": "Best price-to-size among in-stock official listings",
                "rule": "Pick cheapest in-stock 55″ from Samsung/LG/Sharp/Tornado/TCL",
            },
            {
                "id": "kit_65_official",
                "name": "65″ official under 30k",
                "note": "Samsung U8000H / LG NANO / Tornado-Sharp 65″ options",
                "rule": "Confirm seating distance ≥2.2m",
            },
            {
                "id": "kit_brand_service",
                "name": "Brand service priority",
                "note": "Samsung or LG official store even if slightly higher",
                "rule": "Prefer in-stock official cart over OOS cheaper listing",
            },
        ],
        "excludedExamples": excluded_examples,
        "disclaimer": (
            "Scraped 2026-07-20 via Playwright from official manufacturer sites in Egypt only "
            "(Samsung.com/eg, LG.com/eg_en, Elaraby Group, Fresh.com.eg). "
            "Beko had no 55–65″ models; Haier listed models without EG e-commerce prices; "
            "Hisense Middle East site was unavailable. Prices and stock change — re-verify before purchase."
        ),
        "items": final,
    }

    out_path = APP / "tv_catalog.json"
    out_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(
        f"Included: {len(main_items)} | Excluded: {len(out_of)} | "
        f"In stock main: {sum(1 for i in main_items if i.get('inStock'))}"
    )
    print("Brands:", by_brand)
    print("Sources:", by_source)
    print("Top in-stock:")
    for it in [i for i in main_items if i.get("inStock")][:10]:
        print(
            f"  #{it['rank']} {it['priceEGP']:>6} {it['sizeInches']}\" "
            f"{it['brand']:8} {it['name'][:55]}"
        )


if __name__ == "__main__":
    main()
