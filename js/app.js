/**
 * Egypt Apartment Decision Hub
 * Works offline from localStorage; can import/export JSON for the data/ folder.
 */

const STORAGE_KEY = "egypt-apt-hub-v1";

const DEFAULT_STATE = {
  profile: null,
  rooms: null,
  categories: null,
  products: null,
  decisions: null,
  checklist: null,
  ui: {
    activeTab: "dashboard",
    selectedRoom: null
  }
};

let state = structuredClone(DEFAULT_STATE);

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function toast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.remove("show"), 2800);
}

function saveLocal() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function loadLocal() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) state = { ...structuredClone(DEFAULT_STATE), ...JSON.parse(raw) };
  } catch {
    /* ignore */
  }
}

async function tryLoadSeedFiles() {
  const files = [
    ["profile", "data/profile.json"],
    ["rooms", "data/rooms.json"],
    ["categories", "data/categories.json"],
    ["products", "data/products.json"],
    ["decisions", "data/decisions.json"],
    ["checklist", "data/checklist.json"]
  ];
  let any = false;
  for (const [key, path] of files) {
    if (state[key]) continue;
    try {
      const res = await fetch(path);
      if (res.ok) {
        state[key] = await res.json();
        any = true;
      }
    } catch {
      /* file:// or missing */
    }
  }
  if (any) saveLocal();
}

function ensureSeeds() {
  if (!state.profile) {
    state.profile = {
      location: { country: "Egypt", city: "", area: "" },
      apartment: {
        type: "two_bedroom",
        bedrooms: 2,
        bathrooms: null,
        approxSqm: null,
        furnishedStatus: "",
        whatComesWithApartment: [],
        hasBalcony: null
      },
      household: {
        kids: false,
        pets: "",
        workFromHome: "",
        cookingFrequency: "",
        guestsFrequency: ""
      },
      budget: {
        currency: "EGP",
        totalRough: null,
        preferBuyOnceCryOnce: null,
        openToUsedRefurbished: null
      },
      style: { keywords: [], colorPalette: [], lightingMood: "" },
      priorities: { mustHaveNow: [], niceToHaveLater: [], canSkip: [] },
      shopping: { preferredRetailers: [] }
    };
  }
  if (!state.rooms) {
    state.rooms = {
      rooms: [
        { id: "living", name: "Living room", status: "planning", needs: ["seating", "lighting"], notes: "", decisions: [] },
        { id: "master_bedroom", name: "Master bedroom", status: "planning", needs: ["bed", "wardrobe", "lighting"], notes: "", decisions: [] },
        { id: "second_bedroom", name: "Second bedroom", status: "planning", plannedUse: null, needs: [], notes: "", decisions: [] },
        { id: "kitchen", name: "Kitchen", status: "planning", needs: ["fridge", "cooker", "lighting"], notes: "", decisions: [] },
        { id: "bathrooms", name: "Bathrooms", status: "planning", needs: ["water heater", "lighting"], notes: "", decisions: [] }
      ]
    };
  }
  if (!state.categories) {
    state.categories = {
      categories: [
        { id: "fridge", name: "Refrigerator", priority: "high", status: "not_started", egyptNotes: "" },
        { id: "cooking", name: "Cooker / hob", priority: "high", status: "not_started", egyptNotes: "" },
        { id: "washer", name: "Washing machine", priority: "high", status: "not_started", egyptNotes: "" },
        { id: "ac", name: "Air conditioning", priority: "high", status: "not_started", egyptNotes: "" },
        { id: "lighting", name: "Lighting plan", priority: "high", status: "not_started", egyptNotes: "" },
        { id: "second_room", name: "Second bedroom setup", priority: "medium", status: "not_started", egyptNotes: "" }
      ]
    };
  }
  if (!state.products) state.products = { products: [], comparisons: [], researchLog: [], currency: "EGP" };
  if (!state.decisions) state.decisions = { decisions: [], shortlists: {}, rejected: [], sessionNotes: [] };
  if (!state.checklist) {
    state.checklist = {
      phases: [
        {
          id: "discover",
          name: "Discover & profile",
          items: [
            { id: "city", label: "Confirm city / area", done: false },
            { id: "budget", label: "Set overall budget band (EGP)", done: false },
            { id: "what_exists", label: "List what the apartment already has", done: false },
            { id: "style", label: "Agree style keywords + colors", done: false },
            { id: "second_room", label: "Decide second bedroom use", done: false },
            { id: "priorities", label: "Rank buy-now vs later", done: false }
          ]
        },
        {
          id: "big_ticket",
          name: "Big ticket appliances",
          items: [
            { id: "fridge", label: "Fridge shortlist + decision", done: false },
            { id: "cooker", label: "Cooker / hob decision", done: false },
            { id: "washer", label: "Washer decision", done: false },
            { id: "ac", label: "AC plan per room", done: false },
            { id: "heater", label: "Water heater plan", done: false }
          ]
        },
        {
          id: "comfort",
          name: "Comfort & light",
          items: [
            { id: "lighting", label: "Whole-home lighting plan", done: false },
            { id: "curtains", label: "Curtains / blinds", done: false },
            { id: "mattress", label: "Mattress + bed", done: false }
          ]
        },
        {
          id: "furnish",
          name: "Furnish & style",
          items: [
            { id: "living_furn", label: "Living furniture", done: false },
            { id: "dining", label: "Dining solution", done: false },
            { id: "second_setup", label: "Second room furniture", done: false },
            { id: "soft", label: "Rugs, textiles, decor", done: false }
          ]
        }
      ]
    };
  }
  if (!state.ui) state.ui = { activeTab: "dashboard", selectedRoom: null };
}

/* ---------- Tabs ---------- */
function applyTab(id) {
  state.ui.activeTab = id || "dashboard";
  $$(".tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === state.ui.activeTab));
  $$(".panel").forEach((p) => p.classList.toggle("active", p.id === `panel-${state.ui.activeTab}`));
}

function setTab(id) {
  // Only switch visible panel — do not call render() (that used to recurse forever).
  applyTab(id);
  saveLocal();
}

/* ---------- Checklist ---------- */
function checklistStats() {
  const items = state.checklist.phases.flatMap((p) => p.items);
  const done = items.filter((i) => i.done).length;
  return { done, total: items.length, pct: items.length ? Math.round((done / items.length) * 100) : 0 };
}

function renderChecklist() {
  const root = $("#checklist-root");
  if (!root) return;
  root.innerHTML = state.checklist.phases
    .map(
      (phase) => `
    <div class="phase-title">${escapeHtml(phase.name)}</div>
    <ul class="checklist">
      ${phase.items
        .map(
          (item) => `
        <li class="${item.done ? "done" : ""}" data-phase="${phase.id}" data-item="${item.id}">
          <input type="checkbox" id="chk-${phase.id}-${item.id}" ${item.done ? "checked" : ""} />
          <label for="chk-${phase.id}-${item.id}">${escapeHtml(item.label)}</label>
        </li>`
        )
        .join("")}
    </ul>`
    )
    .join("");

  root.querySelectorAll('input[type="checkbox"]').forEach((input) => {
    input.addEventListener("change", () => {
      const li = input.closest("li");
      const phase = state.checklist.phases.find((p) => p.id === li.dataset.phase);
      const item = phase.items.find((i) => i.id === li.dataset.item);
      item.done = input.checked;
      saveLocal();
      renderDashboard();
      renderChecklist();
      toast(item.done ? "Marked done" : "Reopened");
    });
  });
}

/* ---------- Dashboard ---------- */
function renderDashboard() {
  const { done, total, pct } = checklistStats();
  $("#stat-progress").textContent = `${pct}%`;
  $("#stat-done").textContent = `${done}/${total}`;
  $("#progress-bar").style.width = `${pct}%`;

  const p = state.profile;
  $("#stat-city").textContent = p.location?.city || "Not set";
  $("#stat-budget").textContent = p.budget?.totalRough
    ? `${Number(p.budget.totalRough).toLocaleString()} ${p.budget.currency || "EGP"}`
    : "Not set";

  const openCats = (state.categories?.categories || []).filter((c) => c.status !== "decided").length;
  $("#stat-open-cats").textContent = String(openCats);

  const productCount = state.products?.products?.length || 0;
  $("#stat-products").textContent = String(productCount);

  const notes = state.decisions?.sessionNotes || [];
  const notesEl = $("#session-notes");
  if (notes.length) {
    notesEl.innerHTML = notes
      .slice()
      .reverse()
      .slice(0, 5)
      .map((n) => `<li><strong>${escapeHtml(n.date || "")}</strong> — ${escapeHtml(n.note || "")}</li>`)
      .join("");
  } else {
    notesEl.innerHTML = `<li class="muted">No notes yet.</li>`;
  }
}

/* ---------- Profile form ---------- */
const STYLE_CHIPS = [
  "Modern",
  "Minimal",
  "Warm Scandinavian",
  "Japandi",
  "Classic Egyptian / traditional accents",
  "Industrial",
  "Soft contemporary",
  "Luxury hotel",
  "Boho",
  "Coastal / Mediterranean"
];

const COLOR_CHIPS = [
  "Warm neutrals",
  "Cool greys",
  "Beige + wood",
  "White + black contrast",
  "Earth tones",
  "Soft pastels",
  "Deep greens",
  "Navy accents",
  "Gold / brass metal"
];

function renderProfileForm() {
  const p = state.profile;
  $("#f-city").value = p.location?.city || "";
  $("#f-area").value = p.location?.area || "";
  $("#f-sqm").value = p.apartment?.approxSqm ?? "";
  $("#f-baths").value = p.apartment?.bathrooms ?? "";
  $("#f-furnished").value = p.apartment?.furnishedStatus || "";
  $("#f-balcony").value = p.apartment?.hasBalcony === true ? "yes" : p.apartment?.hasBalcony === false ? "no" : "";
  $("#f-budget").value = p.budget?.totalRough ?? "";
  $("#f-buyonce").value =
    p.budget?.preferBuyOnceCryOnce === true ? "yes" : p.budget?.preferBuyOnceCryOnce === false ? "no" : "";
  $("#f-used").value =
    p.budget?.openToUsedRefurbished === true ? "yes" : p.budget?.openToUsedRefurbished === false ? "no" : "";
  $("#f-wfh").value = p.household?.workFromHome || "";
  $("#f-cook").value = p.household?.cookingFrequency || "";
  $("#f-guests").value = p.household?.guestsFrequency || "";
  $("#f-pets").value = p.household?.pets || "";
  $("#f-exists").value = (p.apartment?.whatComesWithApartment || []).join("\n");
  $("#f-lightmood").value = p.style?.lightingMood || "";

  const styleRoot = $("#style-chips");
  const selectedStyle = new Set(p.style?.keywords || []);
  styleRoot.innerHTML = STYLE_CHIPS.map(
    (s) => `<button type="button" class="chip ${selectedStyle.has(s) ? "selected" : ""}" data-chip="${escapeAttr(s)}">${escapeHtml(s)}</button>`
  ).join("");
  styleRoot.querySelectorAll(".chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.classList.toggle("selected");
    });
  });

  const colorRoot = $("#color-chips");
  const selectedColor = new Set(p.style?.colorPalette || []);
  colorRoot.innerHTML = COLOR_CHIPS.map(
    (s) => `<button type="button" class="chip ${selectedColor.has(s) ? "selected" : ""}" data-chip="${escapeAttr(s)}">${escapeHtml(s)}</button>`
  ).join("");
  colorRoot.querySelectorAll(".chip").forEach((btn) => {
    btn.addEventListener("click", () => btn.classList.toggle("selected"));
  });
}

function saveProfileFromForm() {
  const p = state.profile;
  p.location = p.location || {};
  p.apartment = p.apartment || {};
  p.budget = p.budget || { currency: "EGP" };
  p.household = p.household || {};
  p.style = p.style || {};

  p.location.city = $("#f-city").value.trim();
  p.location.area = $("#f-area").value.trim();
  p.apartment.approxSqm = numOrNull($("#f-sqm").value);
  p.apartment.bathrooms = numOrNull($("#f-baths").value);
  p.apartment.furnishedStatus = $("#f-furnished").value;
  const bal = $("#f-balcony").value;
  p.apartment.hasBalcony = bal === "yes" ? true : bal === "no" ? false : null;
  p.apartment.whatComesWithApartment = $("#f-exists")
    .value.split("\n")
    .map((s) => s.trim())
    .filter(Boolean);

  p.budget.totalRough = numOrNull($("#f-budget").value);
  p.budget.currency = "EGP";
  const bo = $("#f-buyonce").value;
  p.budget.preferBuyOnceCryOnce = bo === "yes" ? true : bo === "no" ? false : null;
  const us = $("#f-used").value;
  p.budget.openToUsedRefurbished = us === "yes" ? true : us === "no" ? false : null;

  p.household.workFromHome = $("#f-wfh").value;
  p.household.cookingFrequency = $("#f-cook").value;
  p.household.guestsFrequency = $("#f-guests").value;
  p.household.pets = $("#f-pets").value;
  p.household.kids = false;

  p.style.keywords = $$("#style-chips .chip.selected").map((b) => b.dataset.chip);
  p.style.colorPalette = $$("#color-chips .chip.selected").map((b) => b.dataset.chip);
  p.style.lightingMood = $("#f-lightmood").value;

  p.lastUpdated = new Date().toISOString();

  // Auto-tick checklist bits if filled
  const setChk = (phaseId, itemId, cond) => {
    const phase = state.checklist.phases.find((x) => x.id === phaseId);
    const item = phase?.items.find((i) => i.id === itemId);
    if (item && cond) item.done = true;
  };
  setChk("discover", "city", !!p.location.city);
  setChk("discover", "budget", !!p.budget.totalRough);
  setChk("discover", "what_exists", (p.apartment.whatComesWithApartment || []).length > 0);
  setChk("discover", "style", (p.style.keywords || []).length > 0);

  saveLocal();
  toast("Profile saved in this browser");
  renderDashboard();
  renderChecklist();
  renderExport();
}

/* ---------- Rooms ---------- */
function renderRooms() {
  const root = $("#rooms-grid");
  root.innerHTML = state.rooms.rooms
    .map(
      (r) => `
    <article class="card room-card" data-room="${r.id}">
      <span class="status">${escapeHtml(r.status || "planning")}</span>
      <h3>${escapeHtml(r.name)}</h3>
      ${r.plannedUse ? `<p class="muted">Use: <strong>${escapeHtml(r.plannedUse)}</strong></p>` : ""}
      <ul class="needs">${(r.needs || []).map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul>
      ${r.notes ? `<p class="muted" style="margin-top:0.6rem">${escapeHtml(r.notes)}</p>` : ""}
    </article>`
    )
    .join("");

  root.querySelectorAll(".room-card").forEach((card) => {
    card.addEventListener("click", () => openRoomEditor(card.dataset.room));
  });
}

function openRoomEditor(id) {
  const room = state.rooms.rooms.find((r) => r.id === id);
  if (!room) return;
  state.ui.selectedRoom = id;
  $("#room-editor").hidden = false;
  $("#room-editor-title").textContent = room.name;
  $("#re-status").value = room.status || "planning";
  $("#re-use").value = room.plannedUse || "";
  $("#re-notes").value = room.notes || "";
  $("#re-needs").value = (room.needs || []).join(", ");
  $("#re-use-wrap").hidden = id !== "second_bedroom";
  saveLocal();
  $("#room-editor").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function saveRoomEditor() {
  const id = state.ui.selectedRoom;
  const room = state.rooms.rooms.find((r) => r.id === id);
  if (!room) return;
  room.status = $("#re-status").value;
  room.notes = $("#re-notes").value.trim();
  room.needs = $("#re-needs")
    .value.split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (id === "second_bedroom") {
    room.plannedUse = $("#re-use").value.trim() || null;
    if (room.plannedUse) {
      const phase = state.checklist.phases.find((p) => p.id === "discover");
      const item = phase?.items.find((i) => i.id === "second_room");
      if (item) item.done = true;
    }
  }
  saveLocal();
  toast("Room updated");
  renderRooms();
  renderDashboard();
  renderChecklist();
}

/* ---------- Categories ---------- */
function renderCategories() {
  const root = $("#categories-list");
  root.innerHTML = state.categories.categories
    .map(
      (c) => `
    <div class="cat-row">
      <div>
        <strong>${escapeHtml(c.name)}</strong>
        <div class="muted" style="font-size:0.85rem;margin-top:0.2rem">${escapeHtml(c.egyptNotes || "")}</div>
      </div>
      <div style="display:flex;gap:0.4rem;align-items:center;flex-wrap:wrap">
        <span class="tag ${escapeAttr(c.priority || "medium")}">${escapeHtml(c.priority || "medium")}</span>
        <select data-cat-status="${c.id}" style="width:auto;padding:0.35rem 0.5rem;font-size:0.85rem">
          ${["not_started", "researching", "shortlist", "decided", "deferred"]
            .map((s) => `<option value="${s}" ${c.status === s ? "selected" : ""}>${s.replace("_", " ")}</option>`)
            .join("")}
        </select>
      </div>
    </div>`
    )
    .join("");

  root.querySelectorAll("select[data-cat-status]").forEach((sel) => {
    sel.addEventListener("change", () => {
      const cat = state.categories.categories.find((c) => c.id === sel.dataset.catStatus);
      if (cat) {
        cat.status = sel.value;
        saveLocal();
        renderDashboard();
        toast(`${cat.name}: ${sel.value}`);
      }
    });
  });
}

/* ---------- Priority board ---------- */
const DEFAULT_PRIO_POOL = [
  "Fridge",
  "Cooker / hob",
  "Washing machine",
  "AC (living)",
  "AC (bedroom)",
  "Water heater",
  "Mattress + bed",
  "Wardrobe / storage",
  "Sofa",
  "Dining table",
  "Lighting upgrade",
  "Curtains / blackout",
  "TV + stand",
  "Small kitchen appliances",
  "Second room desk setup",
  "Vacuum / cleaning",
  "Water filter / cooler"
];

function ensurePriorityPool() {
  const pr = state.profile.priorities;
  pr.mustHaveNow = pr.mustHaveNow || [];
  pr.niceToHaveLater = pr.niceToHaveLater || [];
  pr.canSkip = pr.canSkip || [];
  const all = new Set([...pr.mustHaveNow, ...pr.niceToHaveLater, ...pr.canSkip]);
  if (all.size === 0) {
    pr.mustHaveNow = DEFAULT_PRIO_POOL.slice(0, 6);
    pr.niceToHaveLater = DEFAULT_PRIO_POOL.slice(6, 12);
    pr.canSkip = DEFAULT_PRIO_POOL.slice(12);
  }
}

function renderPriorityBoard() {
  ensurePriorityPool();
  const pr = state.profile.priorities;
  const cols = [
    ["now", "Buy first (must)", pr.mustHaveNow],
    ["later", "Phase 2 (later)", pr.niceToHaveLater],
    ["skip", "Skip / gifts / maybe never", pr.canSkip]
  ];
  const root = $("#priority-board");
  root.innerHTML = cols
    .map(
      ([key, title, items]) => `
    <div class="prio-col ${key}" data-col="${key}">
      <h4>${title}</h4>
      ${items.map((t, i) => `<div class="prio-item" draggable="true" data-col="${key}" data-idx="${i}">${escapeHtml(t)}</div>`).join("")}
    </div>`
    )
    .join("");

  let drag = null;
  root.querySelectorAll(".prio-item").forEach((el) => {
    el.addEventListener("dragstart", () => {
      drag = { col: el.dataset.col, idx: Number(el.dataset.idx), text: el.textContent };
      el.style.opacity = "0.5";
    });
    el.addEventListener("dragend", () => {
      el.style.opacity = "";
      drag = null;
    });
  });
  root.querySelectorAll(".prio-col").forEach((col) => {
    col.addEventListener("dragover", (e) => {
      e.preventDefault();
      col.classList.add("drag-over");
    });
    col.addEventListener("dragleave", () => col.classList.remove("drag-over"));
    col.addEventListener("drop", (e) => {
      e.preventDefault();
      col.classList.remove("drag-over");
      if (!drag) return;
      const map = { now: "mustHaveNow", later: "niceToHaveLater", skip: "canSkip" };
      const fromKey = map[drag.col];
      const toKey = map[col.dataset.col];
      const fromArr = state.profile.priorities[fromKey];
      const [item] = fromArr.splice(drag.idx, 1);
      state.profile.priorities[toKey].push(item);
      const phase = state.checklist.phases.find((p) => p.id === "discover");
      const it = phase?.items.find((i) => i.id === "priorities");
      if (it) it.done = true;
      saveLocal();
      renderPriorityBoard();
      renderChecklist();
      toast("Priorities updated");
    });
  });
}

/* ---------- Products & compare ---------- */
function renderProducts() {
  const list = state.products.products || [];
  const root = $("#products-list");
  if (!list.length) {
    root.innerHTML = `<div class="empty-state"><strong>No products researched yet</strong>As we browse Egyptian retailers together, products will land here for comparison.</div>`;
  } else {
    root.innerHTML = `
      <div class="table-wrap"><table class="compare">
        <thead><tr>
          <th>Select</th><th>Name</th><th>Category</th><th>Price (EGP)</th><th>Retailer</th><th>Score</th><th>Status</th><th></th>
        </tr></thead>
        <tbody>
          ${list
            .map(
              (p, i) => `
            <tr>
              <td><input type="checkbox" class="cmp-pick" data-idx="${i}" ${p._compare ? "checked" : ""} /></td>
              <td><strong>${escapeHtml(p.name)}</strong>${p.url ? `<br><a href="${escapeAttr(p.url)}" target="_blank" rel="noopener">Link</a>` : ""}</td>
              <td>${escapeHtml(p.category || "")}</td>
              <td>${p.price != null ? Number(p.price).toLocaleString() : "—"}</td>
              <td>${escapeHtml(p.retailer || "")}</td>
              <td class="score">${p.score != null ? p.score : "—"}</td>
              <td><span class="tag ${p.status === "chosen" ? "done" : "open"}">${escapeHtml(p.status || "research")}</span></td>
              <td><button type="button" class="btn ghost" data-del="${i}" style="padding:0.3rem 0.5rem;font-size:0.8rem">Remove</button></td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table></div>`;
    root.querySelectorAll(".cmp-pick").forEach((cb) => {
      cb.addEventListener("change", () => {
        state.products.products[Number(cb.dataset.idx)]._compare = cb.checked;
        saveLocal();
        renderCompare();
      });
    });
    root.querySelectorAll("[data-del]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.products.products.splice(Number(btn.dataset.del), 1);
        saveLocal();
        renderProducts();
        renderCompare();
        renderDashboard();
        toast("Product removed");
      });
    });
  }
  renderCompare();
}

function renderCompare() {
  const picks = (state.products.products || []).filter((p) => p._compare);
  const root = $("#compare-root");
  if (picks.length < 2) {
    root.innerHTML = `<p class="muted">Select 2+ products with the checkboxes to compare side by side.</p>`;
    return;
  }
  const fields = [
    ["name", "Name"],
    ["category", "Category"],
    ["price", "Price (EGP)"],
    ["retailer", "Retailer"],
    ["energy", "Energy / efficiency"],
    ["capacity", "Capacity / size"],
    ["warranty", "Warranty"],
    ["pros", "Pros"],
    ["cons", "Cons"],
    ["score", "Our score"],
    ["notes", "Notes"]
  ];
  const prices = picks.map((p) => p.price).filter((x) => x != null);
  const minPrice = prices.length ? Math.min(...prices) : null;
  const scores = picks.map((p) => p.score).filter((x) => x != null);
  const maxScore = scores.length ? Math.max(...scores) : null;

  root.innerHTML = `<div class="table-wrap"><table class="compare"><thead><tr><th>Field</th>${picks
    .map((p) => {
      const best =
        (p.price != null && p.price === minPrice) || (p.score != null && p.score === maxScore);
      return `<th class="${best ? "best" : ""}">${escapeHtml(p.name)}</th>`;
    })
    .join("")}</tr></thead><tbody>
    ${fields
      .map(([key, label]) => {
        return `<tr><th>${label}</th>${picks
          .map((p) => {
            let val = p[key];
            if (key === "price" && val != null) val = Number(val).toLocaleString();
            if (Array.isArray(val)) val = val.join("; ");
            return `<td>${escapeHtml(val != null && val !== "" ? String(val) : "—")}</td>`;
          })
          .join("")}</tr>`;
      })
      .join("")}
    </tbody></table></div>`;
}

function addProductFromForm(e) {
  e.preventDefault();
  const product = {
    id: "p_" + Date.now(),
    name: $("#p-name").value.trim(),
    category: $("#p-cat").value.trim(),
    price: numOrNull($("#p-price").value),
    retailer: $("#p-retailer").value.trim(),
    url: $("#p-url").value.trim(),
    energy: $("#p-energy").value.trim(),
    capacity: $("#p-capacity").value.trim(),
    warranty: $("#p-warranty").value.trim(),
    pros: $("#p-pros")
      .value.split("\n")
      .map((s) => s.trim())
      .filter(Boolean),
    cons: $("#p-cons")
      .value.split("\n")
      .map((s) => s.trim())
      .filter(Boolean),
    score: numOrNull($("#p-score").value),
    notes: $("#p-notes").value.trim(),
    status: "research",
    _compare: false,
    addedAt: new Date().toISOString()
  };
  if (!product.name) {
    toast("Name required");
    return;
  }
  state.products.products.push(product);
  state.products.lastUpdated = new Date().toISOString();
  saveLocal();
  e.target.reset();
  renderProducts();
  renderDashboard();
  toast("Product added");
}

/* ---------- Lighting planner ---------- */
const LIGHT_ROOMS = [
  { id: "living", label: "Living", defaultK: 2700, layers: ["ambient", "task", "accent"] },
  { id: "master", label: "Master bedroom", defaultK: 2700, layers: ["ambient", "bedside", "wardrobe"] },
  { id: "second", label: "Second bedroom", defaultK: 3000, layers: ["ambient", "desk"] },
  { id: "kitchen", label: "Kitchen", defaultK: 4000, layers: ["ambient", "counter task"] },
  { id: "bath", label: "Bathroom", defaultK: 4000, layers: ["ambient", "mirror"] },
  { id: "entry", label: "Entry / hall", defaultK: 3000, layers: ["ambient"] }
];

function ensureLighting() {
  if (!state.decisions.lightingPlan) {
    state.decisions.lightingPlan = LIGHT_ROOMS.map((r) => ({
      roomId: r.id,
      label: r.label,
      kelvin: r.defaultK,
      dimmable: r.id === "living" || r.id === "master",
      smart: false,
      layers: r.layers.join(", "),
      notes: ""
    }));
  }
}

function renderLighting() {
  ensureLighting();
  const root = $("#lighting-plan");
  root.innerHTML = state.decisions.lightingPlan
    .map(
      (row, i) => `
    <div class="card" style="box-shadow:none">
      <h3>${escapeHtml(row.label)}</h3>
      <div class="form-grid">
        <label class="field">Color temp (Kelvin)
          <input type="range" min="2700" max="5000" step="100" value="${row.kelvin}" data-light="${i}" data-field="kelvin" />
          <span class="muted" id="k-label-${i}">${row.kelvin}K — ${kelvinMood(row.kelvin)}</span>
        </label>
        <label class="field">Layers / fixtures
          <input type="text" value="${escapeAttr(row.layers)}" data-light="${i}" data-field="layers" />
        </label>
        <label class="field" style="display:flex;align-items:center;gap:0.5rem;flex-direction:row">
          <input type="checkbox" ${row.dimmable ? "checked" : ""} data-light="${i}" data-field="dimmable" /> Dimmable
        </label>
        <label class="field" style="display:flex;align-items:center;gap:0.5rem;flex-direction:row">
          <input type="checkbox" ${row.smart ? "checked" : ""} data-light="${i}" data-field="smart" /> Smart bulbs interest
        </label>
        <label class="field">Notes
          <input type="text" value="${escapeAttr(row.notes || "")}" data-light="${i}" data-field="notes" />
        </label>
      </div>
    </div>`
    )
    .join("");

  root.querySelectorAll("[data-light]").forEach((el) => {
    const handler = () => {
      const i = Number(el.dataset.light);
      const field = el.dataset.field;
      const row = state.decisions.lightingPlan[i];
      if (el.type === "checkbox") row[field] = el.checked;
      else if (field === "kelvin") {
        row.kelvin = Number(el.value);
        const lab = $(`#k-label-${i}`);
        if (lab) lab.textContent = `${row.kelvin}K — ${kelvinMood(row.kelvin)}`;
      } else row[field] = el.value;
      saveLocal();
    };
    el.addEventListener("input", handler);
    el.addEventListener("change", handler);
  });
}

function kelvinMood(k) {
  if (k <= 2900) return "Warm cozy (living / sleep)";
  if (k <= 3500) return "Soft neutral";
  if (k <= 4200) return "Bright task (kitchen / bath)";
  return "Cool daylight";
}

/* ---------- Budget allocator ---------- */
function renderBudget() {
  const total = state.profile.budget?.totalRough;
  $("#budget-total-display").textContent = total
    ? `${Number(total).toLocaleString()} EGP`
    : "Set total in Profile";

  const defaults = state.profile.budget.prioritySplit || {};
  const keys = [
    ["kitchenAppliances", "Kitchen appliances", 30],
    ["laundry", "Laundry", 10],
    ["climate", "AC / climate", 20],
    ["lighting", "Lighting", 5],
    ["furniture", "Furniture", 25],
    ["softFurnishings", "Curtains / textiles", 5],
    ["misc", "Misc / buffer", 5]
  ];
  const root = $("#budget-sliders");
  root.innerHTML = keys
    .map(([key, label, def]) => {
      const val = defaults[key] != null ? defaults[key] : def;
      return `
      <label class="field">${label}
        <input type="range" min="0" max="50" value="${val}" data-bud="${key}" />
        <span class="muted"><span id="bud-pct-${key}">${val}</span>% → <strong id="bud-egp-${key}">${fmtBudget(total, val)}</strong></span>
      </label>`;
    })
    .join("");

  root.querySelectorAll("[data-bud]").forEach((el) => {
    el.addEventListener("input", () => {
      const key = el.dataset.bud;
      const v = Number(el.value);
      if (!state.profile.budget.prioritySplit) state.profile.budget.prioritySplit = {};
      state.profile.budget.prioritySplit[key] = v;
      $(`#bud-pct-${key}`).textContent = v;
      $(`#bud-egp-${key}`).textContent = fmtBudget(state.profile.budget.totalRough, v);
      const sum = Object.values(state.profile.budget.prioritySplit).reduce((a, b) => a + Number(b || 0), 0);
      $("#budget-sum").textContent = `Allocations sum to ${sum}% ${sum === 100 ? "✓" : "(aim for ~100%)"}`;
      saveLocal();
    });
  });
  const sum = keys.reduce((a, [k, , d]) => a + Number(defaults[k] != null ? defaults[k] : d), 0);
  $("#budget-sum").textContent = `Allocations sum to ${sum}% ${sum === 100 ? "✓" : "(aim for ~100%)"}`;
}

function fmtBudget(total, pct) {
  if (!total) return "—";
  return Math.round((Number(total) * pct) / 100).toLocaleString() + " EGP";
}

/* ---------- Export / import ---------- */
function renderExport() {
  const bundle = {
    exportedAt: new Date().toISOString(),
    profile: state.profile,
    rooms: state.rooms,
    categories: state.categories,
    products: state.products,
    decisions: state.decisions,
    checklist: state.checklist
  };
  $("#export-json").textContent = JSON.stringify(bundle, null, 2);
}

function downloadExport() {
  renderExport();
  const blob = new Blob([$("#export-json").textContent], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `egypt-apartment-hub-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  toast("Download started — share this file back so I can update data/");
}

function importJsonFile(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const data = JSON.parse(reader.result);
      ["profile", "rooms", "categories", "products", "decisions", "checklist"].forEach((k) => {
        if (data[k]) state[k] = data[k];
      });
      saveLocal();
      toast("Import OK");
      render();
    } catch {
      toast("Invalid JSON");
    }
  };
  reader.readAsText(file);
}

/* ---------- Helpers ---------- */
function numOrNull(v) {
  if (v === "" || v == null) return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(s) {
  return escapeHtml(s).replace(/'/g, "&#39;");
}

function render() {
  ensureSeeds();
  renderDashboard();
  renderChecklist();
  renderProfileForm();
  renderRooms();
  renderCategories();
  renderPriorityBoard();
  renderProducts();
  renderLighting();
  renderBudget();
  renderExport();
  applyTab(state.ui.activeTab || "dashboard");
}

async function init() {
  loadLocal();
  ensureSeeds();
  await tryLoadSeedFiles();
  ensureSeeds();

  $$(".tabs button").forEach((b) => b.addEventListener("click", () => setTab(b.dataset.tab)));
  $("#btn-save-profile").addEventListener("click", saveProfileFromForm);
  $("#btn-save-room").addEventListener("click", saveRoomEditor);
  $("#form-product").addEventListener("submit", addProductFromForm);
  $("#btn-export").addEventListener("click", downloadExport);
  $("#btn-copy-export").addEventListener("click", async () => {
    renderExport();
    try {
      await navigator.clipboard.writeText($("#export-json").textContent);
      toast("Copied to clipboard");
    } catch {
      toast("Copy failed — select the JSON manually");
    }
  });
  $("#import-file").addEventListener("change", (e) => {
    const f = e.target.files?.[0];
    if (f) importJsonFile(f);
  });
  $("#btn-reset").addEventListener("click", () => {
    if (confirm("Clear all hub data saved in this browser?")) {
      localStorage.removeItem(STORAGE_KEY);
      state = structuredClone(DEFAULT_STATE);
      ensureSeeds();
      render();
      toast("Reset complete");
    }
  });
  $("#btn-add-note").addEventListener("click", () => {
    const note = prompt("Session note:");
    if (!note) return;
    state.decisions.sessionNotes = state.decisions.sessionNotes || [];
    state.decisions.sessionNotes.push({ date: new Date().toISOString().slice(0, 10), note });
    saveLocal();
    renderDashboard();
    toast("Note added");
  });

  render();
}

init();
