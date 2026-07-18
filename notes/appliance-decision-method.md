# How we decide big appliances

## Loop (per category: fridge, washer, heater, …)

1. **Teach + ask** — Explain real tradeoffs in plain language, tied to *your* lifestyle where we know it. Max **3 questions** per turn. Prefer depth over checklist trivia.
2. **Log answers** — Preferences → `data/*-brief.json`, `notes/`, `data/decisions.json`.
3. **Parallel research (subagents)** — Multiple agents dig into shortlisted SKUs: pros/cons, warranty patterns, noise/energy notes, Egypt service reputation, price sanity vs catalog.
4. **Synthesize** — One comparison table + recommendation lanes (not a single forced pick).
5. **You lock** — Dual gate (function + aesthetics) on expensive items; status → decided in JSON.

## What “preferences” means here

Not “do you want 401 or 420 liters?” first. Instead:

- How you shop, cook, freeze, host  
- What friction you hate (noise, defrosting, door swing, cleaning)  
- Budget **band** and what else is competing for money  
- Brand trust / service anxiety  
- Then we **translate** that into liters, freezer priority, inverter, layout  

## Fridge education anchors (Egypt couple, meal-prep heavy)

| Situation | What usually matters |
|-----------|----------------------|
| Friday prep for the whole week + big shop every 1–2 weeks | More **total liters** (~380–500 L class for two who batch); don’t go tiny (~300 L) unless kitchen forces it |
| Batch cook / freeze a lot | **Freezer share and organization** matter as much as fridge shelves; bulk meat/veg needs real freezer volume |
| Rare hosting | No need for giant SBS “party fridge” |
| No ice/water dispenser (your preference) | Fewer leaks/filter costs/failures |
| Empty home, many big tickets | Mid band often wins; ultra-premium only if dual-gate both love it |
| Hot climate, long run hours | **Inverter + NoFrost** usually worth it within budget |

## Subagent research brief (template)

For each candidate SKU: price check, key specs, pros, cons, who it’s for, red flags, Egypt availability/service notes, fit vs couple brief score 1–10.
