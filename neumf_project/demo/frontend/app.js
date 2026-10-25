const API = "/api";
// Bộ dữ liệu đang xem (?ds=amazon), gửi kèm mọi lời gọi API; đổi bộ dữ liệu = tải lại trang với ?ds= mới.
const DS = new URLSearchParams(location.search).get("ds") === "amazon" ? "amazon" : "hm";
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (v, d = 4) => (v == null || Number.isNaN(Number(v)) ? "—" : Number(v).toFixed(d));
const num = (v) => Number(v).toLocaleString("vi-VN");
const SHOW = { "MostPopular": "Most Popular" };
const show = (m) => SHOW[m] || m;
// Màu tên mô hình: NeuMF-F (mô hình đề xuất) màu chính, các mô hình khác màu chữ thường — giống trang Kết quả đánh giá.
const color = (m) => (m === "NeuMF-F" ? "var(--accent)" : "var(--ink)");
// Mô hình chính của cửa hàng: luôn là NeuMF-F (bản chạy thử thiếu NeuMF-F thì lấy mô hình đầu tiên).
const mainModel = () => (CTX.models.includes("NeuMF-F") ? "NeuMF-F" : CTX.models[0]);

async function api(path, opts) {
  const res = await fetch(`${API}${path}${path.includes("?") ? "&" : "?"}dataset=${DS}`, opts);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `Lỗi HTTP ${res.status}`);
  return body;
}

let CTX = null;
const inited = {};
let charts = [];

/* ------------------------------------------------------------ routing */
// Cửa hàng (trang mặc định) · Kết quả đánh giá (có đúng hướng không) · Giới thiệu đề tài · Bảng số liệu (mở từ trang kết quả)
const VIEWS = ["shop", "results", "overview", "dashboard"];
function currentView() {
  const v = location.hash.replace(/^#\/?/, "");
  return VIEWS.includes(v) ? v : "shop";  // gồm cả #/admin cũ
}
function route() {
  const view = currentView();
  VIEWS.forEach((x) => $("view-" + x).classList.toggle("hidden", x !== view));
  document.querySelectorAll("#main-nav a").forEach((a) => {
    if (a.dataset.view === view) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  if (!CTX) return;
  if (view === "overview") loadOverview();
  if (view === "shop" && !inited.admin) initAdmin();
  if (view === "results") loadResults();
  if (view === "dashboard") loadDashboard();
}
window.addEventListener("hashchange", route);

// Thanh chọn bộ dữ liệu: liên kết ?ds=..., bộ chưa có kết quả đánh giá cuối ghi rõ lý do (di chuột để xem lệnh cần chạy).
async function renderDatasets() {
  try {
    const list = await api("/datasets");
    $("ds-nav").innerHTML = list.map((d) => `<a href="?${new URLSearchParams({ ds: d.key })}${location.hash}"
      ${d.key === DS ? 'aria-current="true"' : ""}${d.reason ? ` title="${esc(d.reason)}"` : ""}>${esc(d.label)}${d.reason
        ? ' <span class="muted-tag">chưa có kết quả</span>' : ""}</a>`).join("");
  } catch { /* không đọc được danh sách: chỉ còn bộ dữ liệu đang xem */ }
}

/* ------------------------------------------------------------ sáng / tối */
// data-theme trên <html> đã đặt trong <head>; nút đổi chế độ lưu lựa chọn và vẽ lại biểu đồ theo màu mới.
const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
function chartTheme() {
  if (!window.Chart) return;
  Chart.defaults.color = cssVar("--muted");
  Chart.defaults.borderColor = cssVar("--line");
  Chart.defaults.font.family = cssVar("--font");
}
function setTheme(t) {
  document.documentElement.dataset.theme = t;
  try { localStorage.setItem("demo.theme", t); } catch { /* trình duyệt chặn lưu: chỉ đổi trong lần xem này */ }
  chartTheme();
  if (currentView() === "dashboard" && CTX) loadDashboard();
}
$("theme-btn").addEventListener("click", () => setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));
chartTheme();

async function init() {
  route();
  renderDatasets();
  try {
    CTX = await api("/context");
  } catch (e) {
    $("info-strip").innerHTML = `<span class="error">${esc(e.message)}</span>`;
    $("ov-lede").innerHTML = `<span class="error">${esc(e.message)}</span>`;
    return;
  }
  document.title = `Demo khuyến nghị — ${CTX.dataset_label}`;
  document.querySelector(".brand small").textContent = `Dự án CNTT · ${CTX.tagline}`;
  const sample = CTX.dry_run ? "mẫu phát triển (bản chạy thử)" : DS === "hm" ? "mẫu kiểm định" : "tập kiểm thử";
  $("info-strip").textContent = `${CTX.dataset_label} · ${sample} · mô hình của lần đánh giá cuối`;
  route();
}

/* ------------------------------------------------------------ shared UI */
// Ô sản phẩm: ảnh thật đã lưu trên máy chủ demo nếu có (H&M: ảnh đã chép; Amazon: ảnh đã tải về), không thì ô màu theo nhóm hàng.
const TYPE_VI = { "Trousers": "Quần dài", "Pyjama set": "Bộ đồ ngủ", "Sweater": "Áo len", "Underwear Tights": "Quần tất",
  "Bra": "Áo ngực", "Underwear bottom": "Quần lót", "Leggings/Tights": "Quần legging", "T-shirt": "Áo thun", "Top": "Áo",
  "Shorts": "Quần short", "Vest top": "Áo ba lỗ", "Swimwear bottom": "Quần bơi", "Swimwear top": "Áo bơi", "Skirt": "Chân váy",
  "Dress": "Váy liền", "Blouse": "Áo kiểu", "Shirt": "Sơ mi", "Hoodie": "Áo hoodie", "Cardigan": "Áo cardigan",
  "Jacket": "Áo khoác", "Coat": "Áo măng tô", "Blazer": "Áo blazer", "Jumpsuit/Playsuit": "Đồ liền", "Socks": "Tất",
  "Bodysuit": "Áo bodysuit", "Sneakers": "Giày thể thao", "Bag": "Túi", "Hat/beanie": "Mũ", "Scarf": "Khăn" };
const typeVi = (t) => TYPE_VI[t] || t;
function productGroup(t) {
  t = String(t || "");
  if (/Bra|Underwear|Swimwear|Pyjama|Bodysuit|Socks/i.test(t)) return ["under", "g-under"];
  if (/Shorts/i.test(t)) return ["bottom", "g-short"];
  if (/Trousers|Leggings|Tights|Jeans/i.test(t)) return ["bottom", "g-bottom"];
  if (/Skirt|Dress|Jumpsuit/i.test(t)) return ["knit", "g-dress"];
  if (/Sweater|Hoodie|Cardigan|Jacket|Coat|Blazer/i.test(t)) return ["knit", "g-knit"];
  if (/T-shirt|Top|Vest|Blouse|Shirt/i.test(t)) return ["top", "g-top"];
  if (DS === "amazon") return ["other", "g-beauty"];
  return ["other", "g-other"];
}
const tile = (t) => { const [g, ic] = productGroup(t); return `<span class="tile" style="background:var(--p-${g});color:var(--p-${g}-ink)"><svg aria-hidden="true"><use href="#${ic}"/></svg></span>`; };
function media(it) {
  if (!CTX || !CTX.has_images || !it.image_url) return tile(it.product_type_name);
  return `<img loading="lazy" src="${esc(it.image_url)}" alt="${esc(it.product_type_name)}" data-type="${esc(it.product_type_name)}" onerror="productImageFailed(this)">`;
}
function productImageFailed(el) { el.outerHTML = tile(el.dataset.type); }
const kOptions = (sel) => {
  sel.innerHTML = CTX.k_values.map((k) => `<option value="${k}">${k}</option>`).join("");
  sel.value = Math.max(...CTX.k_values);
};

/* ------------------------------------------------------------ cửa hàng: chọn khách */
// Tham khảo: thanh khách + bảng chọn mở bằng Ctrl K (kiểu bảng lệnh của Linear / Vercel), danh sách có ô lọc, tab
// nhóm và avatar (SelectPanel của GitHub Primer, resource index của Shopify Polaris).
const ad = { user: null, prev: null, next: null, facets: null, seq: 0 };
const pk = { q: "", bucket: "", area: "", hit: "", sort: "train_desc", items: [], total: 0, view: [], active: -1,
  loading: false, seq: 0, timer: null, loadedQ: null };
const BUCKET_SHORT = { low: "Ít giao dịch", mid: "Trung bình", high: "Nhiều giao dịch" };
const AREA_VI = { "Ladieswear": "Đồ nữ", "Menswear": "Đồ nam", "Divided": "Divided", "Baby/Children": "Trẻ em", "Sport": "Thể thao",
  // Amazon Beauty: danh mục cấp 1
  "Skin Care": "Chăm sóc da", "Makeup": "Trang điểm", "Hair Care": "Chăm sóc tóc", "Fragrance": "Nước hoa",
  "Tools & Accessories": "Dụng cụ & phụ kiện", "Bath & Body": "Tắm & cơ thể" };
const areaLabel = (a) => AREA_VI[a] || a;
const SORT_LABELS = { train_desc: "Mua nhiều nhất", train_asc: "Mua ít nhất", targets_desc: "Mua sau mốc nhiều nhất",
  rank: "Khuyến nghị đúng sớm nhất", id: "Theo mã khách" };
// Lọc / sắp theo kết quả khuyến nghị cần chấm mọi khách với mô hình đang chọn (lần đầu mỗi mô hình mất vài giây).
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
const userMeta = (r) => [`${num(r.train_count)} món đã mua`, `${num(r.n_targets)} món mua sau mốc`,
  r.area && areaLabel(r.area), r.age != null && `${Math.round(r.age)} tuổi`].filter(Boolean).join(" · ");
const filterParams = (extra = {}) => {
  const p = new URLSearchParams({ sort: pk.sort, model: mainModel(), k: $("ad-k").value, ...extra });
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
  const b = $("ad-model-b");
  $("ad-main").textContent = show(mainModel());
  // Ô so sánh chỉ liệt kê các mô hình khác NeuMF-F; "Không so sánh" chỉ hiện danh sách của NeuMF-F.
  const others = CTX.models.filter((m) => m !== mainModel());
  b.innerHTML = others.map((m) => `<option value="${esc(m)}">${esc(show(m))}</option>`).join("")
    + '<option value="">Không so sánh</option>';
  b.value = ["NeuMF", "BPR-MF"].find((m) => others.includes(m)) || others[0] || "";
  kOptions($("ad-k"));
  const un = Object.entries(CTX.unavailable_models || {});
  $("ad-unavailable").innerHTML = un.map(([m, r]) => `<b>${esc(m)}</b> bị ẩn: ${esc(r)}`).join("<br>");
  [b, $("ad-k")].forEach((el) => el.addEventListener("change", loadAdmin));
  $("ad-k").addEventListener("change", () => {  // lọc trúng / trượt theo NeuMF-F và K
    if (!needsRanks()) return;
    pk.loadedQ = null;  // mở bảng chọn lần sau thì tải lại danh sách
    if (ad.user) loadPosition();
  });

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
  $("cust-showcase").addEventListener("click", showcase);
  // Khách mới: một mã chưa có trong dữ liệu đã học -> hệ thống khuyến nghị sản phẩm bán chạy (không báo lỗi).
  $("cust-new").addEventListener("click", () => selectUser(`KHACHMOI${String(Date.now()).slice(-6)}`));
  $("sh-reveal").addEventListener("click", () => { ad.revealed = !ad.revealed; renderShop(); });
  // Bấm thẻ sản phẩm ở bất kỳ đâu trong cửa hàng hoặc trong thẻ chi tiết -> mở thẻ chi tiết của sản phẩm đó.
  const onCard = (e) => { const c = e.target.closest(".pcard, .prow"); if (c) openProduct(Number(c.dataset.item)); };
  $("ad-grid").addEventListener("click", onCard);
  $("pd-body").addEventListener("click", onCard);
  $("pd-close").addEventListener("click", () => $("product").close());
  $("product").addEventListener("click", (e) => { if (e.target === $("product")) $("product").close(); });
  $("cust-prev").addEventListener("click", () => ad.prev && selectUser(ad.prev.customer_id));
  $("cust-next").addEventListener("click", () => ad.next && selectUser(ad.next.customer_id));
  document.addEventListener("keydown", onAdminKey);

  try {
    ad.facets = await api("/users/facets");
    renderFilters();
  } catch (e) { showAdminError(e); }

  // Mở thẳng một khách (dùng khi chụp ảnh minh hoạ): ?user=<customer_id>&b=<mô hình đối chứng, để trống = không so sánh>&k=<K>
  const params = new URLSearchParams(location.search);
  if (params.has("b") && (params.get("b") === "" || others.includes(params.get("b")))) b.value = params.get("b");
  if (CTX.k_values.includes(Number(params.get("k")))) $("ad-k").value = params.get("k");
  if (params.get("user")) {
    const loaded = selectUser(params.get("user"));
    // Dùng khi chụp ảnh minh hoạ: &reveal=1 lật sẵn đáp án, &item=<chỉ số sản phẩm> mở sẵn thẻ chi tiết.
    if (params.get("reveal") === "1") ad.revealed = true;
    if (params.get("item")) loaded.then(() => openProduct(Number(params.get("item"))));
    return;
  }
  // Mở trang lần đầu: hiện ngay khách ví dụ (NeuMF-F khuyến nghị đúng, NeuMF chỉ dùng mã khuyến nghị sai), so sánh hai mô hình.
  try {
    const ex = await api("/example");
    if (ad.user) return;  // người xem đã tự chọn khách trong lúc chờ
    if (others.includes(ex.model_b)) b.value = ex.model_b;
    $("ad-k").value = String(ex.k || 10);
    selectUser(ex.customer_id);
  } catch { /* chưa tìm được ví dụ: để trống, người xem tự chọn khách */ }
}

// Xem ví dụ: khách có món đích nằm trong top-K của NeuMF-F nhưng không nằm trong top-K của mô hình đối chứng (hạng trùng số
// đã lưu ở đánh giá cuối). Đang để "Không so sánh" thì so với NeuMF. Lần đầu với mỗi mô hình phải chấm mọi khách (vài giây).
async function showcase() {
  const btn = $("cust-showcase"), label = btn.textContent;
  const [a, k] = [mainModel(), $("ad-k").value];
  const sel = $("ad-model-b");
  const b = sel.value || [...sel.options].map((o) => o.value).find((m) => m === "NeuMF") || sel.options[0].value;
  btn.disabled = true;
  btn.textContent = "Đang tìm…";
  try {
    const res = await api(`/users/showcase?${new URLSearchParams({ a, b, k, limit: 20 })}`);
    if (!res.items.length) throw new Error(`Không tìm thấy khách nào mà ${show(a)} khuyến nghị đúng còn ${show(b)} khuyến nghị sai trong top-${k}. Thử đổi mô hình đối chứng hoặc số khuyến nghị.`);
    sel.value = b;
    const row = res.items[Math.floor(Math.random() * res.items.length)];
    selectUser(row.customer_id);
  } catch (e) { showAdminError(e); } finally {
    btn.disabled = false;
    btn.textContent = label;
  }
}

// Ctrl K: mở / đóng bảng chọn; "/": mở; ← →: khách trước / sau (khi không gõ trong ô nhập).
function onAdminKey(e) {
  if ($("view-shop").classList.contains("hidden") || $("product").open) return;
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
    { value: "hit", label: "Khuyến nghị trúng", title: `Có ít nhất một món khách mua trong ${k} khuyến nghị` },
    { value: "miss", label: "Khuyến nghị trượt", title: `Không có món khách mua nào trong ${k} khuyến nghị` }],
  pk.hit, (v) => { pk.hit = v; renderFilters(); loadUsers(); });
  $("pk-hit-note").textContent = `theo ${show(mainModel())}, ${k} khuyến nghị`;
}

async function loadUsers(more = false) {
  const seq = ++pk.seq;
  const q = pk.q;
  pk.loading = true;
  const slow = setTimeout(() => {  // chấm mọi khách lần đầu với một mô hình mất vài giây
    if (seq === pk.seq && !more) {
      $("pk-list").innerHTML = `<div class="pk-empty">${needsRanks()
        ? `Đang chấm mọi khách với <b>${esc(show(mainModel()))}</b>… (lần đầu với mỗi mô hình mất khoảng 5–15 giây)`
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
  // Mã gõ vào không có trong danh sách (khách mới, hoặc khách không có sản phẩm đích): vẫn xem được khuyến nghị cho mã đó.
  const anyId = pk.q ? `<button type="button" class="btn" id="pk-any">Xem khuyến nghị cho mã “${esc(pk.q)}”</button>
      <div class="note">Khách chưa có trong dữ liệu đã học nhận danh sách sản phẩm phổ biến; khách đã có lịch sử nhận khuyến nghị của mô hình.</div>` : "";
  $("pk-list").innerHTML = (recent.length ? head("Xem gần đây") + recent.map(opt).join("") : "")
    + (pk.items.length
      ? head(pk.q ? "Kết quả tìm" : "Khách có sản phẩm đích") + pk.items.map((r, i) => opt(r, i + recent.length)).join("")
      : `<div class="pk-empty">${empty}<br>Thử bỏ bớt bộ lọc hoặc kiểm tra lại mã.${anyId ? `<br>${anyId}` : ""}</div>`);
  $("pk-any")?.addEventListener("click", () => { $("picker").close(); selectUser(pk.q); });
  $("pk-count").textContent = `${num(pk.items.length)} / ${num(pk.total)} khách${pk.items.length < pk.total ? " · cuộn để xem thêm" : ""}`;
  paintActive(!keepActive);
}

// Hạng tốt nhất của món đích theo mô hình đang chọn: trong top-K = khuyến nghị trúng.
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

function selectUser(cid, caseNote = null) {
  cid = String(cid || "").trim();
  if (!cid) return;
  ad.user = cid;
  ad.caseNote = caseNote;
  ad.revealed = false;  // khách mới chọn: ẩn đáp án, để người xem tự đoán trước
  ad.prev = ad.next = null;
  $("cust-pos").textContent = "…";
  $("cust-prev").disabled = $("cust-next").disabled = true;
  const loaded = loadAdmin();
  loadPosition();
  return loaded;
}

// Vị trí của khách trong danh sách đang lọc + khách liền trước / liền sau cho nút ‹ ›.
async function loadPosition() {
  const cid = ad.user;
  try {
    const res = await api(`/users/${encodeURIComponent(cid)}/position?${filterParams()}`);
    if (cid !== ad.user) return;
    ad.prev = res.prev;
    ad.next = res.next;
    $("cust-pos").textContent = res.index == null ? "—" : `${num(res.index + 1)} / ${num(res.total)}`;
    $("cust-prev").disabled = !res.prev;
    $("cust-next").disabled = !res.next;
  } catch { if (cid === ad.user) $("cust-pos").textContent = "—"; }
}

function syncUrl() {
  const p = new URLSearchParams(location.search);
  p.set("user", ad.user);
  p.set("k", $("ad-k").value);
  p.set("b", $("ad-model-b").value);
  p.delete("a");
  p.delete("compare");
  history.replaceState(null, "", `${location.pathname}?${p}${location.hash}`);
}

function renderCustomerEmpty() {
  const recent = recentUsers();
  $("cust-current").innerHTML = `<span class="avatar lg ghost" aria-hidden="true">?</span>
    <div class="cust-info"><div class="cust-title">Chưa chọn khách hàng</div>
      <div class="note">Bấm <b>Xem ví dụ</b> để mở một khách có sẵn, <b>Ngẫu nhiên</b> để thử một khách bất kỳ, hoặc <b>Chọn khách</b> để tìm theo mã.</div>
      ${recent.length ? `<div class="recent-row"><span>Xem gần đây</span>${recent.map((r) => `<button type="button" class="recent-chip" data-id="${esc(r.customer_id)}" title="${esc(r.customer_id)}">${avatar(r.customer_id)}${esc(r.customer_id.slice(0, 8))}…</button>`).join("")}</div>` : ""}
    </div>`;
  $("cust-current").querySelectorAll(".recent-chip").forEach((btn) => btn.addEventListener("click", () => selectUser(btn.dataset.id)));
}

function renderCustomer(hist) {
  const p = hist.profile;
  if (hist.is_new) {  // khách chưa có trong dữ liệu đã học: chỉ có mã, khuyến nghị phổ biến
    $("cust-current").innerHTML = `${avatar(p.customer_id, "lg")}
      <div class="cust-info">
        <div class="cust-id"><span class="mono" title="${esc(p.customer_id)}">Khách ${esc(p.customer_id.slice(0, 8))}…</span></div>
        <div class="cust-chips"><span class="badge new">Khách mới</span></div>
        <div class="cust-top">Chưa có lịch sử mua, nên hệ thống khuyến nghị các sản phẩm bán chạy.</div>
      </div>`;
    return;
  }
  const counts = {};
  hist.items.forEach((it) => { counts[it.product_type_name] = (counts[it.product_type_name] || 0) + 1; });
  const top = Object.entries(counts).sort((x, y) => y[1] - x[1]).slice(0, 3)
    .map(([t]) => (DS === "hm" ? typeVi(t) : t).toLowerCase()).join(", ");
  $("cust-current").innerHTML = `${avatar(p.customer_id, "lg")}
    <div class="cust-info">
      <div class="cust-id"><span class="mono" title="${esc(p.customer_id)}">Khách ${esc(p.customer_id.slice(0, 8))}…</span>
        <button type="button" class="icon-btn" id="cust-copy" title="Chép mã khách đầy đủ" aria-label="Chép mã khách đầy đủ">${COPY_ICON}</button></div>
      <div class="cust-chips">
        <span class="pill"><b>${num(p.train_count)}</b> món đã mua trước đây</span>
        <span class="pill"><b>${num(p.n_targets)}</b> món mua sau ${esc(vnDate(CTX.test_start))}</span>
        ${p.age != null ? `<span class="pill"><b>${Math.round(p.age)}</b> tuổi</span>` : ""}
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
  $("ad-empty").classList.remove("hidden");
  $("ad-empty").innerHTML = `<div class="error">${esc(e.message)}</div>`;
}

async function loadAdmin() {
  if (!ad.user) return;
  const seq = ++ad.seq;  // bấm ‹ › liên tục: chỉ vẽ kết quả của lần chọn sau cùng
  const k = $("ad-k").value;
  const models = [mainModel()];
  if ($("ad-model-b").value) models.push($("ad-model-b").value);
  const uid = encodeURIComponent(ad.user);
  syncUrl();
  $("ad-grid").classList.add("loading");
  try {
    const [hist, ...recs] = await Promise.all([
      api(`/users/${uid}/history`),
      ...models.map((m) => api(`/users/${uid}/recommend?model=${encodeURIComponent(m)}&k=${k}`)),
    ]);
    if (seq !== ad.seq) return;
    if (!hist.is_new) rememberUser(hist.profile);
    renderCustomer(hist);
    $("ad-empty").classList.add("hidden");
    $("ad-case").textContent = ad.caseNote || "";
    $("ad-case").classList.toggle("hidden", !ad.caseNote);
    $("ad-grid").classList.remove("hidden");
    ad.hist = hist;
    ad.recs = recs[0].fallback ? recs.slice(0, 1) : recs;  // khách mới: mọi mô hình trả cùng danh sách phổ biến
    ad.k = Number(k);
    renderHistory(hist);
    renderShop();
  } catch (e) {
    if (seq === ad.seq) { renderCustomerEmpty(); showAdminError(e); }
    return;
  } finally {
    if (seq === ad.seq) $("ad-grid").classList.remove("loading");
  }
  loadNeighbors(uid, seq);
}

/* ------------------------------------------------------------ cửa hàng: thẻ sản phẩm */
// Thẻ sản phẩm dùng chung (đã mua, khuyến nghị, món khách mua sau đó, sản phẩm tương tự); bấm để mở thẻ chi tiết.
const typeOf = (it) => (DS === "hm" ? typeVi(it.product_type_name) : it.product_type_name);
const GROUP_VI = { "Garment Upper body": "Áo", "Garment Lower body": "Quần, váy", "Garment Full body": "Đồ liền thân",
  "Underwear": "Đồ lót", "Swimwear": "Đồ bơi", "Nightwear": "Đồ ngủ", "Socks & Tights": "Tất", "Accessories": "Phụ kiện",
  "Shoes": "Giày", "Items": "Vật dụng", "Cosmetic": "Mỹ phẩm", "Bags": "Túi", "Underwear/nightwear": "Đồ lót, đồ ngủ" };
function pcard(it, { rank = null, hit = false, extra = "" } = {}) {
  const sub = DS === "hm" ? `${typeOf(it)} · ${it.n_colours} màu` : (it.subtitle || typeOf(it));
  return `<button type="button" class="pcard ${hit ? "hit" : ""}" data-item="${it.item_idx}" title="${esc(it.prod_name)}">
    <span class="pimg">${media(it)}${rank != null ? `<span class="prank">#${rank}</span>` : ""}${hit ? '<span class="pbought">✓ Khách đã mua</span>' : ""}</span>
    <span class="pname">${esc(it.prod_name)}</span><span class="pmeta">${esc(sub)}</span>${extra}</button>`;
}

// Dòng sản phẩm trong cột so sánh: thứ hạng, ảnh nhỏ, tên và loại hàng.
function prow(it, hit) {
  return `<button type="button" class="prow ${hit ? "hit" : ""}" data-item="${it.item_idx}" title="${esc(it.prod_name)}">
    <span class="r num">${it.rank}</span><span class="pth">${media(it)}</span>
    <span class="t"><span class="pname">${esc(it.prod_name)}</span><span class="pmeta">${esc(typeOf(it))}</span></span>
    ${hit ? '<span class="ok">✓ đã mua</span>' : ""}</button>`;
}

function renderHistory(hist) {
  if (!hist.items.length) {
    $("sh-hist-note").textContent = "";
    $("sh-history").innerHTML = `<div class="note">Khách mới, chưa có lịch sử mua.</div>`;
    return;
  }
  $("sh-hist-note").textContent = `${hist.items.length} món, trước ${vnDate(CTX.test_start)}`;
  $("sh-history").innerHTML = [...hist.items].reverse()  // mới nhất trước
    .map((it) => pcard(it, { extra: `<span class="pdate">mua ${esc(vnDate(it.t_dat))}</span>` })).join("");
}

// Kết luận ngắn cho từng mô hình sau khi lật đáp án.
function verdict(r) {
  if (!r.evaluation) return "";
  const nHit = r.items.filter((it) => it.is_target).length;
  return nHit
    ? `<span class="pill good">Đúng ${nHit}/${r.targets.length} món · món đầu tiên ở vị trí ${num(r.evaluation.rank)}</span>`
    : `<span class="pill bad">Chưa trúng món nào · món gần nhất ở vị trí ${num(r.evaluation.rank)}</span>`;
}

function renderShop() {
  const recs = ad.recs, k = ad.k, date = vnDate(CTX.test_start);
  const fallback = !!recs[0].fallback, canReveal = !!recs[0].evaluation;
  $("sh-recs-title").innerHTML = `<span class="step">2</span>${fallback ? `${k} sản phẩm bán chạy (khách mới)` : `${k} khuyến nghị dành cho khách này`}`;
  const btn = $("sh-reveal");
  btn.classList.toggle("hidden", !canReveal);
  btn.setAttribute("aria-pressed", ad.revealed);
  btn.textContent = ad.revealed ? "Ẩn đáp án" : `Xem khách đã mua gì sau ${date}`;
  const head = (r, i) => `<div class="recs-head"><b class="mc" style="--mc:${color(r.model)}">${esc(fallback ? "Khuyến nghị phổ biến" : show(r.model))}</b>
      ${fallback ? "" : `<span class="pill">${i ? "mô hình đối chứng" : "mô hình đề xuất"}</span>`}${ad.revealed ? verdict(r) : ""}</div>`;
  // Một mô hình: lưới thẻ sản phẩm. Hai mô hình: hai cột đặt cạnh nhau, NeuMF-F bên trái, cùng thứ hạng cùng hàng.
  $("sh-recs").innerHTML = recs.length === 1
    ? `<div class="recs-row">${head(recs[0], 0)}<div class="pgrid">${recs[0].items.map((it) =>
        pcard(it, { rank: it.rank, hit: ad.revealed && it.is_target })).join("")}</div></div>`
    : `<div class="recs-cols">${recs.map((r, i) => `<div class="recs-col ${i ? "" : "me"}">${head(r, i)}
        <ol class="plist">${r.items.map((it) => `<li>${prow(it, ad.revealed && it.is_target)}</li>`).join("")}</ol></div>`).join("")}</div>`;
  renderAnswer();
  renderNeighbors();
}

// Đáp án: những món khách thật sự mua sau ngày dự đoán, kèm vị trí của từng món trong danh sách của từng mô hình.
function renderAnswer() {
  const box = $("sh-answer"), recs = ad.recs;
  if (!ad.revealed || !recs[0].evaluation) { box.classList.add("hidden"); return; }
  const rankOf = recs.map((r) => Object.fromEntries(r.targets.map((t) => [t.item_idx, t.rank])));
  const saved = recs.filter((r) => r.evaluation.final && !r.evaluation.final.match)
    .map((r) => `${show(r.model)}: theo kết quả đã lưu của đánh giá cuối, vị trí ${num(r.evaluation.final.rank)}.`);
  box.innerHTML = `<h3>Sau ${vnDate(CTX.test_start)}, khách mua ${recs[0].targets.length} món mới</h3>
    <div class="strip">${recs[0].targets.map((t) => pcard(t, { extra: `<span class="chips">${recs.map((r, i) =>
      `<span class="rchip ${rankOf[i][t.item_idx] <= ad.k ? "in" : ""}">${esc(show(r.model))} #${num(rankOf[i][t.item_idx])}</span>`).join("")}</span>` })).join("")}</div>
    ${saved.length ? `<p class="note">${saved.map(esc).join(" ")}</p>` : ""}`;
  box.classList.remove("hidden");
}

// Khách có gu giống (UserKNN): 5 khách gần nhất, món mua chung; sau khi lật đáp án, đánh dấu khách đã mua món mà khách
// đang xem sẽ mua — đây là cách lọc cộng tác chọn ra khuyến nghị.
async function loadNeighbors(uid, seq) {
  const card = $("sh-nb-card");
  ad.nb = null;
  if (!CTX.has_neighbors) { card.classList.add("hidden"); return; }
  try {
    const res = await api(`/users/${uid}/neighbors?k=6`);
    if (seq !== ad.seq) return;
    ad.nb = res.neighbors;
  } catch { ad.nb = null; }
  renderNeighbors();
}

function renderNeighbors() {
  const card = $("sh-nb-card");
  if (!ad.nb || !ad.nb.length) { card.classList.add("hidden"); return; }
  card.classList.remove("hidden");
  $("sh-nb").innerHTML = ad.nb.map((n) => `<div class="nb">${avatar(n.customer_id)}
    <div><div class="nb-id">Khách ${esc(n.customer_id.slice(0, 8))}…</div>
      <div class="nb-meta">mua chung ${num(n.n_common)} món · đã mua ${num(n.train_count)} món</div>
      <div class="nb-items">${n.common_items.map((it) => `<span title="${esc(it.prod_name)}">${esc(it.prod_name)} <i>(${esc(typeOf(it))})</i></span>`).join("")}</div>
      ${ad.revealed && n.bought_target.length ? `<div class="nb-hit">✓ Đã mua món khách này mua sau đó: ${n.bought_target.map((it) => esc(it.prod_name)).join(", ")}</div>` : ""}
    </div></div>`).join("");
}

// Thẻ chi tiết sản phẩm: thông tin, mô tả, vị trí trong khuyến nghị của khách đang xem, sản phẩm tương tự theo ItemKNN.
async function openProduct(item) {
  const dlg = $("product");
  if (!dlg.open) dlg.showModal();
  $("pd-body").innerHTML = '<p class="note">Đang tải…</p>';
  let res;
  try { res = await api(`/items/${item}/similar?k=6`); } catch (e) {
    $("pd-body").innerHTML = `<div class="error">${esc(e.message)}</div>`;
    return;
  }
  const it = res.item;
  const inRecs = (ad.recs || []).map((r) => {
    const x = r.items.find((y) => y.item_idx === it.item_idx);
    return x ? `${show(r.fallback ? "Khuyến nghị phổ biến" : r.model)} xếp #${x.rank}` : null;
  }).filter(Boolean);
  const bought = ad.hist && ad.hist.items.some((y) => y.item_idx === it.item_idx);
  const later = ad.revealed && ad.recs && ad.recs[0].targets.some((t) => t.item_idx === it.item_idx);
  const kv = [["Loại", typeOf(it)], ["Nhóm hàng", DS === "hm" ? GROUP_VI[it.product_group_name] || it.product_group_name : it.index_group_name],
    DS === "hm" ? ["Màu", it.colours || `${it.n_colours} màu`] : ["Thông tin", it.subtitle],
    ["Số khách đã mua", `${num(res.buyers)} (trước ${vnDate(CTX.test_start)})`]];
  $("pd-body").innerHTML = `<div class="pd-top">
      <div class="pd-img">${media(it)}</div>
      <div class="pd-info"><span class="eyebrow">${esc(DS === "hm" ? areaLabel(it.index_group_name) : it.index_group_name)}</span>
        <h2>${esc(it.prod_name)}</h2>
        <dl class="pd-kv">${kv.map(([k, v]) => `<dt>${k}</dt><dd>${esc(v)}</dd>`).join("")}</dl>
        ${it.description ? `<p class="pd-desc">${esc(it.description)}</p><span class="note">Mô tả gốc của H&amp;M (tiếng Anh)</span>` : ""}
        ${bought ? '<div class="pd-flag">Khách đang xem đã mua món này trước đây.</div>' : ""}
        ${later ? '<div class="pd-flag good">Khách đang xem mua món này sau ngày dự đoán.</div>' : ""}
        ${inRecs.length ? `<div class="pd-ranks">Trong khuyến nghị cho khách đang xem: ${esc(inRecs.join(" · "))}</div>` : ""}
      </div></div>
    <h3>Sản phẩm tương tự</h3>
    <p class="note">Lọc cộng tác theo sản phẩm (ItemKNN): những món thường được cùng nhóm khách mua.</p>
    <div class="pgrid small">${res.similar.map((s) => pcard(s, { extra: `<span class="pdate">độ giống ${vi(s.similarity, 2)}</span>` })).join("")}</div>`;
  $("pd-body").scrollTop = 0;
}

/* ------------------------------------------------------------ dashboard */
function body(block, render) {
  return block.status === "ok" ? render(block.data) : `<div class="missing">${esc(block.message)}</div>`;
}
function chart(id, config) {
  const el = $(id);
  if (el) charts.push(new Chart(el, config));
}

const pct = (x, d = 1) => (x == null ? "—" : `${(100 * Number(x)).toFixed(d)}%`);

function sigTable(rows) {
  const said = (r) => (r.verdict === "không khác biệt có ý nghĩa" ? "ngang nhau"
    : r.verdict === "A tốt hơn" ? `${show(r.A)} tốt hơn` : r.verdict === "B tốt hơn" ? `${show(r.B)} tốt hơn` : r.verdict);
  return `<div class="scroll"><table class="sig"><tr><th>So sánh</th><th>NDCG@10</th><th>Chênh lệch</th><th>Kết luận</th></tr>${rows.map((r) => `<tr>
    <td>${esc(show(r.A))} so với ${esc(show(r.B))}</td><td>${fmt(r.mean_A, 4)} so với ${fmt(r.mean_B, 4)}</td>
    <td>${r.rel_diff >= 0 ? "+" : ""}${pct(r.rel_diff)}</td>
    <td class="${r.verdict === "không khác biệt có ý nghĩa" ? "" : "best"}">${esc(said(r))}</td></tr>`).join("")}</table></div>
    <div class="note">Chỉ kết luận "tốt hơn" khi chênh lệch từ 5% trở lên và có ý nghĩa thống kê; còn lại coi là ngang nhau.</div>`;
}

function simpleTable(rows, cols) {
  return `<div class="scroll"><table><tr><th>Mô hình</th>${cols.map(([, label]) => `<th>${esc(label)}</th>`).join("")}</tr>${rows.map((r) =>
    `<tr><td>${esc(show(r.model))}</td>${cols.map(([key, , f]) => `<td>${f(r[key])}</td>`).join("")}</tr>`).join("")}</table></div>`;
}

// Đánh giá theo K: NDCG@10 / @15 / @20 của từng mô hình (cột nhóm, một sắc xanh nhạt -> đậm theo K) + bảng mọi chỉ
// số @K có trong file kết quả (by_k.csv: tính lại từ hạng đã lưu của đánh giá cuối).
const BY_K = [10, 15, 20];
const K_SHADES = ["#8fb0dc", "#4f7fc0", "#1f4785"];
function byKCard(block, note) {
  if (!block) return "";  // máy chủ demo cũ chưa có khối này: bỏ thẻ, không làm hỏng cả dashboard
  return `<div class="card wide"><h2>Khi đổi số khuyến nghị K = 10, 15, 20</h2>${body(block, (rows) => {
    const cols = ["NDCG", "HR"].flatMap((m) => BY_K.map((k) => `${m}@${k}`))
      .filter((c) => rows.some((r) => r[`${c}_mean`] != null));
    return `<canvas id="c-byk"></canvas>
      <div class="scroll"><table><tr><th>Mô hình</th>${cols.map((c) => `<th>${c}</th>`).join("")}</tr>${rows.map((r) =>
        `<tr><td>${esc(show(r.model))}</td>${cols.map((c) => `<td>${fmt(r[`${c}_mean`], 4)}</td>`).join("")}</tr>`).join("")}</table></div>
      <div class="note">Danh sách dài hơn thì dễ chứa món khách mua hơn, nên chỉ so sánh các mô hình ở cùng một K. ${note}</div>`;
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
  const metrics = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@20"];
  const ablName = { "neumf_f": "NeuMF-F (đầy đủ)", "neumf_f-text": "Bỏ vector văn bản", "neumf_f-time": "Bỏ đặc trưng thời gian",
    "neumf_f-user": "Bỏ thông tin khách hàng", "neumf_f-attr": "Bỏ thuộc tính sản phẩm" };
  dash.innerHTML = `
    ${d.dry_run ? '<div class="card wide"><div class="error">Đang hiển thị bản <b>chạy thử</b> (mẫu phát triển, tập xác thực, 1 epoch) — số liệu không có ý nghĩa, chỉ để kiểm tra đường ống.</div></div>' : ""}
    <div class="card wide"><h2>Dữ liệu dùng để chấm</h2><div class="stats">${[
      ["Khách được chấm", num(s.n_test_users)], ["Sản phẩm", num(s.n_items)],
      ["Món khách mua sau mốc", num(s.targets)], ["Sản phẩm xếp hạng cho mỗi khách", num(s.n_candidates)],
    ].map(([l, n]) => `<div class="stat"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("")}</div></div>

    <div class="card wide"><h2>Kết quả của từng mô hình (trung bình ± độ lệch chuẩn qua 5 lần chạy)</h2>${body(d.summary, (rows) => `
      <canvas id="c-final"></canvas>
      <div class="scroll"><table><tr><th>Mô hình</th>${metrics.map((m) => `<th>${m}</th>`).join("")}</tr>${rows.map((r) =>
        `<tr><td>${esc(show(r.model))}${r.supplementary ? "*" : ""}</td>${metrics.map((m) => `<td>${fmt(r[m + "_mean"], 5)} ± ${fmt(r[m + "_std"], 5)}</td>`).join("")}</tr>`).join("")}</table></div>
      ${rows.some((r) => r.supplementary) ? `<div class="note">* Mô hình lai truyền thống (Content + UserKNN + ItemKNN), bổ sung sau đánh giá cuối, không thuộc họ 10 so sánh.</div>` : ""}`)}</div>

    ${byKCard(d.by_k, "")}

    <div class="card wide"><h2>Kiểm định thống kê: NeuMF-F có thật sự hơn không? (NDCG@10)</h2>${body(d.significance, sigTable)}</div>
    ${d.significance_bs ? `<div class="card wide"><h2>So sánh thêm với mô hình lai truyền thống</h2>${body(d.significance_bs, sigTable)}</div>` : ""}

    <div class="card"><h2>Độ phủ và thời gian huấn luyện</h2>${body(d.beyond, (rows) => simpleTable(rows,
      [["coverage10", "Độ phủ", (v) => pct(v)], ["train_min", "Phút / lần chạy", (v) => fmt(v, 1)]]))}</div>
    <div class="card"><h2>Bỏ từng nhóm đặc trưng khỏi NeuMF-F</h2>${body(d.ablation, (rows) => `<div class="scroll"><table>
      <tr><th>Biến thể</th><th>NDCG@10</th><th>Thay đổi</th><th>CI 95% của hiệu</th></tr>${rows.map((r) =>
        `<tr><td>${esc(ablName[r.variant] || r.variant)}</td><td>${fmt(r["NDCG@10"], 5)}</td><td>${r.variant === "neumf_f" ? "—" : (r.rel >= 0 ? "+" : "") + pct(r.rel)}</td>
        <td>${r.variant === "neumf_f" ? "—" : `[${fmt(r.ci_low, 5)}; ${fmt(r.ci_high, 5)}]`}</td></tr>`).join("")}</table></div>`)}</div>`;
  if (d.summary.status === "ok") {
    const rows = d.summary.data;
    chart("c-final", {
      type: "bar",
      data: { labels: rows.map((r) => show(r.model)),
              datasets: [{ label: "NDCG@10 (trung bình qua seed)", data: rows.map((r) => r["NDCG@10_mean"]), backgroundColor: rows.map((r) => (r.model === "NeuMF-F" ? cssVar("--accent") : cssVar("--bar"))), borderRadius: 4 }] },
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

/* ------------------------------------------------------------ tổng quan & kết quả đánh giá */
// Số liệu từ /api/results (file kết quả của lần đánh giá cuối, cùng nguồn với báo cáo) và /api/example (một khách thật mà
// NeuMF-F khuyến nghị trúng còn NeuMF trượt, hạng trùng số đã lưu). Không có số gõ tay ở đây.
let RESULTS = null;
const vi = (x, d) => Number(x).toLocaleString("vi-VN", { minimumFractionDigits: d, maximumFractionDigits: d });
const signedPct = (x) => (x > 0 ? "+" : "") + vi(100 * x, 1) + "%";
const vnDate = (iso) => String(iso || "").split("-").reverse().join("/");
const icon = (id, size = 22) => `<svg width="${size}" height="${size}" aria-hidden="true"><use href="#${id}"/></svg>`;
const errorBox = (e) => `<div class="error">${esc(e.message)}</div>`;

async function getResults() {
  if (!RESULTS) RESULTS = await api("/results");
  return RESULTS;
}

function loadOverview() {
  if (inited.overview) return;
  inited.overview = true;
  getResults().then(renderOverviewText).catch((e) => { $("ov-lede").innerHTML = errorBox(e); });
  api("/example").then(renderExample).catch((e) => {
    $("ov-result").innerHTML = `<div class="big">Chưa có khách ví dụ</div><p class="small">${esc(e.message)}</p>`;
    $("ov-example").innerHTML = errorBox(e);
  });
}

function renderOverviewText(R) {
  const nModels = R.models.length;
  $("ov-eyebrow").textContent = `Hệ thống khuyến nghị · ${CTX.dataset_label}`;
  $("ov-lede").textContent = `Từ lịch sử mua của khách, NeuMF-F xếp hạng khoảng ${num(R.candidates)} sản phẩm `
    + `và khuyến nghị những món khách có khả năng mua sau ngày ${vnDate(R.test_start)}.`;
  $("ov-chips").innerHTML = [
    ["i-users", num(R.users), "khách được đánh giá"], ["i-grid", nModels, "mô hình"],
    ["i-clock", R.seeds, "lần chạy mỗi mô hình"],
  ].map(([ic, n, t]) => `<span class="chip">${icon(ic, 16)}<b class="num">${n}</b> ${t}</span>`).join("");
}

function exampleList(items, hits) {
  return `<ul class="items">${items.map((it) => `<li class="${it.is_target ? "hit" : ""}"><span class="r num">${it.rank}</span>${media(it)}
    <span class="t"><div title="${esc(it.prod_name)}">${esc(it.prod_name)}</div><small>${esc(DS === "hm" ? typeVi(it.product_type_name) : it.product_type_name)}</small></span>
    ${it.is_target ? '<span class="badge">✓ đã mua</span>' : "<span></span>"}</li>`).join("")}</ul>`;
}

async function renderExample(ex) {
  await getResults().catch(() => null);  // số khách của câu kết; trang vẫn vẽ nếu thiếu file kết quả
  const { a, b, k } = ex;
  const p = ex.profile;
  const targets = a.targets;
  const hitRanks = targets.filter((t) => t.rank <= k).map((t) => t.rank);
  const bBest = b.evaluation.rank;
  const shortId = `${ex.customer_id.slice(0, 8)}…`;
  $("ov-result").innerHTML = `
    <div class="row"><span>Ví dụ một khách thật</span><span class="num">Khách ${esc(shortId)}</span></div>
    <div class="big">Khách mua ${targets.length} món mới. Mô hình đặt chúng ở vị trí nào trong danh sách khuyến nghị?</div>
    <div class="vs">
      <div class="win"><span>${esc(ex.model_a)}</span><b class="num">${hitRanks.map((r) => "#" + r).join(" · ")}</b>
        <small>${hitRanks.length === targets.length ? `Cả ${targets.length === 2 ? "hai" : targets.length} lọt` : `${hitRanks.length}/${targets.length} lọt`} top ${k}</small></div>
      <div><span>${esc(ex.model_b)}</span><b class="num">#${num(bBest)}</b><small>Không lọt top ${k}</small></div>
    </div>`;
  const area = p.area ? ` · mua nhiều nhất ở ${areaLabel(p.area).toLowerCase()}` : "";
  const age = p.age != null ? `${Math.round(p.age)} tuổi` : "";
  $("ov-profile").textContent = [age, area.replace(/^ · /, ""), `${num(p.train_count)} món từ ${vnDate(p.first_date)} đến ${vnDate(p.last_date)}`]
    .filter(Boolean).join(" · ");
  const recent = ex.history.slice(-8);
  $("ov-example").innerHTML = `
    <div class="col"><div class="col-head"><span class="dot"></span><div><h3>Khách đã mua</h3><small>${recent.length} món gần nhất trước ${vnDate(CTX.test_start)}</small></div></div>
      <ul class="items hist">${recent.map((it) => `<li>${media(it)}<span class="t"><div title="${esc(it.prod_name)}">${esc(it.prod_name)}</div>
        <small>${esc(DS === "hm" ? typeVi(it.product_type_name) : it.product_type_name)}</small></span><span class="date num">${vnDate(it.t_dat)}</span></li>`).join("")}</ul>
      ${ex.history.length > recent.length ? `<div class="more">và ${num(ex.history.length - recent.length)} món trước đó</div>` : ""}</div>
    <div class="col"><div class="col-head me"><span class="dot"></span><div><h3>${esc(ex.model_a)} khuyến nghị</h3><small>Mô hình đề xuất</small></div></div>${exampleList(a.items)}</div>
    <div class="col"><div class="col-head"><span class="dot"></span><div><h3>${esc(ex.model_b)} khuyến nghị</h3><small>Mô hình đối chứng</small></div></div>${exampleList(b.items)}</div>`;
  $("ov-outcome").innerHTML = `<span class="ico">${icon("i-bag")}</span><div>
    <p>Sau ngày ${vnDate(CTX.test_start)}, khách mua ${targets.map((t) => `<b>${esc(t.prod_name)}</b>`).join(" và ")}.
      ${esc(ex.model_a)} đặt ${targets.length > 1 ? "các món này" : "món này"} ở <span class="pill good num">vị trí ${targets.map((t) => num(t.rank)).join(" và ")}</span>,
      ${esc(ex.model_b)} đặt món gần nhất ở <span class="pill bad num">vị trí ${num(bBest)}</span>.</p>
</div>`;
  $("ov-outcome").classList.remove("hidden");
}

// ---- Kết quả đánh giá
const VERDICT_PILL = { A: '<span class="pill good">NeuMF-F tốt hơn</span>', B: '<span class="pill bad">NeuMF-F kém hơn</span>', "=": '<span class="pill grey">ngang nhau</span>' };

async function loadResults() {
  if (inited.results) return;
  inited.results = true;
  try { renderResults(await getResults()); } catch (e) { $("rs-lede").innerHTML = errorBox(e); }
}

function renderResults(R) {
  const byKey = Object.fromEntries(R.models.map((m) => [m.key, m]));
  const other = DS === "hm" ? "Amazon Beauty" : "H&M";
  $("rs-eyebrow").textContent = `Bộ dữ liệu ${CTX.dataset_label}`;
  $("rs-lede").textContent = `${num(R.users)} khách · khoảng ${num(R.candidates)} sản phẩm xếp hạng cho mỗi khách · trung bình ${R.seeds} lần chạy.`;

  const me = byKey.neumf_f;
  const max = R.models[0].ndcg10;
  // NeuMF-F so với từng mô hình: NDCG@10 hai bên, chênh lệch tương đối và kết luận kiểm định đã lưu.
  const order = R.models.map((m) => m.key);
  const pairs = R.pairs.filter((p) => p.a === "neumf_f" && byKey[p.b]).sort((x, y) => order.indexOf(x.b) - order.indexOf(y.b));
  const cmp = pairs.map((p) => `<div class="pr">
      <span class="nm">${esc(p.b_name)}</span>
      <span class="bars"><span class="bar me" style="width:${(me.ndcg10 / max) * 100}%"></span><span class="bar" style="width:${(byKey[p.b].ndcg10 / max) * 100}%"></span></span>
      <span class="v num">${vi(byKey[p.b].ndcg10, 4)}</span>
      <span class="d num">${signedPct(p.rel)}</span>${VERDICT_PILL[p.verdict]}</div>`).join("");

  const pos = R.models.findIndex((m) => m.key === "neumf_f") + 1;
  const rank = R.models.map((m, i) => {
    const c = m.key === "neumf_f" ? "me" : (m.key === "random" || m.key === "popularity") ? "ref" : "";
    return `<div class="r ${c}"><span class="i num">${i + 1}</span><span class="nm">${esc(m.name)}${m.supplementary ? "*" : ""}</span>
      <span class="track"><span class="fill" style="width:${(m.ndcg10 / max) * 100}%"></span></span><span class="v num">${vi(m.ndcg10, 4)}</span></div>`;
  }).join("");

  const amax = Math.max(...R.ablation.map((a) => Math.abs(a.rel)));
  const abl = R.ablation.map((a) => `<div class="a ${a.unsure ? "unsure" : ""}"><div class="lab"><span>${esc(a.label)}</span>
    <span class="num">${signedPct(a.rel)}${a.unsure ? ' <span class="pill grey">chưa khẳng định</span>' : ""}</span></div>
    <div class="track"><span class="fill" style="width:${(Math.max(0, -a.rel) / amax) * 100}%"></span></div></div>`).join("");

  $("rs-body").innerHTML = `
    <div class="card cmp-card"><div class="cmp-head"><h2>NeuMF-F so với từng mô hình đối chứng</h2>
        <span class="me-score">NeuMF-F <b class="num">${vi(me.ndcg10, 4)}</b></span></div>
      <div class="pr pr-head"><span>Mô hình đối chứng</span><span></span><span>NDCG@10</span><span>Chênh lệch</span><span>Kiểm định</span></div>
      ${cmp}
      <div class="legend"><span><i style="background:var(--accent)"></i>NeuMF-F</span><span><i style="background:var(--bar)"></i>Mô hình đối chứng</span></div></div>
    <div class="two">
      <div class="card"><h3>Xếp hạng ${R.models.length} mô hình theo NDCG@10</h3>
        <p class="sub">NeuMF-F đứng thứ ${pos}.${R.models.some((m) => m.supplementary) ? " * Mô hình lai truyền thống, bổ sung sau." : ""}</p>
        <div class="rank">${rank}</div></div>
      <div class="card"><h3>Bỏ từng nhóm đặc trưng khỏi NeuMF-F</h3>
        <p class="sub">Mức thay đổi NDCG@10 so với NeuMF-F đầy đủ.</p>
        <div class="abl">${abl}</div></div>
    </div>
    <p class="source"><a href="#/dashboard">Xem bảng số liệu đầy đủ</a> · chuyển sang ${other} ở góc trên để xem bộ dữ liệu còn lại.</p>`;
}

init();
