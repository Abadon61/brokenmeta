// Crafters directory page (/wow-forever/artisans/): the cards crafters chose to publish from the
// BrokenMeta addon (opt-in, see wow-worker /v1/crafter*). Lists them with filters, shows their
// recipes as Wowhead links (the site's tooltip script adds names and icons), and lets a crafter
// publish or delete their own card.
(function () {
  "use strict";
  const T = JSON.parse(document.getElementById("crI18n").textContent);
  let API = window.BM_WOW_API;
  // Local testing only: ?api=http://localhost:8788 when the page itself is served from localhost.
  const override = new URLSearchParams(location.search).get("api");
  if (override && location.hostname === "localhost") API = override;

  const CLASS_COLOR = { WARRIOR: "#c69b6d", PALADIN: "#f48cba", HUNTER: "#aad372", ROGUE: "#fff468", PRIEST: "#ffffff",
    SHAMAN: "#0070dd", MAGE: "#3fc7eb", WARLOCK: "#8788ee", DRUID: "#ff7c0a" };
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  let all = [];

  function ago(ts) {
    const d = Math.max(0, Math.floor((Date.now() / 1000 - ts) / 86400));
    return d === 0 ? T.today : T.days_ago.replace("{n}", d);
  }

  function profLabel(p) {
    return `<span><b>${esc(T.profs[p[0]] || p[0])}</b> ${p[1]}<em>/${p[2]}</em></span>`;
  }

  function card(c) {
    const color = CLASS_COLOR[c.class] || "#f0e7d8";
    const star = c.favs > 0 ? ` <span class="cr-favs" title="${esc(T.favs_title)}">★ ${c.favs}</span>` : "";
    return `<article class="bmh-card cr-card" data-key="${esc(c.realm)}|${esc(c.name)}">
      <div class="bmh-portrait" style="--cc:${color}">${esc(c.name[0])}</div>
      <div class="bmh-body">
        <div class="bmh-name" style="color:${color}">${esc(c.name)} <span>${c.level}</span>${star}</div>
        <div class="cr-meta">${esc(c.realm)} · ${esc(T.factions[c.faction] || c.faction)} · ${esc(T.updated)} ${ago(c.updated_at)}</div>
        <div class="bmh-profs">${c.profs.map(profLabel).join("")}</div>
        ${c.msg ? `<div class="bmh-msg">« ${esc(c.msg)} »</div>` : ""}
        <div class="cr-recipes" hidden></div>
      </div>
      <div class="cr-actions">
        ${c.n_recipes ? `<button type="button" class="bmh-btn cr-rec">${esc(T.recipes.replace("{n}", c.n_recipes))}</button>` : ""}
        <button type="button" class="bmh-btn bmh-primary cr-whisper" data-name="${esc(c.name)}">${esc(T.whisper)}</button>
      </div>
    </article>`;
  }

  function render() {
    const realm = $("crRealm").value, faction = $("crFaction").value, prof = $("crProf").value;
    const q = $("crName").value.trim().toLowerCase();
    const list = all.filter((c) => (!realm || c.realm === realm) && (!faction || c.faction === faction)
      && (!prof || c.profs.some((p) => String(p[0]) === prof)) && (!q || c.name.toLowerCase().includes(q)));
    list.sort((a, b) => (b.favs - a.favs) || (b.updated_at - a.updated_at));
    $("crCount").textContent = T.count.replace("{n}", list.length);
    $("crList").innerHTML = list.length ? list.map(card).join("") : `<p class="cr-empty">${esc(all.length ? T.none_filter : T.none)}</p>`;
  }

  function fillSelect(sel, values, label) {
    sel.innerHTML = `<option value="">${esc(label)}</option>` + values.map(([v, l]) => `<option value="${esc(v)}">${esc(l)}</option>`).join("");
  }

  async function load() {
    try {
      // no-store: the worker allows 2 min of caching, which hid a card right after publishing it.
      const r = await fetch(`${API}/v1/crafters`, { cache: "no-store" });
      if (!r.ok) throw new Error(r.status);
      all = (await r.json()).crafters || [];
    } catch (e) {
      $("crList").innerHTML = `<p class="cr-empty">${esc(T.load_error)}</p>`;
      return;
    }
    const realms = [...new Set(all.map((c) => c.realm))].sort();
    fillSelect($("crRealm"), realms.map((r) => [r, r]), T.all_realms);
    const profs = [...new Set(all.flatMap((c) => c.profs.map((p) => p[0])))].sort((a, b) => a - b);
    fillSelect($("crProf"), profs.map((p) => [String(p), T.profs[p] || p]), T.all_profs);
    render();
  }

  async function showRecipes(article, btn) {
    const box = article.querySelector(".cr-recipes");
    if (!box.hidden) { box.hidden = true; return; }
    box.hidden = false;
    if (box.dataset.loaded) return;
    box.textContent = T.loading;
    const [realm, name] = article.dataset.key.split("|");
    try {
      const r = await fetch(`${API}/v1/crafter?realm=${encodeURIComponent(realm)}&name=${encodeURIComponent(name)}`);
      const c = await r.json();
      const blocks = Object.entries(c.recipes || {}).map(([line, ids]) => `<div class="cr-rblock"><b>${esc(T.profs[line] || line)}</b> ` +
        ids.map((id) => id > 0
          ? `<a href="https://www.wowhead.com/forever/item=${id}" data-wh-rename-link="true" data-wh-icon-size="small">item ${id}</a>`
          : `<a href="https://www.wowhead.com/forever/spell=${-id}" data-wh-rename-link="true" data-wh-icon-size="small">spell ${-id}</a>`).join(", ") + "</div>");
      box.innerHTML = blocks.join("") || esc(T.no_recipes);
      box.dataset.loaded = "1";
      if (window.$WowheadPower && window.$WowheadPower.refreshLinks) window.$WowheadPower.refreshLinks();
    } catch (e) {
      box.textContent = T.load_error;
    }
  }

  $("crList").addEventListener("click", (ev) => {
    const article = ev.target.closest(".cr-card");
    if (!article) return;
    if (ev.target.closest(".cr-rec")) showRecipes(article, ev.target);
    const w = ev.target.closest(".cr-whisper");
    if (w) {
      const text = `/w ${w.dataset.name} `;
      (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(
        () => { w.textContent = T.copied; setTimeout(() => { w.textContent = T.whisper; }, 1500); },
        () => { window.prompt(T.whisper_hint, text); });
    }
  });
  ["crRealm", "crFaction", "crProf"].forEach((id) => $(id).addEventListener("change", render));
  $("crName").addEventListener("input", render);

  // Publish / update / delete my card.
  function status(el, text, ok) { el.textContent = text; el.className = "ms-status " + (ok ? "ok" : "err"); }
  $("crConsent").addEventListener("change", () => { $("crPublish").disabled = !$("crConsent").checked; });
  $("crPublish").addEventListener("click", async () => {
    const card = $("crCard").value.trim();
    if (!card.startsWith("BMC1;")) return status($("crStatus"), T.err.bad_card, false);
    $("crPublish").disabled = true;
    try {
      const r = await fetch(`${API}/v1/crafter`, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consent: true, card }) });
      const j = await r.json();
      if (!r.ok) return status($("crStatus"), T.err[j.error] || T.err.server, false);
      status($("crStatus"), (j.updated ? T.updated_ok : T.published_ok).replace("{name}", j.name), true);
      $("crCode").textContent = j.deletion_code;
      $("crCodeBox").hidden = false;
      load();
    } catch (e) {
      status($("crStatus"), T.err.server, false);
    } finally {
      $("crPublish").disabled = !$("crConsent").checked;
    }
  });
  $("crDelete").addEventListener("click", async () => {
    const v = $("crDel").value.trim();
    const body = v.startsWith("BMC1;") ? { card: v } : { code: v };
    try {
      const r = await fetch(`${API}/v1/crafter`, { method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      if (r.ok) { status($("crDelStatus"), T.deleted_ok, true); load(); }
      else status($("crDelStatus"), T.err.not_found, false);
    } catch (e) {
      status($("crDelStatus"), T.err.server, false);
    }
  });

  load();
})();
