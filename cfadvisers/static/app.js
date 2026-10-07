/* UK CF Advisers web app. Loads data/advisers.json once (served by the API, or baked in by
   `python -m cfadvisers build-static`) and filters in the browser. Filter state lives in the URL hash,
   so a filtered view can be bookmarked or shared. */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const PAGE = 100;
  const SCALE = { lo: 0.1, hi: 100 }; // £m EBITDA, log scale of the deal size bars
  const PRESETS = { any: [null, null], sme: [0.5, 2], lmm: [2, 10], mm: [10, null] };
  let DATA = [], META = {}, STATS = {}, shown = PAGE, view = [];

  const state = {
    q: "", emin: null, emax: null, unknown: false, ft: [], region: [], hq: [], sector: [], service: [],
    cfmin: null, cfmax: null, contact: false, email: false, sort: "name",
  };

  /* ---------- helpers ---------- */
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtM = (v) => v == null ? "?" : (v >= 10 ? Math.round(v) : +v.toFixed(v < 1 ? 2 : 1)).toString();
  const num = (v) => (v === "" || v == null || isNaN(+v)) ? null : +v;
  const overlaps = (lo, hi, a, b) => (lo == null && hi == null) ? null : (lo == null || lo <= b) && (hi == null || hi >= a);
  const token = () => { try { return localStorage.getItem("cfa_token") || ""; } catch (e) { return ""; } };
  const withToken = (url) => token() ? url + (url.includes("?") ? "&" : "?") + "token=" + encodeURIComponent(token()) : url;

  /* ---------- load ---------- */
  async function load() {
    let res = await fetch(withToken("data/advisers.json"));
    if (res.status === 401) {
      const t = prompt("This directory needs an access token:");
      if (t) { try { localStorage.setItem("cfa_token", t); } catch (e) {} }
      res = await fetch(withToken("data/advisers.json"));
    }
    if (!res.ok) { $("subtitle").textContent = "Could not load the data (" + res.status + ")"; return; }
    const j = await res.json();
    DATA = j.items; META = j.meta; STATS = j.stats;
    $("mult").textContent = META.ev_to_ebitda_multiple;
    $("multipleHint").textContent = "EV-only ranges converted at " + META.ev_to_ebitda_multiple + "× EBITDA.";
    $("subtitle").textContent = DATA.length + " firms · deal sizes, sectors, regions and contacts";
    // static builds have no API: point the API button at the README instead
    const readme = () => { $("apiLink").href = "https://github.com/sparkember2026/cfadvisers#api"; };
    if (window.CFA_EMBED) readme(); else fetch("v1/health").then((r) => { if (!r.ok) throw 0; }).catch(readme);
    readHash();
    buildFilters();
    renderKpis();
    apply();
  }

  /* ---------- filters ---------- */
  function counts(key) {
    const c = {};
    for (const r of DATA) for (const v of [].concat(r[key] || [])) c[v] = (c[v] || 0) + 1;
    return c;
  }
  function checkList(el, values, labels, key, cnt) {
    el.innerHTML = values.filter((v) => cnt[v]).map((v) =>
      `<label class="check"><input type="checkbox" value="${esc(v)}" ${state[key].includes(v) ? "checked" : ""}>` +
      `<span>${esc(labels ? labels[v] : v)}</span><span class="n">${cnt[v] || 0}</span></label>`).join("");
    el.onchange = () => { state[key] = [...el.querySelectorAll("input:checked")].map((i) => i.value); changed(); };
  }
  function buildFilters() {
    checkList($("fFirmType"), Object.keys(META.firm_types), META.firm_types, "ft", counts("firm_type"));
    checkList($("fRegion"), META.regions, null, "region", counts("regions_covered"));
    checkList($("fHq"), META.regions.concat(["International"]), null, "hq", counts("hq_region"));
    const sc = counts("sectors");
    checkList($("fSector"), META.sectors.slice().sort((a, b) => (sc[b] || 0) - (sc[a] || 0)), null, "sector", sc);
    checkList($("fService"), Object.keys(META.services), META.services, "service", counts("services"));
    syncInputs();
  }
  function syncInputs() {
    $("q").value = state.q;
    $("emin").value = state.emin ?? ""; $("emax").value = state.emax ?? "";
    $("cfmin").value = state.cfmin ?? ""; $("cfmax").value = state.cfmax ?? "";
    $("unknownSize").checked = state.unknown; $("hasContact").checked = state.contact; $("hasEmail").checked = state.email;
    $("sort").value = state.sort;
    for (const b of $("sizePresets").children) {
      const [a, z] = PRESETS[b.dataset.p];
      b.classList.toggle("on", a === state.emin && z === state.emax);
    }
    for (const [el, key] of [["fFirmType", "ft"], ["fRegion", "region"], ["fHq", "hq"], ["fSector", "sector"], ["fService", "service"]])
      for (const i of $(el).querySelectorAll("input")) i.checked = state[key].includes(i.value);
  }

  function filter() {
    const terms = state.q.toLowerCase().split(/\s+/).filter(Boolean);
    const sized = state.emin != null || state.emax != null;
    const lo = state.emin ?? 0, hi = state.emax ?? Infinity;
    return DATA.filter((r) => {
      if (terms.length) {
        const hay = [r.name, (r.aliases || []).join(" "), r.domain, r.hq, r.offices.join(" "), r.sectors.join(" "),
          r.sector_note, r.description, r.parent].filter(Boolean).join(" ").toLowerCase();
        if (!terms.every((t) => hay.includes(t))) return false;
      }
      if (state.ft.length && !state.ft.includes(r.firm_type)) return false;
      if (state.region.length && !state.region.some((x) => r.regions_covered.includes(x))) return false;
      if (state.hq.length && !state.hq.includes(r.hq_region)) return false;
      if (state.sector.length && !state.sector.some((x) => r.sectors.includes(x))) return false;
      if (state.service.length && !state.service.some((x) => r.services.includes(x))) return false;
      if (sized) {
        const ov = overlaps(r.ebitda_min_m, r.ebitda_max_m, lo, hi);
        if (!(ov || (ov == null && state.unknown))) return false;
      }
      if (state.cfmin != null && !(r.cf_professionals != null && r.cf_professionals >= state.cfmin)) return false;
      if (state.cfmax != null && !(r.cf_professionals != null && r.cf_professionals <= state.cfmax)) return false;
      if (state.contact && !(r.contact_email || r.team_url || r.contact_url)) return false;
      if (state.email && !r.contact_email) return false;
      return true;
    });
  }
  function sortRows(rows) {
    const [key, dir] = state.sort.split(":");
    const val = {
      name: (r) => r.name.toLowerCase(), cf_professionals: (r) => r.cf_professionals, ebitda_min: (r) => r.ebitda_min_m,
      ebitda_max: (r) => r.ebitda_max_m, hq: (r) => (r.hq || "").toLowerCase() || null, firm_type: (r) => r.firm_type_label,
      completeness: (r) => r.completeness, pitchbook_deals: (r) => (r.pitchbook || {}).deals ?? null,
    }[key] || ((r) => r.name.toLowerCase());
    const s = dir === "desc" ? -1 : 1;
    return rows.slice().sort((a, b) => {
      const x = val(a), y = val(b);
      if (x == null && y == null) return a.name.localeCompare(b.name);
      if (x == null) return 1; if (y == null) return -1;
      return (x < y ? -1 : x > y ? 1 : a.name.localeCompare(b.name)) * s;
    });
  }

  /* ---------- render ---------- */
  function renderKpis() {
    const sme = DATA.filter((r) => r.covers_sme).length;
    const contact = DATA.filter((r) => r.contact_email || r.team_url || r.contact_url).length;
    const people = DATA.reduce((s, r) => s + (r.cf_professionals || 0), 0);
    const regions = new Set(DATA.map((r) => r.hq_region).filter(Boolean)).size;
    const k = [[DATA.length, "advisers mapped"], [sme, "cover £0.5–2m EBITDA deals"], [contact, "with contact details"],
      [people.toLocaleString(), "CF professionals counted"], [regions, "head-office regions"]];
    $("kpis").innerHTML = k.map(([v, l]) => `<div class="kpi"><b>${v}</b><span>${l}</span></div>`).join("");
  }

  const pos = (v) => (Math.log10(Math.min(Math.max(v, SCALE.lo), SCALE.hi)) - Math.log10(SCALE.lo)) /
    (Math.log10(SCALE.hi) - Math.log10(SCALE.lo)) * 100;
  function sizeCell(r) {
    const band = `<div class="band" style="left:${pos(0.5)}%;width:${pos(2) - pos(0.5)}%" title="SME band £0.5–2m"></div>`;
    if (r.ebitda_min_m == null && r.ebitda_max_m == null) return `<div class="scale">${band}<span class="unk">unknown</span></div>`;
    const a = pos(r.ebitda_min_m ?? SCALE.lo), b = r.ebitda_max_m == null ? 100 : pos(r.ebitda_max_m);
    const est = r.deal_size_basis === "estimate";
    const lbl = r.ebitda_max_m == null ? `£${fmtM(r.ebitda_min_m)}m+` : r.ebitda_min_m == null ? `up to £${fmtM(r.ebitda_max_m)}m`
      : `£${fmtM(r.ebitda_min_m)}–${fmtM(r.ebitda_max_m)}m`;
    return `<div class="scale" title="${esc(r.deal_size_note || lbl)}">${band}<div class="bar${est ? " est" : ""}${r.ebitda_max_m == null ? " open-r" : ""}" ` +
      `style="left:${a}%;width:${Math.max(b - a, 1.5)}%"></div></div><div class="sizelbl">${lbl}${est ? ' <span class="est">est.</span>' : ""}</div>`;
  }
  function row(r) {
    const sectors = r.sectors.slice(0, 3).map((s) => `<span class="chip">${esc(s)}</span>`).join("") +
      (r.sectors.length > 3 ? `<span class="chip more">+${r.sectors.length - 3}</span>` : "");
    const cf = r.cf_professionals == null ? "" : r.cf_professionals + (r.cf_professionals_basis === "estimate" ? ' <span class="est">est.</span>' : "");
    return `<tr tabindex="0" data-id="${esc(r.id)}">
      <td><div class="nm">${esc(r.name)}${r.covers_sme ? '<span class="sme" title="Core deal size overlaps £0.5–2m EBITDA">SME</span>' : ""}</div>
        <div class="dom">${esc(r.domain)}</div></td>
      <td class="type hide-s">${esc(r.firm_type_label)}</td>
      <td class="hide-s">${esc(r.hq || "")}<div class="dom">${r.offices.length > 1 ? r.offices.length + " offices" : ""}</div></td>
      <td class="num hide-s">${cf}</td>
      <td>${sizeCell(r)}</td>
      <td class="hide-m">${sectors}</td></tr>`;
  }
  function render() {
    $("count").textContent = `${view.length} of ${DATA.length} advisers`;
    $("rows").innerHTML = view.slice(0, shown).map(row).join("") ||
      `<tr><td colspan="6" style="text-align:center;color:var(--muted);padding:30px">No advisers match these filters.</td></tr>`;
    $("more").innerHTML = view.length > shown ? `<button class="btn ghost" id="moreBtn">Show ${Math.min(PAGE, view.length - shown)} more</button>` : "";
    if ($("moreBtn")) $("moreBtn").onclick = () => { shown += PAGE; render(); };
  }
  function apply() { view = sortRows(filter()); shown = PAGE; render(); }
  function changed() { syncInputs(); writeHash(); apply(); }

  /* ---------- detail drawer ---------- */
  const link = (u, t) => u ? `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t || u.replace(/^https?:\/\/(www\.)?/, ""))}</a>` : "";
  function open(id) {
    const r = DATA.find((x) => x.id === id); if (!r) return;
    const basis = (b) => b ? ` <span class="est">(${b === "team_page" ? "counted on team page" : b === "deals" ? "from its deals" : b})</span>` : "";
    const ev = (r.deal_ev_min_m != null || r.deal_ev_max_m != null) ? `£${fmtM(r.deal_ev_min_m)}–${r.deal_ev_max_m == null ? "" : fmtM(r.deal_ev_max_m)}m EV` : "";
    const eb = (r.ebitda_min_m != null || r.ebitda_max_m != null) ? `£${fmtM(r.ebitda_min_m)}–${r.ebitda_max_m == null ? "" : fmtM(r.ebitda_max_m)}m EBITDA` +
      (r.deal_ebitda_min_m == null && r.deal_ebitda_max_m == null ? ` <span class="est">(from EV ÷ ${META.ev_to_ebitda_multiple})</span>` : "") : "unknown";
    const pb = r.pitchbook ? `<h3>PitchBook</h3><dl>
      <dt>Deals advised</dt><dd>${r.pitchbook.deals} (${r.pitchbook.deals_in_sme_band} in the £0.5–2m EBITDA band)</dd>
      <dt>Median deal size</dt><dd>${r.pitchbook.median_deal_size_m != null ? "£" + r.pitchbook.median_deal_size_m + "m" : "–"}</dd>
      <dt>Last deal</dt><dd>${esc(r.pitchbook.last_deal || "–")}</dd>
      <dt>Recent</dt><dd>${(r.pitchbook.recent || []).map((d) => esc(`${d.company || "?"} (${d.date || ""})`)).join("<br>")}</dd></dl>` : "";
    const dd = (label, v) => v ? `<dt>${label}</dt><dd>${v}</dd>` : "";
    $("dBody").innerHTML = `
      <h2 id="dName">${esc(r.name)}</h2>
      <div class="dom">${esc(r.firm_type_label)}${r.parent ? " · " + esc(r.parent) : ""}${r.covers_sme ? '<span class="sme">SME</span>' : ""}</div>
      <p class="lede">${esc(r.description || "")}</p>
      <div class="cta">
        ${r.website ? `<a class="btn" href="${esc(r.website)}" target="_blank" rel="noopener">Website</a>` : ""}
        ${r.team_url ? `<a class="btn ghost" href="${esc(r.team_url)}" target="_blank" rel="noopener">Team</a>` : ""}
        ${r.contact_url ? `<a class="btn ghost" href="${esc(r.contact_url)}" target="_blank" rel="noopener">Contact page</a>` : ""}
        ${r.contact_email ? `<a class="btn ghost" href="mailto:${esc(r.contact_email)}">Email</a>` : ""}
        ${r.linkedin_url ? `<a class="btn ghost" href="${esc(r.linkedin_url)}" target="_blank" rel="noopener">LinkedIn</a>` : ""}
      </div>
      <h3>Deals</h3><dl>
        ${dd("Core deal size", eb)}
        ${dd("Stated / EV", [ev, r.deal_size_note ? "“" + esc(r.deal_size_note) + "”" : ""].filter(Boolean).join("<br>") + basis(r.deal_size_basis))}
        ${dd("Services", r.services.map((s) => esc(META.services[s] || s)).join(", "))}
        ${dd("Sectors", r.sectors.map((s) => `<span class="chip">${esc(s)}</span>`).join(""))}
        ${dd("Sector focus", esc(r.sector_note || ""))}
      </dl>
      <h3>Firm</h3><dl>
        ${dd("CF professionals", r.cf_professionals != null ? r.cf_professionals + basis(r.cf_professionals_basis) : "")}
        ${dd("Head office", esc([r.hq, r.hq_region].filter(Boolean).join(", ")))}
        ${dd("Offices", esc(r.offices.join(", ")))}
        ${dd("Coverage", esc((r.coverage || "") + (r.regions_covered.length && r.regions_covered.length < 12 ? ": " + r.regions_covered.join(", ") : r.regions_covered.length === 12 ? ": all UK regions" : "")))}
      </dl>
      <h3>Contact</h3><dl>
        ${dd("Email", r.contact_email ? `<a href="mailto:${esc(r.contact_email)}">${esc(r.contact_email)}</a>` : "")}
        ${dd("Phone", r.contact_phone ? `<a href="tel:${esc(r.contact_phone.replace(/\s/g, ""))}">${esc(r.contact_phone)}</a>` : "")}
        ${dd("Team page", link(r.team_url))}
        ${dd("Contact page", link(r.contact_url))}
        ${dd("Website", link(r.website))}
      </dl>
      ${pb}
      <h3>Sources</h3><ul>${(r.sources || []).map((s) => `<li>${link(s)}</li>`).join("")}</ul>
      ${r.notes ? `<h3>Notes</h3><p>${esc(r.notes)}</p>` : ""}
      ${r.missing.length ? `<p class="missing">Not yet found: ${r.missing.map((m) => m.replace(/_/g, " ")).join(", ")}</p>` : ""}
      <p class="dom">Record ${esc(r.id)}${r.updated ? " · updated " + esc(r.updated) : ""} · <a href="v1/advisers/${esc(r.id)}" target="_blank">JSON</a></p>`;
    $("drawer").classList.add("open"); $("drawer").setAttribute("aria-hidden", "false"); $("scrim").hidden = false;
    $("dClose").focus();
  }
  function close() { $("drawer").classList.remove("open"); $("drawer").setAttribute("aria-hidden", "true"); $("scrim").hidden = true; }

  /* ---------- URL hash ---------- */
  function writeHash() {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(state)) {
      if (Array.isArray(v)) { if (v.length) p.set(k, v.join("|")); }
      else if (v !== null && v !== "" && v !== false && !(k === "sort" && v === "name")) p.set(k, v === true ? "1" : v);
    }
    history.replaceState(null, "", "#" + p.toString());
  }
  function readHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    if (![...p.keys()].length) { state.emin = 0.5; state.emax = 2; state.unknown = false; return; } // default view: SME band
    for (const k of Object.keys(state)) {
      if (!p.has(k)) { if (k === "emin" || k === "emax") state[k] = null; continue; }
      const v = p.get(k);
      if (Array.isArray(state[k])) state[k] = v.split("|").filter(Boolean);
      else if (typeof state[k] === "boolean") state[k] = v === "1";
      else if (["emin", "emax", "cfmin", "cfmax"].includes(k)) state[k] = num(v);
      else state[k] = v;
    }
  }

  /* ---------- CSV of the current view ---------- */
  function csvLines(sep) {
    const cols = META.csv_fields;
    const cell = (v) => { if (v == null) return ""; const s = Array.isArray(v) ? v.join("; ") : String(v); return /[",\n\t]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
    return [cols.join(sep)].concat(view.map((r) => cols.map((c) => cell(c === "pitchbook_deals" ? (r.pitchbook || {}).deals : r[c])).join(sep)));
  }
  // Tab-separated, so it pastes straight into Excel or Google Sheets as columns.
  function copyCsv() {
    const text = csvLines("\t").join("\n"), btn = $("copyCsv"), label = btn.textContent;
    const done = (msg) => { btn.textContent = msg; setTimeout(() => { btn.textContent = label; }, 2000); };
    navigator.clipboard.writeText(text).then(() => done("Copied " + view.length + " rows"), () => {
      const ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); done("Copied " + view.length + " rows"); } catch (e) { done("Copy blocked"); }
      ta.remove();
    });
  }
  function csv() {
    const lines = csvLines(",");
    const blob = new Blob(["﻿" + lines.join("\n")], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "uk-cf-advisers.csv"; a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  /* ---------- wire up ---------- */
  let qt;
  $("q").addEventListener("input", () => { clearTimeout(qt); qt = setTimeout(() => { state.q = $("q").value; writeHash(); apply(); }, 120); });
  for (const [id, key] of [["emin", "emin"], ["emax", "emax"], ["cfmin", "cfmin"], ["cfmax", "cfmax"]])
    $(id).addEventListener("change", () => { state[key] = num($(id).value); changed(); });
  $("unknownSize").onchange = () => { state.unknown = $("unknownSize").checked; changed(); };
  $("hasContact").onchange = () => { state.contact = $("hasContact").checked; changed(); };
  $("hasEmail").onchange = () => { state.email = $("hasEmail").checked; changed(); };
  $("sort").onchange = () => { state.sort = $("sort").value; changed(); };
  $("sizePresets").onclick = (e) => { const p = e.target.dataset.p; if (!p) return; [state.emin, state.emax] = PRESETS[p]; changed(); };
  $("reset").onclick = () => { Object.assign(state, { q: "", emin: null, emax: null, unknown: false, ft: [], region: [], hq: [], sector: [], service: [], cfmin: null, cfmax: null, contact: false, email: false, sort: "name" }); changed(); };
  $("rows").onclick = (e) => { const tr = e.target.closest("tr[data-id]"); if (tr) open(tr.dataset.id); };
  $("rows").onkeydown = (e) => { const tr = e.target.closest("tr[data-id]"); if (tr && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); open(tr.dataset.id); } };
  $("dClose").onclick = close; $("scrim").onclick = close;
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
  $("dlCsv").onclick = csv;
  $("copyCsv").onclick = copyCsv;
  // embedded builds (build-static --embed) run in frames that block downloads and service workers
  if (window.CFA_EMBED) { $("dlCsv").hidden = true; $("copyCsv").classList.remove("ghost"); }
  $("toggleFilters").onclick = () => { const o = $("filters").classList.toggle("open"); $("toggleFilters").setAttribute("aria-expanded", o); };

  let deferred;
  window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); deferred = e; $("installBtn").hidden = false; });
  $("installBtn").onclick = async () => { if (!deferred) return; deferred.prompt(); await deferred.userChoice; deferred = null; $("installBtn").hidden = true; };
  if (!window.CFA_EMBED && "serviceWorker" in navigator && location.protocol !== "file:") navigator.serviceWorker.register("sw.js").catch(() => {});

  load().catch((e) => { $("subtitle").textContent = "Could not load the data: " + e; });
})();
