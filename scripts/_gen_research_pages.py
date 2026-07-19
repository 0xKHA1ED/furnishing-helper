"""Generate research gallery HTML pages from a simple config."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    {
        "file": "ceiling-fans-gallery.html",
        "title": "Ceiling fans 56″ white",
        "h1": "Ceiling fans — 56″ white",
        "lead": "Three matching white 56″ ceiling fans for living, master, and second bedroom. Soft budget: value packs or known brands. Ready-made, no custom.",
        "catalog": "data/research/ceiling-fans.json",
        "star": "egypt-apt-fans-stars-v1",
        "badge": "×3 rooms",
    },
    {
        "file": "tv-stands-gallery.html",
        "title": "TV stands ≤6k",
        "h1": "TV stands",
        "lead": "Soft budget ≤ <strong>6,000 EGP</strong>. Warm contemporary / nest look for living <strong>375×450</strong>. Prefer ~120–140 cm width.",
        "catalog": "data/research/tv-stands.json",
        "star": "egypt-apt-tvstand-stars-v1",
        "badge": "≤ 6k soft",
    },
    {
        "file": "desks-gallery.html",
        "title": "Office desks ≤3k",
        "h1": "Office desks — minimal",
        "lead": "Soft budget ≤ <strong>3,000 EGP</strong>. Four legs + top preferred. Sized for hybrid guest + office second bedroom.",
        "catalog": "data/research/desks.json",
        "star": "egypt-apt-desk-stars-v1",
        "badge": "≤ 3k soft",
    },
    {
        "file": "office-chairs-gallery.html",
        "title": "Office chairs ≤6k",
        "h1": "Office chairs — long hours",
        "lead": "Soft budget ≤ <strong>6,000 EGP</strong>. Mesh preferred for Egypt heat. Aim mid-band for real WFH comfort.",
        "catalog": "data/research/office-chairs.json",
        "star": "egypt-apt-chair-stars-v1",
        "badge": "≤ 6k soft",
    },
    {
        "file": "dining-tables-gallery.html",
        "title": "Dining tables ≤5k",
        "h1": "Dining tables — minimal / metal",
        "lead": "Soft budget ≤ <strong>5,000 EGP</strong>. Metal frame or simple minimal. Creative fold/drop-leaf options included.",
        "catalog": "data/research/dining-tables.json",
        "star": "egypt-apt-dtable-stars-v1",
        "badge": "≤ 5k soft",
    },
    {
        "file": "dining-chairs-gallery.html",
        "title": "Dining chairs ×4 ≤10k",
        "h1": "Dining chairs — set of 4",
        "lead": "Soft budget ≤ <strong>10,000 EGP</strong> for four chairs. Stack/fold OK for rare hosting; beech/Eames for nest look.",
        "catalog": "data/research/dining-chairs.json",
        "star": "egypt-apt-dchair-stars-v1",
        "badge": "4 chairs ≤10k",
    },
    {
        "file": "water-filters-gallery.html",
        "title": "Water filters RO",
        "h1": "Water filters — RO systems",
        "lead": "Apartment drinking water. Prefer <strong>7-stage RO</strong> with tank. Soft target ~3.5–5.5k + install.",
        "catalog": "data/research/water-filters.json",
        "star": "egypt-apt-filter-stars-v1",
        "badge": "7-stage RO",
    },
    {
        "file": "guest-sleep-gallery.html",
        "title": "Guest sleep cheap",
        "h1": "Guest sleep — cheap & flexible",
        "lead": "Rare guests · office-first second bedroom. Fold mattresses and air beds you can store away. No custom.",
        "catalog": "data/research/guest-sleep.json",
        "star": "egypt-apt-guest-stars-v1",
        "badge": "Store-away",
    },
]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} — Egypt home hub</title>
    <link rel="stylesheet" href="css/styles.css" />
    <link rel="stylesheet" href="css/appliances.css" />
  </head>
  <body data-catalog="{catalog}" data-star-key="{star}">
    <div class="shell">
      <header class="app-header">
        <div>
          <p class="eyebrow">
            <a href="index.html">← Hub</a> ·
            <a href="index.html#site-map">All pages</a> · Phase 2 research
          </p>
          <h1>{h1}</h1>
          <p class="lead">{lead}</p>
          <p class="budget-pill" id="budget-note"></p>
        </div>
        <div class="badge-row">
          <span class="badge gold" id="count-badge">—</span>
          <span class="badge">{badge}</span>
        </div>
      </header>

      <div class="help-callout" id="disclaimer">Loading…</div>

      <div class="preset-row" id="preset-row"></div>

      <div class="gallery-toolbar">
        <label>Search
          <input id="f-q" type="search" placeholder="brand, white, mesh…" />
        </label>
        <label>Shop
          <select id="f-source">
            <option value="all">All shops</option>
          </select>
        </label>
        <label>Max EGP
          <input id="f-max" type="number" min="0" step="100" placeholder="e.g. 4000" />
        </label>
        <label>Sort
          <select id="f-sort">
            <option value="price_asc">Price ↑</option>
            <option value="price_desc">Price ↓</option>
            <option value="pick">Recommended first</option>
            <option value="name">Name</option>
          </select>
        </label>
      </div>

      <p class="sticky-count" id="result-count"></p>
      <div class="product-grid" id="product-grid"></div>

      <div class="card" style="margin-top: 1.5rem">
        <h2>Shopping route</h2>
        <ol id="route" class="muted"></ol>
      </div>

      <footer class="app-footer">
        Data: <code>{catalog}</code> · Prices move — re-check before buy ·
        <a href="index.html#site-map">All hub pages</a>
      </footer>
    </div>

    <div class="modal-backdrop" id="modal-backdrop">
      <div class="modal">
        <div class="modal-head">
          <div>
            <h2 id="modal-title">Item</h2>
            <p class="muted" id="modal-sub" style="margin: 0.25rem 0 0; font-size: 0.85rem"></p>
          </div>
          <button type="button" class="modal-close" id="modal-close">Close</button>
        </div>
        <div class="modal-body">
          <div class="modal-gallery">
            <div class="research-thumb" style="width: 100%; min-height: 220px; border-radius: 12px">
              <div class="research-thumb-inner">
                <span class="research-source">Product</span>
                <span class="research-brand" style="font-size: 1.2rem">Open link for photo</span>
              </div>
            </div>
          </div>
          <div class="modal-info">
            <div class="price-lg" id="modal-price"></div>
            <p class="muted" id="modal-summary" style="margin: 0.5rem 0 0"></p>
            <div class="pc-grid">
              <div class="pc-box pros"><h4>Pros</h4><ul id="modal-pros"></ul></div>
              <div class="pc-box cons"><h4>Cons</h4><ul id="modal-cons"></ul></div>
            </div>
            <ul class="spec-list" id="modal-specs"></ul>
            <div class="btn-row" style="margin-top: 1rem">
              <button type="button" class="btn ghost" id="modal-star">☆ Star</button>
              <a class="btn primary" id="modal-link" href="#" target="_blank" rel="noopener">Open product</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <script src="js/site-nav.js"></script>
    <script src="js/research-gallery.js"></script>
  </body>
</html>
"""

for p in PAGES:
    html = TEMPLATE.format(**p)
    out = ROOT / p["file"]
    out.write_text(html, encoding="utf-8")
    print("wrote", out.name)

print("done", len(PAGES))
