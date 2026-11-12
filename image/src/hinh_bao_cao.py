"""Chín hình sơ đồ của báo cáo DACNTT, vẽ lại cho trực quan (11/11/2026), thay các hình bc_* cũ.

Lối vẽ học từ sơ đồ khóa luận của nhóm (Report KLTN/so_do/gen2.py) và kiểu sơ đồ kiến trúc tác tử AI, nhưng mỗi hình
chỉ nói một việc: thẻ bo góc có biểu tượng ô màu (bieu_tuong.py), số thứ tự ở góc thẻ, vùng nền nhạt gom các khối cùng
nhóm, một hướng đọc, không đường nào cắt hình hay cắt nhau. Màu chỉ để phân loại, giống lời văn báo cáo: xám là dữ liệu,
xanh là bước xử lý và nhánh GMF, tím là nhánh MLP, cam là bước chính và phép hợp nhất, xanh lá là kết quả.

Chạy (từ image/src, cần mạng để nạp trình xem draw.io):  python hinh_bao_cao.py
-> ../hinh_bao_cao.drawio (mỗi hình một trang, sửa tay được), ../hinh_*.png, và PDF vector chép vào
   Report DACNTT/media/figures/so_do/hinh_*.pdf mà các chương C1–C3 đang dùng.
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from bieu_tuong import o as bt
from xuat_anh_drawio import xuat

HERE = Path(__file__).resolve().parent
IMAGE = HERE.parent
REPORT = IMAGE.parent / "Report DACNTT"
PDF_DIR = REPORT / "media" / "figures" / "so_do"
OUT = IMAGE / "hinh_bao_cao.drawio"

F = "fontFamily=Segoe UI;"
CHU, PHU, DUONG, BLUE = "#111827", "#4B5563", "#1F3A5F", "#1E6FC2"
MAU = {  # nền, viền của thẻ
    "trang": ("#FFFFFF", "#B8C7D9"), "xam": ("#F6F8FB", "#7A8CA5"), "xanh": ("#FFFFFF", "#1E6FC2"),
    "tim": ("#FFFFFF", "#6A4C93"), "cam": ("#FFF8F1", "#E07B24"), "la": ("#F3FAF4", "#2E7D32"),
    "navy": ("#1F3A5F", "#1F3A5F"),
}
VUNG = {"xanh": ("#F5F8FD", "#8DB3DA"), "cam": ("#FFF8F1", "#EBB07D"), "xam": ("#F7F9FC", "#C3CEDD")}
DAM = {"xam": "#64748B", "xanh": "#1E6FC2", "tim": "#6A4C93", "cam": "#E07B24", "la": "#2E7D32", "navy": "#1F3A5F",
       "trang": "#1E6FC2"}
O_NEN = {"xanh": ("#CFE0FA", "#1E6FC2"), "tim": ("#E2D8F2", "#6A4C93"), "cam": ("#FDD9B5", "#E07B24"),
         "la": ("#D3EDD8", "#2E7D32"), "xam": ("#FFFFFF", "#7A8CA5")}
O_BT = {"trang": "xanh", "navy": "xanh"}  # thẻ trắng và thẻ navy dùng biểu tượng xanh

# ---------------------------------------------------------------------------------------------- macro số liệu
BS = chr(92)
_MACRO = re.compile(re.escape(BS + "csname ") + r"(\S+?)" + re.escape(BS + "endcsname{") + r"(.*)}")
M = {k: v.replace("{,}", ",") for f in ("v2/results_v2_macros.tex", "amazon/results_amazon_macros.tex")
     for k, v in _MACRO.findall((REPORT / "content/tables" / f).read_text(encoding="utf-8"))}


def nhan(t, s="", co=14, mau_phu=PHU):
    return f"<b style='font-size:{co}px'>{t}</b>" + (
        f"<br><span style='font-size:{co - 1.5}px;color:{mau_phu}'>{s}</span>" if s else "")


def vien_(mau):
    return 1.6 if mau in ("trang", "xam") else 2.2


def tren(a, s, d=""):
    return f"{a}<sup>{s}</sup>" + (f"<sub>{d}</sub>" if d else "")


class Trang:
    def __init__(self, ten):
        self.ten, self.cells, self.n, self.geo = ten, [], 0, {}

    def v(self, x, y, w, h, label, style):
        self.n += 1
        cid = f"c{self.n}"
        c = ET.Element("mxCell", id=cid, value=label, style=style, vertex="1", parent="1")
        ET.SubElement(c, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        self.cells.append(c)
        self.geo[cid] = (x, y, w, h)
        return cid

    # ---- hình cơ bản
    def chu(self, x, y, w, h, label, co=13, mau=CHU, them=""):
        return self.v(x, y, w, h, label, F + "text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;"
                      f"align=center;verticalAlign=middle;fontSize={co};fontColor={mau};{them}")

    def hop(self, x, y, w, h, mau="trang", label="", co=13, them=""):
        nen, vien = MAU[mau]
        return self.v(x, y, w, h, label, F + f"rounded=1;arcSize=14;html=1;whiteSpace=wrap;fillColor={nen};"
                      f"strokeColor={vien};strokeWidth={vien_(mau)};fontSize={co};fontColor={CHU};{them}")

    def the(self, x, y, w, h, icon, t, s="", mau="xanh", o=34, co=14, o_mau=None):
        """Thẻ ngang: biểu tượng ô màu bên trái, tên và một dòng phụ bên phải."""
        nen, vien = MAU[mau]
        trang = mau == "navy"
        return self.v(x, y, w, h, nhan(t, s, co, "#D6E2F0" if trang else PHU),
                      F + f"shape=label;html=1;whiteSpace=wrap;rounded=1;arcSize=16;image={bt(icon, o_mau or O_BT.get(mau, mau))};"
                      f"imageWidth={o};imageHeight={o};imageAlign=left;imageVerticalAlign=middle;spacingLeft={o + 14};"
                      f"spacing=9;align=left;verticalAlign=middle;fillColor={nen};strokeColor={vien};strokeWidth={vien_(mau)};"
                      f"fontSize={co};fontColor={'#FFFFFF' if trang else CHU};")

    def the_doc(self, x, y, w, h, icon, t, s="", mau="xanh", o=40, co=14):
        """Thẻ dọc: biểu tượng ô màu ở trên, chữ ở dưới."""
        nen, vien = MAU[mau]
        return self.v(x, y, w, h, nhan(t, s, co), F + f"shape=label;html=1;whiteSpace=wrap;rounded=1;arcSize=12;"
                      f"image={bt(icon, O_BT.get(mau, mau))};imageWidth={o};imageHeight={o};imageAlign=center;imageVerticalAlign=top;"
                      f"spacingTop={o + 12};spacing=8;align=center;verticalAlign=top;fillColor={nen};"
                      f"strokeColor={vien};strokeWidth={vien_(mau)};fontSize={co};fontColor={CHU};")

    def so(self, x, y, n, mau="navy"):
        return self.v(x, y, 26, 26, f"<b>{n}</b>", F + f"ellipse;html=1;fillColor={BLUE};strokeColor=#FFFFFF;"
                      "strokeWidth=2;fontColor=#FFFFFF;fontSize=13;")

    def vung(self, x, y, w, h, label, mau="xanh", net_dut=True, vi="top", canh="left"):
        """Vùng nền nhạt gom các khối cùng nhóm, tên ở góc trên trái (hoặc dưới trái)."""
        nen, vien = VUNG.get(mau, VUNG["xam"])
        return self.v(x, y, w, h, f"<b>{label}</b>", F + f"rounded=1;arcSize=4;html=1;whiteSpace=wrap;fillColor={nen};"
                      f"strokeColor={vien};strokeWidth=1.6;{'dashed=1;dashPattern=7 4;' if net_dut else ''}"
                      f"align={canh};verticalAlign={vi};spacingLeft=12;spacingRight=12;spacingTop=6;spacingBottom=6;fontSize=14;"
                      f"fontColor={DUONG};")

    def vec(self, x, y, n, mau, dam=None, o=16, chuyen=None):
        """Vector vẽ thành dãy ô (quy ước bài báo NCF); dam: chỉ số ô tô đậm của vector one-hot;
        chuyen: màu chuyển sang ở mỗi ô (vector lai = nhúng ID + đặc trưng). Trả về khung bao để nối cạnh."""
        mau = mau if isinstance(mau, list) else [mau] * n
        for k in range(n):
            nen, vien = O_NEN[mau[k]]
            if dam == k:
                nen = vien
            g = f"gradientColor={chuyen};gradientDirection=south;" if chuyen else ""
            self.v(x + k * o, y, o, o, "", f"rounded=0;html=1;fillColor={nen};strokeColor={vien};strokeWidth=1;{g}")
        return self.v(x, y, n * o, o, "", "rounded=0;html=1;fillColor=none;strokeColor=none;")

    def phep(self, cx, cy, label, mau="trang", d=32):
        nen, vien = MAU[mau]
        return self.v(cx - d / 2, cy - d / 2, d, d, f"<b>{label}</b>", F + f"ellipse;html=1;fillColor={nen};"
                      f"strokeColor={vien if mau != 'trang' else DUONG};strokeWidth=2.2;fontSize=17;fontColor={CHU};")

    def ket_qua(self, x, y, w, h, label, co=14):
        nen, vien = MAU["la"]
        return self.v(x, y, w, h, label, F + f"ellipse;html=1;fillColor={nen};strokeColor={vien};strokeWidth=2.2;"
                      f"fontSize={co};fontColor={CHU};")

    def noi(self, a, b, p1, p2, label="", mau=DUONG, pts=None, net_dut=False, dau=True):
        """Cạnh nối hai hình tại hai điểm (toạ độ trang); cạnh giữ liên kết khi kéo thả trong draw.io."""
        def frac(cid, p):
            x, y, w, h = self.geo[cid]
            return round((p[0] - x) / w, 4), round((p[1] - y) / h, 4)
        ex, ey = frac(a, p1)
        nx, ny = frac(b, p2)
        self.n += 1
        st = (F + "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;strokeWidth=2;"
              f"endArrow={'block' if dau else 'none'};endFill=1;endSize=6;fontSize=12.5;labelBackgroundColor=#FFFFFF;"
              f"strokeColor={mau};fontColor={mau};exitX={ex};exitY={ey};entryX={nx};entryY={ny};"
              f"exitDx=0;exitDy=0;entryDx=0;entryDy=0;{'dashed=1;' if net_dut else ''}")
        c = ET.Element("mxCell", id=f"c{self.n}", value=label, style=st, edge="1", parent="1", source=a, target=b)
        g = ET.SubElement(c, "mxGeometry", relative="1", **{"as": "geometry"})
        if pts:
            arr = ET.SubElement(g, "Array", **{"as": "points"})
            for px, py in pts:
                ET.SubElement(arr, "mxPoint", x=str(px), y=str(py))
        self.cells.append(c)

    def xml(self):
        d = ET.Element("diagram", name=self.ten, id=re.sub(r"\W", "", self.ten.lower())[:20] or "p")
        xs = [x + w for x, y, w, h in self.geo.values()]
        ys = [y + h for x, y, w, h in self.geo.values()]
        m = ET.SubElement(d, "mxGraphModel", dx="1000", dy="700", grid="1", gridSize="10", guides="1",
                          tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1",
                          pageWidth=str(int(max(xs)) + 20), pageHeight=str(int(max(ys)) + 20), math="0", shadow="0")
        root = ET.SubElement(m, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")
        root.extend(self.cells)
        return d


# ============================================================================================== C1: các bước
def cac_buoc():
    """Bốn bước xếp dọc, mỗi bước một hàng (đọc dễ hơn bốn thẻ ngang khi thu vào khổ giấy)."""
    t = Trang("Các bước thực hiện đề tài")
    buoc = [("books", "Nghiên cứu tài liệu", "lọc cộng tác, nhân tử hoá ma trận, NeuMF, mô hình lai có đặc trưng"),
            ("filter", "Xử lý dữ liệu", "lấy mẫu theo khách, lọc 10-core, chia theo thời gian, tính đặc trưng"),
            ("brain", "Huấn luyện", "NeuMF-F và các mô hình đối chứng, cùng ngân sách tinh chỉnh"),
            ("scale", "Đánh giá", "đăng ký trước, 5 seed, Wilcoxon, bootstrap, hiệu chỉnh Holm")]
    ids = []
    for k, (ic, a, b) in enumerate(buoc):
        y = 12 + k * 110  # khe 44 giữa hai thẻ cho mũi tên đủ dài
        ids.append(t.the(30, y, 560, 66, ic, a, b, "trang", o=38, co=15.5))
        t.so(17, y - 11, k + 1)
    for k in range(3):
        y1 = 12 + k * 110 + 66
        t.noi(ids[k], ids[k + 1], (310, y1), (310, y1 + 44))
    return t


# ============================================================================================== C2: NeuMF, NeuMF-F
def so_canh(n, mau="navy"):
    """Nhãn số thứ tự đặt trên mũi tên, cùng màu với mũi tên."""
    return (f"<span style='background:{DAM[mau]};color:#fff;border-radius:10px;padding:1px 7px;font-weight:bold;"
            f"font-size:12.5px'>{n}</span>")


def _neumf(t, dac_trung):
    """NeuMF (C2) hoặc NeuMF-F (C3) đọc từ trên xuống, theo lối sơ đồ actor–critic của khóa luận: thẻ trắng viền rõ,
    số thứ tự trên mũi tên, khối hợp nhất nền navy, vòng cập nhật nét đứt xanh lá ở lề phải.
    Hai nhánh đặt cạnh nhau (GMF trái, MLP phải) nên mọi mũi tên đi thẳng xuống, không cắt nhau.
    Năm hàng cách nhau đủ xa để mỗi mũi tên (kể cả đoạn cuối của mũi tên gấp khúc) dài khoảng 40 đơn vị trở lên."""
    XL, XR = 185, 515
    Y1, Y2, Y3, Y4, Y5 = 10, 122, 290, 462, 632  # đỉnh của năm hàng
    hau_to = "-F" if dac_trung else ""
    # hàng 1: đầu vào
    sub_u = "mã ID + đặc trưng khách" if dac_trung else "mã hoá one-hot"
    sub_i = "mã ID + đặc trưng sản phẩm" if dac_trung else "mã hoá one-hot"
    u = t.the(40, Y1, 290, 60, "users", "Khách hàng u", sub_u, "xam", o=34, co=14.5)
    i = t.the(370, Y1, 290, 60, "shirt", "Sản phẩm i", sub_i, "xam", o=34, co=14.5)
    # hàng 2: lớp nhúng / lớp biểu diễn lai (cao 112)
    k2 = t.hop(40, Y2, 620, 112, "cam" if dac_trung else "trang")
    d2 = Y2 - 112
    t.chu(56, 118 + d2, 300, 26, "<b>" + ("Lớp biểu diễn lai" if dac_trung else "Lớp nhúng") + "</b>", 14.5, DUONG,
          them="align=left;")
    if dac_trung:
        x0 = 214
        t.vec(x0, 150 + d2, 4, "xanh")
        t.chu(x0 - 6, 168 + d2, 76, 20, "nhúng ID", 12, PHU)
        t.chu(x0 + 66, 144 + d2, 56, 28, "<b>+ W ·</b>", 15, CHU)
        t.vec(x0 + 124, 150 + d2, 4, "cam")
        t.chu(x0 + 114, 168 + d2, 84, 20, "đặc trưng", 12, PHU)
        t.chu(x0 + 190, 144 + d2, 30, 28, "<b>=</b>", 16, CHU)
        t.vec(x0 + 222, 150 + d2, 4, "xanh", chuyen="#FDD9B5")
        t.chu(x0 + 210, 168 + d2, 88, 20, "vector lai", 12, PHU)
        t.chu(56, 194 + d2, 588, 22, "mỗi nhánh có bảng nhúng ID và ma trận chiếu W riêng", 12.5, PHU)
    else:
        t.vec(150, 150 + d2, 8, "xam", dam=2)
        t.chu(150, 168 + d2, 128, 20, "one-hot", 12, PHU)
        t.chu(284, 144 + d2, 100, 28, "<b>→ tra bảng →</b>", 13.5, CHU)
        t.vec(392, 140 + d2, 4, "xanh")
        t.chu(460, 136 + d2, 170, 24, "vector nhúng cho GMF", 12.5, DAM["xanh"], them="align=left;")
        t.vec(392, 164 + d2, 4, "tim")
        t.chu(460, 160 + d2, 170, 24, "vector nhúng cho MLP", 12.5, DAM["tim"], them="align=left;")
        t.chu(56, 194 + d2, 588, 22, "mỗi nhánh có bảng nhúng riêng, cùng số chiều d", 12.5, PHU)
    t.noi(u, k2, (290, Y1 + 60), (290, Y2), so_canh(1), DUONG)
    t.noi(i, k2, (420, Y1 + 60), (420, Y2), so_canh(1), DUONG)
    # hàng 3: hai nhánh (cao 92)
    d3 = Y3 - 268
    g = t.hop(40, Y3, 290, 92, "xanh")
    t.phep(84, 314 + d3, "⊙", "xanh", d=44)
    t.chu(118, 274 + d3, 206, 80, nhan(f"Nhánh GMF{hau_to}", "nhân từng phần tử<br>" + tren("p", "G", "u") + " ⊙ "
                                       + tren("q", "G", "i"), 14.5), 14.5, CHU, them="align=left;")
    m = t.hop(370, Y3, 290, 92, "tim")
    for k, bw in enumerate((52, 38, 24)):  # tháp ba lớp ẩn thu hẹp dần
        t.v(412 - bw / 2, 288 + d3 + k * 18, bw, 12, "", f"rounded=1;arcSize=40;html=1;fillColor={DAM['tim']};"
            "strokeColor=none;")
    t.chu(448, 274 + d3, 208, 80, nhan(f"Nhánh MLP{hau_to}", "nối [" + tren("p", "M", "u") + " ; " +
                                       tren("q", "M", "i") + "], 3 lớp ẩn ReLU<br>" +
                                       ("64 → 32 → 16 → 8" if dac_trung else "mỗi lớp giảm một nửa"), 14.5), 14.5,
          CHU, them="align=left;")
    t.noi(k2, g, (XL, Y2 + 112), (XL, Y3), so_canh(2, "xanh"), DAM["xanh"])
    t.noi(k2, m, (XR, Y2 + 112), (XR, Y3), so_canh(2, "tim"), DAM["tim"])
    # hàng 4: hợp nhất sớm và lớp dự đoán, nền navy (cao 96); mũi tên trắng bên trong dài 36–38
    hn_k = t.hop(160, Y4, 380, 96, "navy")
    t.chu(176, Y4 + 4, 340, 26, "<b>Hợp nhất sớm, lớp dự đoán</b>", 14.5, "#FFFFFF", them="align=left;")
    hn = t.vec(178, Y4 + 40, 6, ["xanh"] * 4 + ["tim"] * 2)
    t.chu(158, Y4 + 60, 136, 22, "φ = [" + tren("φ", "G") + " ; " + tren("φ", "M") + "]", 12.5, "#D6E2F0")
    sg = t.v(310, Y4 + 31, 34, 34, "<b>σ</b>", F + "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#FDBA74;"
             f"strokeWidth=2.5;fontSize=17;fontColor={CHU};")
    y = t.v(382, Y4 + 30, 142, 36, "<b>ŷ<sub>ui</sub> ∈ (0, 1)</b>", F + "rounded=1;arcSize=50;html=1;"
            f"fillColor=#FFFFFF;strokeColor=#86D49A;strokeWidth=2.5;fontSize=14;fontColor={CHU};")
    t.noi(hn, sg, (274, Y4 + 48), (310, Y4 + 48), mau="#FFFFFF")
    t.noi(sg, y, (344, Y4 + 48), (382, Y4 + 48), mau="#FFFFFF")
    yb = (Y3 + 92 + Y4) / 2 - 20  # chỗ gấp của mũi tên 3, để đoạn cuối dài khoảng 64
    t.noi(g, hn_k, (XL, Y3 + 92), (300, Y4), so_canh(3, "xanh") + " " + tren("φ", "G"), DAM["xanh"],
          pts=[(XL, yb), (300, yb)])
    t.noi(m, hn_k, (XR, Y3 + 92), (400, Y4), so_canh(3, "tim") + " " + tren("φ", "M"), DAM["tim"],
          pts=[(XR, yb), (400, yb)])
    if not dac_trung:
        return t
    # hàng 5: đầu ra; vòng cập nhật trọng số đi ngoài lề phải
    kn = t.the(40, Y5, 290, 60, "list-numbers", "Khi khuyến nghị", "xếp hạng ứng viên, lấy Top-K", "la", o=34,
               co=14.5)
    hl = t.the(370, Y5, 290, 60, "settings", "Khi huấn luyện", "BCE, mỗi cặp dương lấy 8 mẫu âm", "xanh", o=34,
               co=14.5)
    yb = (Y4 + 96 + Y5) / 2 - 16
    t.noi(hn_k, kn, (260, Y4 + 96), (XL, Y5), so_canh(4), DUONG, pts=[(260, yb), (XL, yb)])
    t.noi(hn_k, hl, (440, Y4 + 96), (XR, Y5), so_canh(4), DUONG, pts=[(440, yb), (XR, yb)])
    t.noi(hl, k2, (660, Y5 + 30), (660, Y2 + 56), "", DAM["la"], pts=[(704, Y5 + 30), (704, Y2 + 56)], net_dut=True)
    t.v(712, Y5 + 30, 1, 1, "", "html=1;fillColor=none;strokeColor=none;")  # nới khung bao cho vòng cập nhật
    t.chu(552, Y3 + 104, 144, 26, so_canh(5, "la") + f" <span style='color:{DAM['la']}'>cập nhật trọng số</span>",
          12.5, them="align=right;")
    return t


def _neumf_ngang(t, dac_trung):
    """Bản nằm ngang của hình NeuMF/NeuMF-F cho slide (khổ 16:9): cùng thẻ, cùng màu, cùng số thứ tự với hình dọc
    của báo cáo, đọc từ trái sang phải; GMF hàng trên, MLP hàng dưới nên mọi mũi tên nằm ngang, không cắt nhau.
    Hai bản có cùng toạ độ để trên slide hình NeuMF đổi thành NeuMF-F tại chỗ."""
    YG, YM = 95, 285  # tâm hàng GMF, hàng MLP
    hau_to = "-F" if dac_trung else ""
    co = 17
    # cột 1: đầu vào
    sub_u = "mã ID + đặc trưng" if dac_trung else "mã hoá one-hot"
    u = t.the(0, YG - 36, 220, 72, "users", "Khách hàng u", sub_u, "xam", o=38, co=co)
    i = t.the(0, YM - 36, 220, 72, "shirt", "Sản phẩm i", sub_u, "xam", o=38, co=co)
    # cột 2: lớp nhúng / lớp biểu diễn lai
    k2 = t.hop(280, 30, 330, 320, "cam" if dac_trung else "trang")
    t.chu(296, 40, 300, 30, "<b>" + ("Lớp biểu diễn lai" if dac_trung else "Lớp nhúng") + "</b>", co, DUONG,
          them="align=left;")
    if dac_trung:
        t.vec(381, 100, 4, "xanh", o=32)
        t.chu(381, 130, 128, 24, "nhúng ID", 14, PHU)
        t.chu(381, 156, 128, 28, "<b>+ W ·</b>", 18, CHU)
        t.vec(381, 186, 4, "cam", o=32)
        t.chu(381, 216, 128, 24, "đặc trưng", 14, PHU)
        t.chu(381, 240, 128, 26, "<b>=</b>", 19, CHU)
        t.vec(381, 270, 4, "xanh", o=32, chuyen="#FDD9B5")
        t.chu(381, 300, 128, 24, "vector lai", 14, PHU)
    else:
        t.vec(317, 120, 8, "xam", dam=2, o=32)
        t.chu(317, 150, 256, 24, "one-hot", 14, PHU)
        t.chu(317, 178, 256, 28, "<b>↓ tra bảng nhúng ↓</b>", 15, CHU)
        t.vec(381, 222, 4, "xanh", o=32)
        t.chu(381, 252, 128, 22, "cho GMF", 14, DAM["xanh"])
        t.vec(381, 280, 4, "tim", o=32)
        t.chu(381, 310, 128, 22, "cho MLP", 14, DAM["tim"])
    t.noi(u, k2, (220, YG), (280, YG), so_canh(1), DUONG)
    t.noi(i, k2, (220, YM), (280, YM), so_canh(1), DUONG)
    # cột 3: hai nhánh
    g = t.hop(680, YG - 60, 300, 120, "xanh")
    t.phep(726, YG, "⊙", "xanh", d=48)
    t.chu(762, YG - 54, 212, 108, nhan(f"Nhánh GMF{hau_to}", "nhân từng phần tử", co), co, CHU, them="align=left;")
    m = t.hop(680, YM - 60, 300, 120, "tim")
    for k, bw in enumerate((56, 40, 24)):  # tháp ba lớp ẩn thu hẹp dần
        t.v(726 - bw / 2, YM - 28 + k * 20, bw, 14, "", f"rounded=1;arcSize=40;html=1;fillColor={DAM['tim']};"
            "strokeColor=none;")
    t.chu(762, YM - 54, 212, 108, nhan(f"Nhánh MLP{hau_to}", "nối, 3 lớp ẩn ReLU<br>" +
                                       ("64 → 32 → 16 → 8" if dac_trung else "mỗi lớp giảm một nửa"), co), co, CHU,
          them="align=left;")
    t.noi(k2, g, (610, YG), (680, YG), so_canh(2, "xanh"), DAM["xanh"])
    t.noi(k2, m, (610, YM), (680, YM), so_canh(2, "tim"), DAM["tim"])
    # cột 4: hợp nhất sớm và lớp dự đoán, nền navy
    hn_k = t.hop(1050, 100, 300, 200, "navy")
    t.chu(1066, 108, 270, 30, "<b>Hợp nhất sớm,<br>lớp dự đoán</b>", co, "#FFFFFF", them="align=left;")
    hn = t.vec(1070, 170, 6, ["xanh"] * 4 + ["tim"] * 2, o=22)
    t.chu(1062, 194, 160, 24, "φ = [" + tren("φ", "G") + " ; " + tren("φ", "M") + "]", 14, "#D6E2F0")
    sg = t.v(1240, 161, 40, 40, "<b>σ</b>", F + "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#FDBA74;strokeWidth=2.5;"
             f"fontSize=19;fontColor={CHU};")
    y = t.v(1100, 242, 200, 38, "<b>ŷ<sub>ui</sub> ∈ (0, 1)</b>", F + "rounded=1;arcSize=50;html=1;fillColor=#FFFFFF;"
            f"strokeColor=#86D49A;strokeWidth=2.5;fontSize=16;fontColor={CHU};")
    t.noi(hn, sg, (1202, 181), (1240, 181), mau="#FFFFFF")
    t.noi(sg, y, (1260, 201), (1260, 242), mau="#FFFFFF")
    t.noi(g, hn_k, (980, YG), (1050, 150), so_canh(3, "xanh"), DAM["xanh"], pts=[(1015, YG), (1015, 150)])
    t.noi(m, hn_k, (980, YM), (1050, 230), so_canh(3, "tim"), DAM["tim"], pts=[(1015, YM), (1015, 230)])
    if not dac_trung:
        t.v(1640, 340, 1, 1, "", "html=1;fillColor=none;strokeColor=none;")  # cùng khung bao với bản NeuMF-F
        return t
    # cột 5: đầu ra; vòng cập nhật trọng số đi dưới đáy hình
    kn = t.the(1420, YG - 40, 240, 80, "list-numbers", "Khi khuyến nghị", "xếp hạng, lấy Top-K", "la", o=38, co=co)
    hl = t.the(1420, YM - 40, 240, 80, "settings", "Khi huấn luyện", "BCE, 8 mẫu âm / cặp", "xanh", o=38, co=co)
    t.noi(hn_k, kn, (1350, 150), (1420, YG), so_canh(4), DUONG, pts=[(1385, 150), (1385, YG)])
    t.noi(hn_k, hl, (1350, 230), (1420, YM), so_canh(4), DUONG, pts=[(1385, 230), (1385, YM)])
    t.noi(hl, k2, (1540, YM + 40), (445, 350), "", DAM["la"], pts=[(1540, 380), (445, 380)], net_dut=True)
    t.chu(860, 382, 240, 28, so_canh(5, "la") + f" <span style='color:{DAM['la']}'>cập nhật trọng số</span>", 14)
    return t


def kien_truc_neumf():
    return _neumf(Trang("Kiến trúc NeuMF"), False)


def kien_truc_neumf_f():
    return _neumf(Trang("Kiến trúc mô hình đề xuất NeuMF-F"), True)


def neumf_ngang():
    return _neumf_ngang(Trang("Slide: NeuMF nằm ngang"), False)


def neumf_f_ngang():
    return _neumf_ngang(Trang("Slide: NeuMF-F nằm ngang"), True)


def hop_nhat():
    """Hai khung cạnh nhau, cùng các tầng; khe giữa các tầng 44 để mũi tên đủ dài."""
    t = Trang("Hợp nhất sớm và hợp nhất muộn")

    def khung(x0, ten, a, b, chuan_hoa, giua, cap, icon_a, icon_b):
        t.vung(x0, 6, 320, 420, ten, "xam", net_dut=False)
        ga = t.the(x0 + 16, 46, 138, 56, icon_a, a[0], a[1], "xanh", o=26, co=13)
        gb = t.the(x0 + 166, 46, 138, 56, icon_b, b[0], b[1], "tim", o=26, co=13)
        cx = x0 + 160
        y_tron = 226
        if chuan_hoa:
            na = t.hop(x0 + 26, 146, 118, 36, "xam", "chuẩn hoá min–max", 11.5)
            nb = t.hop(x0 + 176, 146, 118, 36, "xam", "chuẩn hoá min–max", 11.5)
            t.noi(ga, na, (x0 + 85, 102), (x0 + 85, 146), mau=DAM["xanh"])
            t.noi(gb, nb, (x0 + 235, 102), (x0 + 235, 146), mau=DAM["tim"])
            src_a, src_b, ya = na, nb, 182
        else:
            v = t.vec(cx - 48, 166, 6, ["xanh"] * 4 + ["tim"] * 2)
            t.chu(cx + 52, 162, 100, 24, "nối biểu diễn", 11.5, PHU, them="align=left;")
            t.noi(ga, v, (x0 + 85, 102), (cx - 16, 166), pts=[(x0 + 85, 126), (cx - 16, 126)], mau=DAM["xanh"])
            t.noi(gb, v, (x0 + 235, 102), (cx + 32, 166), pts=[(x0 + 235, 126), (cx + 32, 126)], mau=DAM["tim"])
            src_a = src_b = v
            ya = 182
        tron = t.hop(x0 + 50, y_tron, 220, 56, "navy", giua, 13, them="fontColor=#FFFFFF;")
        if chuan_hoa:
            t.noi(src_a, tron, (x0 + 85, ya), (x0 + 85, y_tron), mau=DAM["xanh"])
            t.noi(src_b, tron, (x0 + 235, ya), (x0 + 235, y_tron), mau=DAM["tim"])
        else:
            t.noi(src_a, tron, (cx, ya), (cx, y_tron))
        y = t.ket_qua(cx - 45, y_tron + 100, 90, 36, "<b>ŷ<sub>ui</sub></b>")
        t.noi(tron, y, (cx, y_tron + 56), (cx, y_tron + 100))
        t.chu(x0 + 10, y_tron + 146, 300, 30, f"<i>{cap}</i>", 13, PHU)

    khung(6, "(a) Hợp nhất sớm: NeuMF, NeuMF-F", ("Nhánh GMF", tren("φ", "G")), ("Nhánh MLP", tren("φ", "M")),
          False, "<b>Một lớp dự đoán chung</b>", "một mạng, huấn luyện chung", "math-function", "stack-2")
    khung(346, "(b) Hợp nhất muộn: LateFusion-F", ("GMF-F", "điểm " + tren("s", "G")),
          ("MLP-F", "điểm " + tren("s", "M")), True,
          "<b>Trộn điểm</b><br>w·" + tren("s̃", "G") + " + (1 − w)·" + tren("s̃", "M"),
          "hai mạng, huấn luyện riêng", "math-function", "stack-2")
    return t


# ============================================================================================== C3
def duong_ong():
    t = Trang("Đường ống huấn luyện và đánh giá mô hình")
    ys = [4, 110, 216, 322, 452]  # khe 44; trước bước cuối khe 68 để đặt vạch mốc τ
    the_ = [t.the(110, ys[0], 330, 62, "database", "Dữ liệu H&amp;M", "giao dịch, sản phẩm, khách hàng", "xam"),
            t.the(110, ys[1], 330, 62, "filter", "Tiền xử lý", "gộp màu, lọc 10-core", "trang"),
            t.the(110, ys[2], 330, 62, "adjustments-horizontal", "Xây dựng đặc trưng", "tính tại mốc τ", "trang"),
            t.the(110, ys[3], 330, 62, "device-floppy", "Huấn luyện và lưu mô hình", "dữ liệu trước mốc τ", "trang"),
            t.the(110, ys[4], 330, 62, "list-numbers", "Suy luận Top-K", "khuyến nghị cho giai đoạn sau τ", "la")]
    for k in range(1, 5):
        t.so(99, ys[k] - 10, k)
    for k in range(4):
        t.noi(the_[k], the_[k + 1], (275, ys[k] + 62), (275, ys[k + 1]))
    # vạch mốc τ: phía trên chỉ dùng dữ liệu trước τ, phía dưới là giai đoạn được khuyến nghị
    yt = (ys[3] + 62 + ys[4]) / 2
    t.v(4, yt - 1, 446, 2, "", f"html=1;fillColor=none;strokeColor={DAM['cam']};strokeWidth=2;dashed=1;dashPattern=8 4;")
    t.chu(4, yt - 30, 100, 28, "<b>trước τ</b> ↑", 12.5, DAM["xanh"], them="align=left;")
    t.chu(4, yt + 4, 100, 28, "<b>sau τ</b> ↓", 12.5, DAM["la"], them="align=left;")
    t.chu(452, yt - 13, 70, 26, "<b>mốc τ</b>", 13, DAM["cam"], them="align=left;")
    mh = t.the(530, ys[3], 230, 62, "brain", "NeuMF-F", "và các mô hình đối chứng", "navy")
    t.noi(mh, the_[3], (530, ys[3] + 31), (440, ys[3] + 31), mau=DUONG)
    return t


def xu_ly_du_lieu():
    t = Trang("Quy trình xử lý dữ liệu H&M")
    src = t.the(100, 4, 350, 60, "database", "Giao dịch H&amp;M", "31,8 triệu giao dịch", "xam")
    buoc = [("users", "Lấy mẫu theo khách hàng", "hai mẫu tách rời, không chồng nhau"),
            ("shirt", "Gộp màu, gộp cặp", "một sản phẩm là một mẫu thiết kế"),
            ("filter", "Lọc 10-core", "trên các cặp trước mốc kiểm thử"),
            ("calendar-time", "Chia theo thời gian", "giai đoạn xác thực, giai đoạn kiểm thử")]
    ids = [src]
    for k, (ic, a, b) in enumerate(buoc):
        y = 108 + k * 102  # khe 44 giữa hai thẻ
        ids.append(t.the(100, y, 350, 58, ic, a, b, "trang"))
        t.so(90, y - 9, k + 1, "xanh")
        g = t.geo[ids[k]]
        t.noi(ids[k], ids[k + 1], (275, g[1] + g[3]), (275, y))
    dm = t.the(510, 210, 210, 58, "file-text", "Danh mục sản phẩm", "loại, màu, mẫu thiết kế", "xam")
    t.noi(dm, ids[2], (510, 239), (450, 239))
    # hai đầu ra đối xứng qua trục giữa của cột bước (x = 275), mũi tên đi thẳng xuống giữa mỗi thẻ
    a = t.the(40, 516, 225, 76, "users", "Mẫu phát triển", f"{M['vdata-A-nusers']} khách<br>"
              f"{M['vdata-A-nitems']} sản phẩm", "la", co=14)
    b = t.the(285, 516, 225, 76, "users", "Mẫu kiểm định", f"{M['vdata-B-nusers']} khách<br>"
              f"{M['vdata-B-nitems']} sản phẩm", "la", co=14)
    t.noi(ids[4], a, (152.5, 472), (152.5, 516))
    t.noi(ids[4], b, (397.5, 472), (397.5, 516))
    return t


def chia_thoi_gian():
    """Hai giai đoạn trên một trục thời gian. Không vẽ vạch dọc xuyên qua các thanh: mốc τ ghi ngay dưới ngày trên trục,
    ranh giới hai giai đoạn đã thấy ở mép các thanh."""
    t = Trang("Chia dữ liệu theo thời gian")
    X0, XV, XT, XE = 230, 540, 660, 840
    t.the(4, 26, 210, 52, "settings", "Giai đoạn xác thực", "chọn cấu hình", "trang", o=28, co=13.5, o_mau="la")
    t.the(4, 96, 210, 52, "flask", "Giai đoạn kiểm thử", "đánh giá cuối", "trang", o=28, co=13.5, o_mau="cam")

    def thanh(x1, x2, y, label, nen, vien):
        t.v(x1, y, x2 - x1, 44, label, F + f"rounded=1;arcSize=24;html=1;whiteSpace=wrap;fillColor={nen};"
            f"strokeColor={vien};strokeWidth=1.5;fontSize=13;fontColor={CHU};")
    thanh(X0, XV, 30, "huấn luyện", "#DCE8FF", MAU["xanh"][1])
    thanh(XV, XT, 30, "<b>xác thực</b><br>4 tuần", "#D3F2DF", MAU["la"][1])
    thanh(X0, XT, 100, "huấn luyện lại<br><span style='font-size:11.5px;color:#5B6577'>gồm cả 4 tuần xác thực</span>",
          "#DCE8FF", MAU["xanh"][1])
    thanh(XT, XE, 100, "<b>kiểm thử</b><br>8 tuần", "#FFE1C7", MAU["cam"][1])
    # trục thời gian: một thanh mảnh và một đầu mũi tên tam giác (không dùng cạnh nối nên không có móc ở đầu trục)
    YA = 168
    t.v(X0, YA - 1, XE + 24 - X0, 2, "", f"html=1;fillColor={PHU};strokeColor=none;")
    t.v(XE + 22, YA - 6, 11, 12, "", f"triangle;direction=east;html=1;fillColor={PHU};strokeColor=none;")
    t.chu(XE + 38, YA - 10, 70, 20, "<i>thời gian</i>", 12, PHU, them="align=left;")
    for x, d, moc in [(X0, "20/09/2018", ""), (XV, "01/07/2020", "τ<sub>val</sub>"), (XT, "29/07/2020", "τ<sub>test</sub>"),
                      (XE, "22/09/2020", "")]:
        t.v(x - 1, YA - 6, 2, 12, "", f"html=1;fillColor={PHU};strokeColor=none;")
        t.chu(x - 50, YA + 8, 100, 20, d, 12, PHU)
        if moc:
            t.chu(x - 50, YA + 26, 100, 20, f"<b>{moc}</b>", 13, CHU)
    return t


def tinh_chinh_danh_gia():
    """Các thẻ cách nhau 36 (mũi tên đủ dài); mũi tên vào mẫu kiểm định dừng ở mép vùng để không cắt tên vùng."""
    t = Trang("Quy trình tinh chỉnh và đánh giá cuối")
    H, KHE = 56, 36
    t.vung(10, 6, 420, 36 + 2 * H + KHE + 16, "Mẫu phát triển · tập xác thực", "trang")
    a1 = t.the(40, 42, 360, H, "settings", "Tinh chỉnh", "6 cấu hình mỗi mô hình, cùng ngân sách", "trang")
    a2 = t.the(40, 42 + H + KHE, 360, H, "target-arrow", "Cấu hình tốt nhất", "theo NDCG@10", "trang")
    yk = 42 + 2 * H + KHE + 16 + KHE
    k = t.the(40, yk, 360, H, "lock", "Khoá kế hoạch đánh giá", "đăng ký trước khi mở tập kiểm thử", "trang")
    yv = yk + H + KHE
    yb = [yv + 36 + j * (H + KHE) for j in range(4)]
    v2 = t.vung(10, yv, 420, yb[-1] + H + 16 - yv, "Mẫu kiểm định · tập kiểm thử", "xam")
    b = [t.the(40, yb[0], 360, H, "player-play", "Huấn luyện lại", "5 seed, mọi cặp trước 29/07/2020", "trang"),
         t.the(40, yb[1], 360, H, "list-numbers", "Xếp hạng mọi ứng viên", "cùng tập ứng viên cho mọi mô hình",
               "trang"),
         t.the(40, yb[2], 360, H, "scale", "Kiểm định thống kê", "Wilcoxon, bootstrap, Holm", "trang"),
         t.the(40, yb[3], 360, H, "checks", "Kết luận", "theo tiêu chí cố định", "la")]
    chuoi = [a1, a2, k] + b
    for p_, q in zip(chuoi, chuoi[1:]):
        y1 = t.geo[p_][1] + H
        if q == b[0]:
            t.noi(p_, v2, (220, y1), (220, yv))
        else:
            t.noi(p_, q, (220, y1), (220, t.geo[q][1]))
    return t


def kien_truc_demo():
    """Ba tầng xếp chồng, tên tầng nằm ngang trên nhãn màu ở góc trên trái (không xoay chữ), mũi tên đi thẳng xuống."""
    t = Trang("Kiến trúc ba tầng của hệ thống demo")

    def tang(y, h, ten, mau):
        c = t.vung(10, y, 700, h, "", mau, net_dut=False)
        t.v(28, y + 9, 30 + 7.4 * len(ten), 28, f"<b>{ten}</b>", F + "rounded=1;arcSize=50;html=1;"
            f"fillColor={DAM['navy']};strokeColor=none;fontColor=#FFFFFF;fontSize=14;")
        return c

    def ba_the(y, the_):
        for k, (ic, a, b) in enumerate(the_):
            t.the_doc(28 + k * 228, y + 2, 208, 100, ic, a, b, "trang", o=34, co=13.5)

    t1 = tang(6, 166, "Tầng giao diện", "xam")
    ba_the(56, [("shopping-bag", "Cửa hàng", "chọn khách, so hai danh sách"),
                ("chart-bar", "Kết quả đánh giá", "NeuMF-F với từng đối chứng"),
                ("presentation", "Giới thiệu đề tài", "bài toán, một khách ví dụ")])
    t2 = tang(228, 124, "Tầng API", "xam")
    t.the(180, 278, 360, 60, "server-2", "API suy luận (FastAPI)", "tra cứu khách, gọi mô hình, chỉ suy luận", "trang")
    t3 = tang(408, 166, "Tầng mô hình và dữ liệu", "xam")
    ba_the(458, [("brain", "Mô hình đã huấn luyện", "trọng số của đánh giá cuối"),
                 ("database", "Dữ liệu, tập ứng viên", "dựng lại bằng hàm đánh giá"),
                 ("file-text", "Kết quả đánh giá cuối", "đọc lại, không chấm mới")])
    t.noi(t1, t2, (360, 172), (360, 228), "HTTP/JSON")
    t.noi(t2, t3, (360, 352), (360, 408), "nạp một lần khi khởi động")
    return t


HINH = [("hinh_cac_buoc", cac_buoc), ("hinh_kien_truc_neumf", kien_truc_neumf), ("hinh_hop_nhat", hop_nhat),
        ("hinh_duong_ong", duong_ong), ("hinh_xu_ly_du_lieu", xu_ly_du_lieu), ("hinh_chia_thoi_gian", chia_thoi_gian),
        ("hinh_kien_truc_neumf_f", kien_truc_neumf_f), ("hinh_tinh_chinh_danh_gia", tinh_chinh_danh_gia),
        ("hinh_kien_truc_demo", kien_truc_demo)]

def _du_lieu_ngang(t, nguon, buoc, ra, danh_muc=None):
    """Bản nằm ngang của quy trình xử lý dữ liệu, cho slide: nguồn → bốn bước → đầu ra, đọc từ trái sang phải."""
    co, W_, H_, GAP, YC = 17, 205, 96, 48, 70
    src = t.the(0, YC - H_ / 2, W_, H_, nguon[0], nguon[1], nguon[2], "xam", o=38, co=co)
    ids = [src]
    for k, (ic, a, b) in enumerate(buoc):
        x = (k + 1) * (W_ + GAP)
        ids.append(t.the(x, YC - H_ / 2, W_, H_, ic, a, b, "trang", o=36, co=co))
        t.so(x - 11, YC - H_ / 2 - 11, k + 1)
    for k in range(len(buoc)):
        x1 = (k + 1) * (W_ + GAP) - GAP
        t.noi(ids[k], ids[k + 1], (x1, YC), (x1 + GAP, YC))
    xo = (len(buoc) + 1) * (W_ + GAP)
    if len(ra) == 2:
        for j, (a, b) in enumerate(ra):
            y = YC - 82 + j * 84
            o_ = t.the(xo, y, 250, 76, "users", a, b, "la", o=34, co=co)
            t.noi(ids[-1], o_, (xo - GAP, YC - 20 + j * 40), (xo, y + 38), pts=[(xo - GAP + 12, YC - 20 + j * 40),
                                                                              (xo - GAP + 12, y + 38)])
    else:
        a, b = ra[0]
        o_ = t.the(xo, YC - H_ / 2, 250, H_, "database", a, b, "la", o=36, co=co)
        t.noi(ids[-1], o_, (xo - GAP, YC), (xo, YC))
    if danh_muc:
        x2 = 2 * (W_ + GAP)
        dm = t.the(x2, YC + H_ / 2 + 44, W_, 64, "file-text", danh_muc[0], danh_muc[1], "xam", o=30, co=15)
        t.noi(dm, ids[2], (x2 + W_ / 2, YC + H_ / 2 + 44), (x2 + W_ / 2, YC + H_ / 2))
    t.v(xo + 250, YC + H_ / 2 + 108, 1, 1, "", "html=1;fillColor=none;strokeColor=none;")  # cùng khung bao cho hai bản
    return t


def du_lieu_hm_ngang():
    return _du_lieu_ngang(
        Trang("Slide: xử lý dữ liệu H&M nằm ngang"), ("database", "Giao dịch H&amp;M", "31,8 triệu giao dịch"),
        [("users", "Lấy mẫu theo khách", "hai mẫu tách rời"), ("shirt", "Gộp màu, gộp cặp", "theo mẫu thiết kế"),
         ("filter", "Lọc 10-core", "trước mốc kiểm thử"), ("calendar-time", "Chia theo thời gian", "xác thực, kiểm thử")],
        [("Mẫu phát triển", f"{M['vdata-A-nusers']} khách<br>{M['vdata-A-nitems']} sản phẩm"),
         ("Mẫu kiểm định", f"{M['vdata-B-nusers']} khách<br>{M['vdata-B-nitems']} sản phẩm")],
        ("Danh mục sản phẩm", "loại, màu, mẫu thiết kế"))


def du_lieu_amazon_ngang():
    return _du_lieu_ngang(
        Trang("Slide: xử lý dữ liệu Amazon nằm ngang"), ("perfume", "Amazon Beauty", f"{M['adata-all-rows']} đánh giá"),
        [("calendar-time", "Cắt theo mốc", "chỉ cặp trước 01/01/2014"), ("filter", "Lọc lại 5-core", "thưa hơn H&amp;M"),
         ("clock", "Chia theo thời gian", "xác thực, kiểm thử"), ("lock", "Giữ cấu hình", "chọn trên H&amp;M")],
        [("Dữ liệu đã lọc", f"{M['adata-all-nusers']} khách<br>{M['adata-all-nitems']} sản phẩm")])


def demo_ngang():
    """Bản nằm ngang của kiến trúc ba tầng cho slide: ba tầng là ba cột, đọc từ trái sang phải."""
    t = Trang("Slide: kiến trúc demo nằm ngang")
    cot = [("Giao diện web", "xam", [("shopping-bag", "Cửa hàng", "chọn khách, so hai danh sách"),
                                     ("chart-bar", "Kết quả đánh giá", "NeuMF-F với từng đối chứng"),
                                     ("presentation", "Giới thiệu đề tài", "bài toán, khách ví dụ")]),
           ("API suy luận", "xam", [("server-2", "FastAPI", "tra cứu khách, gọi mô hình, chỉ suy luận")]),
           ("Mô hình, dữ liệu", "xam", [("brain", "Mô hình đã huấn luyện", "trọng số của đánh giá cuối"),
                                        ("database", "Dữ liệu, ứng viên", "dựng lại bằng hàm đánh giá"),
                                        ("file-text", "Kết quả đánh giá", "đọc lại, không chấm mới")])]
    W_, GAP, H_ = 340, 110, 330
    khung = []
    for k, (ten, mau, the_) in enumerate(cot):
        x = k * (W_ + GAP)
        khung.append(t.vung(x, 0, W_, H_, "", mau, net_dut=False))
        t.v(x, 0, W_, 40, f"<b>{ten}</b>", F + f"rounded=1;arcSize=20;html=1;fillColor={DAM['navy']};strokeColor=none;"
            "fontColor=#FFFFFF;fontSize=17;")
        if len(the_) == 1:
            ic, a, b = the_[0]
            t.the(x + 16, 135, W_ - 32, 110, ic, a, b, "trang", o=40, co=17)
        else:
            for j, (ic, a, b) in enumerate(the_):
                t.the(x + 16, 56 + j * 90, W_ - 32, 76, ic, a, b, "trang", o=36, co=17)
    t.noi(khung[0], khung[1], (W_, 190), (W_ + GAP, 190), "HTTP/JSON")
    t.noi(khung[2], khung[1], (2 * W_ + 2 * GAP, 190), (2 * W_ + GAP, 190), "nạp một lần<br>khi khởi động")
    return t



HINH_SLIDE = [("hinh_neumf_ngang", neumf_ngang), ("hinh_neumf_f_ngang", neumf_f_ngang),
              ("hinh_du_lieu_hm_ngang", du_lieu_hm_ngang),
              ("hinh_du_lieu_amazon_ngang", du_lieu_amazon_ngang),
              ("hinh_demo_ngang", demo_ngang)]


def _ghi(ds, path):
    mx = ET.Element("mxfile", host="app.diagrams.net", type="device")
    for _, fn in ds:
        mx.append(fn().xml())
    ET.indent(mx)
    ET.ElementTree(mx).write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    import sys
    chon = sys.argv[1:]  # chỉ xuất PNG của các hình có tên trong danh sách (để sửa nhanh); không có thì xuất hết
    tat_ca = HINH + HINH_SLIDE
    _ghi(tat_ca, OUT)
    print("ok", OUT)
    tam = HERE / "_tam.drawio"
    if chon:
        _ghi([h for h in tat_ca if h[0] in chon], tam)
        xuat(tam, IMAGE, [n for n, _ in tat_ca if n in chon])
    else:
        _ghi(HINH, tam)
        xuat(tam, IMAGE, [n for n, _ in HINH], PDF_DIR)
        _ghi(HINH_SLIDE, tam)
        xuat(tam, IMAGE, [n for n, _ in HINH_SLIDE])
        _ghi([h for h in HINH if h[0] == "hinh_kien_truc_neumf_f"], tam)  # cho poster, nét hơn
        xuat(tam, REPORT / "poster" / "media", ["poster_mo_hinh"], scale=4)
    tam.unlink()
