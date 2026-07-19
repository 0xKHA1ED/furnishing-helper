import re
from pathlib import Path

path = Path(
    r"C:\Users\h\.grok\sessions\C%3A%5CUsers%5Ch%5CDesktop%5CNew%20folder%20%282%29"
    r"\019f7c86-67c1-73e1-9320-7d54d446f3d9\mcp"
    r"\call-4f0fe35a-4e8d-4001-9da2-ad6e74b53f97-47.txt"
)
text = path.read_text(encoding="utf-8", errors="ignore")
names = re.findall(r'"name":"([^"]{8,200})"', text)
print("TOTAL NAMES", len(names))
for n in names:
    nl = n.lower()
    if any(k in nl for k in ["top", "9kg", "9 kg", "9 k.", "black", "علو", "front"]):
        if any(k in nl for k in ["wash", "غسال", "load", "top", "front", "9", "kg"]):
            print("-", n[:160])

# section by source url
for src in [
    "samsung.com",
    "lg.com",
    "toshiba",
    "zanussi",
    "whitepoint",
    "kiriazi",
    "unionaire",
    "fresh.com",
]:
    print("\n===", src, "===")
    # find chunks
    idxs = [m.start() for m in re.finditer(src, text)]
    print("mentions", len(idxs))
