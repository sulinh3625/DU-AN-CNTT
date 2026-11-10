"""Dựng poster đồ án NeuMF-F trên khung mẫu Khoa CNTT TDTU (Poster.pptx).

Cùng bố cục với poster khóa luận của nhóm (Khoa_luan/Report KLTN/build_poster.py). Số liệu lấy từ báo cáo
(Chương 4, macro do scripts/24_report_v2.py sinh) và tong_hop.md mục 3-4; sửa số ở đây khi kết quả đổi.
Chạy: python build_poster.py [đường_dẫn_ra.pptx]
"""
import copy
import io
import os
import sys

import qrcode
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
SRC, OUT = f"{ROOT}/Poster.pptx", sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/Poster_DACNTT.pptx"
REPO_URL = "https://github.com/sulinh3625/DU-AN-CNTT"

# Bảng màu lấy từ khung nền Khoa CNTT: tím mận làm chủ đạo, cam hổ phách làm điểm nhấn
PURPLE = RGBColor(0x4A, 0x1A, 0x45)
ORANGE = RGBColor(0xE0, 0x81, 0x2A)
TINT = RGBColor(0xF7, 0xF1, 0xF6)
TEXT = RGBColor(0x2A, 0x2A, 0x2A)
MUTED = RGBColor(0x66, 0x66, 0x66)
GREY_BAR = RGBColor(0xCD, 0xBF, 0xCB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ROSE = RGBColor(0x8E, 0x5C, 0x60)      # nâu hồng của dải băng tiêu đề trong poster mẫu
FONT = "Arial"
BODY = 21
B = {"bold": True}

prs = Presentation(SRC)
s = prs.slides[0]

# 1. Bỏ nội dung đề tài cũ (bảng + hình), giữ ảnh nền và các ô tiêu đề
for sh in list(s.shapes):
    if sh.has_table or sh.shape_type == 13:
        if sh.shape_type == 13:
            s.part.drop_rel(sh._element.blipFill.blip.rEmbed)
        sh._element.getparent().remove(sh._element)


# 2. Ô tiêu đề: giữ định dạng run đầu, thay chữ
def set_runs(shape, parts, bold=False):
    """parts: list[(text, superscript?)]. Font SVN-Gilroy của mẫu thường không có trên máy in → Arial, bỏ giãn chữ."""
    p = shape.text_frame.paragraphs[0]
    runs = p.runs
    rpr = copy.deepcopy(runs[0]._r.find(qn("a:rPr")))
    rpr.attrib.pop("spc", None)
    rpr.set("b", "1" if bold else "0")
    for tag in ("a:latin", "a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is not None:
            el.set("typeface", FONT)
            el.attrib.pop("panose", None)
    for r in runs:
        p._p.remove(r._r)
    for extra in shape.text_frame.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)
    end = p._p.find(qn("a:endParaRPr"))
    for text, sup in parts:
        if text == "\n":  # ngắt dòng chủ động, tránh tách một cụm từ ra hai dòng
            br = etree.SubElement(p._p, qn("a:br"))
            br.append(copy.deepcopy(rpr))
            continue
        r = etree.SubElement(p._p, qn("a:r"))
        rp = copy.deepcopy(rpr)
        rp.attrib.pop("baseline", None)
        if sup:
            rp.set("baseline", "30000")
        r.append(rp)
        etree.SubElement(r, qn("a:t")).text = text
        if end is not None:
            p._p.remove(end)
            p._p.append(end)


boxes = [sh for sh in s.shapes if sh.has_text_frame]
head = lambda pre: next(b for b in boxes if b.text_frame.text.strip().startswith(pre))
set_runs(head("DỰ ÁN CÔNG N"), [("DỰ ÁN CÔNG NGHỆ THÔNG TIN", False)], bold=True)
set_runs(head("Năm triển kh"), [("Năm triển khai: 2026", False)])
title = head("Đề tài: Phát")
set_runs(title, [("Xây dựng mô hình khuyến nghị lai kết hợp", False), ("\n", False),
                  ("nhân tử hóa ma trận và mạng lưới thần kinh sâu", False)], bold=True)
for r in title.text_frame.paragraphs[0].runs:
    r.font.size = Pt(42)
title.top, title.height = Inches(3.3), Inches(2.1)
authors = head("Nguyễn Hoàng")
set_runs(authors, [("Lê Minh Lý", False), ("1", True), (", Sử Thị Yến Linh", False),
                   ("1", True), (", TS. Hồ Thị Linh", False), ("*", True)])
authors.top = Inches(5.55)
aff = head("1 Sinh viên n")
set_runs(aff, [("1", True), (" Sinh viên ngành Mạng máy tính và Truyền thông dữ liệu, ", False),
               ("*", True), (" GVHD Khoa Công nghệ thông tin", False)])
aff.top, aff.height = Inches(6.6), Inches(1.0)

# 3. QR vào ô "Xem chi tiết" (ô trắng x 18,65–21,97; y 3,65–6,99)
qr = qrcode.QRCode(border=1, box_size=20)
qr.add_data(REPO_URL)
buf = io.BytesIO()
qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
buf.seek(0)
s.shapes.add_picture(buf, Inches(18.96), Inches(3.97), Inches(2.7), Inches(2.7)).name = "QR kho mã nguồn"


# ---------- tiện ích ----------
def textbox(x, y, w, h, name):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tb, tf


def style(run, size=BODY, bold=False, color=TEXT, italic=False):
    f = run.font
    f.name, f.size, f.bold, f.italic = FONT, Pt(size), bold, italic
    f.color.rgb = color


def add_par(tf, segments, size=BODY, align=PP_ALIGN.JUSTIFY, bullet=False, after=6, first=False):
    """segments: str hoặc list[(text, dict style)]"""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(after)
    if isinstance(segments, str):
        segments = [(segments, {})]
    for text, st in segments:
        r = p.add_run()
        r.text = text
        style(r, size=st.get("size", size), bold=st.get("bold", False),
              color=st.get("color", TEXT), italic=st.get("italic", False))
    if bullet:
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Inches(0.38)))
        pPr.set("indent", str(-Inches(0.38)))
        etree.SubElement(pPr, qn("a:buFont")).set("typeface", FONT)
        etree.SubElement(pPr, qn("a:buChar")).set("char", "–")
    return p


def card(x, y, w, h, name, fill=TINT):
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    c.name = name
    c.adjustments[0] = 0.08
    c.fill.solid()
    c.fill.fore_color.rgb = fill
    c.line.fill.background()
    c.shadow.inherit = False
    tf = c.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.15)
    tf.margin_top = tf.margin_bottom = Inches(0.08)
    return c, tf


XL, XR, CW = 2.05, 11.95, 9.35


def ribbon(x, y, text):
    """Tiêu đề mục: dải băng hình mũi nhọn màu nâu hồng, chữ trắng in đậm."""
    w = 0.95 + 0.205 * len(text)
    sh = s.shapes.add_shape(MSO_SHAPE.PENTAGON, Inches(x), Inches(y), Inches(w), Inches(0.62))
    sh.name = f"Tiêu đề {text}"
    sh.fill.solid()
    sh.fill.fore_color.rgb = ROSE
    sh.line.fill.background()
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.margin_left, tf.margin_right, tf.margin_top, tf.margin_bottom = Inches(0.3), Inches(0.2), 0, 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    add_par(tf, [(text, {"bold": True, "color": WHITE, "size": 24})], align=PP_ALIGN.LEFT, after=0, first=True)
    return y + 0.8


def bullets(x, y, w, h, name, items, size=BODY):
    """items: phần tử là list[(text, style)]; phần tử dạng ("+", [...]) là ý con."""
    _, tf = textbox(x, y, w, h, name)
    for i, it in enumerate(items):
        con = isinstance(it, tuple) and it[0] == "+"
        p = add_par(tf, it[1] if con else it, size=size - (2 if con else 0), bullet=True,
                    align=PP_ALIGN.LEFT, after=5, first=(i == 0))
        if con:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(Inches(0.8)))
            pPr.find(qn("a:buChar")).set("char", "+")
    return tf


def anh(path, x, y, w, name, khung=None):
    im = Image.open(path)
    h = w * im.height / im.width
    if khung is not None:
        fr = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x - 0.12), Inches(y - 0.12),
                                Inches(w + 0.24), Inches(h + 0.24))
        fr.name = f"Khung {name}"
        fr.fill.solid()
        fr.fill.fore_color.rgb = WHITE
        fr.line.color.rgb = khung
        fr.line.width = Pt(3)
        fr.shadow.inherit = False
    s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h)).name = name
    return y + h


def chu_thich(x, y, w, text):
    _, tf = textbox(x, y, w, 0.45, f"Chú thích {text[:20]}")
    add_par(tf, [(text, {"size": 15, "color": MUTED, "italic": True})], align=PP_ALIGN.CENTER, first=True)


# ===== CỘT TRÁI: TÓM TẮT, DỮ LIỆU, KẾT QUẢ =====
y = ribbon(XL, 8.6, "TÓM TẮT")
_, tf = textbox(XL, y, CW, 2.9, "Tóm tắt")
add_par(tf, "Hệ khuyến nghị thời trang thường chỉ có lịch sử mua, rất thưa. Đề tài xây dựng NeuMF-F: giữ hai nhánh "
            "nhân tử hóa ma trận (GMF) và mạng nơ-ron sâu (MLP) của NeuMF, hợp nhất sớm, và bổ sung đặc trưng sản "
            "phẩm, khách hàng, thời gian. Trên H&M, NeuMF-F hơn NeuMF chỉ dùng ID 43,8% và hơn mọi mô "
            "hình truyền thống; lợi ích của đặc trưng lặp lại trên Amazon Beauty. Hợp nhất muộn LateFusion-F cao nhất "
            "trên cả hai bộ.",
        size=20, first=True)

y = ribbon(XL, 12.2, "DỮ LIỆU")
bullets(XL, y, CW, 3.2, "Dữ liệu", [
    [("H&M (Kaggle): ", B), ("giao dịch mua 20/09/2018 – 22/09/2020", {})],
    ("+", [("hai mẫu khách tách rời: mẫu phát triển để tinh chỉnh, mẫu kiểm định để kết luận", {})]),
    ("+", [("gộp màu theo mẫu thiết kế, lọc 10-core: 7.994 khách · 6.749 sản phẩm", {})]),
    [("Amazon Beauty 5-core: ", B), ("10.681 khách · 6.069 sản phẩm, dùng để kiểm chứng", {})],
    [("Chia theo thời gian: ", B), ("kiểm thử 8 tuần cuối; xếp hạng toàn bộ khoảng 6.700 ứng viên mỗi khách", {})]],
    size=20)

y = ribbon(XL, 16.3, "KẾT QUẢ THỰC NGHIỆM")
_, tf = textbox(XL, y, CW, 0.45, "Tên biểu đồ")
add_par(tf, [("NDCG@10 của 14 mô hình trên tập kiểm thử H&M", {"bold": True, "size": 18})],
        align=PP_ALIGN.LEFT, first=True)
# Báo cáo Bảng 4.4 / tong_hop.md mục 3.2; xếp tăng dần vì biểu đồ thanh vẽ mục đầu ở dưới cùng
data = [("Random", 0.00098), ("Content", 0.00506), ("Most Popular", 0.02184), ("MLP", 0.02373),
        ("BPR-MF", 0.02661), ("GMF", 0.02695), ("MostPopular-Recent", 0.02760), ("NeuMF", 0.02783),
        ("ItemKNN", 0.02860), ("UserKNN", 0.03114), ("MLP-F", 0.03480), ("GMF-F", 0.03902),
        ("NeuMF-F", 0.04003), ("LateFusion-F", 0.04093)]
CH_H = 6.0
cd = CategoryChartData()
cd.categories = [d[0] for d in data]
cd.add_series("NDCG@10", [v for _, v in data])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(XL), Inches(y + 0.45), Inches(CW), Inches(CH_H), cd)
gf.name = "Biểu đồ NDCG@10"
ch_ = gf.chart
ch_.has_legend = False
ch_.has_title = False
ch_.font.name, ch_.font.size = FONT, Pt(16)
plot = ch_.plots[0]
plot.gap_width = 40
ser = plot.series[0]
# Mọi cột cùng một màu, nhãn như nhau (góp ý GVHD 09/11/2026: không tô nổi mô hình đề xuất, không dùng xám).
for i, (name, v) in enumerate(data):
    pt = ser.points[i]
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = ORANGE
    pt.data_label.position = XL_LABEL_POSITION.OUTSIDE_END
    dtf = pt.data_label.text_frame
    dtf.text = f"{v:.4f}".replace(".", ",")
    style(dtf.paragraphs[0].runs[0], size=16, color=TEXT)
va = ch_.value_axis
va.minimum_scale, va.maximum_scale = 0, 0.047
va.visible = False
va.has_major_gridlines = False
ca = ch_.category_axis
ca.tick_labels.font.size = Pt(16)
ca.tick_labels.font.name = FONT
ca.format.line.color.rgb = RGBColor(0xBF, 0xBF, 0xBF)
_, tf = textbox(XL, y + 0.5 + CH_H, CW, 0.75, "Ghi chú biểu đồ")
add_par(tf, [("Trung bình 5 lần chạy, 3.165 khách. NeuMF-F thấp hơn LateFusion-F 2,2% nhưng không khác biệt có ý "
              "nghĩa (p Holm = 0,735); NeuMF-F hơn có ý nghĩa 7/9 mô hình trong họ so sánh đăng ký trước.",
              {"size": 14, "color": MUTED, "italic": True})], align=PP_ALIGN.LEFT, first=True)

# ===== CỘT PHẢI: MÔ HÌNH ĐỀ XUẤT, KẾT LUẬN =====
y = ribbon(XR, 8.6, "MÔ HÌNH ĐỀ XUẤT: NeuMF-F")
# Sơ đồ gần vuông: để rộng 6,3 in cho chữ trong hình đọc được khi in, ý thiết kế xếp cột hẹp bên phải
W_MH = 6.3
yb = anh(f"{ROOT}/media/poster_mo_hinh.png", XR + 0.15, y + 0.15, W_MH, "Sơ đồ NeuMF-F", khung=ROSE)
bullets(XR + W_MH + 0.5, y + 0.15, CW - W_MH - 0.5, yb - y, "Điểm thiết kế", [
    [("Nhánh GMF: ", B), ("nhân từng phần tử hai vector.", {})],
    [("Nhánh MLP: ", B), ("nối hai vector, qua 3 lớp ReLU.", {})],
    [("Hợp nhất sớm: ", B), ("nối hai đầu ra trước lớp σ.", {})],
    [("Đặc trưng: ", B), ("thuộc tính, mô tả, doanh số theo thời điểm; thông tin khách.", {})],
    [("Top-K ", B), ("theo điểm ŷ; huấn luyện bằng BCE.", {})]],
    size=17)

y = ribbon(XR, yb + 0.5, "KẾT LUẬN")
stats = [("+43,8%", "so với NeuMF chỉ dùng ID trên H&M", PURPLE),
         ("+65,7%", "so với NeuMF chỉ dùng ID trên Amazon", PURPLE),
         ("7/9", "đối thủ NeuMF-F tốt hơn có ý nghĩa (H&M)", PURPLE),
         ("+25,8%", "so với lai truyền thống Hybrid-CBCF (H&M)", PURPLE)]
sw = (CW - 0.25) / 2
for i, (big, lab, col) in enumerate(stats):
    c, ctf = card(XR + (i % 2) * (sw + 0.25), y + (i // 2) * 1.42, sw, 1.3, f"Chỉ số {i}")
    add_par(ctf, [(big, {"bold": True, "color": col, "size": 32})], align=PP_ALIGN.CENTER, after=0, first=True)
    add_par(ctf, [(lab, {"color": TEXT, "size": 15})], align=PP_ALIGN.CENTER, after=0)
y += 2 * 1.42 + 0.12
bullets(XR, y, CW, 24.4 - y, "Kết luận", [
    [("Đặc trưng là phần đóng góp chính: ", B),
     ("NeuMF-F hơn mọi mô hình truyền thống trên cả hai bộ; bỏ đặc trưng thời gian làm NDCG@10 giảm 42,3% "
      "(H&M) và 31,6% (Amazon).", {})],
    [("Hợp nhất sớm chưa hơn từng nhánh: ", B),
     ("NeuMF-F ngang nhánh GMF-F đứng riêng; LateFusion-F cao nhất trên cả hai bộ, trên Amazon NeuMF-F thấp "
      "hơn có ý nghĩa 12,5%.", {})],
    [("Lợi ích của đặc trưng lặp lại trên Amazon Beauty ", B),
     ("dù khác lĩnh vực, không có thông tin khách và không tinh chỉnh lại.", {})],
    [("Đánh giá tin cậy: ", B),
     ("kế hoạch đăng ký trước, tập kiểm thử mở đúng một lần, 5 lần chạy, kiểm định có hiệu chỉnh Holm.", {})]],
    size=19)

# ===== HÀNG DƯỚI CẢ BỀ NGANG: DEMO (ảnh chụp ứng dụng web) =====
Y_DEMO, W_DEMO = 24.55, 8.9
y = ribbon(XL, Y_DEMO, "DEMO ỨNG DỤNG")
lech = (CW - W_DEMO) / 2
yb = anh(f"{ROOT}/media/poster_so_sanh.png", XL + lech, y + 0.05, W_DEMO, "Ảnh so sánh gợi ý", khung=GREY_BAR)
chu_thich(XL, yb + 0.12, CW, "Gợi ý của NeuMF-F cạnh NeuMF cho cùng một khách; món khách thật sự mua được tô xanh")
yb = anh(f"{ROOT}/media/poster_ket_qua.png", XR + lech, y + 0.05, W_DEMO, "Ảnh trang kết quả", khung=GREY_BAR)
chu_thich(XR, yb + 0.12, CW, "Trang kết quả đánh giá: NeuMF-F so với từng mô hình đối chứng")

prs.save(OUT)
print("saved", OUT)
