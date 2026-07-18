# Project vision — Wedding home (Egypt)

Living document. Revisit anytime. Detailed state lives in `data/*.json` and topic notes under `notes/`.

## What this is

A **long-running home planning system** for a couple setting up an **empty 2-bedroom apartment in 6th of October City, Egypt** (no kids planned). It is not a one-shot shopping list.

We plan the **whole home**, including small details over time, while keeping:

- **Decisions, lifestyle, personality, inventory, research, and style** in files you can reopen for months
- **Interactive HTML** tools when they help decide (grow only if useful)
- **Chat** as the working conversation — meaningful questions, answers logged back into files

## Primary aims

1. **Whole-home plan** — rooms, layout, styling, appliances, textiles, lighting, phases — not only big-box SKUs.
2. **Durable memory** — MD + JSON so revisiting the project never means starting from zero.
3. **Expensive purchases first** — money and regret risk ordered by cost/impact before tiny accessories.
4. **Interior design quality** — layout and styling guided by solid design standards (light, scale, flow, storage, cohesion), adapted to Egypt / this apartment.
5. **Couple-shared clarity** — written so **both partners** can read, disagree, and decide — not a private monologue for one person.
6. **Slow, deliberate choices** — deep understanding before shortlists and “buy this” pressure.

## What success looks like

- Move-in (and the months after) feel **planned**, not chaotic; essentials are not forgotten.
- Big spends are **conscious**: you know *why* you chose them.
- Rooms feel **like you two**, not a random showroom mix.
- There is a **phased path** you can follow and update as life changes.
- Returning to this folder always answers: *What did we decide? Why? What’s next?*

## Out of scope (for now)

- Buying on your behalf or placing orders
- Treating AI shortlists as final without your lock-in
- Over-building a polished “app” before the content and decisions exist
- AC shopping (decision: not purchasing AC)

## How we work

| Rule | Detail |
|------|--------|
| Questions | **Max 3 at a time** |
| Depth | Prefer **personality, values, lifestyle, how you live together** over shallow product quizzes |
| Specs | Only ask technical constraints when they **block** a real choice |
| Logging | After meaningful answers → update the **right** MD and/or JSON |
| Purchase order | **Highest cost / highest regret** categories first (within your constraints, e.g. no AC) |
| Research | Egyptian market (retailers, delivery to Oct 6) when a category is ripe — not before |
| Pace | Slow and deliberate; you set when to move from talk → research → shortlist → decision |
| Digital polish | Start light; grow HTML/tools when they clearly help |

## File map (what goes where)

| Kind of data | Where |
|--------------|--------|
| Project vision, process, success criteria | `PROJECT.md` (this file), `data/project-charter.json` |
| Couple lifestyle, budget bands, location, priorities | `data/profile.json` |
| Personality / how you live together (deeper notes) | `notes/lifestyle-and-personality.md` + JSON slices as needed |
| Already owned / gifted | `data/inventory.json` |
| Per-room intent, layout notes | `data/rooms.json`, `notes/rooms/*.md` as rooms deepen |
| Style direction, palette, materials | `notes/style-direction.md`, profile style fields |
| Category status (fridge, washer, …) | `data/categories.json` |
| Product research & comparisons | `data/products.json`, topic briefs e.g. `data/fridge-brief.json` |
| Locked decisions + session log | `data/decisions.json` |
| Checklist / phases | `data/checklist.json` |
| Interactive tools | `index.html`, `fridge.html`, … |

## Current snapshot (high level)

- Location: 6th of October City · empty 2BR · hybrid guest+office second bedroom  
- No AC · inventory includes cooker, vacuum, air fryer, kettle, iron, blender  
- Fridge: space-first finalists (Ariston ~420L vs LG ~401L); not locked  
- **Meta phase:** aligning on project aims (this document)

## Current focus (user-directed)

**Big appliances repository** + **guided decisions**: explain tradeoffs → ask preferences (≤3 Qs) → **parallel subagent research** on pros/cons → shortlist → you lock.

See `notes/appliance-decision-method.md`.

- Catalog: `data/appliances/catalog.json`  
- Browser UI: `appliances.html`  
- Excluded: cooker (owned), AC (not buying)

### Personality snapshot (started)

- Arrival: **cozy shared nest** (recharge together)  
- Taste: **function (you) ↔ aesthetics (partner)**  
- Meaning: **stable base** after wedding whirlwind  
- See `notes/lifestyle-and-personality.md`
