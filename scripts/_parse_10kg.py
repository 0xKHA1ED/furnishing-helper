import re, json
from pathlib import Path

path = Path(
    r"C:\Users\h\.grok\sessions\C%3A%5CUsers%5Ch%5CDesktop%5CNew%20folder%20%282%29"
    r"\019f7c86-67c1-73e1-9320-7d54d446f3d9\mcp"
    r"\call-bc275973-d7f7-4a11-895e-413a8435f953-71.txt"
)
text = path.read_text(encoding="utf-8", errors="ignore")

# Find product names mentioning 10
for m in re.finditer(r'"name":"([^"]{10,200})"', text):
    n = m.group(1)
    if re.search(r"10\s*k|10kg|10 Kg|Black|Dark|Middle", n, re.I):
        if re.search(r"wash|top|load|10", n, re.I):
            print("-", n[:170])

print("\n--- ELARABY product-item style ---")
for m in re.finditer(r'"name":"(TORNADO|SHARP|HOOVER|HITACHI)[^"]{5,160}"', text):
    print(m.group(0)[:200])
