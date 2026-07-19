/**
 * Site-wide navigation for the Egypt Apartment Decision Hub.
 * Injects a sticky bar + optional full map when #site-nav-mount or body[data-site-nav] is present.
 */
(function () {
  const PAGES = [
    {
      group: "Hub",
      items: [{ href: "index.html", label: "Decision hub", blurb: "Profile, rooms, budget, export" }]
    },
    {
      group: "Big appliances",
      items: [
        { href: "fridge-gallery.html", label: "Fridge" },
        { href: "washer-gallery.html", label: "Washer" },
        { href: "water-heater-gallery.html", label: "Water heater" },
        { href: "tv-gallery.html", label: "TV" },
        { href: "appliances.html", label: "All appliances" },
        { href: "fridge.html", label: "Fridge deep-dive" }
      ]
    },
    {
      group: "Kitchen & comfort",
      items: [
        { href: "kitchen-gallery.html", label: "Kitchen storage" },
        { href: "mattress-gallery.html", label: "Mattress" },
        { href: "carpet-gallery.html", label: "Carpets" },
        { href: "protein-gallery.html", label: "Protein snacks" },
        { href: "furniture-gallery.html", label: "Sofa & bedroom" }
      ]
    },
    {
      group: "Phase 2 research",
      items: [
        { href: "ceiling-fans-gallery.html", label: "Ceiling fans 56″" },
        { href: "tv-stands-gallery.html", label: "TV stands" },
        { href: "desks-gallery.html", label: "Office desks" },
        { href: "office-chairs-gallery.html", label: "Office chairs" },
        { href: "dining-tables-gallery.html", label: "Dining tables" },
        { href: "dining-chairs-gallery.html", label: "Dining chairs ×4" },
        { href: "water-filters-gallery.html", label: "Water filters RO" },
        { href: "guest-sleep-gallery.html", label: "Guest sleep" }
      ]
    }
  ];

  const flat = PAGES.flatMap((g) => g.items.map((i) => ({ ...i, group: g.group })));

  function currentFile() {
    const p = (location.pathname || "").split("/").pop() || "index.html";
    return p === "" ? "index.html" : p;
  }

  function injectBar() {
    if (document.getElementById("site-nav-bar")) return;
    const file = currentFile();
    const bar = document.createElement("nav");
    bar.id = "site-nav-bar";
    bar.className = "site-nav-bar";
    bar.setAttribute("aria-label", "Site");

    const links = [
      { href: "index.html", label: "Hub" },
      { href: "index.html#site-map", label: "All pages" },
      { href: "ceiling-fans-gallery.html", label: "Fans" },
      { href: "desks-gallery.html", label: "Desk" },
      { href: "office-chairs-gallery.html", label: "Chair" },
      { href: "dining-tables-gallery.html", label: "Dining" },
      { href: "water-filters-gallery.html", label: "Filter" },
      { href: "fridge-gallery.html", label: "Fridge" },
      { href: "furniture-gallery.html", label: "Furniture" }
    ];

    bar.innerHTML = `
      <div class="site-nav-inner">
        <a class="site-nav-brand" href="index.html">Apt Hub</a>
        <div class="site-nav-links">
          ${links
            .map((l) => {
              const active =
                l.href === file || (file === "index.html" && l.href === "index.html")
                  ? " is-active"
                  : "";
              return `<a class="site-nav-link${active}" href="${l.href}">${l.label}</a>`;
            })
            .join("")}
        </div>
        <details class="site-nav-more">
          <summary>More ▾</summary>
          <div class="site-nav-dropdown">
            ${PAGES.map(
              (g) => `
              <div class="site-nav-drop-group">
                <div class="site-nav-drop-title">${g.group}</div>
                ${g.items
                  .map(
                    (i) =>
                      `<a href="${i.href}" class="${i.href === file ? "is-active" : ""}">${i.label}</a>`
                  )
                  .join("")}
              </div>`
            ).join("")}
          </div>
        </details>
      </div>`;

    const shell = document.querySelector(".shell");
    if (shell) shell.insertBefore(bar, shell.firstChild);
    else document.body.insertBefore(bar, document.body.firstChild);
  }

  function renderMap(root) {
    if (!root) return;
    root.innerHTML = PAGES.map(
      (g) => `
      <section class="site-map-group">
        <h3 class="site-map-heading">${g.group}</h3>
        <div class="site-map-grid">
          ${g.items
            .map(
              (i) => `
            <a class="site-map-card" href="${i.href}">
              <span class="site-map-card-label">${i.label}</span>
              ${i.blurb ? `<span class="site-map-card-blurb">${i.blurb}</span>` : ""}
            </a>`
            )
            .join("")}
        </div>
      </section>`
    ).join("");
  }

  function init() {
    injectBar();
    const map = document.getElementById("site-map");
    if (map) renderMap(map);
    // expose for debugging
    window.__SITE_PAGES__ = flat;
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
