/**
 * Visual appliances gallery — loads data/appliances/catalog.json
 */
const STAR_KEY = "egypt-apt-appliance-stars-v1";
const COMPARE_KEY = "egypt-apt-appliance-compare-v1";

let items = [];
let stars = new Set(JSON.parse(localStorage.getItem(STAR_KEY) || "[]"));
let compare = new Set(JSON.parse(localStorage.getItem(COMPARE_KEY) || "[]"));
let active = null;
let galleryIdx = 0;

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

function toast(m) {
  const t = $("#toast");
  t.textContent = m;
  t.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove("show"), 2200);
}

function saveStars() {
  localStorage.setItem(STAR_KEY, JSON.stringify([...stars]));
}

function fmtPrice(n) {
  if (n == null) return "—";
  return Number(n).toLocaleString() + " EGP";
}

function capLabel(it) {
  if (it.capacity == null) return "—";
  return `${it.capacity} ${it.capacityUnit || ""}`.trim();
}

function typeLabel(it) {
  const s = it.specs || {};
  return s.layout || s.type || s.fuel || "—";
}

function invLabel(it) {
  const v = it.specs?.inverter;
  if (v === true) return "Inverter";
  if (v === false) return "No inverter";
  return "";
}

function filtered() {
  const cat = $("#f-cat").value;
  const q = $("#f-q").value.trim().toLowerCase();
  const min = Number($("#f-min").value) || 0;
  const max = Number($("#f-max").value) || Infinity;
  const minCap = Number($("#f-cap").value) || 0;
  const inv = $("#f-inv").value;
  const color = $("#f-color").value;
  const onlyStar = $("#f-star").value === "yes";
  const onlyDeep = $("#f-deep").value === "yes";
  const sort = $("#f-sort").value;

  let list = items.filter((it) => {
    if (cat !== "all" && it.category !== cat) return false;
    if ((it.priceEGP || 0) < min || (it.priceEGP || 0) > max) return false;
    if (minCap && (it.capacity == null || it.capacity < minCap)) return false;
    if (inv === "yes" && it.specs?.inverter !== true) return false;
    if (inv === "no" && it.specs?.inverter === true) return false;
    if (color === "black" && !(it.color === "black" || /black/i.test(it.name || ""))) return false;
    if (onlyStar && !stars.has(it.id)) return false;
    if (onlyDeep && !it.hasDeepResearch) return false;
    if (q) {
      const hay = `${it.name} ${it.brand} ${(it.tags || []).join(" ")} ${it.summary || ""}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  list.sort((a, b) => {
    if (sort === "price_asc") return (a.priceEGP || 0) - (b.priceEGP || 0);
    if (sort === "price_desc") return (b.priceEGP || 0) - (a.priceEGP || 0);
    if (sort === "cap_desc") return (b.capacity || 0) - (a.capacity || 0);
    if (sort === "brand") return (a.brand || "").localeCompare(b.brand || "");
    if (sort === "research") {
      const ra = a.researchFitScore ?? a.lifestyleFitScore ?? 0;
      const rb = b.researchFitScore ?? b.lifestyleFitScore ?? 0;
      return rb - ra;
    }
    // default: deep research first, then lifestyle fit
    const da = a.hasDeepResearch ? 1 : 0;
    const db = b.hasDeepResearch ? 1 : 0;
    if (db !== da) return db - da;
    return (b.researchFitScore ?? b.lifestyleFitScore ?? 0) - (a.researchFitScore ?? a.lifestyleFitScore ?? 0);
  });
  return list;
}

function renderGrid() {
  const list = filtered();
  $("#result-count").textContent = `Showing ${list.length} of ${items.length} · ${stars.size} starred · images on ${items.filter((i) => i.imageUrl).length}`;
  const grid = $("#product-grid");
  if (!list.length) {
    grid.innerHTML = `<div class="empty-gallery" style="grid-column:1/-1">No products match these filters.</div>`;
    return;
  }
  grid.innerHTML = list
    .map((it) => {
      const fit = it.researchFitScore ?? it.lifestyleFitScore;
      const img = it.imageUrl
        ? `<img src="${esc(it.imageUrl)}" alt="" loading="lazy" referrerpolicy="no-referrer" />`
        : `<div class="ph">No image yet</div>`;
      return `<article class="product-card ${stars.has(it.id) ? "starred" : ""}" data-id="${esc(it.id)}">
        <div class="thumb">
          ${img}
          <div class="badge-abs">
            ${it.hasDeepResearch ? `<span class="chip-mini hot">Researched</span>` : ""}
            ${it.status && it.status !== "catalog" ? `<span class="chip-mini">${esc(it.status)}</span>` : ""}
          </div>
          <button type="button" class="star-btn ${stars.has(it.id) ? "on" : ""}" data-star="${esc(it.id)}" title="Shortlist">★</button>
        </div>
        <div class="body">
          <div class="brand">${esc(it.brand || "")} · ${esc(it.category)}</div>
          <h3>${esc(it.name)}</h3>
          <div class="meta">${esc(capLabel(it))} · ${esc(typeLabel(it))}${invLabel(it) ? " · " + invLabel(it) : ""}</div>
          <div class="chips">
            ${fit != null ? `<span class="chip-mini hot">Fit ${fit}</span>` : ""}
            ${it.color ? `<span class="chip-mini">${esc(it.color)}</span>` : ""}
          </div>
          <div class="price">${fmtPrice(it.priceEGP)}</div>
        </div>
      </article>`;
    })
    .join("");

  grid.querySelectorAll(".product-card").forEach((card) => {
    card.addEventListener("click", (e) => {
      if (e.target.closest("[data-star]")) return;
      openModal(card.dataset.id);
    });
  });
  grid.querySelectorAll("[data-star]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = btn.dataset.star;
      if (stars.has(id)) stars.delete(id);
      else stars.add(id);
      saveStars();
      renderGrid();
    });
  });
}

function openModal(id) {
  active = items.find((i) => i.id === id);
  if (!active) return;
  galleryIdx = 0;
  $("#modal-backdrop").classList.add("open");
  renderModal();
}

function closeModal() {
  $("#modal-backdrop").classList.remove("open");
  active = null;
}

function renderModal() {
  const it = active;
  if (!it) return;
  const g = it.imageGallery?.length ? it.imageGallery : it.imageUrl ? [it.imageUrl] : [];
  $("#modal-title").textContent = it.name;
  $("#modal-sub").textContent = `${it.brand || ""} · ${it.category} · ${it.retailer || ""} · scraped ${it.scrapedAt || ""}`;
  $("#modal-price").textContent = fmtPrice(it.priceEGP);
  $("#modal-summary").textContent = it.summary || it.notes || "No deep research notes yet — open retailer link for full specs.";

  const main = $("#modal-main-img");
  if (g[galleryIdx]) {
    main.src = g[galleryIdx];
    main.alt = it.name;
    main.style.display = "block";
    $("#modal-no-img").style.display = "none";
  } else {
    main.style.display = "none";
    $("#modal-no-img").style.display = "block";
  }

  $("#modal-thumbs").innerHTML = g
    .map(
      (src, i) =>
        `<button type="button" class="${i === galleryIdx ? "active" : ""}" data-g="${i}"><img src="${esc(src)}" alt="" loading="lazy" referrerpolicy="no-referrer" /></button>`
    )
    .join("");
  $$("#modal-thumbs button").forEach((b) =>
    b.addEventListener("click", () => {
      galleryIdx = Number(b.dataset.g);
      renderModal();
    })
  );

  const pros = it.pros?.length ? it.pros : ["Open B.TECH link for feature list", "Add notes after showroom visit"];
  const cons = it.cons?.length
    ? it.cons
    : it.hasDeepResearch
      ? []
      : ["Pros/cons not researched yet for this SKU", "Re-verify price & warranty before buy"];
  $("#modal-pros").innerHTML = pros.map((p) => `<li>${esc(p)}</li>`).join("");
  $("#modal-cons").innerHTML = cons.map((p) => `<li>${esc(p)}</li>`).join("");

  const specs = [
    ["Capacity", capLabel(it)],
    ["Type / layout", typeLabel(it)],
    ["Inverter", it.specs?.inverter === true ? "Yes" : it.specs?.inverter === false ? "No / not claimed" : "—"],
    ["NoFrost", it.specs?.nofrost === true ? "Yes" : it.specs?.nofrost === false ? "No" : "—"],
    ["Color (guess)", it.color || "—"],
    ["Lifestyle fit score", it.lifestyleFitScore ?? "—"],
    ["Research fit score", it.researchFitScore ?? "—"],
    ["Status", it.status || "catalog"],
    ["Tags", (it.tags || []).join(", ") || "—"],
  ];
  $("#modal-specs").innerHTML = specs.map(([k, v]) => `<li><span>${esc(k)}</span><span>${esc(String(v))}</span></li>`).join("");

  const link = $("#modal-link");
  link.href = it.url || "#";
  link.textContent = "Open on B.TECH ↗";

  const starBtn = $("#modal-star");
  starBtn.textContent = stars.has(it.id) ? "★ Starred" : "☆ Star";
  starBtn.classList.toggle("primary", stars.has(it.id));
}

function applyPreset(name) {
  $$(".preset-row button").forEach((b) => b.classList.toggle("active", b.dataset.preset === name));
  // reset basics
  $("#f-star").value = "no";
  $("#f-deep").value = "no";
  $("#f-color").value = "any";
  $("#f-inv").value = "any";
  $("#f-min").value = "";
  $("#f-max").value = "";
  $("#f-cap").value = "";
  $("#f-cat").value = "all";
  $("#f-sort").value = "default";

  if (name === "fridge-black-35k") {
    $("#f-cat").value = "fridge";
    $("#f-max").value = "35000";
    $("#f-color").value = "black";
    $("#f-cap").value = "360";
    $("#f-sort").value = "research";
  } else if (name === "fridge-under-35k") {
    $("#f-cat").value = "fridge";
    $("#f-max").value = "35000";
    $("#f-cap").value = "360";
  } else if (name === "researched") {
    $("#f-deep").value = "yes";
    $("#f-sort").value = "research";
  } else if (name === "starred") {
    $("#f-star").value = "yes";
  } else if (name === "washers") {
    $("#f-cat").value = "washer";
  } else if (name === "heaters") {
    $("#f-cat").value = "water_heater";
  }
  renderGrid();
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function init() {
  try {
    const res = await fetch("data/appliances/catalog.json");
    if (!res.ok) throw new Error("fetch failed");
    const data = await res.json();
    items = data.items || [];
    $("#count-badge").textContent = `${items.length} products`;
    $("#img-badge").textContent = `${data.ui?.imageCoverage ?? items.filter((i) => i.imageUrl).length} with photos`;
    $("#disclaimer").textContent =
      data.disclaimer ||
      "Prices from B.TECH scrape — re-verify. Photos hotlinked from retailer CDN.";
  } catch {
    $("#disclaimer").innerHTML =
      "Could not load catalog. Run a local server: <code>python -m http.server 8765</code> then open <code>http://localhost:8765/appliances.html</code>.";
    return;
  }

  ["f-cat", "f-q", "f-min", "f-max", "f-cap", "f-inv", "f-color", "f-star", "f-deep", "f-sort"].forEach((id) => {
    $("#" + id).addEventListener("input", renderGrid);
    $("#" + id).addEventListener("change", renderGrid);
  });

  $$(".preset-row button").forEach((b) => b.addEventListener("click", () => applyPreset(b.dataset.preset)));

  $("#modal-close").onclick = closeModal;
  $("#modal-backdrop").addEventListener("click", (e) => {
    if (e.target.id === "modal-backdrop") closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
  $("#modal-star").onclick = () => {
    if (!active) return;
    if (stars.has(active.id)) stars.delete(active.id);
    else stars.add(active.id);
    saveStars();
    renderModal();
    renderGrid();
  };

  $("#btn-export-stars").onclick = () => {
    const picked = items.filter((i) => stars.has(i.id));
    const blob = new Blob(
      [JSON.stringify({ exportedAt: new Date().toISOString(), items: picked }, null, 2)],
      { type: "application/json" }
    );
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "appliance-shortlist.json";
    a.click();
    toast(picked.length ? `Exported ${picked.length}` : "Nothing starred");
  };

  $("#btn-clear-stars").onclick = () => {
    stars.clear();
    saveStars();
    renderGrid();
    toast("Stars cleared");
  };

  renderGrid();
}

init();
