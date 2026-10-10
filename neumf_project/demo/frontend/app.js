const API = "/api";
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (v, d = 4) => (v == null || Number.isNaN(Number(v)) ? "—" : Number(v).toFixed(d));
const num = (v) => Number(v).toLocaleString("vi-VN");
const MODEL_COLORS = {
  "NeuMF-F": "#2a78d6", "GMF-F": "#5b9be6", "MLP-F": "#173f7a", "LateFusion-F": "#7b4fa3", "NeuMF": "#e07a5f",
  "GMF": "#28528f", "MLP": "#6a8fc7", "BPR-MF": "#1d7a46", "ItemKNN": "#b07d12", "UserKNN": "#d9a425",
  "MostPopular-Recent": "#6b6b6b", "Content": "#1baf7a", "MostPopular": "#9a9a9a", "Random": "#d4d0ca",
};
const SHOW = { "MostPopular": "Most Popular" };
const show = (m) => SHOW[m] || m;
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
  const sample = CTX.dry_run ? "mẫu phát triển (bản chạy thử, tập xác thực)" : "mẫu kiểm định";
  $("info-strip").innerHTML = `
    <span>Dataset <b>H&amp;M</b> · ${sample} (${CTX.date_min} → ${CTX.date_max}) · k-core ${CTX.k_core}</span>
    <span>Mô hình của <b>đánh giá cuối</b> (seed ${esc(CTX.run_tag.replace("v2_seed", ""))}, commit ${esc(CTX.commit)})</span>
    <span><b>${num(CTX.n_users)}</b> khách · <b>${num(CTX.n_items)}</b> sản phẩm sau k-core</span>`;
  route();
}

/* ------------------------------------------------------------ shared UI */
const img = (it) => `<img loading="lazy" src="${API}/image/${esc(it.article_id)}" alt="${esc(it.product_type_name)}">`;
const kOptions = (sel) => {
  sel.innerHTML = CTX.k_values.map((k) => `<option value="${k}">${k}</option>`).join("");
  sel.value = Math.max(...CTX.k_values);
};

function rowItem(it, left, right, cls = "") {
  return `<div class="row-item ${cls}">${left}${img(it)}
    <div class="txt"><div class="name" title="${esc(it.prod_name)}">${esc(it.prod_name)}</div>
      <div class="meta">${esc(it.product_type_name)} · ${num(it.n_colours)} màu</div></div>${right}</div>`;
}

/* ------------------------------------------------------------ admin */
const targetLabel = () => "sản phẩm đích";

function renderProtocol() {
  $("ad-protocol").innerHTML = `<b>Cách chấm (đúng Chương 4)</b><br>
    • <b>Một sản phẩm</b> = một mẫu (<code>product_code</code>), mọi màu gộp lại; ảnh và tên lấy theo màu đầu tiên của mẫu.<br>
    • <b>Chia theo mốc thời gian</b>: mô hình đã được huấn luyện lại trên mọi cặp trước ${esc(CTX.test_start)}; lịch sử bên trái là đúng dữ liệu mô hình đã học.<br>
    • <b>Sản phẩm đích</b> = mọi sản phẩm khách mua <i>lần đầu</i> sau mốc (có thể nhiều món).<br>
    • <b>Full ranking</b> trên ${num(CTX.n_candidates)} sản phẩm có dữ liệu huấn luyện, trừ những món khách đã mua.<br>
    • <code>HR@K = 1</code> nếu có ít nhất một món đích trong top-K; <code>Recall@K</code> = số món đích trong top-K / số món đích; <code>NDCG@K = DCG/IDCG</code>.<br>
    • Số trên màn hình khớp file per-user của đánh giá cuối (seed 42); đây là hiển thị lại, không phải một lần chấm mới.`;
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
  const opts = CTX.models.map((m) => `<option value="${esc(m)}">${esc(show(m))}</option>`).join("");
  a.innerHTML = opts;
  b.innerHTML = opts;
  const pick = (prefs, fallback) => prefs.find((m) => CTX.models.includes(m)) || fallback;
  a.value = pick(["NeuMF-F"], CTX.models[0]);
  b.value = pick(["NeuMF", "BPR-MF"], CTX.models[1] || CTX.models[0]);
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
        <td style="text-align:left">${n.common_items.map((it) => `${esc(it.prod_name)} <span class="meta">(${esc(it.product_type_name)})</span>`).join("<br>")}</td>
        <td style="text-align:left">${n.bought_target.map((it) => `<span class="tag head">${esc(it.prod_name)}</span>`).join(" ") || "—"}</td></tr>`).join("")}
      </table>`;
  } catch (e) {
    card.classList.remove("hidden");
    $("ad-neighbors").innerHTML = `<div class="error">${esc(e.message)}</div>`;
  }
}

function renderHistory(hist) {
  $("ad-history").innerHTML = `<div class="note" style="margin-bottom:8px">${hist.items.length} sản phẩm mô hình đã học (mua trước ${esc(CTX.test_start)}), sắp theo ngày mua đầu.</div>` +
    hist.items.map((it) => rowItem(it, "", `<div class="score">${it.t_dat}</div>`)).join("");
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
        `<div class="score">${esc(r.score_kind)} ${fmt(it.score, r.model === "MostPopular" ? 0 : 3)}${it.is_target ? `<br><span class="tag tail">ĐÍCH</span>` : ""}</div>`,
        it.is_target ? "hit" : "")).join("")}
      <div class="note" style="margin-top:8px">${note}</div>
    </div>`;
  }).join("");
}

function renderAnswer(recs, hist) {
  const targets = recs[0].targets;
  // Hạng của từng sản phẩm đích theo từng mô hình đang xem.
  const rankOf = recs.map((r) => Object.fromEntries(r.targets.map((t) => [t.item_idx, t.rank])));
  const metricCols = ["HR", "NDCG", "Recall"];
  const blocks = recs.map((r) => {
    const e = r.evaluation;
    const rows = CTX.k_values.map((k) => `<tr><td>K = ${k}</td>${metricCols.map((m) =>
      `<td>${fmt(e.metrics[`${m}@${k}`], m === "HR" ? 0 : 4)}</td>`).join("")}</tr>`).join("");
    return `<div class="eval-block"><h3 style="color:${color(r.model)}">${esc(show(r.model))}</h3>
      <dl class="kv"><dt>Hạng tốt nhất</dt><dd>${num(e.rank)} / ${num(e.n_candidates)}</dd>
      <dt>Số candidates</dt><dd>${num(e.n_candidates)}</dd></dl>
      <table style="margin-top:8px"><tr><th></th>${metricCols.map((m) => `<th>${m}@K</th>`).join("")}</tr>${rows}</table></div>`;
  }).join("");
  const title = `${targets.length} ${targetLabel()}: sản phẩm khách mua lần đầu từ ${esc(CTX.test_start)}`;
  const targetRows = targets.map((t) => rowItem(t, "",
    `<div class="score">${recs.map((r, i) => rankOf[i][t.item_idx] ? `<span style="color:${color(r.model)}">#${num(rankOf[i][t.item_idx])}</span>` : "").join("<br>")}</div>`,
    "hit")).join("");
  const cand = `Candidates = ${num(CTX.n_candidates)} sản phẩm − ${hist.items.length} món khách đã mua.`;
  $("ad-answer").innerHTML = `
    <h3>${title}</h3>
    ${targetRows}
    <div class="note" style="margin-bottom:10px">${cand}</div>
    ${blocks}`;
}

/* ------------------------------------------------------------ dashboard */
function srcLine(block) {
  return `<div class="source">Nguồn: ${esc(block.source)}</div>`;
}
function body(block, render) {
  return block.status === "ok" ? render(block.data) + srcLine(block) : `<div class="missing">${esc(block.message)}</div>`;
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

function renderDashboard(d, dash) {
  const s = d.stats.data;
  const metrics = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5", "NDCG@20"];
  const ablName = { "neumf_f": "NeuMF-F (đầy đủ)", "neumf_f-text": "Bỏ vector văn bản", "neumf_f-time": "Bỏ đặc trưng thời gian",
    "neumf_f-user": "Bỏ thông tin khách hàng", "neumf_f-attr": "Bỏ thuộc tính sản phẩm" };
  dash.innerHTML = `
    ${d.dry_run ? '<div class="card wide"><div class="error">Đang hiển thị bản <b>chạy thử</b> (mẫu phát triển, tập xác thực, 1 epoch) — số liệu không có ý nghĩa, chỉ để kiểm tra đường ống.</div></div>' : ""}
    <div class="card wide"><h2>Dữ liệu của đánh giá cuối</h2><div class="stats">${[
      ["Khách sau k-core", num(s.n_users)], ["Sản phẩm (product_code)", num(s.n_items)], ["Cặp trước mốc kiểm thử", num(s.n_interactions)],
      ["Cặp huấn luyện", num(s.train_pairs)], ["Khách được chấm", num(s.n_test_users)], ["Cặp đúng", num(s.targets)],
      ["Ứng viên", num(s.n_candidates)], ["k-core", s.k_core], ["Commit", esc(s.commit)],
    ].map(([l, n]) => `<div class="stat"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("")}</div>${srcLine(d.stats)}</div>

    <div class="card wide"><h2>Kết quả — trung bình ± độ lệch chuẩn qua seed</h2>${body(d.summary, (rows) => `
      <canvas id="c-final"></canvas>
      <div class="scroll"><table><tr><th>Mô hình</th>${metrics.map((m) => `<th>${m}</th>`).join("")}</tr>${rows.map((r) =>
        `<tr><td>${esc(show(r.model))}</td>${metrics.map((m) => `<td>${fmt(r[m + "_mean"], 5)} ± ${fmt(r[m + "_std"], 5)}</td>`).join("")}</tr>`).join("")}</table></div>`)}</div>

    ${byKCard(d.by_k, "Các chỉ số @K có trong outputs/v2/final/summary.csv.")}

    <div class="card wide"><h2>Kiểm định cặp theo khách hàng (NDCG@10) — họ 10 so sánh đăng ký trước</h2>${body(d.significance, sigTable)}</div>

    <div class="card"><h2>Độ phủ top-10 và chi phí huấn luyện</h2>${body(d.beyond, (rows) => simpleTable(rows,
      [["coverage10", "Độ phủ", (v) => pct(v)], ["best_epoch_mean", "Số epoch", (v) => fmt(v, 1)],
       ["train_min", "Phút / seed", (v) => fmt(v, 1)]]))}</div>
    <div class="card"><h2>Ablation NeuMF-F (seed 42, mô tả)</h2>${body(d.ablation, (rows) => `<div class="scroll"><table>
      <tr><th>Biến thể</th><th>NDCG@10</th><th>Thay đổi</th><th>CI 95% của hiệu</th></tr>${rows.map((r) =>
        `<tr><td>${esc(ablName[r.variant] || r.variant)}</td><td>${fmt(r["NDCG@10"], 5)}</td><td>${r.variant === "neumf_f" ? "—" : (r.rel >= 0 ? "+" : "") + pct(r.rel)}</td>
        <td>${r.variant === "neumf_f" ? "—" : `[${fmt(r.ci_low, 5)}; ${fmt(r.ci_high, 5)}]`}</td></tr>`).join("")}</table></div>`)}</div>`;
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
  try { renderDashboard(await api("/dashboard"), dash); } catch (e) { dash.innerHTML = `<div class="error">${esc(e.message)}</div>`; }
}

init();
