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


def el(name, brand, price, inch, url, img, oos, panel="LED", res="4K UHD", extra=None, os_name=None):
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
        "os": os_name,
    }


def detect_os(it: dict) -> str:
    """Best-effort OS label from brand + name/features."""
    if it.get("os"):
        return it["os"]
    blob = (" ".join(it.get("features") or []) + " " + it["name"]).lower()
    brand = it["brand"]
    if "google tv" in blob:
        return "Google TV"
    if "android" in blob:
        return "Android TV"
    if "webos" in blob or brand == "LG":
        return "webOS"
    if "tizen" in blob or brand == "Samsung":
        return "Tizen"
    if brand == "TCL":
        return "Google TV"
    if brand == "Fresh":
        return "Google TV"
    if brand == "Sharp":
        return "Google TV"
    if brand in {"Tornado", "Kajito"}:
        return "Smart TV"
    return "Smart TV"


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
            "os": "Tizen",
            "features": [
                "Mini LED local dimming",
                "4K",
                "Samsung Vision AI",
                "Tizen smart TV",
                "2026 model",
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
            "os": "Tizen",
            "features": [
                "QLED quantum-dot color",
                "4K",
                "2025 model",
                "Tizen smart TV",
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
            "os": "Tizen",
            "features": [
                "Crystal UHD",
                "4K",
                "65 inch large living-room size",
                "Samsung Vision AI",
                "Tizen smart TV",
                "2026 model",
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
            "os": "Tizen",
            "features": [
                "Crystal UHD",
                "4K",
                "Samsung Vision AI",
                "Tizen smart TV",
                "2026 model",
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
            "os": "webOS",
            "features": [
                "NanoCell / NANO 4K",
                "webOS",
                "AI picture processing",
                "AI Magic remote ecosystem",
                "2026 model",
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
            "os": "webOS",
            "features": [
                "NANO 4K AI NU85",
                "webOS",
                "AI picture processing",
                "2026 model",
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
            "os": "webOS",
            "features": [
                "QNED Mini LED local dimming",
                "webOS",
                "AI picture processing",
                "LG Online Exclusive",
                "2026 model",
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
            "os": "webOS",
            "features": [
                "65 inch NANO",
                "webOS",
                "AI picture processing",
                "2026 model",
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
            "os": "webOS",
            "features": [
                "QNED70 Mini LED local dimming",
                "webOS",
                "AI picture processing",
                "2026 model",
                "In stock on LG Egypt",
            ],
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
            "os": "webOS",
            "features": [
                "65 inch",
                "NANO 4K AI",
                "webOS",
                "AI picture processing",
                "2026 model",
                "In stock",
                "Official LG store",
            ],
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
            "os": "webOS",
            "features": [
                "QNED Mini LED 65\" local dimming",
                "webOS",
                "AI picture processing",
                "2026 model",
                "Just under 30k",
                "Buy now available",
            ],
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

    # name, brand, price, inch, url_key, oos, panel, features, os
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
            "Smart TV",
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
            "Smart TV",
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
            ["Frameless", "Built-in receiver", "Out of stock"],
            "Smart TV",
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
            "Smart TV",
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
            ["Frameless", "Android TV", "Built-in receiver", "In stock"],
            "Android TV",
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
            ["Frameless", "Android TV", "Built-in receiver", "3 HDMI / 2 USB", "Out of stock"],
            "Android TV",
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
            ["Frameless", "Built-in receiver", "Out of stock"],
            "Smart TV",
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
            ["Sharp brand via Elaraby", "Frameless 4K", "Google TV ecosystem", "In stock"],
            "Google TV",
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
            ["QLED quantum-dot color", "Frameless", "Built-in receiver", "Google TV", "TCL via official Elaraby"],
            "Google TV",
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
            ["Elaraby house brand Kajito", "QLED", "Frameless", "Built-in receiver", "Out of stock"],
            "Smart TV",
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
            ["Frameless", "Built-in receiver", "Google TV ecosystem", "Out of stock"],
            "Google TV",
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
            ["QLED", "Frameless", "Built-in receiver", "Out of stock"],
            "Smart TV",
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
            ["65 inch Sharp", "Frameless", "Google TV ecosystem", "In stock", "Elaraby official"],
            "Google TV",
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
            ["QLED", "Frameless", "Built-in receiver", "In stock"],
            "Smart TV",
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
            ["65 inch", "Frameless", "Built-in receiver", "In stock"],
            "Smart TV",
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
            ["Android TV 65\"", "Frameless", "Built-in receiver", "In stock"],
            "Android TV",
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
            "Smart TV",
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
            ["Android TV", "Frameless", "Built-in receiver", "3 HDMI / 2 USB", "Out of stock"],
            "Android TV",
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
            ["QLED", "Frameless", "Built-in receiver", "Out of stock"],
            "Smart TV",
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
            ["65 inch DLED", "Frameless", "Built-in receiver", "In stock"],
            "Smart TV",
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
            ["QLED P8K (higher TCL tier)", "Frameless", "Built-in receiver", "Google TV", "In stock"],
            "Google TV",
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
            ["QD-Mini LED", "Frameless", "Built-in receiver", "Google TV", "PDP price above 30k"],
            "Google TV",
        ),
    ]

    for name, brand, price, inch, url, key, oos, panel, feats, os_name in elaraby:
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
                os_name,
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
            "os": "Google TV",
            "features": [
                "Google TV",
                "QLED UHD quantum-dot color",
                "Monitor-style chassis",
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
        """
        Quality-first score (higher = better). Dimensions:
        image panel, brand processing, OS, design, features, size, budget fit, stock.
        Pros/cons are written per dimension for the gallery modal.
        """
        s = 0  # higher is better quality
        pros, cons = [], []
        inch, price, brand = it["sizeInches"], it["priceEGP"], it["brand"]
        panel = it["panel"]
        stock = it.get("inStock")
        blob = (" ".join(it.get("features") or []) + " " + it["name"]).lower()
        os_name = detect_os(it)
        year_2026 = "2026" in it["name"] or "2026" in blob
        year_2025 = "2025" in it["name"] or "2025" in blob
        frameless = "frameless" in blob
        has_receiver = "receiver" in blob or "built-in receiver" in blob
        has_ai = any(k in blob for k in ("vision ai", "ai picture", "nano 4k ai", "qned ai", " ai "))
        mini_led = panel == "Mini-LED" or "mini led" in blob or "mini-led" in blob or "qned" in blob

        # --- Image quality / panel (0–42) ---
        if mini_led:
            s += 42
            pros.append(
                "Image: Mini-LED / multi-zone local dimming — strongest contrast & HDR punch in this budget"
            )
        elif panel == "QLED":
            s += 30
            pros.append(
                "Image: QLED quantum-dot color — brighter, more vivid color than basic LED"
            )
        elif panel == "NanoCell":
            s += 28
            pros.append(
                "Image: NanoCell filter — cleaner color and better off-angle viewing than plain LED"
            )
        elif panel == "OLED":
            s += 45
            pros.append("Image: OLED perfect blacks — top-tier picture (rare under 30k)")
        else:
            s += 14
            pros.append(
                "Image: Standard LED/Crystal UHD 4K — solid for streaming; average blacks & peak brightness"
            )
            cons.append(
                "Image: No Mini-LED / QLED layer — less pop in bright rooms and darker movie scenes"
            )

        # Brand processing & reliability (0–14)
        if brand in {"Samsung", "LG"}:
            s += 14
            pros.append(
                f"Quality: {brand} processing + Egypt service network — better upscaling, motion, and warranty path"
            )
        elif brand in {"Sharp", "Sony", "Toshiba"}:
            s += 10
            pros.append(
                f"Quality: {brand} — established brand with credible Egypt service via official channel"
            )
        elif brand in {"TCL", "Hisense"}:
            s += 8
            pros.append(
                f"Quality: {brand} — strong panel value; confirm warranty card and service centre"
            )
        elif brand in {"Tornado", "Fresh", "Haier", "Beko"}:
            s += 4
            pros.append(
                f"Quality: {brand} — common Egypt retail brand with local service; image tuning is mid-tier"
            )
            cons.append(
                "Quality: Value-brand pipeline — expect average HDR tone-mapping and motion handling"
            )
        else:
            s += 1
            cons.append(
                "Quality: Lesser-known brand — verify warranty length and spare-parts support before buying"
            )

        # --- OS / smart platform (0–18) ---
        if os_name == "webOS":
            s += 18
            pros.append(
                "OS: LG webOS — polished home UI, Magic Remote pointer, strong long-term app support"
            )
        elif os_name == "Tizen":
            s += 17
            pros.append(
                "OS: Samsung Tizen — fast menus, full app set (Netflix/YouTube/Disney+), reliable updates"
            )
        elif os_name == "Google TV":
            s += 15
            pros.append(
                "OS: Google TV — best content discovery, Chromecast built-in, Play Store apps"
            )
        elif os_name == "Android TV":
            s += 11
            pros.append(
                "OS: Android TV — familiar Google apps; useful if you already live in that ecosystem"
            )
            cons.append(
                "OS: Android TV on local brands may lag major OS upgrades vs Tizen/webOS flagships"
            )
        else:
            s += 5
            pros.append("OS: Basic smart TV — streaming apps present; confirm Netflix/YouTube versions")
            cons.append(
                "OS: Proprietary/basic smart platform — fewer apps and slower feature updates than Tizen/webOS/Google TV"
            )

        # --- Design (0–10) ---
        design_pts = 0
        if frameless:
            design_pts += 5
            pros.append("Design: Frameless bezel — cleaner modern look on a living-room wall")
        if brand in {"Samsung", "LG"}:
            design_pts += 4
            pros.append("Design: Premium chassis/stand language from a global design line")
        elif "monitor" in blob:
            design_pts += 3
            pros.append("Design: Monitor-style slim chassis — easy to wall-mount or desk-place")
        if design_pts == 0:
            design_pts = 2
        s += design_pts

        # --- Features (0–16) ---
        if has_ai:
            s += 5
            pros.append(
                "Features: AI picture processing — auto upscaling and scene optimization for mixed content"
            )
        if has_receiver:
            s += 5
            pros.append(
                "Features: Built-in satellite receiver — fewer boxes for Egyptian dish setups"
            )
        if year_2026:
            s += 4
            pros.append(
                "Features: 2026 model year — fresher smart features and a longer support window"
            )
        elif year_2025:
            s += 2
            pros.append("Features: Recent 2025 model — still current-gen software/features")
            if brand == "Samsung" and panel == "QLED":
                cons.append("Features: 2025 QLED generation — one year behind the newest 2026 line")
        if "hdmi" in blob:
            s += 1
            pros.append("Features: Multiple HDMI/USB ports called out for consoles and sticks")
        if "free delivery" in blob or "installation" in blob:
            s += 1
            pros.append("Features: Free delivery/installation offers on official store")

        # Size for living room (secondary, 0–10)
        if inch and inch >= 65:
            s += 10
            pros.append(f'Size: {inch}" — max living-room immersion in the 55–65 band')
        elif inch and inch >= 60:
            s += 7
            pros.append(f'Size: {inch}" — generous mid-size between common 55 and 65 options')
        elif inch and inch >= 58:
            s += 5
            pros.append(f'Size: {inch}" — slightly larger than 55" without a full 65" footprint')
        else:
            s += 4
            pros.append(f'Size: {inch or "?"}" — solid living-room size under budget')

        # Budget fit (weak, 0–5) — quality-first, price only breaks ties
        if price is not None:
            head = MAX_PRICE - price
            if head >= 7000:
                s += 5
                pros.append(f"Value: Leaves ~{head:,} EGP under 30k for stand/soundbar")
            elif head >= 3000:
                s += 3
                pros.append(f"Value: Under budget by ~{head:,} EGP")
            elif head < 500:
                s += 0
                cons.append("Value: Near the 30k ceiling — little headroom for stand or soundbar")
            else:
                s += 1

        # Channel / stock (soft — quality still leads)
        if "official" in it["source"].lower():
            s += 3
            pros.append(f"Buy path: Official manufacturer channel ({it['source']})")
        if stock is True:
            s += 4
            pros.append("Stock: In stock on official site at scrape time")
        elif stock is False:
            s -= 8
            cons.append("Stock: Out of stock / not available for cart — re-check before planning a trip")

        # Dimensional cons when list is thin (so every card teaches tradeoffs)
        if mini_led and price is not None and price > 28000:
            cons.append(
                "Tradeoff: Mini-LED premium eats most of the 30k budget — plan soundbar/stand separately"
            )
        if panel == "QLED" and brand not in {"Samsung", "LG", "TCL", "Sony"}:
            cons.append(
                "Image: Entry QLED branding varies — real brightness/local dimming may be modest vs Samsung/LG"
            )
        if panel in ("LED",) and inch and inch >= 65:
            cons.append(
                "Image: Large LED without Mini-LED dimming — more backlight bloom on dark scenes at 65\""
            )
        if inch and inch <= 55 and brand in {"Samsung", "LG"} and mini_led:
            cons.append(
                "Size: 55\" Mini-LED prioritizes picture over screen size — step up to 65\" if seating is far"
            )
        if os_name == "Smart TV":
            cons.append(
                "Features: Fewer smart extras (voice, AI, casting) than Tizen/webOS/Google TV peers"
            )
        if brand in {"Tornado", "Kajito", "Fresh"} and not has_receiver:
            cons.append(
                "Features: No built-in receiver called out — may still need an external satellite box"
            )

        # Cap pros/cons for readable modals; keep dimension variety
        pros = list(dict.fromkeys(pros))[:8]
        cons = list(dict.fromkeys(cons))[:6]
        if len(cons) < 2:
            cons.append("Re-verify price, stock, and warranty terms the day you buy")
        return s, pros, cons, os_name

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

        quality, pros, cons, os_name = score(it)
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
        panel_label = it["panel"]
        item = {
            "id": f"tv_{slug}",
            "rank": quality,  # temporary; reassigned after quality sort
            "qualityScore": quality,
            "name": it["name"],
            "brand": it["brand"],
            "priceEGP": int(round(price)) if price is not None else None,
            "sizeInches": inch,
            "panel": panel_label,
            "resolution": it["resolution"],
            "os": os_name,
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
                f'{inch or "?"}″ {panel_label} {it["resolution"]} · {os_name}. '
                f"Ranked by image quality, OS, design, features, and brand. "
                f'Availability: {"in stock" if it.get("inStock") else "not in stock / unavailable"}.'
            ),
            "pros": pros,
            "cons": cons,
            "tags": [
                t
                for t in [
                    it["brand"].lower(),
                    f"{inch}in" if inch else None,
                    panel_label.lower().replace(" ", "_").replace("-", "_"),
                    it["resolution"].lower().replace(" ", "_"),
                    os_name.lower().replace(" ", "_"),
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
        # Quality first; in-stock preferred on ties; then price; then size as footprint bonus
        return (
            -(x.get("qualityScore") or 0),
            0 if x.get("inStock") else 1,
            x.get("priceEGP") or 10**9,
            -(x.get("sizeInches") or 0),
            x["name"],
        )

    main_items.sort(key=sort_key)
    out_of.sort(key=sort_key)
    for i, it in enumerate(main_items, 1):
        it["rank"] = i
    for i, it in enumerate(out_of, 1):
        it["rank"] = 800 + i

    final = main_items + out_of

    # Recommended = top quality in-stock across panel tiers
    picks = []
    for it in main_items:
        if it.get("inStock"):
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
        "version": 3,
        "title": "TV shortlist — 55–65″ · under 30,000 EGP · official manufacturers only",
        "lastUpdated": "2026-07-20",
        "currency": "EGP",
        "rankMethod": (
            "Quality-first: image panel (Mini-LED > QLED/NanoCell > LED) + brand processing + "
            "OS (webOS/Tizen > Google TV > Android TV > basic smart) + design + features + size; "
            "stock and price break ties. Pros/cons cover each dimension."
        ),
        "filtersApplied": {
            "maxPriceEGP": MAX_PRICE,
            "minSizeInches": MIN_INCH,
            "maxSizeInches": MAX_INCH,
            "sources": "official manufacturer websites in Egypt only",
            "prefer": [
                "higher image-quality panels (Mini-LED, QLED, NanoCell)",
                "mature OS (webOS, Tizen, Google TV)",
                "frameless / premium design",
                "AI processing and built-in receiver when useful",
                "official manufacturer store / brand group",
                "in-stock models when quality is comparable",
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
            "Sort by Our rank — quality-first (panel + OS + design + features), not cheapest-first",
            "Top tier under 30k: Mini-LED (LG QNED / Samsung M70H) for the best picture",
            "Mid tier: Samsung QLED / LG NanoCell for color + polished Tizen/webOS",
            "Value: TCL/Fresh QLED or Sharp frameless if you want size + Google TV under less spend",
            "Local practical: Tornado Android + built-in receiver when dish setup matters more than panel class",
            "Prefer in-stock official carts; re-check price/stock the day you buy",
        ],
        "kits": [
            {
                "id": "kit_picture_first",
                "name": "Picture-first under 30k",
                "note": "Mini-LED LG QNED or Samsung M70H — best image quality in band",
                "rule": "Pick highest-ranked Mini-LED that is in stock",
            },
            {
                "id": "kit_os_design",
                "name": "OS + design priority",
                "note": "webOS NanoCell / Tizen QLED — polished software and cleaner living-room look",
                "rule": "Prefer Samsung or LG official store even if slightly higher",
            },
            {
                "id": "kit_65_size",
                "name": "65″ immersion under 30k",
                "note": "LG 65 QNED / 65 Nano / Samsung 65 U8000H / Sharp 65",
                "rule": "Confirm seating distance ≥2.2m for 65\"",
            },
            {
                "id": "kit_value_apps",
                "name": "Value + apps",
                "note": "TCL/Fresh QLED Google TV or Sharp frameless for app ecosystem without flagship spend",
                "rule": "Confirm built-in receiver only if you need satellite",
            },
        ],
        "excludedExamples": excluded_examples,
        "disclaimer": (
            "Scraped 2026-07-20 via Playwright from official manufacturer sites in Egypt only "
            "(Samsung.com/eg, LG.com/eg_en, Elaraby Group, Fresh.com.eg). "
            "Ranked by image quality, OS, design, features, and brand — not by price alone. "
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
    print("Top by quality (all main):")
    for it in main_items[:12]:
        stock = "IN" if it.get("inStock") else "OOS"
        print(
            f"  #{it['rank']:2} q={it.get('qualityScore'):3} {stock:3} "
            f"{it['priceEGP']:>6} {it['sizeInches']}\" {it['panel']:10} "
            f"{it.get('os','?'):10} {it['brand']:8} {it['name'][:45]}"
        )


if __name__ == "__main__":
    main()
