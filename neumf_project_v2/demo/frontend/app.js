const API = "/api";
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (v, d = 4) => (v == null || Number.isNaN(Number(v)) ? "—" : Number(v).toFixed(d));
const num = (v) => Number(v).toLocaleString("vi-VN");
const MODEL_COLORS = {
  "NeuMF-Pretrained": "#b3261e", "NeuMF-Scratch": "#e07a5f", "GMF": "#28528f", "MLP": "#6a8fc7",
  "EarlyFusion": "#7a6c5d", "MostPopular": "#9a9a9a", "BPR-MF": "#1d7a46", "Random": "#d4d0ca",
};
const color = (m) => MODEL_COLORS[m] || "#555";

async function api(path, opts) {
  const res = await fetch(API + path, opts);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `Lỗi HTTP ${res.status}`);
  return body;
}

let CTX = null;
const inited = {};
let charts = [];

/* ------------------------------------------------------------ routing */
const VIEWS = ["home", "new", "admin", "dashboard"];
function route() {
  const v = location.hash.replace(/^#\/?/, "") || "home";
  const view = VIEWS.includes(v) ? v : "home";
  VIEWS.forEach((x) => $("view-" + x).classList.toggle("hidden", x !== view));
  document.querySelectorAll("nav a").forEach((a) => a.classList.toggle("active", a.dataset.view === view));
  if (!CTX) return;
  if (view === "new" && !inited.new) initNew();
  if (view === "admin" && !inited.admin) initAdmin();
  if (view === "dashboard") loadDashboard();
}
window.addEventListener("hashchange", route);

async function init() {
  route();
  try {
    CTX = await api("/context");
  } catch (e) {
    $("info-strip").innerHTML = `<span class="error">${esc(e.message)}</span>`;
    return;
  }
  const slice = CTX.nrows ? `${num(CTX.nrows)} dòng đầu transactions_train` : "toàn bộ transactions_train";
  $("info-strip").innerHTML = `
    <span>Dataset <b>H&amp;M</b> · lát cắt ${slice} (${CTX.date_min} → ${CTX.date_max}) · k-core ${CTX.k_core}</span>
    <span>run_tag <b>${esc(CTX.run_tag)}</b></span>
    <span><b>${num(CTX.n_users)}</b> users · <b>${num(CTX.n_items)}</b> items sau k-core</span>`;
  route();
}

/* ------------------------------------------------------------ shared UI */
const img = (it) => `<img loading="lazy" src="${API}/image/${esc(it.article_id)}" alt="${esc(it.product_type_name)}">`;
const headTag = (isHead) => (isHead ? '<span class="tag head">Head</span>' : '<span class="tag tail">Long-tail</span>');
const kOptions = (sel) => {
  sel.innerHTML = CTX.k_values.map((k) => `<option value="${k}">${k}</option>`).join("");
  sel.value = Math.max(...CTX.k_values);
};

function productCard(it, extra = "") {
  return `<div class="product">${img(it)}<div class="body">
    <div class="name">${esc(it.prod_name)}</div>
    <div class="meta">${esc(it.product_type_name)} · ${esc(it.colour_group_name)}</div>
    ${extra}</div></div>`;
}

function rowItem(it, left, right, cls = "") {
  return `<div class="row-item ${cls}">${left}${img(it)}
    <div class="txt"><div class="name" title="${esc(it.prod_name)}">${esc(it.prod_name)}</div>
      <div class="meta">${esc(it.product_type_name)} · ${esc(it.colour_group_name)}</div></div>${right}</div>`;
}

function chips(el, items, selected, onToggle) {
  el.innerHTML = items.map((x) => `<button type="button" class="chip ${selected(x.value) ? "on" : ""}" data-v="${esc(x.value)}">${esc(x.label)}${x.small ? `<small>${esc(x.small)}</small>` : ""}</button>`).join("");
  el.querySelectorAll(".chip").forEach((b) => b.addEventListener("click", () => onToggle(b.dataset.v)));
}

/* ------------------------------------------------------------ new customer */
const ob = { options: null, area: null, types: new Set(), colours: new Set() };

async function initNew() {
  inited.new = true;
  try {
    ob.options = await api("/onboarding/options");
  } catch (e) {
    $("ob-result").innerHTML = `<div class="error">${esc(e.message)}</div>`;
    return;
  }
  const o = ob.options;
  ob.area = o.areas.find((a) => a.n_items > 0)?.key;
  kOptions($("ob-k"));
  const age = $("ob-age");
  if (o.age_groups.length) {
    age.innerHTML = `<option value="">Không chọn</option>` + o.age_groups.map((g) =>
      `<option value="${g.key}">${g.label} (${num(g.n_transactions)} giao dịch train)</option>`).join("");
  } else {
    age.innerHTML = `<option value="">customers.csv không có tuổi</option>`;
    age.disabled = true;
  }
  $("ob-note").textContent =
    `Độ phổ biến = số khách mua mỗi sản phẩm trong tập TRAIN, cửa sổ tối đa ${o.popularity_window_days} ngày cuối của train ` +
    `(thực tế ${o.popularity_window[0]} → ${o.popularity_window[1]}). Lọc tuổi chỉ áp dụng khi nhóm có ≥ ${o.min_age_group_transactions} giao dịch; ` +
    `${Math.round(o.age_coverage * 100)}% giao dịch trong cửa sổ có thông tin tuổi. Không lưu thông tin của bạn.`;
  renderObForm();
  $("ob-go").addEventListener("click", runOnboarding);
}

function renderObForm() {
  const o = ob.options;
  const area = o.areas.find((a) => a.key === ob.area);
  chips($("ob-area"), o.areas.map((a) => ({ value: a.key, label: a.label, small: `${a.index_group_names.join(", ")} · ${a.n_items} sp` })),
    (v) => v === ob.area, (v) => { ob.area = v; ob.types.clear(); ob.colours.clear(); renderObForm(); });
  const toggle = (set) => (v) => { set.has(v) ? set.delete(v) : set.add(v); renderObForm(); };
  chips($("ob-types"), (area?.product_groups || []).map((v) => ({ value: v, label: v })), (v) => ob.types.has(v), toggle(ob.types));
  chips($("ob-colours"), (area?.colours || []).map((v) => ({ value: v, label: v })), (v) => ob.colours.has(v), toggle(ob.colours));
}

async function runOnboarding() {
  const btn = $("ob-go");
  btn.disabled = true;
  try {
    const res = await api("/onboarding/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        area: ob.area, product_groups: [...ob.types], colours: [...ob.colours],
        age_group: $("ob-age").value || null, k: Number($("ob-k").value),
      }),
    });
    const notices = [
      ...res.relaxations.map((r) => `<div class="missing">Không đủ sản phẩm khớp lựa chọn — ${esc(r.toLowerCase())}.</div>`),
      ...res.notes.map((n) => `<div class="banner" style="margin:0;font-weight:500">${esc(n)}</div>`),
    ].join("");
    const card = (it) => productCard(it, `
      <div><span class="tag rule">Rule-based</span> ${it.relax_level ? `<span class="tag relax">${esc(it.match)}</span>` : ""}</div>
      <div class="reason">${esc(it.reason)}</div><div class="meta">${esc(it.detail)}</div>`);
    $("ob-result").innerHTML = `
      <div class="section-block"><h2>Hợp sở thích của bạn</h2><div class="notice-list">${notices}</div>
        <div class="grid-products">${res.preferred.map(card).join("") || '<div class="note">Không có sản phẩm nào có lượt mua trong khu vực này.</div>'}</div></div>
      <div class="section-block"><h2>Đang hot trong khu vực bạn chọn (${esc(res.area)})</h2>
        <div class="grid-products">${res.hot_in_area.map(card).join("") || '<div class="note">Không còn sản phẩm nào khác.</div>'}</div></div>`;
  } catch (e) {
    $("ob-result").innerHTML = `<div class="error" style="margin-top:16px">${esc(e.message)}</div>`;
  } finally {
    btn.disabled = false;
  }
}

/* ------------------------------------------------------------ admin */
const ad = { bucket: null, user: null, buckets: null };

async function initAdmin() {
  inited.admin = true;
  const [a, b] = [$("ad-model-a"), $("ad-model-b")];
  const opts = CTX.models.map((m) => `<option>${m}</option>`).join("");
  a.innerHTML = opts;
  b.innerHTML = opts;
  a.value = CTX.models.includes("NeuMF-Pretrained") ? "NeuMF-Pretrained" : CTX.models[0];
  b.value = CTX.models.includes("GMF") ? "GMF" : CTX.models[1] || CTX.models[0];
  kOptions($("ad-k"));
  const un = Object.entries(CTX.unavailable_models || {});
  $("ad-unavailable").innerHTML = un.map(([m, r]) => `<b>${esc(m)}</b> bị ẩn: ${esc(r)}`).join("<br>");

  ad.buckets = await api("/users/buckets");
  const [t1, t2] = ad.buckets.thresholds;
  const range = { low: `≤ ${t1}`, mid: `${t1} < n ≤ ${t2}`, high: `> ${t2}` };
  const renderBuckets = () => chips($("ad-bucket"),
    [{ value: "", label: "Tất cả" }, ...ad.buckets.buckets.map((x) => ({ value: x.key, label: x.label, small: `${range[x.key]} · ${x.n_users} user` }))],
    (v) => v === (ad.bucket || ""), (v) => { ad.bucket = v || null; renderBuckets(); });
  renderBuckets();

  let timer;
  $("ad-search").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(suggest, 250); });
  $("ad-search").addEventListener("keydown", (e) => { if (e.key === "Enter") selectUser($("ad-search").value.trim()); });
  $("ad-random").addEventListener("click", async () => {
    try {
      const u = await api(`/users/random${ad.bucket ? `?bucket=${ad.bucket}` : ""}`);
      selectUser(u.customer_id);
    } catch (e) { showAdminError(e); }
  });
  $("ad-compare").addEventListener("change", () => { b.disabled = !$("ad-compare").checked; loadAdmin(); });
  [a, b, $("ad-k")].forEach((el) => el.addEventListener("change", loadAdmin));
}

async function suggest() {
  const q = $("ad-search").value.trim();
  const box = $("ad-suggest");
  if (!q) { box.classList.add("hidden"); return; }
  const rows = await api(`/users/search?q=${encodeURIComponent(q)}&limit=15${ad.bucket ? `&bucket=${ad.bucket}` : ""}`).catch(() => []);
  box.innerHTML = rows.map((r) => `<div data-id="${r.customer_id}">${r.customer_id.slice(0, 24)}… · ${r.train_count} giao dịch train</div>`).join("")
    || `<div>Không có user có test item khớp tiền tố này.</div>`;
  box.classList.remove("hidden");
  box.querySelectorAll("[data-id]").forEach((d) => d.addEventListener("click", () => selectUser(d.dataset.id)));
}

function selectUser(cid) {
  if (!cid) return;
  ad.user = cid;
  $("ad-search").value = cid;
  $("ad-suggest").classList.add("hidden");
  loadAdmin();
}

function showAdminError(e) {
  $("ad-grid").classList.add("hidden");
  $("ad-empty").classList.remove("hidden");
  $("ad-empty").innerHTML = `<div class="error">${esc(e.message)}</div>`;
}

async function loadAdmin() {
  if (!ad.user) return;
  const k = $("ad-k").value;
  const models = [$("ad-model-a").value];
  if ($("ad-compare").checked && $("ad-model-b").value !== models[0]) models.push($("ad-model-b").value);
  const uid = encodeURIComponent(ad.user);
  try {
    const [hist, ...recs] = await Promise.all([
      api(`/users/${uid}/history`),
      ...models.map((m) => api(`/users/${uid}/recommend?model=${encodeURIComponent(m)}&k=${k}`)),
    ]);
    $("ad-empty").classList.add("hidden");
    $("ad-grid").classList.remove("hidden");
    renderHistory(hist);
    renderRecs(recs, k);
    renderAnswer(recs, hist);
  } catch (e) { showAdminError(e); }
}

function renderHistory(hist) {
  $("ad-history").innerHTML = `<div class="note" style="margin-bottom:8px">${hist.items.length} sản phẩm trong train, sắp theo ngày mua.</div>` +
    hist.items.map((it) => rowItem(it, "", `<div class="score">${it.t_dat}${it.interaction_count > 1 ? `<br>×${it.interaction_count}` : ""}<br>${headTag(it.is_head)}</div>`)).join("");
}

function renderRecs(recs, k) {
  $("ad-recs-title").textContent = `Top-${k} gợi ý`;
  const wrap = $("ad-recs");
  wrap.classList.toggle("compare", recs.length > 1);
  wrap.innerHTML = recs.map((r) => {
    const hit = r.items.some((it) => it.is_test_item);
    return `<div>
      <h3 style="color:${color(r.model)}">${esc(r.model)}</h3>
      ${r.items.map((it) => rowItem(it, `<div class="rank">#${it.rank}</div>`,
        `<div class="score">${r.score_kind === "logit" ? "logit" : "lượt mua"} ${fmt(it.score, r.score_kind === "logit" ? 3 : 0)}<br>${headTag(it.is_head)}${it.is_test_item ? '<br><span class="tag tail">TEST ITEM</span>' : ""}</div>`,
        it.is_test_item ? "hit" : "")).join("")}
      <div class="note" style="margin-top:8px">${hit ? "Test item nằm trong top-K (tô xanh)." : `Test item không có trong top-${k} (rank ${r.evaluation.rank}).`}</div>
    </div>`;
  }).join("");
}

function renderAnswer(recs, hist) {
  const t = recs[0].test_item;
  const v = recs[0].val_item;
  const blocks = recs.map((r) => {
    const e = r.evaluation;
    const rows = CTX.k_values.map((k) => `<tr><td>K = ${k}</td><td>${fmt(e.metrics[`HR@${k}`], 0)}</td><td>${fmt(e.metrics[`NDCG@${k}`])}</td></tr>`).join("");
    return `<div class="eval-block"><h3 style="color:${color(r.model)}">${esc(r.model)}</h3>
      <dl class="kv"><dt>Rank test item</dt><dd>${num(e.rank)} / ${num(e.n_candidates)}</dd>
      <dt>Số candidates</dt><dd>${num(e.n_candidates)}</dd></dl>
      <table style="margin-top:8px"><tr><th></th><th>Hit@K</th><th>NDCG@K</th></tr>${rows}</table></div>`;
  }).join("");
  $("ad-answer").innerHTML = `
    <div class="cid" style="margin-bottom:8px">${esc(ad.user)}</div>
    <h3>Test item (giao dịch cuối, bị giấu khỏi train)</h3>
    ${rowItem(t, "", `<div class="score">${headTag(t.is_head)}</div>`, "hit")}
    ${v ? `<div class="note" style="margin:8px 0 14px">Validation item (dùng cho early stopping, cũng bị loại khỏi candidates): ${esc(v.prod_name)} — ${esc(v.product_type_name)}</div>` : ""}
    <div class="note" style="margin-bottom:10px">Candidates = ${num(CTX.n_items)} item − ${hist.items.length} item train − ${v ? 1 : 0} item validation.</div>
    ${blocks}`;
}

/* ------------------------------------------------------------ dashboard */
function srcLine(block) {
  return `<div class="source">Nguồn: ${esc(block.source)}${block.run_tag ? ` · run_tag ${esc(block.run_tag)}` : ""}</div>`;
}
function body(block, render) {
  return block.status === "ok" ? render(block.data) + srcLine(block) : `<div class="missing">${esc(block.message)}</div>`;
}
function metricTable(rows, cols, digits = 4) {
  const best = Object.fromEntries(cols.map((c) => [c, Math.max(...rows.map((r) => Number(r[c])).filter((x) => !Number.isNaN(x)))]));
  return `<table><tr><th>Model</th>${cols.map((c) => `<th>${esc(c)}</th>`).join("")}</tr>${rows.map((r) =>
    `<tr><td>${esc(r.model)}</td>${cols.map((c) => `<td class="${Number(r[c]) === best[c] ? "best" : ""}">${fmt(r[c], digits)}</td>`).join("")}</tr>`).join("")}</table>`;
}
function chart(id, config) {
  const el = $(id);
  if (el) charts.push(new Chart(el, config));
}

async function loadDashboard() {
  charts.forEach((c) => c.destroy());
  charts = [];
  const dash = $("dash");
  dash.innerHTML = '<div class="note">Đang đọc file kết quả...</div>';
  let d;
  try { d = await api("/dashboard"); } catch (e) { dash.innerHTML = `<div class="error">${esc(e.message)}</div>`; return; }
  const metricCols = CTX.k_values.flatMap((k) => [`HR@${k}`, `NDCG@${k}`]);

  dash.innerHTML = `
    <div class="card wide"><h2>Thống kê dữ liệu (sau k-core)</h2>${body(d.stats, (s) => `<div class="stats">${[
      ["Users", num(s.n_users)], ["Items", num(s.n_items)], ["Interactions", num(s.n_interactions)],
      ["Độ thưa", `${(100 * (1 - s.density)).toFixed(3)}%`], ["Train", num(s.train)], ["Validation", num(s.validation)],
      ["Test", num(s.test)], ["k-core", s.k_core], ["Head items (10%)", num(s.n_head_items)],
    ].map(([l, n]) => `<div class="stat"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("")}</div>`)}</div>

    <div class="card wide"><h2>HR@K / NDCG@K — full ranking (1 run)</h2>${body(d.primary, (rows) =>
      `<canvas id="c-primary"></canvas>${metricTable(rows, metricCols)}`)}
      <h2 style="margin-top:20px">Multi-seed (mean ± std)</h2>${body(d.multi_seed, (m) => `<div class="note">${m.seeds.length} seed: ${m.seeds.join(", ")}</div>
        <table><tr><th>Model</th>${metricCols.map((c) => `<th>${c}</th>`).join("")}</tr>${m.rows.map((r) =>
          `<tr><td>${esc(r.model)}</td>${metricCols.map((c) => `<td>${fmt(r[c + "_mean"])} ± ${fmt(r[c + "_std"])}</td>`).join("")}</tr>`).join("")}</table>`)}</div>

    <div class="card wide"><h2>Phân phối rank của test item</h2>${body(d.rank_distribution, (r) =>
      `<canvas id="c-rank"></canvas><div class="note">Bin theo thang log của rank (1, 2, 3–4, 5–10, ...). Không vẽ histogram HR per-user vì giá trị chỉ là 0/1.</div>
       <table style="margin-top:8px"><tr><th>Model</th><th>Median rank</th><th>Số test user</th></tr>${Object.entries(r.series).map(([m, s]) =>
         `<tr><td>${esc(m)}</td><td>${num(s.median_rank)}</td><td>${num(s.n_users)}</td></tr>`).join("")}</table>`)}</div>

    <div class="card"><h2>Beyond-accuracy</h2>${body(d.beyond, (rows) =>
      `<canvas id="c-beyond"></canvas>${metricTable(rows.map((r) => ({ ...r, Coverage: r.coverage, Novelty: r.novelty, "Head Rec Rate": r.head_rec_rate })), ["Coverage", "Novelty", "Head Rec Rate"])}
       <div class="note">Head Rec Rate cao = gợi ý tập trung vào 10% item phổ biến nhất trong train.</div>`)}</div>

    <div class="card"><h2>Popularity bias — top 20 item được gợi ý nhiều nhất</h2>${body(d.popularity_bias, (rows) => {
      const models = [...new Set(rows.map((r) => r.model))];
      return `<select id="pb-model">${models.map((m) => `<option ${m === "NeuMF-Pretrained" ? "selected" : ""}>${esc(m)}</option>`).join("")}</select>
        <div class="note" style="margin:6px 0">Đếm trong top-${rows[0]?.top_k} của toàn bộ test user; so với số lượt mua trong train.</div><div id="pb-table"></div>`;
    })}</div>`;

  if (d.primary.status === "ok") {
    const rows = d.primary.data;
    chart("c-primary", {
      type: "bar",
      data: { labels: rows.map((r) => r.model), datasets: metricCols.map((c, i) => ({ label: c, data: rows.map((r) => r[c]), backgroundColor: ["#e3b5a4", "#b3261e", "#a9bfdf", "#28528f"][i % 4] })) },
      options: { plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true } } },
    });
  }
  if (d.rank_distribution.status === "ok") {
    const r = d.rank_distribution.data;
    chart("c-rank", {
      type: "bar",
      data: { labels: r.bins, datasets: Object.entries(r.series).map(([m, s]) => ({ label: m, data: s.counts, backgroundColor: color(m) })) },
      options: { plugins: { legend: { position: "bottom" } }, scales: { x: { title: { display: true, text: "rank của test item (bin log)" } }, y: { title: { display: true, text: "số test user" } } } },
    });
  }
  if (d.beyond.status === "ok") {
    const rows = d.beyond.data;
    chart("c-beyond", {
      type: "bar",
      data: { labels: rows.map((r) => r.model), datasets: [
        { label: "Coverage", data: rows.map((r) => r.coverage), backgroundColor: "#28528f" },
        { label: "Head Rec Rate", data: rows.map((r) => r.head_rec_rate), backgroundColor: "#b3261e" },
      ] },
      options: { plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: true, max: 1 } } },
    });
  }
  if (d.popularity_bias.status === "ok") {
    const rows = d.popularity_bias.data;
    const render = () => {
      const m = $("pb-model").value;
      $("pb-table").innerHTML = `<div class="scroll" style="max-height:420px"><table><tr><th>#</th><th>Sản phẩm</th><th>% test user</th><th>Lượt mua train</th><th>Hạng phổ biến train</th></tr>${rows.filter((r) => r.model === m).map((r) =>
        `<tr><td>${r.position}</td><td style="text-align:left">${esc(r.prod_name)} <span class="meta">(${esc(r.product_type_name)})</span> ${headTag(r.is_head)}</td>
         <td>${(100 * r.share_of_test_users).toFixed(1)}%</td><td>${num(r.train_count)}</td><td>${num(r.train_popularity_rank)}</td></tr>`).join("")}</table></div>`;
    };
    $("pb-model").addEventListener("change", render);
    render();
  }
}

init();
