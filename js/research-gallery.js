/**
 * Shared research gallery for phase-2 product pages.
 * Usage: <body data-catalog="data/research/foo.json" data-star-key="egypt-apt-foo-stars-v1">
 */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  const catalogUrl = document.body.dataset.catalog;
  const starKey = document.body.dataset.starKey || "egypt-apt-research-stars-v1";
  if (!catalogUrl) {
    console.error("research-gallery: missing data-catalog on body");
    return;
  }

  let catalog = null;
  let items = [];
  let stars = new Set(JSON.parse(localStorage.getItem(starKey) || "[]"));
  let activePreset = "all";
  let active = null;

  function toast(msg) {
    let t = $("#toast");
    if (!t) {
      t = document.createElement("div");
      t.id = "toast";
      t.className = "toast";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => t.classList.remove("show"), 2200);
  }

  function saveStars() {
    localStorage.setItem(starKey, JSON.stringify([...stars]));
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function fmtPrice(n, note) {
    if (n == null || n === "") return "—";
    const base = Number(n).toLocaleString() + " EGP";
    return note ? `${base} · ${note}` : base;
  }

  function pickBadge(pick) {
    if (pick === "recommended") return `<span class="chip-mini hot">Recommended</span>`;
    if (pick === "value") return `<span class="chip-mini">Value</span>`;
    if (pick === "stretch") return `<span class="chip-mini">Soft stretch</span>`;
    return "";
  }

  function matchesPreset(it, preset) {
    if (preset === "all") return true;
    if (preset === "starred") return stars.has(it.id);
    if (preset === "pack") return (it.tags || []).includes("pack");
    if (preset === "value") return it.pick === "value" || (it.tags || []).includes("value");
    if (preset === "brand") return (it.tags || []).includes("brand");
    if (preset === "remote_light") return (it.tags || []).includes("remote_light");
    if (preset === "under2k") return (it.priceEGP || 0) < 2000 || (it.tags || []).includes("under2k");
    if (preset === "under15") return (it.priceEGP || 0) < 1500 || (it.tags || []).includes("under15");
    if (preset === "under3k") return (it.priceEGP || 0) <= 3000 || (it.tags || []).includes("under3k");
    if (preset === "under4k") return (it.priceEGP || 0) < 4000 || (it.tags || []).includes("under4k");
    if (preset === "mid") return (it.priceEGP || 0) >= 2000 && (it.priceEGP || 0) < 4500;
    if (preset === "top") return (it.priceEGP || 0) >= 4500;
    if (preset === "mesh") return (it.tags || []).includes("mesh");
    if (preset === "headrest") return (it.tags || []).includes("headrest");
    if (preset === "minimal") return (it.tags || []).includes("minimal");
    if (preset === "storage") return (it.tags || []).includes("storage");
    if (preset === "wood") return (it.tags || []).includes("wood");
    if (preset === "metal") return (it.tags || []).includes("metal");
    if (preset === "fold") return (it.tags || []).includes("fold");
    if (preset === "seats4") return (it.tags || []).includes("seats4");
    if (preset === "modern") return (it.tags || []).includes("modern");
    if (preset === "sets") return (it.tags || []).includes("sets");
    if (preset === "tank") return (it.tags || []).includes("tank");
    if (preset === "plus") return (it.tags || []).includes("plus");
    if (preset === "air") return (it.tags || []).includes("air");
    if (preset === "comfort") return (it.tags || []).includes("comfort");
    if (preset === "creative") return (it.tags || []).includes("creative");
    if (preset === "under2k") return (it.priceEGP || 0) < 2000;
    // tag match fallback
    return (it.tags || []).includes(preset);
  }

  function filtered() {
    const q = ($("#f-q")?.value || "").trim().toLowerCase();
    const source = $("#f-source")?.value || "all";
    const max = Number($("#f-max")?.value) || Infinity;
    const sort = $("#f-sort")?.value || "price_asc";

    let list = items.filter((it) => {
      if (!matchesPreset(it, activePreset)) return false;
      if (source !== "all" && it.source !== source) return false;
      if ((it.priceEGP || 0) > max) return false;
      if (q) {
        const hay = `${it.name} ${it.brand} ${it.summary} ${(it.tags || []).join(" ")}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });

    list.sort((a, b) => {
      if (sort === "price_desc") return (b.priceEGP || 0) - (a.priceEGP || 0);
      if (sort === "name") return (a.name || "").localeCompare(b.name || "");
      if (sort === "pick") {
        const rank = { recommended: 0, value: 1, stretch: 2 };
        return (rank[a.pick] ?? 9) - (rank[b.pick] ?? 9) || (a.priceEGP || 0) - (b.priceEGP || 0);
      }
      return (a.priceEGP || 0) - (b.priceEGP || 0);
    });
    return list;
  }

  function renderGrid() {
    const list = filtered();
    const countEl = $("#result-count");
    if (countEl) {
      countEl.textContent = `Showing ${list.length} of ${items.length} · ${stars.size} starred`;
    }
    const badge = $("#count-badge");
    if (badge) badge.textContent = `${items.length} options`;

    const grid = $("#product-grid");
    if (!grid) return;
    if (!list.length) {
      grid.innerHTML = `<div class="empty-gallery" style="grid-column:1/-1">No options match these filters.</div>`;
      return;
    }

    grid.innerHTML = list
      .map((it) => {
        const starred = stars.has(it.id);
        return `<article class="product-card ${starred ? "starred" : ""}" data-id="${esc(it.id)}">
          <div class="thumb research-thumb">
            <div class="research-thumb-inner">
              <span class="research-source">${esc(it.source || "")}</span>
              <span class="research-brand">${esc(it.brand || "")}</span>
            </div>
            <div class="badge-abs">
              ${pickBadge(it.pick)}
              ${starred ? `<span class="chip-mini">★</span>` : ""}
            </div>
            <button type="button" class="star-btn ${starred ? "on" : ""}" data-star="${esc(it.id)}" title="Shortlist">★</button>
          </div>
          <div class="body">
            <div class="brand">${esc(it.source || "")} · ${esc(it.brand || "")}</div>
            <h3>${esc(it.name)}</h3>
            <div class="meta">${esc((it.tags || []).slice(0, 4).join(" · "))}</div>
            <p class="muted" style="font-size:0.82rem;margin:0.35rem 0 0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">${esc(it.summary || "")}</p>
            <div class="price">${fmtPrice(it.priceEGP, it.priceNote)}</div>
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
    active = items.find((x) => x.id === id);
    if (!active) return;
    $("#modal-title").textContent = active.name;
    $("#modal-sub").textContent = `${active.brand || ""} · ${active.source || ""}`;
    $("#modal-price").textContent = fmtPrice(active.priceEGP, active.priceNote);
    $("#modal-summary").textContent = active.summary || "";
    $("#modal-pros").innerHTML = (active.pros || []).map((p) => `<li>${esc(p)}</li>`).join("") || "<li class='muted'>—</li>";
    $("#modal-cons").innerHTML = (active.cons || []).map((p) => `<li>${esc(p)}</li>`).join("") || "<li class='muted'>—</li>";
    const specs = active.specs || {};
    const extra = [
      active.priceNote ? ["Price note", active.priceNote] : null,
      active.url ? ["Link", "Open product"] : null,
      ...(active.tags || []).length ? [["Tags", (active.tags || []).join(", ")]] : []
    ].filter(Boolean);
    $("#modal-specs").innerHTML =
      extra.map(([k, v]) => `<li><strong>${esc(k)}</strong> ${esc(v)}</li>`).join("") +
      Object.entries(specs)
        .map(([k, v]) => `<li><strong>${esc(k)}</strong> ${esc(v)}</li>`)
        .join("");
    const link = $("#modal-link");
    if (active.url) {
      link.href = active.url;
      link.style.display = "";
    } else {
      link.style.display = "none";
    }
    const starBtn = $("#modal-star");
    if (starBtn) {
      starBtn.textContent = stars.has(active.id) ? "★ Starred" : "☆ Star";
    }
    $("#modal-backdrop").classList.add("open");
  }

  function closeModal() {
    $("#modal-backdrop")?.classList.remove("open");
    active = null;
  }

  function bindUI() {
    const presets = catalog.presets || [{ id: "all", label: "All" }];
    const row = $("#preset-row");
    if (row) {
      row.innerHTML = presets
        .map(
          (p, i) =>
            `<button type="button" data-preset="${esc(p.id)}" class="${i === 0 ? "active" : ""}">${esc(p.label)}</button>`
        )
        .join("");
      row.querySelectorAll("button").forEach((btn) => {
        btn.addEventListener("click", () => {
          activePreset = btn.dataset.preset;
          row.querySelectorAll("button").forEach((b) => b.classList.toggle("active", b === btn));
          renderGrid();
        });
      });
    }

    const sources = [...new Set(items.map((i) => i.source).filter(Boolean))].sort();
    const srcSel = $("#f-source");
    if (srcSel) {
      srcSel.innerHTML =
        `<option value="all">All shops</option>` +
        sources.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join("");
    }

    ["f-q", "f-source", "f-max", "f-sort"].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("input", renderGrid);
      el.addEventListener("change", renderGrid);
    });

    $("#modal-close")?.addEventListener("click", closeModal);
    $("#modal-backdrop")?.addEventListener("click", (e) => {
      if (e.target.id === "modal-backdrop") closeModal();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeModal();
    });
    $("#modal-star")?.addEventListener("click", () => {
      if (!active) return;
      if (stars.has(active.id)) stars.delete(active.id);
      else stars.add(active.id);
      saveStars();
      $("#modal-star").textContent = stars.has(active.id) ? "★ Starred" : "☆ Star";
      renderGrid();
      toast(stars.has(active.id) ? "Starred" : "Unstarred");
    });

    const disc = $("#disclaimer");
    if (disc) disc.innerHTML = `<strong>Note:</strong> ${esc(catalog.disclaimer || "")}`;
    const budget = $("#budget-note");
    if (budget) budget.textContent = catalog.softBudgetNote || "";
    const route = $("#route");
    if (route && catalog.route) {
      route.innerHTML = catalog.route.map((r) => `<li>${esc(r)}</li>`).join("");
    }
  }

  async function init() {
    try {
      const res = await fetch(catalogUrl);
      if (!res.ok) throw new Error(res.statusText);
      catalog = await res.json();
      items = catalog.items || [];
      bindUI();
      renderGrid();
    } catch (e) {
      const disc = $("#disclaimer");
      if (disc) {
        disc.innerHTML = `<strong>Could not load catalog.</strong> Serve this folder over HTTP (not file://) so <code>fetch</code> works. ${esc(e.message)}`;
      }
    }
  }

  init();
})();
