"""Generate list of remaining URLs without images for scrape."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
urls = json.loads((root / "data/appliances/_urls.json").read_text(encoding="utf-8"))
partial = {}
pp = root / "data/appliances/images_partial.json"
if pp.exists():
    partial = json.loads(pp.read_text(encoding="utf-8"))
have = set(partial.keys())
missing = [u for u in urls if u not in have]
print(len(missing))
(root / "data/appliances/_missing_urls.json").write_text(json.dumps(missing), encoding="utf-8")
print(json.dumps(missing[:35]))
