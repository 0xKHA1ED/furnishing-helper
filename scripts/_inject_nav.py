from pathlib import Path

root = Path(__file__).resolve().parents[1]
tag = '    <script src="js/site-nav.js"></script>\n'
for p in sorted(root.glob("*.html")):
    t = p.read_text(encoding="utf-8")
    if "js/site-nav.js" in t:
        print("skip", p.name)
        continue
    idx = t.rfind("</body>")
    if idx < 0:
        print("no body", p.name)
        continue
    t2 = t[:idx] + tag + t[idx:]
    p.write_text(t2, encoding="utf-8")
    print("added", p.name)
