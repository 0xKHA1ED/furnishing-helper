"""Parse Playwright MCP dump of fridge/washer expand scrape into workspace JSON."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP = Path(
    r"C:\Users\h\.grok\sessions\C%3A%5CUsers%5Ch%5CDesktop%5CNew%20folder%20%282%29"
    r"\019f70f2-353c-7362-95d5-0ad56442c7a3\mcp"
    r"\call-938a6121-b420-4208-8feb-31e9bc264b5a-71.txt"
)
OUT = ROOT / "data/appliances/_btech_expand_scrape.json"


def main() -> None:
    text = MCP.read_text(encoding="utf-8", errors="replace")
    if "### Result" in text:
        raw = text.split("### Result", 1)[1].strip()
    else:
        raw = text[text.find("{") :]
    # drop trailing markdown if any
    if raw.startswith("{"):
        pass
    data = None
    # progressive trim from end for truncated JSON
    for end in range(len(raw), max(1000, len(raw) - 8000), -1):
        chunk = raw[:end].rstrip()
        # close open structures if truncated mid-array — skip
        try:
            data = json.loads(chunk)
            break
        except json.JSONDecodeError:
            continue
    if data is None:
        # salvage arrays with regex
        print("full parse failed; salvaging arrays…", len(raw))
        fr_m = re.search(
            r'"fridgeKeptList"\s*:\s*(\[(?:[^\[\]]|\[[^\]]*\])*\])\s*,\s*"washerCount"',
            raw,
            re.S,
        )
        # simpler: find fridgeKeptList start
        i = raw.find('"fridgeKeptList"')
        j = raw.find('"washerCount"')
        w_i = raw.find('"washers"')
        fridges, washers = [], []
        if i > 0 and j > i:
            arr = raw[raw.find("[", i) : j]
            arr = arr[: arr.rfind("]") + 1]
            try:
                fridges = json.loads(arr)
            except json.JSONDecodeError as e:
                print("fridge salvage fail", e)
        if w_i > 0:
            arr = raw[raw.find("[", w_i) :]
            # try close
            for k in range(len(arr), max(0, len(arr) - 3000), -1):
                try:
                    washers = json.loads(arr[:k])
                    break
                except json.JSONDecodeError:
                    continue
        data = {
            "fridgeTotal": None,
            "fridgeKept": len(fridges),
            "fridgeKeptList": fridges,
            "washerCount": len(washers),
            "washers": washers,
            "salvaged": True,
        }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "wrote",
        OUT,
        "fridges",
        len(data.get("fridgeKeptList") or []),
        "washers",
        len(data.get("washers") or []),
    )


if __name__ == "__main__":
    main()
