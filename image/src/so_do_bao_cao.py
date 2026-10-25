"""Sinh hai tệp sơ đồ rồi xuất hình:
- image/so_do_bao_cao.drawio: các hình của báo cáo (PDF chép vào Report DACNTT/media/figures/so_do/, PNG ở image/).
- image/so_do_slide.drawio: các trang cho slide (PNG ở image/slide_*.png).

Nguyên tắc vẽ (tổng hợp từ hướng dẫn vẽ lưu đồ và khung hướng dẫn sơ đồ mạng nơ-ron của Marshall và cộng sự, 2025):
một hướng đọc cho cả hình, không có đường cắt nhau, mỗi khối một tên ngắn và nhiều nhất một dòng phụ, màu chỉ để
phân loại khối (bảng màu ở drawio_kit), có đủ đầu vào và đầu ra, không đặt khung ghi chú trong hình, không in đậm.
Vector, phép toán và kho dữ liệu được vẽ theo quy ước của bài báo NCF, không dùng biểu tượng trang trí.
    python so_do_bao_cao.py
"""
import shutil
from pathlib import Path

from drawio_kit import Trang, b, ghi, xuat

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
BAO_CAO = HERE.parents[1] / "Report DACNTT" / "media" / "figures" / "so_do"


def k(ten: str, phu: str = "") -> str:
    """Nhãn khối: tên, thêm một dòng phụ nếu có."""
    return b(ten) + (f"<br>{phu}" if phu else "")


def doc(t: Trang, ids: list[str]) -> None:
    for a, c in zip(ids, ids[1:]):
        t.mt(a, c, "duoi", "tren")


def ngang(t: Trang, ids: list[str]) -> None:
    for a, c in zip(ids, ids[1:]):
        t.mt(a, c, "phai", "trai")


def sup(a: str, s: str, d: str) -> str:
    return f"{a}<sup>{s}</sup><sub>{d}</sub>"


# ---------------------------------------------------------------- NeuMF và NeuMF-F

def kien_truc(t: Trang, dac_trung: bool) -> None:
    """Khung chung của NeuMF (chỉ dùng mã ID) và NeuMF-F (mã ID + đặc trưng), đọc từ trên xuống.
    Hai đầu vào xếp chồng ở giữa: đường của khách hàng ra hai cột ngoài, đường của sản phẩm vào hai cột trong, nên
    bốn vector nhúng nằm đúng dưới nhánh của mình mà không đường nào cắt nhau."""
    if dac_trung:
        u = t.o("nguon", 200, 0, 220, 44, k("Khách hàng u", "mã ID + đặc trưng khách"))
        i = t.o("nguon", 200, 62, 220, 44, k("Sản phẩm i", "mã ID + đặc trưng sản phẩm"))
    else:
        u = t.vec(254, 22, 8, "xam", nhan="Khách hàng u (one-hot)", vi="tren", onehot=2)
        i = t.vec(254, 80, 8, "xam", nhan="Sản phẩm i (one-hot)", vi="tren", onehot=5)
    Y = 150
    pg = t.vec(80 - 28, Y, 4, "xanh", nhan=sup("p", "G", "u"), vi="trai", rong_nhan=48)
    qg = t.vec(230 - 28, Y, 4, "xanh", nhan=sup("q", "G", "i"), vi="phai", rong_nhan=44)
    qm = t.vec(390 - 28, Y, 4, "tim", nhan=sup("q", "M", "i"), vi="trai", rong_nhan=44)
    pm = t.vec(540 - 28, Y, 4, "tim", nhan=sup("p", "M", "u"), vi="phai", rong_nhan=48)
    t.mt(u, pg, "trai", "tren")
    t.mt(u, pm, "phai", "tren")
    t.mt(i, qg, (0.3, 1), "tren")
    t.mt(i, qm, (0.7, 1), "tren")
    # nhánh GMF: nhân từng phần tử
    nhan = t.o("phep", 142, 215, 26, 26, "⊙", co=15)
    t.mt(pg, nhan, "duoi", "trai")
    t.mt(qg, nhan, "duoi", "phai")
    t.o("chu", 0, 282, 140, 20, "Nhánh GMF", them="align=right;")
    phig = t.vec(155 - 28, 365, 4, "xanh", nhan="φ<sup>G</sup>", vi="phai", rong_nhan=40)
    t.mt(nhan, phig, "duoi", "tren")
    # nhánh MLP: nối rồi qua tháp 3 lớp ẩn
    noi = t.vec(409, 215, 4, "tim", mau_sau="tim", n_sau=4, nhan="nối", vi="trai", rong_nhan=40)
    t.mt(qm, noi, "duoi", (0.25, 0))
    t.mt(pm, noi, "duoi", (0.75, 0))
    l1 = t.o("mlp", 409, 255, 112, 20, "ReLU", co=11)
    l2 = t.o("mlp", 423, 289, 84, 20, "ReLU", co=11)
    l3 = t.o("mlp", 437, 323, 56, 20, "ReLU", co=11)
    t.o("chu", 530, 240, 110, 20, "Nhánh MLP", them="align=left;")
    t.o("chu", 530, 289, 110, 20, "3 lớp ẩn", co=12, them="align=left;")
    phim = t.vec(465 - 14, 365, 2, "tim", nhan="φ<sup>M</sup>", vi="phai", rong_nhan=40)
    doc(t, [noi, l1, l2, l3, phim])
    # hợp nhất sớm, lớp dự đoán
    hn = t.vec(268, 420, 4, "xanh", mau_sau="tim", n_sau=2,
               nhan="Hợp nhất sớm: φ = [φ<sup>G</sup> ; φ<sup>M</sup>]", vi="phai", rong_nhan=230)
    t.mt(phig, hn, "duoi", (0.33, 0))
    t.mt(phim, hn, "duoi", (0.83, 0))
    sg = t.o("phep", 296, 462, 28, 28, "σ", co=15)
    t.o("chu", 330, 466, 230, 20, "Lớp dự đoán: ŷ<sub>ui</sub> = σ(h<sup>T</sup>φ)", co=12, them="align=left;")
    t.mt(hn, sg, "duoi", "tren")
    y = t.o("ketqua", 265, 512, 90, 34, "ŷ<sub>ui</sub>", co=14)
    t.mt(sg, y, "duoi", "tren")
    if dac_trung:
        hl = t.o("xuly", 50, 580, 240, 46, k("Khi huấn luyện", "BCE với nhãn thật y<sub>ui</sub>"))
        kn = t.o("ketqua_hop", 330, 580, 240, 46, k("Khi khuyến nghị", "xếp hạng ứng viên, lấy Top-K"))
        t.mt(y, hl, "trai", "tren")
        t.mt(y, kn, "phai", "tren")


def neumf() -> Trang:
    t = Trang("Kiến trúc NeuMF")
    kien_truc(t, dac_trung=False)
    return t


def mo_hinh() -> Trang:
    t = Trang("Kiến trúc mô hình đề xuất NeuMF-F")
    kien_truc(t, dac_trung=True)
    return t


def hop_nhat() -> Trang:
    """Hai cách hợp nhất trên cùng hai nhánh, hai khung đặt cạnh nhau, cùng đọc từ trên xuống."""
    t = Trang("Hợp nhất sớm và hợp nhất muộn", co_chu=12)
    t.o("phanhe", 0, 0, 300, 320, "(a) Hợp nhất sớm: NeuMF, NeuMF-F")
    g = t.o("xuly", 15, 40, 125, 44, k("Nhánh GMF", "φ<sup>G</sup>"))
    m = t.o("mlp", 160, 40, 125, 44, k("Nhánh MLP", "φ<sup>M</sup>"))
    v = t.vec(108, 122, 4, "xanh", mau_sau="tim", n_sau=2, nhan="nối biểu diễn", vi="phai", rong_nhan=100)
    t.mt(g, v, "duoi", (0.33, 0))
    t.mt(m, v, "duoi", (0.83, 0))
    p = t.o("chinh", 60, 170, 180, 40, k("Một lớp dự đoán chung"))
    t.mt(v, p, "duoi", "tren")
    ya = t.o("ketqua", 105, 236, 90, 34, "ŷ<sub>ui</sub>", co=13)
    t.mt(p, ya, "duoi", "tren")
    t.o("chu", 0, 284, 300, 20, "<i>một mạng, huấn luyện chung</i>")
    t.o("phanhe", 320, 0, 300, 320, "(b) Hợp nhất muộn: LateFusion-F")
    g2 = t.o("xuly", 335, 40, 125, 44, k("Mô hình GMF-F", "điểm s<sup>G</sup>"))
    m2 = t.o("mlp", 480, 40, 125, 44, k("Mô hình MLP-F", "điểm s<sup>M</sup>"))
    n1 = t.o("nguon", 335, 110, 125, 36, "chuẩn hoá min–max")
    n2 = t.o("nguon", 480, 110, 125, 36, "chuẩn hoá min–max")
    t.mt(g2, n1, "duoi", "tren")
    t.mt(m2, n2, "duoi", "tren")
    tr = t.o("chinh", 380, 170, 180, 40, k("Trộn điểm") + "<br>w·s̃<sup>G</sup> + (1 − w)·s̃<sup>M</sup>")
    t.mt(n1, tr, "duoi", (0.2, 0))
    t.mt(n2, tr, "duoi", (0.8, 0))
    yb = t.o("ketqua", 425, 236, 90, 34, "ŷ<sub>ui</sub>", co=13)
    t.mt(tr, yb, "duoi", "tren")
    t.o("chu", 320, 284, 300, 20, "<i>hai mạng, huấn luyện riêng</i>")
    return t


# ---------------------------------------------------------------- quy trình

def tong_quan_bc() -> Trang:
    """Bốn bước thực hiện đề tài (Chương 1), đọc từ trái sang phải."""
    t = Trang("Các bước thực hiện đề tài")
    buoc = [("xuly", "1. Nghiên cứu tài liệu", "NCF, mô hình lai"),
            ("xuly", "2. Xử lý dữ liệu", "lấy mẫu, lọc, đặc trưng"),
            ("chinh", "3. Huấn luyện", "NeuMF-F, đối chứng"),
            ("ketqua_hop", "4. Đánh giá", "kiểm định, kiểm chứng")]
    ids = [t.o(loai, n * 200, 0, 165, 54, k(a, c)) for n, (loai, a, c) in enumerate(buoc)]
    ngang(t, ids)
    return t


def duong_ong() -> Trang:
    """Quy trình xử lý của hệ thống, đọc từ trên xuống; các mô hình vào bước huấn luyện từ bên phải."""
    t = Trang("Quy trình xử lý của hệ thống khuyến nghị")
    W, H, D = 260, 48, 78
    ids = [
        t.o("tru", 0, -6, W, 60, k("Dữ liệu H&amp;M", "giao dịch, sản phẩm, khách hàng")),
        t.o("xuly", 0, D, W, H, k("Tiền xử lý", "gộp màu, lọc 10-core")),
        t.o("xuly", 0, 2 * D, W, H, k("Đặc trưng", "tính tại mốc τ")),
        t.o("mohinh", 0, 3 * D, W, H, k("Huấn luyện", "dữ liệu trước mốc τ")),
        t.o("tru", 0, 4 * D - 6, W, 60, k("Mô hình đã lưu")),
        t.o("ketqua", 10, 5 * D + 2, W - 20, 54, k("Khuyến nghị Top-K", "cho giai đoạn sau τ")),
    ]
    doc(t, ids)
    mh = t.o("chinh", W + 50, 3 * D, 190, H, k("NeuMF-F", "và các mô hình đối chứng"))
    t.mt(mh, ids[3], "trai", "phai")
    return t


def du_lieu() -> Trang:
    """Bốn bước xử lý dữ liệu H&M; danh mục sản phẩm vào ở bước gộp màu; ra hai mẫu khách hàng."""
    t = Trang("Quy trình xử lý dữ liệu H&M")
    X, W, H, D = 110, 260, 44, 72
    g = t.o("tru", X, -8, W, 58, k("Giao dịch H&amp;M", "31,8 triệu giao dịch"))
    s1 = t.o("xuly", X, D, W, H, k("1. Lấy mẫu theo khách hàng"))
    s2 = t.o("xuly", X, 2 * D, W, H, k("2. Gộp màu, gộp cặp"))
    s3 = t.o("xuly", X, 3 * D, W, H, k("3. Lọc 10-core"))
    s4 = t.o("xuly", X, 4 * D, W, H, k("4. Chia theo thời gian"))
    doc(t, [g, s1, s2, s3, s4])
    dm = t.o("tailieu", X + W + 40, 2 * D - 4, 170, 52, k("Danh mục sản phẩm"))
    t.mt(dm, s2, "trai", "phai")
    m1 = t.o("tru_la", 0, 5 * D + 4, 230, 64, k("Mẫu phát triển", "8.039 khách · 6.801 sản phẩm"))
    m2 = t.o("tru_la", 250, 5 * D + 4, 230, 64, k("Mẫu kiểm định", "7.994 khách · 6.749 sản phẩm"))
    t.mt(s4, m1, (0.3, 1), "tren")
    t.mt(s4, m2, (0.7, 1), "tren")
    return t


def thoi_gian() -> Trang:
    """Hai giai đoạn trên cùng một trục thời gian (không theo tỉ lệ), có vạch mốc."""
    t = Trang("Chia dữ liệu theo thời gian", co_chu=12)
    L, V, T, E = 150, 400, 470, 620  # 20/09/2018 | 01/07/2020 | 29/07/2020 | 22/09/2020
    t.o("chu", 0, 12, 140, 44, k("Giai đoạn xác thực", "chọn cấu hình"), them="align=right;")
    t.o("huanluyen", L, 12, V - L, 40, k("huấn luyện"))
    t.o("xacthuc", V, 12, T - V, 40, k("xác thực", "4 tuần"))
    t.o("chu", 0, 82, 140, 44, k("Giai đoạn kiểm thử", "đánh giá cuối"), them="align=right;")
    t.o("huanluyen", L, 82, T - L, 40, k("huấn luyện lại", "gồm cả 4 tuần xác thực"))
    t.o("kiemthu", T, 82, E - T, 40, k("kiểm thử", "8 tuần"))
    t.duong(V, 4, V, 150, net_dut=True)
    t.duong(T, 4, T, 150, net_dut=True)
    t.duong(L - 10, 150, E + 24, 150, mui_ten=True)
    for x in (L, V, T, E):
        t.duong(x, 145, x, 155)
    t.o("chu", L - 45, 158, 90, 18, "20/09/2018", co=11)
    t.o("chu", V - 75, 158, 80, 18, "01/07/2020", co=11, them="align=right;")
    t.o("chu", T - 5, 158, 80, 18, "29/07/2020", co=11, them="align=left;")
    t.o("chu", E - 30, 158, 90, 18, "22/09/2020", co=11)
    t.o("chu", E + 2, 128, 64, 16, "<i>thời gian</i>", co=10)
    return t


def danh_gia() -> Trang:
    """Tinh chỉnh và đánh giá cuối, đọc từ trên xuống; hai khung là hai mẫu khách hàng."""
    t = Trang("Quy trình tinh chỉnh và đánh giá cuối")
    X, W, H = 70, 260, 44
    t.o("phanhe", 0, 0, 400, 150, "Mẫu phát triển · tập xác thực")
    a1 = t.o("mohinh", X, 36, W, H, k("Tinh chỉnh", "cùng ngân sách cho mọi mô hình"))
    a2 = t.o("ketqua", X, 96, W, 44, k("Cấu hình tốt nhất"))
    a3 = t.o("chinh", X, 180, W, H, k("Khoá kế hoạch đánh giá"))
    t.o("phanhe", 0, 254, 400, 290, "Mẫu kiểm định · tập kiểm thử")
    b1 = t.o("mohinh", X, 290, W, H, k("Huấn luyện lại", "5 lần chạy"))
    b2 = t.o("mohinh", X, 354, W, H, k("Xếp hạng mọi ứng viên"))
    b3 = t.o("mohinh", X, 418, W, H, k("Kiểm định thống kê", "Wilcoxon, bootstrap, Holm"))
    b4 = t.o("ketqua", X, 482, W, 44, k("Kết luận"))
    doc(t, [a1, a2, a3, b1, b2, b3, b4])
    return t


def demo() -> Trang:
    """Ba tầng của demo, đọc từ trên xuống: màn hình giao diện, API, kho dữ liệu và mô hình."""
    t = Trang("Kiến trúc ba tầng của hệ thống demo")
    gd = t.o("phanhe", 0, 0, 560, 110, "Giao diện web")
    for n, s in enumerate(("Cửa hàng", "Kết quả đánh giá", "Giới thiệu đề tài")):
        t.cua_so(20 + n * 180, 34, 160, 60, s)
    api = t.o("mohinh", 140, 160, 280, 52, k("API suy luận (FastAPI)", "tra cứu khách, gọi mô hình"))
    t.mt(gd, api, "duoi", "tren", nhan="HTTP/JSON")
    md = t.o("phanhe", 0, 262, 560, 112, "Mô hình và dữ liệu")
    for n, s in enumerate(("Mô hình đã huấn luyện", "Dữ liệu, tập ứng viên", "Kết quả đánh giá cuối")):
        t.o("tru", 20 + n * 180, 296, 160, 62, k(s))
    t.mt(api, md, "duoi", "tren", nhan="nạp một lần")
    return t


# ---------------------------------------------------------------- trang chỉ dùng cho slide

def tong_quan() -> Trang:
    """Quy trình trên một hàng, đọc từ trái sang phải; các mô hình vào bước huấn luyện từ bên dưới."""
    t = Trang("Tổng quan đề tài")
    W, H, D = 150, 56, 186
    ten = [("tru", "Dữ liệu", "H&amp;M, Amazon Beauty"), ("xuly", "Tiền xử lý", "hai mẫu khách hàng"),
           ("xuly", "Đặc trưng", "theo thời điểm"), ("mohinh", "Huấn luyện", "cùng ngân sách"),
           ("mohinh", "Đánh giá cuối", "tập kiểm thử, kiểm định"), ("ketqua", "Khuyến nghị Top-K", "K = 10, 15, 20")]
    ids = [t.o(loai, n * D, 0 if loai != "tru" else -4, W, H if loai != "tru" else H + 8, k(a, c))
           for n, (loai, a, c) in enumerate(ten)]
    ngang(t, ids)
    mh = t.o("chinh", 3 * D - 20, 104, W + 40, H, k("NeuMF-F", "và các mô hình đối chứng"))
    t.mt(mh, ids[3], "tren", "duoi")
    return t


def doi_chung() -> Trang:
    """NeuMF-F được so với ba nhóm mô hình đối chứng."""
    t = Trang("Các mô hình đối chứng")
    me = t.o("chinh", 270, 0, 220, 48, k("NeuMF-F", "mô hình đề xuất"))
    nhom = [("xuly", "Mô hình đơn lẻ", "GMF · MLP<br>GMF-F · MLP-F"),
            ("mlp", "Học máy truyền thống", "Content · ItemKNN · UserKNN<br>BPR-MF · Hybrid-CBCF"),
            ("nguon", "Chuyên biệt cho khuyến nghị", "Most Popular · MostPopular-Recent<br>NeuMF · LateFusion-F · Random")]
    for n, (loai, a, c) in enumerate(nhom):
        g = t.o(loai, n * 260, 110, 240, 76, k(a, c))
        t.mt(me, g, ((0.25, 0.5, 0.75)[n], 1), "tren")
    return t


BAO_CAO_HINH = [("01_duong_ong", duong_ong), ("02_xu_ly_du_lieu", du_lieu), ("03_chia_thoi_gian", thoi_gian),
                ("04_kien_truc_neumf_f", mo_hinh), ("05_tinh_chinh_danh_gia", danh_gia), ("06_kien_truc_demo", demo),
                ("07_kien_truc_neumf", neumf), ("08_hop_nhat", hop_nhat), ("09_cac_buoc", tong_quan_bc)]
SLIDE = [("01_tong_quan", tong_quan), ("02_du_lieu", du_lieu), ("03_chia_thoi_gian", thoi_gian),
         ("04_neumf_f", mo_hinh), ("05_doi_chung", doi_chung), ("06_tinh_chinh_danh_gia", danh_gia),
         ("07_neumf", neumf), ("08_hop_nhat", hop_nhat)]

if __name__ == "__main__":
    f = OUT / "so_do_bao_cao.drawio"
    ghi([fn() for _, fn in BAO_CAO_HINH], f)
    BAO_CAO.mkdir(parents=True, exist_ok=True)
    for i, (ten, _) in enumerate(BAO_CAO_HINH, 1):
        xuat(f, i, OUT / f"bc_{ten}.png", "png")
        xuat(f, i, BAO_CAO / f"bc_{ten}.pdf", "pdf")
        shutil.copy(BAO_CAO / f"bc_{ten}.pdf", OUT / f"bc_{ten}.pdf")
        print("báo cáo", ten)
    f = OUT / "so_do_slide.drawio"
    ghi([fn() for _, fn in SLIDE], f)
    for i, (ten, _) in enumerate(SLIDE, 1):
        xuat(f, i, OUT / f"slide_{ten}.png", "png")
        print("slide", ten)
