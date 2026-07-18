# Egypt Apartment Decision Hub

Interactive planning kit for a **two-bedroom wedding apartment in Egypt** (no kids planned).

**Start here for aims & process:** [`PROJECT.md`](PROJECT.md)

## What’s here

| Path | Purpose |
|------|---------|
| `index.html` | Interactive decision hub (profile, priorities, rooms, products, lighting, budget) |
| `css/`, `js/` | Styling and client logic |
| `data/profile.json` | Couple + apartment + budget + style answers |
| `data/rooms.json` | Per-room plans |
| `data/categories.json` | Purchase categories + Egypt notes |
| `data/products.json` | Researched products (filled as we shop online together) |
| `data/decisions.json` | Shortlists, lighting plan, session notes |
| `data/checklist.json` | Master progress checklist |
| `data/inventory.json` | Already owned / gifted — do not double-buy |
| `data/fridge-brief.json` | Fridge lifestyle brief + finalists |

## How we work together

1. You answer questions in chat (and/or fill the hub **Profile** tab).
2. I update the JSON files and the hub as we learn more.
3. When you’re ready for a category (e.g. fridge), I use browser tools to research **Egyptian retailers** (B.TECH, Raneen, 2B, Amazon.eg, Jumia, IKEA Egypt, etc.), compare options, and load candidates into `products`.
4. You pick winners in the hub; we mark decisions and move on.
5. Export JSON from the hub anytime so browser edits and chat stay in sync.

## Pages

- **`index.html`** — main hub (profile, rooms, budget, all products)
- **`appliances.html`** — **big appliances repository** (filter/sort/shortlist catalog)
- **`fridge.html`** — fridge decision tool (lifestyle-based lanes + shortlist)
- **`data/appliances/catalog.json`** — researched SKUs (fridge, washer, water heater, …)

## Open the hub

**Option A — double-click** `index.html`  
Works with localStorage. Loading seed JSON via `fetch` may be blocked on `file://`.

**Option B — tiny server** (recommended)

```powershell
cd "C:\Users\h\Desktop\New folder (2)"
python -m http.server 8765
```

Then open http://localhost:8765/

## Ground rules for this project

- **No kids** → second bedroom is flexible (guest / office / hybrid).
- Prices and availability change fast in Egypt — we re-check before purchase.
- Prefer clear warranty and service networks for big appliances.
- Decisions are yours; I surface tradeoffs, not pressure.
