// Profession guide pages: live auction house prices. The page is built with the prices known at
// build time; this script fetches the worker's latest aggregates on every visit and reprices the
// shopping list with the SAME rules as site_build/wow_ah.py price_profession() (keep them in sync):
//   vendor reagent: vendor price, unless the AH is cheaper AND lists at least the quantity needed;
//   farmed: AH price, else unknown; crafted: the cheaper of its AH price and its crafting cost.
// If the worker can't be reached, the build-time prices simply stay.
(function () {
  "use strict";
  const data = JSON.parse(document.getElementById("pfLive").textContent);
  const T = data.i18n;
  const API = window.BM_WOW_API;
  const $ = (sel) => document.querySelector(sel);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function money(copper) {
    const c = Math.floor(copper), u = T.units;
    const g = Math.floor(c / 10000), s = Math.floor((c % 10000) / 100), cu = c % 100;
    const parts = [];
    // Same typography as the built pages: narrow no-break space for thousands, no-break space before the unit.
    if (g) parts.push(String(g).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " " + u[0]);
    if (s) parts.push(s + " " + u[1]);
    if (cu || !parts.length) parts.push(cu + " " + u[2]);
    return parts.join(" ");
  }

  // The realm/faction with the most priced items, like pick_market().
  function pickMarket(agg) {
    let best = null;
    for (const [key, prices] of Object.entries(agg.ah || {})) {
      if (!best || Object.keys(prices).length > Object.keys(best.prices).length) best = { key, prices };
    }
    if (!best) return null;
    const [realm, faction] = best.key.split("|");
    const latest = Math.max(...Object.values(best.prices).map((p) => p[2]));
    return { realm, faction, latest, prices: best.prices };
  }

  function reprice(market) {
    const seenOf = (id) => {
      const p = market.prices[id];
      return p ? { unit: p[0], qty: p[1] } : null;
    };
    function reagentUnit(g, depth) {
      const [id, , kind, copper] = g;
      const seen = seenOf(id);
      if (kind === "vendor") return seen ? Math.min(copper, seen.unit) : copper;
      const options = seen ? [seen.unit] : [];
      const crafted = craftCost(id, depth + 1);
      if (crafted !== null) options.push(crafted);
      return options.length ? Math.min(...options) : null;
    }
    function craftCost(id, depth = 0) {
      const r = data.r[id];
      if (!r || depth > 2) return null;
      let total = 0;
      for (const g of r[1]) {
        const unit = reagentUnit(g, depth);
        if (unit === null) return null;
        total += unit * g[1];
      }
      return Math.ceil(total / Math.max(1, r[0]));
    }
    let known = 0, unknown = 0, thinAny = false;
    for (const m of data.m) {
      const [id, count, kind, copper] = m;
      const seen = seenOf(id);
      const ahUnit = seen ? seen.unit : null, listed = seen ? seen.qty : 0;
      const crafted = kind === "craft" ? craftCost(id) : null;
      let unit = null, source = null;
      if (kind === "vendor") {
        unit = copper; source = "vendor";
        if (ahUnit !== null && ahUnit < unit && listed >= count) { unit = ahUnit; source = "ah"; }
      } else if (crafted !== null && (ahUnit === null || crafted <= ahUnit)) {
        unit = crafted; source = "craft";
      } else if (ahUnit !== null) {
        unit = ahUnit; source = "ah";
      }
      const line = unit !== null ? unit * count : null;
      const thin = source === "ah" && listed < count;
      if (line === null) unknown++; else known += line;
      thinAny = thinAny || thin;
      const tr = document.querySelector(`tr[data-item="${id}"]`);
      if (!tr) continue;
      const ahCell = tr.querySelector(".pf-ah"), lineCell = tr.querySelector(".pf-line");
      if (ahCell) {
        ahCell.innerHTML = ahUnit !== null
          ? `${money(ahUnit)}<br><small class="pf-listed${thin ? " is-thin" : ""}"${thin ? ` title="${esc(T.m_thin)}"` : ""}>${esc(T.m_listed.replace("{n}", listed))}${thin ? " ⚠" : ""}</small>`
          : esc(T.m_none);
      }
      if (lineCell) {
        let note = "";
        if (source === "ah" && kind === "vendor") note = `<br><small>${esc(T.m_cheaper_ah)}</small>`;
        else if (source === "craft") note = `<br><small>${esc(T.m_crafted)}</small>`;
        lineCell.innerHTML = line !== null ? money(line) + note : `<small>${esc(T.m_unknown)}</small>`;
      }
    }
    const setText = (sel, text) => { const el = $(sel); if (el) el.textContent = text; };
    setText("#pfReagTotal", money(known));
    setText("#pfCostTotal", "≈ " + money(known + data.x));
    setText("#pfCostUnknown", unknown ? T.s_cost_unknown.replace("{n}", unknown) : "");
    const thinNote = $("#pfThinNote");
    if (thinNote) thinNote.hidden = !thinAny;
    const d = new Date(market.latest * 1000);
    const pad = (n) => String(n).padStart(2, "0");
    const date = T.date_fr ? `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}` : `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    setText("#pfAhNoteText", T.ah_note.replace("{realm}", market.realm)
      .replace("{faction}", T.factions[market.faction] || market.faction).replace("{date}", date) + " ");
  }

  fetch(`${API}/v1/aggregates`, { cache: "no-store" })
    .then((r) => (r.ok ? r.json() : null))
    .then((agg) => { const market = agg && pickMarket(agg); if (market) reprice(market); })
    .catch(() => { /* keep the build-time prices */ });
})();
