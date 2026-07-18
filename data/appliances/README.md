# Big appliances repository

Research-backed options for the wedding home (Egypt / 6th of October).  
Prices and stock change — every record has `scrapedAt` and product `url`. Re-verify before buy.

## Browse UI (main way to use this)

**`appliances.html`** — photo grid, filters, click for gallery + pros/cons + specs.

```powershell
cd "C:\Users\h\Desktop\New folder (2)"
python -m http.server 8765
```

Open http://localhost:8765/appliances.html  

Presets: fridge black ≤35k, researched only, starred, washers, heaters.

## Scope

| Category | Status | Notes |
|----------|--------|--------|
| Fridge | Active | Preferences + deep research on shortlist |
| Washing machine | Catalog + photos | Decision loop later |
| Water heater | Catalog + photos | Decision loop later |
| Cooker / AC | Skip | Owned / not buying |

## Files

| File | Role |
|------|------|
| `catalog.json` | Gallery source of truth (v2: images + pros/cons) |
| `images_partial.json` | Raw URL → og/gallery scrape map |
| `meta.json` | Scrape waves |
| `../../notes/research/fridge-batch-*.md` | Long research writeups |
| `../../scripts/enrich_catalog.py` | Merge images + research into catalog |

## Record fields (v2)

- `imageUrl`, `imageGallery[]` — B.TECH CloudFront product photos  
- `pros[]`, `cons[]`, `summary`, `hasDeepResearch`, `researchFitScore`  
- Specs, price, tags, status as before  

## After new research

1. Playwright product pages → update `images_partial.json`  
2. Add match rules in `scripts/enrich_catalog.py`  
3. `python scripts/enrich_catalog.py`  
