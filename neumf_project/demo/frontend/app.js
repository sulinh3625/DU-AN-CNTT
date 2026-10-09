const API = "/api";
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (v, d = 4) => (v == null || Number.isNaN(Number(v)) ? "—" : Number(v).toFixed(d));
const num = (v) => Number(v).toLocaleString("vi-VN");
const MODEL_COLORS = {
  "NeuMF-Pretrained": "#b3261e", "NeuMF-Scratch": "#e07a5f", "GMF": "#28528f", "MLP": "#6a8fc7",
  "MostPopular": "#9a9a9a", "BPR-MF": "#1d7a46", "Random": "#d4d0ca",
  "LateFusion-GMF-MLP": "#7b4fa3", "LateFusion-BPR-MLP": "#a97fd0", "ItemKNN": "#b07d12", "UserKNN": "#d9a425",
  // Giao thức v2
  "NeuMF-F": "#2a78d6", "GMF-F": "#5b9be6", "MLP-F": "#173f7a", "LateFusion-F": "#7b4fa3", "NeuMF": "#e07a5f",
  "MostPopular-Recent": "#6b6b6b", "Content": "#1baf7a",
};
const SHOW = { "MostPopular": "Most Popular", "LateFusion-GMF-MLP": "Late Fusion GMF + MLP", "LateFusion-BPR-MLP": "Late Fusion BPR-MF + MLP" };
const show = (m) => SHOW[m] || m;
// Chế độ đánh giá cuối: "final" (giao thức v1) hoặc "v2" (kết quả chính) — nhiều sản phẩm đích mỗi khách, ứng viên theo pool.
const isV2 = () => CTX && CTX.mode === "v2";
const isFinal = () => CTX && (CTX.mode === "final" || CTX.mode === "v2");
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
const VIEWS = ["admin", "dashboard"];
function route() {
  const v = location.hash.replace(/^#\/?/, "");
  const view = VIEWS.includes(v) ? v : "admin";
  VIEWS.forEach((x) => $("view-" + x).classList.toggle("hidden", x !== view));
  document.querySelectorAll("nav a").forEach((a) => a.classList.toggle("active", a.dataset.view === view));
  if (!CTX) return;
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
  const slice = CTX.nrows ? `lát cắt ${num(CTX.nrows)} dòng đầu transactions_train`
    : /hm500k/.test(CTX.config || "") ? "mẫu hm500k theo khách hàng" : "toàn bộ transactions_train";
  const run = isV2()
    ? `<span>Mô hình của <b>đánh giá cuối giao thức v2</b> (${CTX.dry_run ? "bản chạy thử trên mẫu A" : "mẫu kiểm định B"}, seed ${esc(CTX.run_tag.replace("v2_seed", ""))}, commit ${esc(CTX.commit)}) · ứng viên gồm cả ${num(CTX.n_new_items)} sản phẩm mới</span>`
    : isFinal()
    ? `<span>Mô hình của <b>đánh giá cuối</b> (outputs/final/seed${esc(CTX.run_tag.replace("final_seed", ""))}, commit ${esc(CTX.commit)}) · chia theo mốc thời gian chung</span>`
    : `<span>run_tag <b>${esc(CTX.run_tag)}</b> (khám phá, leave-one-out)</span>`;
  $("info-strip").innerHTML = `
    <span>Dataset <b>H&amp;M</b> · ${slice} (${CTX.date_min} → ${CTX.date_max}) · k-core ${CTX.k_core}</span>
    ${run}
    <span><b>${num(CTX.n_users)}</b> users · <b>${num(CTX.n_items)}</b> items sau k-core</span>`;
  route();
}

/* ------------------------------------------------------------ shared UI */
const img = (it) => `<img loading="lazy" src="${API}/image/${esc(it.article_id)}" alt="${esc(it.product_type_name)}">`;
const headTag = (isHead) => (isHead ? '<span class="tag head">Head</span>' : '<span class="tag tail">Long-tail</span>');
// Sản phẩm mới (giao thức v2): chưa từng bán trước mốc dự đoán — mô hình chỉ dùng ID không chấm được.
const itemTag = (it) => (it.is_new ? '<span class="tag new">Mới</span>' : headTag(it.is_head));
const kOptions = (sel) => {
  sel.innerHTML = CTX.k_values.map((k) => `<option value="${k}">${k}</option>`).join("");
  sel.value = Math.max(...CTX.k_values);
};

function rowItem(it, left, right, cls = "") {
  return `<div class="row-item ${cls}">${left}${img(it)}
    <div class="txt"><div class="name" title="${esc(it.prod_name)}">${esc(it.prod_name)}</div>
      <div class="meta">${esc(it.product_type_name)} · ${esc(it.colour_group_name)}</div></div>${right}</div>`;
}

/* ------------------------------------------------------------ admin */
// Item đích = tập mà run đã chấm. Chế độ final: các sản phẩm khách mua lần đầu trong giai đoạn test (có thể nhiều).
// Chế độ explore: validation (run chưa --final, test bị khoá) hoặc test.
const targetLabel = () => (isFinal() ? "sản phẩm đích (test)" : CTX.evaluated_on === "test" ? "test item" : "validation item");

function renderProtocol() {
  const k = Math.max(...CTX.k_values);
  if (isV2()) {
    $("ad-protocol").innerHTML = `<b>Giao thức v2 (đúng Chương 4)</b><br>
    • <b>Chia theo mốc thời gian</b>: mô hình đã được huấn luyện lại trên mọi cặp trước ${esc(CTX.test_start)}; lịch sử bên trái là đúng dữ liệu mô hình đã học.<br>
    • <b>Sản phẩm đích</b> = mọi sản phẩm khách mua <i>lần đầu</i> sau mốc (có thể nhiều món), gồm cả <span class="tag new">Mới</span> sản phẩm chưa từng bán trước mốc.<br>
    • <b>Full ranking</b> trên ${num(CTX.n_candidates)} ứng viên = sản phẩm cũ (có dữ liệu huấn luyện) ∪ ${num(CTX.n_new_items)} sản phẩm mới, trừ những món khách đã mua. Mô hình chỉ dùng ID (NeuMF, GMF, MLP, BPR-MF, KNN, Most Popular) xếp sản phẩm mới cuối danh sách; NeuMF-F, GMF-F, MLP-F, LateFusion-F và Content chấm được sản phẩm mới nhờ đặc trưng.<br>
    • <code>HR@K = 1</code> nếu có ít nhất một món đích trong top-K; <code>Recall@K</code> = số món đích trong top-K / số món đích; <code>NDCG@K = DCG/IDCG</code>.<br>
    • Số trên màn hình khớp file per-user của đánh giá cuối (seed 42); đây là hiển thị lại, không phải một lần chấm mới.`;
    return;
  }
  $("ad-protocol").innerHTML = isFinal() ? `<b>Protocol đánh giá (đúng Chương 4)</b><br>
    • <b>Chia theo một mốc thời gian chung</b>: train &lt; ${esc(CTX.val_start)} ≤ validation &lt; ${esc(CTX.test_start)} ≤ test. Mô hình đã được huấn luyện lại trên train ∪ validation; lịch sử bên trái là đúng dữ liệu mô hình đã học.<br>
    • <b>Sản phẩm đích</b> = mọi sản phẩm khách mua <i>lần đầu</i> trong giai đoạn test (có thể nhiều món).<br>
    • <b>Full ranking</b>: chấm toàn bộ ${num(CTX.n_candidates)} sản phẩm có trong train ∪ validation, trừ những món khách đã mua.<br>
    • <code>HR@K = 1</code> nếu có ít nhất một món đích trong top-K; <code>Recall@K</code> = số món đích trong top-K / số món đích; <code>NDCG@K = DCG/IDCG</code>.<br>
    • Số trên màn hình khớp file per-user của đánh giá cuối; đây là hiển thị lại, không phải một lần chấm mới.`
    : `<b>Protocol đánh giá (run khám phá)</b><br>
    • <b>Temporal leave-one-out</b>: với mỗi khách, giao dịch cuối theo thời gian là <i>test item</i>, giao dịch áp chót là <i>validation item</i>, phần còn lại là train. Test item bị giấu khỏi train.<br>
    • <b>Full ranking</b>: mô hình chấm điểm toàn bộ item trong catalog, trừ các item khách đã mua; item đích được xếp hạng trong tập candidates đó.<br>
    • <b>Item đích</b> = đúng tập mà run đã chấm: <i>validation item</i> nếu run chưa <code>--final</code> (khoá test), <i>test item</i> nếu run đã chấm test.<br>
    • <code>HR@K = 1[rank ≤ K]</code>; <code>NDCG@K = 1/log2(rank+1)</code> nếu rank ≤ K, ngược lại 0 (K tối đa ${k}).`;
}
// ------------------------------------------------------------ chọn khách
// Tham khảo: thanh khách + bảng chọn mở bằng Ctrl K (kiểu bảng lệnh của Linear / Vercel), danh sách có ô lọc, tab
// nhóm và avatar (SelectPanel của GitHub Primer, resource index của Shopify Polaris).
const ad = { user: null, prev: null, next: null, facets: null, seq: 0 };
const pk = { q: "", bucket: "", area: "", hit: "", sort: "train_desc", items: [], total: 0, view: [], active: -1,
  loading: false, seq: 0, timer: null, loadedQ: null };
const BUCKET_SHORT = { low: "Ít giao dịch", mid: "Trung bình", high: "Nhiều giao dịch" };
const AREA_VI = { "Ladieswear": "Đồ nữ", "Menswear": "Đồ nam", "Divided": "Divided", "Baby/Children": "Trẻ em", "Sport": "Thể thao" };
const areaLabel = (a) => AREA_VI[a] || a;
const SORT_LABELS = { train_desc: "Mua nhiều nhất", train_asc: "Mua ít nhất", targets_desc: "Nhiều món đích nhất",
  rank: "Mô hình xếp món đích cao nhất", id: "Theo customer_id" };
// Lọc / sắp theo kết quả gợi ý cần chấm mọi khách với mô hình đang chọn (lần đầu mỗi mô hình mất vài giây).
const needsRanks = () => Boolean(pk.hit) || pk.sort === "rank";
const COPY_ICON = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>';

// Avatar chữ cái: màu cố định theo customer_id (băm chuỗi), hai ký tự đầu của mã.
const hue = (cid) => [...cid].reduce((h, ch) => (h * 31 + ch.charCodeAt(0)) % 360, 7);
const avatar = (cid, cls = "") => `<span class="avatar ${cls}" style="--h:${hue(cid)}" aria-hidden="true">${esc(cid.slice(0, 2).toUpperCase())}</span>`;
// customer_id dài: hiện đầu…cuối; khi đang tìm thì hiện đoạn quanh chỗ khớp và tô đậm phần khớp.
function idHtml(cid, q = "") {
  const p = q ? cid.toLowerCase().indexOf(q.toLowerCase()) : -1;
  if (p < 0) return `${esc(cid.slice(0, 12))}…${esc(cid.slice(-6))}`;
  const s = Math.max(0, p - 6), e = Math.min(cid.length, p + q.length + 8);
  return `${s ? "…" : ""}${esc(cid.slice(s, p))}<mark>${esc(cid.slice(p, p + q.length))}</mark>${esc(cid.slice(p + q.length, e))}${e < cid.length ? "…" : ""}`;
}
const userMeta = (r) => [`${num(r.train_count)} món đã mua`, `${num(r.n_targets)} món đích`,
  r.area && areaLabel(r.area), r.age != null && `${Math.round(r.age)} tuổi`].filter(Boolean).join(" · ");
const filterParams = (extra = {}) => {
  const p = new URLSearchParams({ sort: pk.sort, model: $("ad-model-a").value, k: $("ad-k").value, ...extra });
  if (pk.q) p.set("q", pk.q);
  if (pk.bucket) p.set("bucket", pk.bucket);
  if (pk.area) p.set("area", pk.area);
  if (pk.hit) p.set("hit", pk.hit);
  return p;
};

// Khách xem gần đây (theo từng chế độ / run), chỉ lưu trong trình duyệt.
const recentKey = () => `demo.recent.${CTX.run_tag}`;
function recentUsers() {
  try { return JSON.parse(localStorage.getItem(recentKey())) || []; } catch { return []; }
}
function rememberUser(row) {
  const list = [row, ...recentUsers().filter((r) => r.customer_id !== row.customer_id)].slice(0, 5);
  try { localStorage.setItem(recentKey(), JSON.stringify(list)); } catch { /* trình duyệt chặn lưu: bỏ qua */ }
}

async function initAdmin() {
  inited.admin = true;
  const [a, b] = [$("ad-model-a"), $("ad-model-b")];
  renderProtocol();
  if (isFinal()) $("ad-history-title").textContent = "Lịch sử mua (train ∪ validation)";
  const ext = new Set(CTX.extension_models || []);
  const opts = CTX.models.map((m) => `<option value="${esc(m)}">${esc(show(m))}${ext.has(m) ? " (mở rộng)" : ""}</option>`).join("");
  a.innerHTML = opts;
  b.innerHTML = opts;
  const pick = (prefs, fallback) => prefs.find((m) => CTX.models.includes(m)) || fallback;
  a.value = pick(["NeuMF-F", "NeuMF-Pretrained"], CTX.models[0]);
  b.value = pick(isV2() ? ["NeuMF", "BPR-MF"] : ["GMF"], CTX.models[1] || CTX.models[0]);
  kOptions($("ad-k"));
  const un = Object.entries(CTX.unavailable_models || {});
  $("ad-unavailable").innerHTML = un.map(([m, r]) => `<b>${esc(m)}</b> bị ẩn: ${esc(r)}`).join("<br>");
  $("ad-compare").addEventListener("change", () => { b.disabled = !$("ad-compare").checked; loadAdmin(); });
  [a, b, $("ad-k")].forEach((el) => el.addEventListener("change", loadAdmin));
  [a, $("ad-k")].forEach((el) => el.addEventListener("change", () => {  // lọc trúng / trượt theo mô hình A và K
    if (!needsRanks()) return;
    pk.loadedQ = null;  // mở bảng chọn lần sau thì tải lại danh sách
    if (ad.user) loadPosition();
  }));

  renderCustomerEmpty();
  $("pk-sort").innerHTML = Object.entries(SORT_LABELS).map(([v, l]) => `<option value="${v}">${l}</option>`).join("");
  $("pk-sort").addEventListener("change", () => { pk.sort = $("pk-sort").value; loadUsers(); });
  $("pk-q").addEventListener("input", () => {
    pk.q = $("pk-q").value.trim();
    clearTimeout(pk.timer);
    pk.timer = setTimeout(() => loadUsers(), 150);
  });
  $("pk-q").addEventListener("keydown", onPickerKey);
  const list = $("pk-list");
  list.addEventListener("click", (e) => { const el = e.target.closest(".pk-item"); if (el) pickUser(pk.view[+el.dataset.i]); });
  list.addEventListener("mousemove", (e) => {
    const el = e.target.closest(".pk-item");
    if (el && +el.dataset.i !== pk.active) { pk.active = +el.dataset.i; paintActive(false); }
  });
  list.addEventListener("scroll", () => { if (list.scrollTop + list.clientHeight > list.scrollHeight - 160) loadMore(); });
  $("picker").addEventListener("click", (e) => { if (e.target === $("picker")) $("picker").close(); });  // bấm ra nền
  $("picker").addEventListener("close", () => { if (ad.user) loadPosition(); });  // bộ lọc có thể đã đổi
  $("cust-open").addEventListener("click", openPicker);
  $("cust-random").addEventListener("click", async () => {
    try { selectUser((await api(`/users/random?${filterParams()}`)).customer_id); } catch (e) { showAdminError(e); }
  });
  $("cust-prev").addEventListener("click", () => ad.prev && selectUser(ad.prev.customer_id));
  $("cust-next").addEventListener("click", () => ad.next && selectUser(ad.next.customer_id));
  document.addEventListener("keydown", onAdminKey);

  try {
    ad.facets = await api("/users/facets");
    renderFilters();
  } catch (e) { showAdminError(e); }

  // Mở thẳng một khách (dùng khi chụp ảnh minh hoạ): ?user=<customer_id>&compare=1&a=<mô hình>&b=<mô hình>#admin
  const params = new URLSearchParams(location.search);
  if (CTX.models.includes(params.get("a"))) a.value = params.get("a");
  if (CTX.models.includes(params.get("b"))) b.value = params.get("b");
  if (params.get("compare") === "1") { $("ad-compare").checked = true; b.disabled = false; }
  if (params.get("user")) selectUser(params.get("user"));
}

// Ctrl K: mở / đóng bảng chọn; "/": mở; ← →: khách trước / sau (khi không gõ trong ô nhập).
function onAdminKey(e) {
  if ($("view-admin").classList.contains("hidden")) return;
  const dlg = $("picker");
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    if (dlg.open) dlg.close(); else openPicker();
    return;
  }
  if (dlg.open || e.ctrlKey || e.metaKey || e.altKey || /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement?.tagName)) return;
  if (e.key === "/") { e.preventDefault(); openPicker(); }
  else if (e.key === "ArrowLeft" && ad.prev) selectUser(ad.prev.customer_id);
  else if (e.key === "ArrowRight" && ad.next) selectUser(ad.next.customer_id);
}

async function onPickerKey(e) {
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    e.preventDefault();
    if (!pk.view.length) return;
    pk.active = Math.max(0, Math.min(pk.view.length - 1, pk.active + (e.key === "ArrowDown" ? 1 : -1)));
    paintActive();
    if (pk.active >= pk.view.length - 4) loadMore();
  } else if (e.key === "Enter") {
    e.preventDefault();
    if (pk.loadedQ !== pk.q) { clearTimeout(pk.timer); await loadUsers(); }  // dán mã rồi Enter ngay
    if (pk.view[pk.active]) pickUser(pk.view[pk.active]);
  }
}

function openPicker() {
  const dlg = $("picker");
  if (!dlg.open) dlg.showModal();
  $("pk-q").select();
  if (ad.facets) renderFilters();  // nhãn "theo <mô hình> · top-K" theo lựa chọn hiện tại
  if (pk.loadedQ === null) loadUsers(); else renderPicker();  // vẽ lại: "đang xem", gần đây
}

function seg(el, items, current, onPick) {
  el.innerHTML = items.map((x) => `<button type="button" data-v="${esc(x.value)}" aria-pressed="${x.value === current}"${x.title ? ` title="${esc(x.title)}"` : ""}>${esc(x.label)}${x.n != null ? `<span class="n">${num(x.n)}</span>` : ""}</button>`).join("");
  el.querySelectorAll("button").forEach((btn) => btn.addEventListener("click", () => onPick(btn.dataset.v)));
}

function renderFilters() {
  const f = ad.facets;
  const [lo, hi] = f.thresholds.map(Math.floor);
  const range = { low: `≤ ${lo}`, mid: `${lo + 1}–${hi}`, high: `≥ ${hi + 1}` };
  seg($("pk-bucket"), [{ value: "", label: "Tất cả", n: f.total },
    ...f.buckets.map((x) => ({ value: x.key, label: `${x.label} (${range[x.key]} món)`, n: x.n_users }))],
  pk.bucket, (v) => { pk.bucket = v; renderFilters(); loadUsers(); });
  seg($("pk-area"), [{ value: "", label: "Mọi khu vực" },
    ...f.areas.map((x) => ({ value: x.key, label: areaLabel(x.key), n: x.n_users, title: `Mua nhiều nhất ở ${x.key}` }))],
  pk.area, (v) => { pk.area = v; renderFilters(); loadUsers(); });
  const k = $("ad-k").value;
  seg($("pk-hit"), [{ value: "", label: "Mọi kết quả" },
    { value: "hit", label: "Gợi ý trúng", title: `Có ít nhất một món đích trong top-${k}` },
    { value: "miss", label: "Gợi ý trượt", title: `Không có món đích nào trong top-${k}` }],
  pk.hit, (v) => { pk.hit = v; renderFilters(); loadUsers(); });
  $("pk-hit-note").textContent = `theo ${show($("ad-model-a").value)} · top-${k} (đổi ở ô Mô hình / K)`;
}

async function loadUsers(more = false) {
  const seq = ++pk.seq;
  const q = pk.q;
  pk.loading = true;
  const slow = setTimeout(() => {  // chấm mọi khách lần đầu với một mô hình mất vài giây
    if (seq === pk.seq && !more) {
      $("pk-list").innerHTML = `<div class="pk-empty">${needsRanks()
        ? `Đang chấm mọi khách với <b>${esc(show($("ad-model-a").value))}</b>… (lần đầu với mỗi mô hình mất khoảng 5–15 giây)`
        : "Đang tải…"}</div>`;
    }
  }, 400);
  try {
    const res = await api(`/users/search?${filterParams({ offset: more ? pk.items.length : 0, limit: 40 })}`);
    clearTimeout(slow);
    if (seq !== pk.seq) return;
    pk.items = more ? pk.items.concat(res.items) : res.items;
    pk.total = res.total;
    pk.loadedQ = q;
    renderPicker(more);
  } catch (e) {
    clearTimeout(slow);
    if (seq === pk.seq) $("pk-list").innerHTML = `<div class="error" style="margin:8px">${esc(e.message)}</div>`;
  } finally {
    if (seq === pk.seq) pk.loading = false;
  }
}

function loadMore() {
  if (!pk.loading && pk.items.length < pk.total) loadUsers(true);
}

function renderPicker(keepActive = false) {
  const recent = pk.q || pk.bucket || pk.area || pk.hit ? [] : recentUsers();
  pk.view = [...recent, ...pk.items];
  if (!keepActive) {
    const cur = pk.view.findIndex((r) => r.customer_id === ad.user);
    pk.active = pk.view.length ? Math.max(0, cur) : -1;
  }
  const opt = (r, i) => `<div class="pk-item" role="option" id="pk-opt-${i}" data-i="${i}" aria-selected="false">
      ${avatar(r.customer_id)}
      <div class="pk-text"><div class="pk-id" title="${esc(r.customer_id)}">${idHtml(r.customer_id, pk.q)}</div>
        <div class="pk-meta">${esc(userMeta(r))}</div></div>
      ${r.customer_id === ad.user ? '<span class="pk-check">Đang xem</span>' : ""}
      ${r.best_rank != null ? rankBadge(r.best_rank) : ""}
      <span class="badge ${esc(r.bucket)}">${esc(BUCKET_SHORT[r.bucket] || "")}</span></div>`;
  const head = (t) => `<div class="pk-group">${t}</div>`;
  const filtered = pk.bucket || pk.area || pk.hit;
  const empty = pk.q
    ? `Không có khách nào có customer_id chứa “${esc(pk.q)}”${filtered ? " trong bộ lọc đang chọn" : ""}.`
    : "Không có khách nào trong bộ lọc đang chọn.";
  $("pk-list").innerHTML = (recent.length ? head("Xem gần đây") + recent.map(opt).join("") : "")
    + (pk.items.length
      ? head(pk.q ? "Kết quả tìm" : "Khách có sản phẩm đích") + pk.items.map((r, i) => opt(r, i + recent.length)).join("")
      : `<div class="pk-empty">${empty}<br>Thử bỏ bớt bộ lọc hoặc kiểm tra lại mã.</div>`);
  $("pk-count").textContent = `${num(pk.items.length)} / ${num(pk.total)} khách${pk.items.length < pk.total ? " · cuộn để xem thêm" : ""}`;
  paintActive(!keepActive);
}

// Hạng tốt nhất của món đích theo mô hình đang chọn: trong top-K = gợi ý trúng.
function rankBadge(rank) {
  const hit = rank <= Number($("ad-k").value);
  return `<span class="badge ${hit ? "hit" : "miss"}" title="Món đích xếp cao nhất: hạng ${num(rank)}">${hit ? `Trúng · #${rank}` : `Hạng ${num(rank)}`}</span>`;
}

function paintActive(scroll = true) {
  $("pk-list").querySelectorAll(".pk-item").forEach((el) => {
    const on = +el.dataset.i === pk.active;
    el.classList.toggle("active", on);
    el.setAttribute("aria-selected", on);
    if (on && scroll) el.scrollIntoView({ block: "nearest" });
  });
  $("pk-q").setAttribute("aria-activedescendant", pk.active >= 0 ? `pk-opt-${pk.active}` : "");
}

function pickUser(row) {
  $("picker").close();
  selectUser(row.customer_id);
}

function selectUser(cid) {
  cid = String(cid || "").trim();
  if (!cid) return;
  ad.user = cid;
  ad.prev = ad.next = null;
  $("cust-pos").textContent = "…";
  $("cust-prev").disabled = $("cust-next").disabled = true;
  loadAdmin();
  loadPosition();
}

// Vị trí của khách trong danh sách đang lọc + khách liền trước / liền sau cho nút ‹ ›.
async function loadPosition() {
  const cid = ad.user;
  try {
    const res = await api(`/users/${encodeURIComponent(cid)}/position?${filterParams()}`);
    if (cid !== ad.user) return;
    ad.prev = res.prev;
    ad.next = res.next;
    $("cust-pos").textContent = res.index == null ? "ngoài bộ lọc" : `${num(res.index + 1)} / ${num(res.total)}`;
    $("cust-prev").disabled = !res.prev;
    $("cust-next").disabled = !res.next;
  } catch { if (cid === ad.user) $("cust-pos").textContent = "—"; }
}

function syncUrl() {
  const p = new URLSearchParams(location.search);
  p.set("user", ad.user);
  p.set("a", $("ad-model-a").value);
  if ($("ad-compare").checked) { p.set("compare", "1"); p.set("b", $("ad-model-b").value); }
  else { p.delete("compare"); p.delete("b"); }
  history.replaceState(null, "", `${location.pathname}?${p}${location.hash}`);
}

function renderCustomerEmpty() {
  const recent = recentUsers();
  $("cust-current").innerHTML = `<span class="avatar lg ghost" aria-hidden="true">?</span>
    <div class="cust-info"><div class="cust-title">Chưa chọn khách hàng</div>
      <div class="note">Bấm <b>Chọn khách</b> (<kbd>Ctrl K</kbd> hoặc <kbd>/</kbd>) để tìm theo customer_id, lọc theo nhóm giao dịch
        hoặc khu vực mua sắm; hoặc bấm <b>Ngẫu nhiên</b>.</div>
      ${recent.length ? `<div class="recent-row"><span>Xem gần đây</span>${recent.map((r) => `<button type="button" class="recent-chip" data-id="${esc(r.customer_id)}" title="${esc(r.customer_id)}">${avatar(r.customer_id)}${esc(r.customer_id.slice(0, 8))}…</button>`).join("")}</div>` : ""}
    </div>`;
  $("cust-current").querySelectorAll(".recent-chip").forEach((btn) => btn.addEventListener("click", () => selectUser(btn.dataset.id)));
}

function renderCustomer(hist) {
  const p = hist.profile;
  const counts = {};
  hist.items.forEach((it) => { counts[it.product_type_name] = (counts[it.product_type_name] || 0) + 1; });
  const top = Object.entries(counts).sort((x, y) => y[1] - x[1]).slice(0, 4).map(([t, n]) => `${t} ×${n}`).join(", ");
  $("cust-current").innerHTML = `${avatar(p.customer_id, "lg")}
    <div class="cust-info">
      <div class="cust-id"><span class="mono" title="${esc(p.customer_id)}">${esc(p.customer_id)}</span>
        <button type="button" class="icon-btn" id="cust-copy" title="Chép customer_id" aria-label="Chép customer_id">${COPY_ICON}</button></div>
      <div class="cust-chips">
        <span class="badge ${esc(p.bucket)}">${esc(BUCKET_SHORT[p.bucket] || "")}</span>
        <span class="pill"><b>${num(p.train_count)}</b> món đã mua</span>
        <span class="pill"><b>${num(p.n_targets)}</b> món đích</span>
        ${p.area ? `<span class="pill">${esc(areaLabel(p.area))} <b>${pct(p.area_share, 0)}</b></span>` : ""}
        ${p.age != null ? `<span class="pill"><b>${Math.round(p.age)}</b> tuổi</span>` : ""}
        ${p.first_date ? `<span class="pill muted">mua ${esc(p.first_date)} → ${esc(p.last_date)}</span>` : ""}
      </div>
      ${top ? `<div class="cust-top">Hay mua: ${esc(top)}</div>` : ""}
    </div>`;
  $("cust-copy").addEventListener("click", async (e) => {
    const btn = e.currentTarget;
    try { await navigator.clipboard.writeText(p.customer_id); btn.textContent = "✓"; } catch { btn.textContent = "!"; }
    setTimeout(() => { btn.innerHTML = COPY_ICON; }, 1200);
  });
}

function showAdminError(e) {
  $("ad-grid").classList.add("hidden");
  $("ad-neighbors-card").classList.add("hidden");
  $("ad-empty").classList.remove("hidden");
  $("ad-empty").innerHTML = `<div class="error">${esc(e.message)}</div>`;
}

async function loadAdmin() {
  if (!ad.user) return;
  const seq = ++ad.seq;  // bấm ‹ › liên tục: chỉ vẽ kết quả của lần chọn sau cùng
  const k = $("ad-k").value;
  const models = [$("ad-model-a").value];
  if ($("ad-compare").checked && $("ad-model-b").value !== models[0]) models.push($("ad-model-b").value);
  const uid = encodeURIComponent(ad.user);
  syncUrl();
  $("ad-grid").classList.add("loading");
  try {
    const [hist, ...recs] = await Promise.all([
      api(`/users/${uid}/history`),
      ...models.map((m) => api(`/users/${uid}/recommend?model=${encodeURIComponent(m)}&k=${k}`)),
    ]);
    if (seq !== ad.seq) return;
    rememberUser(hist.profile);
    renderCustomer(hist);
    $("ad-empty").classList.add("hidden");
    $("ad-grid").classList.remove("hidden");
    renderHistory(hist);
    renderRecs(recs, k);
    renderAnswer(recs, hist);
  } catch (e) {
    if (seq === ad.seq) { renderCustomerEmpty(); showAdminError(e); }
    return;
  } finally {
    if (seq === ad.seq) $("ad-grid").classList.remove("loading");
  }
  loadNeighbors(uid);
}

async function loadNeighbors(uid) {
  const card = $("ad-neighbors-card");
  if (!CTX.has_neighbors) { card.classList.add("hidden"); return; }
  try {
    const res = await api(`/users/${uid}/neighbors?k=10`);
    card.classList.remove("hidden");
    const p = res.params || {};
    $("ad-neighbors").innerHTML = `
      <div class="note" style="margin-bottom:10px">UserKNN (k = ${esc(p.k)}, hệ số co ${esc(p.shrink)} — chọn trên validation): độ tương đồng
        cosine trên lịch sử mua nhị phân, <code>sim(u, v) = |chung| / (√(|u|·|v|) + shrink)</code>. Điểm của một sản phẩm
        = tổng độ tương đồng của những láng giềng đã mua nó. Cột cuối: láng giềng đã mua sản phẩm đích nào của khách này.</div>
      <table class="nb-table"><tr><th>#</th><th>Khách tương đồng</th><th>Độ tương đồng</th><th>Mua chung</th><th>Ví dụ món mua chung</th><th>Đã mua ${esc(targetLabel())}</th></tr>
      ${res.neighbors.map((n, i) => `<tr><td>${i + 1}</td><td class="cid">${esc(n.customer_id.slice(0, 16))}…<br><span class="meta">${num(n.train_count)} món đã mua</span></td>
        <td>${fmt(n.similarity, 3)}</td><td>${num(n.n_common)}</td>
        <td style="text-align:left">${n.common_items.map((it) => `${esc(it.prod_name)} <span class="meta">(${esc(it.product_type_name)} · ${esc(it.colour_group_name)})</span>`).join("<br>")}</td>
        <td style="text-align:left">${n.bought_target.map((it) => `<span class="tag head">${esc(it.prod_name)} · ${esc(it.colour_group_name)}</span>`).join(" ") || "—"}</td></tr>`).join("")}
      </table>`;
  } catch (e) {
    card.classList.remove("hidden");
    $("ad-neighbors").innerHTML = `<div class="error">${esc(e.message)}</div>`;
  }
}

function renderHistory(hist) {
  const label = isFinal() ? `sản phẩm mô hình đã học (train ∪ validation, trước ${esc(CTX.test_start)}), sắp theo ngày mua đầu` : "sản phẩm trong train, sắp theo ngày mua";
  $("ad-history").innerHTML = `<div class="note" style="margin-bottom:8px">${hist.items.length} ${label}.</div>` +
    hist.items.map((it) => rowItem(it, "", `<div class="score">${it.t_dat}${it.interaction_count > 1 ? `<br>×${it.interaction_count}` : ""}<br>${itemTag(it)}</div>`)).join("");
}

function renderRecs(recs, k) {
  $("ad-recs-title").textContent = `Top-${k} gợi ý`;
  const wrap = $("ad-recs");
  wrap.classList.toggle("compare", recs.length > 1);
  wrap.innerHTML = recs.map((r) => {
    const nHit = r.items.filter((it) => it.is_target).length;
    const nTarget = (r.targets || []).length || 1;
    const note = nHit
      ? `${nHit}/${nTarget} ${targetLabel()} nằm trong top-${k} (tô xanh).`
      : `Không có ${targetLabel()} nào trong top-${k} (hạng tốt nhất ${num(r.evaluation.rank)}).`;
    return `<div>
      <h3 style="color:${color(r.model)}">${esc(show(r.model))}</h3>
      ${r.items.map((it) => rowItem(it, `<div class="rank">#${it.rank}</div>`,
        `<div class="score">${esc(r.score_kind)} ${fmt(it.score, r.model === "MostPopular" ? 0 : 3)}<br>${itemTag(it)}${it.is_target ? `<br><span class="tag tail">ĐÍCH</span>` : ""}</div>`,
        it.is_target ? "hit" : "")).join("")}
      <div class="note" style="margin-top:8px">${note}</div>
    </div>`;
  }).join("");
}

function renderAnswer(recs, hist) {
  const v = recs[0].val_item;
  const targets = recs[0].targets || [recs[0].target_item];
  // Hạng của từng sản phẩm đích theo từng mô hình đang xem.
  const rankOf = recs.map((r) => Object.fromEntries((r.targets || []).map((t) => [t.item_idx, t.rank])));
  const metricCols = ["HR", "NDCG", ...(isFinal() ? ["Recall"] : [])];
  const blocks = recs.map((r) => {
    const e = r.evaluation;
    const rows = CTX.k_values.map((k) => `<tr><td>K = ${k}</td>${metricCols.map((m) =>
      `<td>${fmt(e.metrics[`${m}@${k}`], m === "HR" ? 0 : 4)}</td>`).join("")}</tr>`).join("");
    return `<div class="eval-block"><h3 style="color:${color(r.model)}">${esc(show(r.model))}</h3>
      <dl class="kv"><dt>Hạng tốt nhất</dt><dd>${num(e.rank)} / ${num(e.n_candidates)}</dd>
      <dt>Số candidates</dt><dd>${num(e.n_candidates)}</dd></dl>
      <table style="margin-top:8px"><tr><th></th>${metricCols.map((m) => `<th>${m}@K</th>`).join("")}</tr>${rows}</table></div>`;
  }).join("");
  const title = isFinal()
    ? `${targets.length} ${targetLabel()}: sản phẩm khách mua lần đầu trong giai đoạn test (từ ${esc(CTX.test_start)})`
    : CTX.evaluated_on === "test" ? "Test item (giao dịch cuối, bị giấu khỏi train)"
      : "Validation item (giao dịch áp chót, bị giấu khỏi train) — run chưa chấm test nên test item được giữ kín";
  const targetRows = targets.map((t) => rowItem(t, "",
    `<div class="score">${recs.map((r, i) => rankOf[i][t.item_idx] ? `<span style="color:${color(r.model)}">#${num(rankOf[i][t.item_idx])}</span>` : "").join("<br>")}<br>${itemTag(t)}</div>`,
    "hit")).join("");
  const cand = isV2()
    ? `Candidates = ${num(CTX.n_candidates)} sản phẩm (cũ ∪ ${num(CTX.n_new_items)} mới) − ${hist.items.length} món khách đã mua.`
    : isFinal()
    ? `Candidates = ${num(CTX.n_candidates)} sản phẩm của train ∪ validation − ${hist.items.length} món khách đã mua.`
    : `Candidates = ${num(CTX.n_items)} item − ${hist.items.length} item train${v ? " − 1 item validation" : ""}.`;
  $("ad-answer").innerHTML = `
    <h3>${title}</h3>
    ${targetRows}
    ${v ? `<div class="note" style="margin:8px 0 14px">Validation item (dùng cho early stopping, cũng bị loại khỏi candidates): ${esc(v.prod_name)} — ${esc(v.product_type_name)}</div>` : ""}
    <div class="note" style="margin-bottom:10px">${cand}</div>
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

const pct = (x, d = 1) => (x == null ? "—" : `${(100 * Number(x)).toFixed(d)}%`);

function sigTable(rows) {
  return `<div class="scroll"><table class="sig"><tr><th>A</th><th>B</th><th>NDCG@10 A</th><th>NDCG@10 B</th><th>Chênh</th><th>CI 95% (A−B)</th>
    <th>p Wilcoxon</th><th>p Holm</th><th>Kết luận</th></tr>${rows.map((r) => `<tr>
    <td>${esc(show(r.A))}</td><td>${esc(show(r.B))}</td><td>${fmt(r.mean_A, 5)}</td><td>${fmt(r.mean_B, 5)}</td>
    <td>${r.rel_diff >= 0 ? "+" : ""}${pct(r.rel_diff)}</td><td>[${fmt(r.ci_low, 5)}; ${fmt(r.ci_high, 5)}]</td>
    <td>${fmt(r.p_wilcoxon, 3)}</td><td>${fmt(r.p_holm, 3)}</td>
    <td class="${r.verdict === "không khác biệt có ý nghĩa" ? "" : "best"}">${esc(r.verdict)}</td></tr>`).join("")}</table></div>
    <div class="note">"Tốt hơn" chỉ khi đồng thời p Holm &lt; 0,05, khoảng tin cậy không chứa 0 và chênh lệch ≥ 5%.</div>`;
}

function simpleTable(rows, cols) {
  return `<div class="scroll"><table><tr><th>Mô hình</th>${cols.map(([, label]) => `<th>${esc(label)}</th>`).join("")}</tr>${rows.map((r) =>
    `<tr><td>${esc(show(r.model))}</td>${cols.map(([key, , f]) => `<td>${f(r[key])}</td>`).join("")}</tr>`).join("")}</table></div>`;
}

// Đánh giá theo K: NDCG@5 / @10 / @20 của từng mô hình (cột nhóm, một sắc xanh nhạt -> đậm theo K) + bảng mọi chỉ số @K
// có trong file kết quả.
const BY_K = [5, 10, 20];
const K_SHADES = ["#8fadd8", "#4f7cbd", "#1f4785"];
function byKCard(block, note) {
  if (!block) return "";  // máy chủ demo cũ chưa có khối này: bỏ thẻ, không làm hỏng cả dashboard
  return `<div class="card wide"><h2>Đánh giá theo K (5 · 10 · 20) — trung bình qua seed</h2>${body(block, (rows) => {
    const cols = ["NDCG", "Recall", "HR", "Precision"].flatMap((m) => BY_K.map((k) => `${m}@${k}`))
      .filter((c) => rows.some((r) => r[`${c}_mean`] != null));
    return `<canvas id="c-byk"></canvas>
      <div class="scroll"><table><tr><th>Mô hình</th>${cols.map((c) => `<th>${c}</th>`).join("")}</tr>${rows.map((r) =>
        `<tr><td>${esc(show(r.model))}</td>${cols.map((c) => `<td>${fmt(r[`${c}_mean`], 4)}</td>`).join("")}</tr>`).join("")}</table></div>
      <div class="note">K lớn hơn thì HR@K và Recall@K tăng (danh sách dài hơn dễ chứa món đích); so sánh các mô hình ở cùng một K. ${note}</div>`;
  })}</div>`;
}
function byKChart(block) {
  if (block?.status !== "ok") return;
  const rows = block.data;
  chart("c-byk", {
    type: "bar",
    data: { labels: rows.map((r) => show(r.model)),
            datasets: BY_K.map((k, i) => ({ label: `NDCG@${k}`, data: rows.map((r) => r[`NDCG@${k}_mean`]),
              backgroundColor: K_SHADES[i], borderRadius: 4, borderSkipped: "start" }))
              .filter((ds) => ds.data.some((v) => v != null)) },
    options: { plugins: { legend: { position: "bottom" } },
               scales: { y: { beginAtZero: true, title: { display: true, text: "NDCG@K" } } } },
  });
}

function renderFinalDashboard(d, dash) {
  const s = d.stats.data;
  const metrics = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"];
  dash.innerHTML = `
    <div class="card wide"><h2>Dữ liệu và giao thức của đánh giá cuối</h2><div class="stats">${[
      ["Users", num(s.n_users)], ["Items", num(s.n_items)], ["Tương tác", num(s.n_interactions)],
      ["Mật độ", `${(100 * s.density).toFixed(3)}%`], ["Train (cặp)", num(s.train)], ["Validation (cặp)", num(s.validation)],
      ["Train ∪ val (huấn luyện lại)", num(s.train_val)], ["Test (cặp)", num(s.test)], ["User test", num(s.n_test_users)],
      ["Ứng viên mỗi user", `≤ ${num(s.n_candidates)}`], ["k-core", s.k_core], ["Commit", esc(s.commit)],
    ].map(([l, n]) => `<div class="stat"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("")}</div>${srcLine(d.stats)}</div>

    <div class="card wide"><h2>Kết quả trên tập test — trung bình ± độ lệch chuẩn qua 3 seed</h2>${body(d.summary, (rows) => `
      <canvas id="c-final"></canvas>
      <div class="scroll"><table><tr><th>Mô hình</th>${metrics.map((m) => `<th>${m}</th>`).join("")}</tr>${rows.map((r) =>
        `<tr><td>${esc(show(r.model))}${r.extension ? " †" : ""}</td>${metrics.map((m) =>
          `<td>${fmt(r[m + "_mean"], 5)} ± ${fmt(r[m + "_std"], 5)}</td>`).join("")}</tr>`).join("")}</table></div>
      <div class="note">† Mô hình mở rộng, thêm sau khi đã xem test (PREREG mục 9), kiểm định trong họ so sánh riêng.</div>`)}</div>

    ${byKCard(d.by_k, "Số @20 do scripts/16_extra_k.py tính lại từ hạng đã lưu của 3 seed — mô tả, không chấm lại tập test.")}

    <div class="card wide"><h2>Kiểm định cặp theo user (NDCG@10) — họ 8 so sánh chính</h2>${body(d.significance, sigTable)}</div>
    <div class="card wide"><h2>Kiểm định cặp — họ 7 so sánh mở rộng</h2>${body(d.ext_significance, sigTable)}</div>

    <div class="card"><h2>NDCG@10 theo nhóm (mô tả, không kiểm định)</h2>${body(d.stratified, (rows) => simpleTable(rows,
      [["all", "Tất cả", (v) => fmt(v, 5)], ["head", "Head", (v) => fmt(v, 5)], ["tail", "Tail", (v) => fmt(v, 5)],
       ["cold", "Cold", (v) => fmt(v, 5)], ["warm", "Warm", (v) => fmt(v, 5)]]))}</div>
    <div class="card"><h2>Ngoài độ chính xác (top-10)</h2>${body(d.beyond, (rows) => simpleTable(rows,
      [["coverage", "Coverage", (v) => pct(v)], ["novelty", "Novelty (bit)", (v) => fmt(v, 2)], ["ARP", "ARP", (v) => fmt(v, 1)],
       ["HRR", "Tỉ lệ head", (v) => pct(v)]]))}</div>
    <div class="card"><h2>Sampled-99 (chỉ đối chiếu)</h2>${body(d.sampled, (rows) => simpleTable(rows,
      [["NDCG@10", "NDCG@10", (v) => fmt(v, 4)], ["HR@10", "HR@10", (v) => fmt(v, 4)]]))}
      <div class="note">Xếp 1 món đúng giữa 100 ứng viên dễ hơn nhiều so với giữa ~10.000 — không dùng để so sánh mô hình.</div></div>
    <div class="card"><h2>Độ trễ gợi ý top-10 trên CPU (ms)</h2>${body(d.latency, (rows) => simpleTable(rows,
      [["p50_ms", "p50", (v) => fmt(v, 2)], ["p95_ms", "p95", (v) => fmt(v, 2)], ["mean_ms", "Trung bình", (v) => fmt(v, 2)]]))}</div>`;
  if (d.summary.status === "ok") {
    const rows = d.summary.data;
    chart("c-final", {
      type: "bar",
      data: { labels: rows.map((r) => show(r.model) + (r.extension ? " †" : "")),
              datasets: [{ label: "NDCG@10 (test, TB 3 seed)", data: rows.map((r) => r["NDCG@10_mean"]), backgroundColor: rows.map((r) => color(r.model)) }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });
  }
  byKChart(d.by_k);
}

function renderV2Dashboard(d, dash) {
  const s = d.stats.data;
  const metrics = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5", "NDCG@20"];
  const ablName = { "neumf_f": "NeuMF-F (đầy đủ)", "neumf_f-text": "Bỏ vector văn bản", "neumf_f-time": "Bỏ đặc trưng thời gian",
    "neumf_f-user": "Bỏ thông tin khách hàng", "neumf_f-attr": "Bỏ thuộc tính sản phẩm", "neumf_f-iddrop": "Không bỏ ID ngẫu nhiên" };
  dash.innerHTML = `
    ${d.dry_run ? '<div class="card wide"><div class="error">Đang hiển thị bản <b>chạy thử</b> (mẫu A, tập xác thực, 1 epoch) — số liệu không có ý nghĩa, chỉ để kiểm tra đường ống.</div></div>' : ""}
    <div class="card wide"><h2>Dữ liệu của đánh giá cuối (giao thức v2)</h2><div class="stats">${[
      ["Khách sau k-core", num(s.n_users)], ["Sản phẩm (có ID + mới)", num(s.n_items)], ["Cặp trước mốc kiểm thử", num(s.n_interactions)],
      ["Cặp huấn luyện", num(s.train_pairs)], ["Khách được chấm", num(s.n_test_users)], ["Cặp đúng", num(s.targets)],
      ["Cặp đúng là SP mới", num(s.new_item_targets)], ["Ứng viên", num(s.n_candidates)], ["Sản phẩm mới", num(s.n_new_items)],
      ["k-core", s.k_core], ["Commit", esc(s.commit)],
    ].map(([l, n]) => `<div class="stat"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("")}</div>${srcLine(d.stats)}</div>

    <div class="card wide"><h2>Kết quả — trung bình ± độ lệch chuẩn qua seed</h2>${body(d.summary, (rows) => `
      <canvas id="c-final"></canvas>
      <div class="scroll"><table><tr><th>Mô hình</th>${metrics.map((m) => `<th>${m}</th>`).join("")}</tr>${rows.map((r) =>
        `<tr><td>${esc(show(r.model))}</td>${metrics.map((m) => `<td>${fmt(r[m + "_mean"], 5)} ± ${fmt(r[m + "_std"], 5)}</td>`).join("")}</tr>`).join("")}</table></div>`)}</div>

    ${byKCard(d.by_k, "Các chỉ số @K có trong outputs/v2/final/summary.csv.")}

    <div class="card wide"><h2>Kiểm định cặp theo khách hàng (NDCG@10) — họ 10 so sánh đăng ký trước</h2>${body(d.significance, sigTable)}</div>

    <div class="card"><h2>NDCG@10 theo nhóm sản phẩm đúng (mô tả)</h2>${body(d.groups, (rows) => simpleTable(rows,
      [["old_mean", "SP cũ", (v) => fmt(v, 5)], ["new_mean", "SP mới", (v) => fmt(v, 5)], ["oldonly_mean", "Chỉ SP cũ trong ứng viên", (v) => fmt(v, 5)]]))}</div>
    <div class="card"><h2>Danh sách top-10 và chi phí huấn luyện</h2>${body(d.beyond, (rows) => simpleTable(rows,
      [["coverage10", "Độ phủ", (v) => pct(v)], ["new_share10", "Tỉ lệ SP mới", (v) => pct(v)], ["best_epoch_mean", "Số epoch", (v) => fmt(v, 1)],
       ["train_min", "Phút / seed", (v) => fmt(v, 1)]]))}</div>
    <div class="card wide"><h2>Ablation NeuMF-F (seed 42, mô tả)</h2>${body(d.ablation, (rows) => `<div class="scroll"><table>
      <tr><th>Biến thể</th><th>NDCG@10</th><th>Thay đổi</th><th>CI 95% của hiệu</th><th>SP cũ</th><th>SP mới</th></tr>${rows.map((r) =>
        `<tr><td>${esc(ablName[r.variant] || r.variant)}</td><td>${fmt(r["NDCG@10"], 5)}</td><td>${r.variant === "neumf_f" ? "—" : (r.rel >= 0 ? "+" : "") + pct(r.rel)}</td>
        <td>${r.variant === "neumf_f" ? "—" : `[${fmt(r.ci_low, 5)}; ${fmt(r.ci_high, 5)}]`}</td><td>${fmt(r["NDCG@10_old"], 5)}</td><td>${fmt(r["NDCG@10_new"], 5)}</td></tr>`).join("")}</table></div>`)}</div>`;
  if (d.summary.status === "ok") {
    const rows = d.summary.data;
    chart("c-final", {
      type: "bar",
      data: { labels: rows.map((r) => show(r.model)),
              datasets: [{ label: "NDCG@10 (trung bình qua seed)", data: rows.map((r) => r["NDCG@10_mean"]), backgroundColor: rows.map((r) => color(r.model)) }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });
  }
  byKChart(d.by_k);
}

async function loadDashboard() {
  charts.forEach((c) => c.destroy());
  charts = [];
  const dash = $("dash");
  dash.innerHTML = '<div class="note">Đang đọc file kết quả...</div>';
  let d;
  try { d = await api("/dashboard"); } catch (e) { dash.innerHTML = `<div class="error">${esc(e.message)}</div>`; return; }
  if (d.mode === "v2") { renderV2Dashboard(d, dash); return; }
  if (d.mode === "final") { renderFinalDashboard(d, dash); return; }
  // Chỉ các K có trong file kết quả của run (demo thêm K = 20 chỉ cho màn Kiểm thử mô hình).
  const metricCols = CTX.k_values.flatMap((k) => [`HR@${k}`, `NDCG@${k}`])
    .filter((c) => d.primary.status !== "ok" || c in d.primary.data[0]);

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

    <div class="card wide"><h2>Phân phối rank của ${targetLabel()}</h2>${body(d.rank_distribution, (r) =>
      `<canvas id="c-rank"></canvas><div class="note">Bin theo thang log của rank (1, 2, 3–4, 5–10, ...). Không vẽ histogram HR per-user vì giá trị chỉ là 0/1.</div>
       <table style="margin-top:8px"><tr><th>Model</th><th>Median rank</th><th>Số user</th></tr>${Object.entries(r.series).map(([m, s]) =>
         `<tr><td>${esc(m)}</td><td>${num(s.median_rank)}</td><td>${num(s.n_users)}</td></tr>`).join("")}</table>`)}</div>

    <div class="card"><h2>Beyond-accuracy</h2>${body(d.beyond, (rows) =>
      `<canvas id="c-beyond"></canvas>${metricTable(rows.map((r) => ({ ...r, Coverage: r.coverage, Novelty: r.novelty, "Head Rec Rate": r.head_rec_rate })), ["Coverage", "Novelty", "Head Rec Rate"])}
       <div class="note">Head Rec Rate cao = gợi ý tập trung vào 10% item phổ biến nhất trong train.</div>`)}</div>

    <div class="card"><h2>Popularity bias — top 20 item được gợi ý nhiều nhất</h2>${body(d.popularity_bias, (rows) => {
      const models = [...new Set(rows.map((r) => r.model))];
      return `<select id="pb-model">${models.map((m) => `<option ${m === "NeuMF-Pretrained" ? "selected" : ""}>${esc(m)}</option>`).join("")}</select>
        <div class="note" style="margin:6px 0">Đếm trong top-${rows[0]?.top_k} của toàn bộ user được chấm; so với số lượt mua trong train.</div><div id="pb-table"></div>`;
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
      options: { plugins: { legend: { position: "bottom" } }, scales: { x: { title: { display: true, text: `rank của ${targetLabel()} (bin log)` } }, y: { title: { display: true, text: "số user" } } } },
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
      $("pb-table").innerHTML = `<div class="scroll" style="max-height:420px"><table><tr><th>#</th><th>Sản phẩm</th><th>% user</th><th>Lượt mua train</th><th>Hạng phổ biến train</th></tr>${rows.filter((r) => r.model === m).map((r) =>
        `<tr><td>${r.position}</td><td style="text-align:left">${esc(r.prod_name)} <span class="meta">(${esc(r.product_type_name)})</span> ${headTag(r.is_head)}</td>
         <td>${(100 * r.share_of_users).toFixed(1)}%</td><td>${num(r.train_count)}</td><td>${num(r.train_popularity_rank)}</td></tr>`).join("")}</table></div>`;
    };
    $("pb-model").addEventListener("change", render);
    render();
  }
}

init();
