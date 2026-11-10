"""Dựng slide bảo vệ DACNTT (khoảng 10 phút) theo thứ tự GVHD dặn ở buổi họp 09/11/2026: bài toán và câu hỏi nghiên cứu
-> cơ sở liên quan -> mô hình đề xuất -> quy trình thực nghiệm -> kết quả và phân tích -> demo -> kết luận -> tài liệu
tham khảo; sau đó là slide dự phòng (không trình chiếu, chỉ mở khi hội đồng hỏi).

Mọi con số lấy từ macro do neumf_project/scripts/24_report_v2.py sinh (Report DACNTT/content/tables/*/..._macros.tex) và
từ summary.csv của đánh giá cuối, không gõ tay. Biểu đồ: mọi cột cùng một màu, không tô riêng mô hình đề xuất (góp ý
GVHD). Hình sơ đồ lấy ở image/slide_*.png (sinh bằng image/src/so_do_bao_cao.py), ảnh demo ở poster/media/.
Chạy: python build_slides.py [đường_dẫn_ra.pptx]
"""
import csv
import os
import re
import sys

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.dirname(HERE)
REPO = os.path.dirname(REPORT)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "Slide_DACNTT.pptx")

# ----------------------------------------------------------------------------------------------- số liệu từ báo cáo
BS = chr(92)
MACRO = re.compile(re.escape(BS + "csname ") + r"(\S+?)" + re.escape(BS + "endcsname{") + r"(.*)}")


def macros(path: str) -> dict:
    """Macro của báo cáo -> chữ thường: {,} -> ',', \\% -> %, $-$ -> −, $<$ -> <."""
    raw = dict(MACRO.findall(open(path, encoding="utf-8").read()))
    fix = [("{,}", ","), (BS + "%", "%"), ("$-$", "−"), ("$<$", "<"), ("$", "")]
    out = {}
    for k, v in raw.items():
        for a, b in fix:
            v = v.replace(a, b)
        out[k] = v
    return out


M = {**macros(os.path.join(REPORT, "content/tables/v2/results_v2_macros.tex")),
     **macros(os.path.join(REPORT, "content/tables/amazon/results_amazon_macros.tex"))}


def summary(ds: str) -> list[tuple[str, float]]:
    """(tên, NDCG@10 trung bình 5 seed) của các mô hình đăng ký trước, tăng dần (biểu đồ thanh ngang vẽ từ dưới lên)."""
    with open(os.path.join(REPO, f"neumf_project/outputs/{ds}/final/summary.csv"), encoding="utf-8") as f:
        rows = [(r["name"], float(r["NDCG@10_mean"])) for r in csv.DictReader(f)]
    return sorted(rows, key=lambda r: r[1])


def n_better(p: str) -> str:
    """Số so sánh trong họ 9 so sánh mà NeuMF-F tốt hơn có ý nghĩa, dạng 'a/9'."""
    v = [M[f"{p}sig-{i}-verdict"] for i in range(1, 10)]
    return f"{sum(x == 'A tốt hơn' for x in v)}/{len(v)}"


def vn4(x: float) -> str:
    return f"{x:.4f}".replace(".", ",")


# ----------------------------------------------------------------------------------------------- giao diện
NAVY = RGBColor(0x1B, 0x26, 0x3B)    # nền slide mở đầu / kết thúc, số liệu lớn
INK = RGBColor(0x1F, 0x23, 0x28)
MUTED = RGBColor(0x5B, 0x62, 0x70)
TINT = RGBColor(0xEE, 0xF2, 0xF8)    # nền thẻ
LINE = RGBColor(0xD5, 0xDB, 0xE5)
BAR = RGBColor(0x2A, 0x78, 0xD6)     # cùng màu cột với biểu đồ trong báo cáo
TAG = RGBColor(0x2A, 0x5F, 0xA8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ICE = RGBColor(0xC9, 0xD6, 0xEA)
HEAD, BODY = "Cambria", "Calibri"
W, H = 13.333, 7.5

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
TITLE_ONLY, BLANK = prs.slide_layouts[5], prs.slide_layouts[6]
SLIDES = []  # (slide, nhãn mục) để đánh số trang sau cùng


def paras(tf, items, size=16, color=INK, bold=False, font=BODY, align=PP_ALIGN.LEFT, after=6, bullet=False):
    """items: chuỗi, hoặc danh sách (chữ, tuỳ chọn) cho một đoạn nhiều kiểu chữ."""
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(after)
        for t, o in ([(it, {})] if isinstance(it, str) else it):
            r = p.add_run()
            r.text = t
            f = r.font
            f.name, f.size, f.bold = o.get("font", font), Pt(o.get("size", size)), o.get("bold", bold)
            f.italic = o.get("italic", False)
            f.color.rgb = o.get("color", color)
        if bullet:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(Emu(Inches(0.28))))
            pPr.set("indent", str(-Emu(Inches(0.28))))
            etree.SubElement(pPr, qn("a:buChar")).set("char", "•")


def text(s, x, y, w, h, items, anchor=MSO_ANCHOR.TOP, name=None, **kw):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras(tf, items, **kw)
    if name:
        tb.name = name
    return tb


def card(s, x, y, w, h, fill=TINT, line=None, name=None):
    c = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    c.adjustments[0] = 0.06
    c.fill.solid()
    c.fill.fore_color.rgb = fill
    if line:
        c.line.color.rgb = line
        c.line.width = Pt(1)
    else:
        c.line.fill.background()
    c.shadow.inherit = False
    if name:
        c.name = name
    return c


def image(s, rel, x, y, w=None, h=None, name=None):
    pic = s.shapes.add_picture(os.path.join(REPO, rel), Inches(x), Inches(y),
                               Inches(w) if w else None, Inches(h) if h else None)
    pic.name = name or os.path.basename(rel)
    return pic


def fit(rel, x, y, w, h):
    """Khung (x, y, w, h) giữ tỉ lệ ảnh, căn giữa trong vùng cho trước."""
    from PIL import Image
    iw, ih = Image.open(os.path.join(REPO, rel)).size
    sc = min(w / iw, h / ih)
    return x + (w - iw * sc) / 2, y + (h - ih * sc) / 2, iw * sc, ih * sc


def picture_fit(s, rel, x, y, w, h, name=None):
    fx, fy, fw, fh = fit(rel, x, y, w, h)
    return image(s, rel, fx, fy, fw, fh, name)


def content(title, tag, notes, tx=0.6, tw=W - 1.2, th=0.8):
    """Slide nội dung: nhãn mục nhỏ + tiêu đề (placeholder tiêu đề thật để PowerPoint đọc được dàn ý)."""
    s = prs.slides.add_slide(TITLE_ONLY)
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(tx), Inches(0.62), Inches(tw), Inches(th)
    tf = t.text_frame
    tf.clear()
    tf.margin_left = tf.margin_right = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    paras(tf, [title], size=32, bold=True, font=HEAD, color=INK)
    text(s, tx, 0.3, 6, 0.3, [tag.upper()], size=12, bold=True, color=TAG, name="Nhãn mục")
    s.notes_slide.notes_text_frame.text = notes
    SLIDES.append(s)
    return s


def dark(notes):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = NAVY
    s.notes_slide.notes_text_frame.text = notes
    SLIDES.append(s)
    return s


def stat(s, x, y, w, big, label, name):
    card(s, x, y, w, 1.35, name=f"Thẻ {name}")
    text(s, x + 0.25, y + 0.14, w - 0.5, 0.65, [big], size=34, bold=True, font=HEAD, color=NAVY, name=f"Số {name}")
    text(s, x + 0.25, y + 0.8, w - 0.5, 0.5, [label], size=13, color=MUTED, name=f"Nhãn {name}")


def bar_chart(s, data, x, y, w, h, title):
    cd = CategoryChartData()
    cd.categories = [n for n, _ in data]
    cd.add_series("NDCG@10", [v for _, v in data])
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    gf.name = title
    ch = gf.chart
    ch.has_legend = False
    ch.has_title = False
    ch.font.name, ch.font.size = BODY, Pt(12)
    ch.font.color.rgb = INK
    plot = ch.plots[0]
    plot.gap_width = 45
    plot.vary_by_categories = False
    ser = plot.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = BAR
    for i, (_, v) in enumerate(data):  # nhãn ghi tay để có dấu phẩy thập phân như báo cáo
        dl = ser.points[i].data_label
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
        dl.text_frame.text = vn4(v)
        dl.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
        dl.text_frame.paragraphs[0].runs[0].font.color.rgb = INK
    va = ch.value_axis
    va.visible = False
    va.has_major_gridlines = False
    va.minimum_scale = 0
    va.maximum_scale = max(v for _, v in data) * 1.22
    ca = ch.category_axis
    ca.format.line.color.rgb = LINE
    ca.tick_labels.font.size = Pt(12)
    return gf


# =============================================================================================== 1. Mở đầu
s = dark("Khoảng 20 giây. Chào hội đồng, giới thiệu tên đề tài, hai thành viên và giảng viên hướng dẫn.")
text(s, 0.8, 0.8, 9, 0.4, ["DỰ ÁN CÔNG NGHỆ THÔNG TIN · 2026"], size=14, bold=True, color=ICE)
text(s, 0.8, 1.6, 11.6, 2.2, ["Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu"],
     size=40, bold=True, font=HEAD, color=WHITE, name="Tên đề tài")
text(s, 0.8, 4.2, 11, 0.5, ["Mô hình đề xuất: NeuMF-F, NeuMF có đặc trưng · thử trên H&M và Amazon Beauty"],
     size=20, color=ICE)
text(s, 0.8, 5.3, 11, 1.4, ["Sinh viên: Lê Minh Lý, Sử Thị Yến Linh", "Giảng viên hướng dẫn: TS. Hồ Thị Linh",
                            "Khoa Công nghệ thông tin, Trường Đại học Tôn Đức Thắng"], size=16, color=WHITE, after=4)

# =============================================================================================== 2. Bài toán
s = content("Bài toán và câu hỏi nghiên cứu", "1 · Bài toán",
            "Khoảng 40 giây, nói nhanh. Dữ liệu thời trang chỉ có lịch sử mua, rất thưa. NeuMF chỉ dùng mã nên bỏ phí "
            "thông tin sẵn có. Đề tài thêm đặc trưng vào cả hai nhánh của NeuMF và đặt ba câu hỏi; phần kết quả sẽ trả "
            "lời lần lượt từng câu.")
text(s, 0.6, 1.75, 5.4, 4.8, [
    "Hệ khuyến nghị thời trang thường chỉ có lịch sử mua: ma trận khách–sản phẩm rất thưa.",
    "NeuMF (He và cộng sự, 2017) ghép nhân tử hoá ma trận (GMF) với mạng nơ-ron (MLP) nhưng chỉ dùng mã khách và mã "
    "sản phẩm.",
    "Thông tin sẵn có bị bỏ phí: thuộc tính, mô tả sản phẩm, doanh số theo thời gian, thông tin khách.",
    [("Đề tài: ", {"bold": True}), ("NeuMF-F, đưa các đặc trưng này vào cả hai nhánh của NeuMF.", {})],
], size=17, bullet=True, after=12)
qs = [("Câu hỏi 1", "NeuMF-F có khuyến nghị tốt hơn các mô hình đối chứng được tinh chỉnh đầy đủ không?"),
      ("Câu hỏi 2", "Đặc trưng có giúp không, và nhóm đặc trưng nào đóng góp nhiều nhất?"),
      ("Câu hỏi 3", "Ghép hai nhánh có tốt hơn từng nhánh; nên hợp nhất sớm hay hợp nhất muộn?")]
for i, (h, q) in enumerate(qs):
    y = 1.75 + i * 1.6
    card(s, 6.6, y, 6.13, 1.38, name=f"Thẻ {h}")
    text(s, 6.9, y + 0.17, 5.6, 0.35, [h], size=14, bold=True, color=TAG)
    text(s, 6.9, y + 0.52, 5.6, 0.8, [q], size=17)

# =============================================================================================== 3. Cơ sở liên quan
s = content("Nền tảng: NeuMF hợp nhất hai nhánh", "2 · Cơ sở liên quan",
            "Khoảng 40 giây. NeuMF gồm nhánh GMF (nhân từng phần tử hai vector, tổng quát hoá MF) và nhánh MLP (nối hai "
            "vector rồi qua các lớp ẩn). Hai đầu ra được nối lại trước lớp dự đoán: đó là hợp nhất sớm. Cách khác là "
            "huấn luyện hai mô hình riêng rồi trộn điểm: hợp nhất muộn. Đề tài so cả hai cách.")
picture_fit(s, "image/slide_07_neumf.png", 0.6, 1.65, 6.3, 5.4, "Sơ đồ NeuMF")
text(s, 7.3, 1.8, 5.4, 4.9, [
    [("GMF", {"bold": True}), (": nhân từng phần tử vector khách và vector sản phẩm, dạng tổng quát của nhân tử hoá "
                               "ma trận (Koren và cộng sự, 2009).", {})],
    [("MLP", {"bold": True}), (": nối hai vector rồi qua các lớp ẩn ReLU để học tương tác phi tuyến.", {})],
    [("Hợp nhất sớm", {"bold": True}), (" (NeuMF): nối đầu ra hai nhánh, một lớp dự đoán chung, học chung.", {})],
    [("Hợp nhất muộn", {"bold": True}), (": hai mô hình huấn luyện riêng, trộn điểm theo trọng số (Atrey và cộng sự, "
                                         "2010).", {})],
    [("Hạn chế", {"bold": True}), (": chỉ dùng mã ID, không tận dụng thông tin của khách và sản phẩm.", {})],
], size=17, bullet=True, after=12)

# =============================================================================================== 4. Mô hình đề xuất
s = content("Mô hình đề xuất NeuMF-F", "3 · Mô hình đề xuất",
            "Khoảng 1 phút, nói trực tiếp trên hình. Đi từ trên xuống: khách và sản phẩm gồm mã ID cộng đặc trưng; bốn "
            "vector nhúng; nhánh GMF nhân từng phần tử; nhánh MLP nối rồi qua tháp 64 → 32 → 16 → 8; nối hai đầu ra "
            "(hợp nhất sớm); sigmoid cho điểm trong (0, 1). Huấn luyện bằng BCE với 8 mẫu âm cho mỗi cặp dương, mẫu âm "
            "lấy theo thời điểm (sản phẩm đã ra mắt). Khi khuyến nghị: xếp hạng mọi ứng viên, lấy Top-K. "
            "Nếu máy chiếu nhỏ: dùng Zoom của PowerPoint (View > Zoom) phóng vào từng nhánh khi nói.",
            tx=8.2, tw=4.55, th=1.25)
picture_fit(s, "image/slide_04_neumf_f.png", 0.3, 0.2, 7.6, 7.1, "Sơ đồ NeuMF-F")
text(s, 8.2, 2.15, 4.55, 0.4, ["Đặc trưng thêm vào"], size=18, bold=True, font=HEAD)
text(s, 8.2, 2.65, 4.55, 4.4, [
    [("Sản phẩm", {"bold": True}), (": thuộc tính danh mục, vector mô tả văn bản.", {})],
    [("Thời gian", {"bold": True}), (": doanh số 7, 28, 91 ngày trước, tuổi sản phẩm, tính tại đúng thời điểm mua.",
                                     {})],
    [("Khách hàng", {"bold": True}), (": nhóm tuổi, hội viên (H&M); số ngày từ lần mua gần nhất.", {})],
    [("Huấn luyện", {"bold": True}), (": BCE, mỗi cặp dương lấy 8 mẫu âm, mẫu âm chỉ lấy sản phẩm đã ra mắt.", {})],
    [("Khuyến nghị", {"bold": True}), (": xếp hạng toàn bộ ứng viên, lấy Top-K.", {})],
], size=16, bullet=True, after=10)

# =============================================================================================== 5. Dữ liệu
s = content("Dữ liệu: H&M và Amazon Beauty", "4 · Quy trình thực nghiệm",
            "Khoảng 40 giây. H&M: lấy hai mẫu khách tách rời, gộp màu theo mẫu thiết kế, lọc 10-core, chia theo thời "
            "gian. Mẫu phát triển để tinh chỉnh, mẫu kiểm định để kết luận. Amazon Beauty dùng để kiểm chứng ở lĩnh "
            "vực khác, giữ nguyên cấu hình chọn trên H&M, không tinh chỉnh lại.")
picture_fit(s, "image/slide_02_du_lieu.png", 0.6, 1.6, 6.2, 5.6, "Sơ đồ xử lý dữ liệu H&M")
stat(s, 7.3, 1.75, 2.6, M["vdata-B-nusers"], "khách, mẫu kiểm định H&M", "khách H&M")
stat(s, 10.15, 1.75, 2.6, M["vdata-B-nitems"], "sản phẩm H&M", "sản phẩm H&M")
stat(s, 7.3, 3.35, 2.6, M["adata-all-nusers"], "khách Amazon Beauty", "khách Amazon")
stat(s, 10.15, 3.35, 2.6, M["adata-all-nitems"], "sản phẩm Amazon Beauty", "sản phẩm Amazon")
text(s, 7.3, 5.05, 5.45, 1.8, [
    f"Mỗi khách xếp hạng khoảng {M['vdata-Btest-cand']} ứng viên (H&M), chấm trên {M['vdata-Btest-users']} khách có "
    f"món mua mới.",
    "Amazon Beauty: giữ cấu hình chọn trên H&M, không tinh chỉnh lại.",
], size=15, bullet=True, after=8, color=INK)

# =============================================================================================== 6. Quy trình
s = content("Quy trình: chia theo thời gian, tập kiểm thử mở một lần", "4 · Quy trình thực nghiệm",
            "Khoảng 1 phút, phần cô dặn phải nói rõ. Chia theo thời gian: học trên quá khứ, đoán tương lai. Tinh chỉnh "
            "mọi mô hình cùng ngân sách trên tập xác thực của mẫu phát triển. Khoá kế hoạch đánh giá (đăng ký trước "
            "03/10/2026) rồi mới mở tập kiểm thử, đúng một lần, huấn luyện lại 5 seed. So sánh bằng Wilcoxon, bootstrap, "
            "hiệu chỉnh Holm cho họ 9 so sánh.")
picture_fit(s, "image/slide_03_chia_thoi_gian.png", 0.6, 1.6, 12.13, 2.4, "Sơ đồ chia theo thời gian")
steps = [("1", "Tinh chỉnh", "Mọi mô hình cùng ngân sách, chọn theo NDCG@10 trên tập xác thực (seed 42)."),
         ("2", "Khoá kế hoạch", "Mô hình đề xuất, họ so sánh và độ đo được đăng ký trước ngày 03/10/2026."),
         ("3", "Kiểm thử một lần", f"Huấn luyện lại {M['vdata-run-seeds']} seed, xếp hạng mọi ứng viên, "
                                   "Wilcoxon + Holm.")]
for i, (n, h, d) in enumerate(steps):
    x = 0.6 + i * 4.18
    card(s, x, 4.45, 3.95, 2.45, name=f"Bước {n}")
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.3), Inches(4.7), Inches(0.55), Inches(0.55))
    o.fill.solid()
    o.fill.fore_color.rgb = NAVY
    o.line.fill.background()
    o.name = f"Số bước {n}"
    paras(o.text_frame, [n], size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    text(s, x + 1.05, 4.78, 2.7, 0.45, [h], size=18, bold=True, font=HEAD)
    text(s, x + 0.3, 5.45, 3.4, 1.35, [d], size=15)

# =============================================================================================== 7. Đối chứng
s = content("Mô hình đối chứng", "4 · Quy trình thực nghiệm",
            "Khoảng 20 giây. Ba nhóm đối chứng theo góp ý của cô: mô hình đơn lẻ, học máy truyền thống, chuyên biệt cho "
            "khuyến nghị. LateFusion-F là hợp nhất muộn của chính hai nhánh có đặc trưng.")
picture_fit(s, "image/slide_05_doi_chung.png", 0.6, 1.9, 12.13, 3.4, "Sơ đồ mô hình đối chứng")
text(s, 0.6, 5.75, 12.13, 1.2, [
    "Mọi mô hình dùng cùng dữ liệu, cùng tập ứng viên, cùng 5 seed và cùng mã nguồn đánh giá; chỉ khác bản thân mô "
    "hình và cấu hình chọn trên tập xác thực.",
], size=17, color=MUTED)

# =============================================================================================== 8–9. Kết quả
def ket_qua(ds, p, ten, n_users, cmp_note, notes):
    s = content(f"Kết quả trên {ten}", "5 · Kết quả và phân tích", notes)
    data = summary(ds)
    bar_chart(s, data, 0.45, 1.5, 7.6, 5.35, f"Biểu đồ NDCG@10 {ten}")
    text(s, 0.6, 6.95, 7.4, 0.35, [f"NDCG@10 trên tập kiểm thử, trung bình 5 seed, {n_users} khách"], size=12,
         color=MUTED)
    stat(s, 8.5, 1.65, 4.25, M[f"{p}sig-1-rel"], "NDCG@10 so với NeuMF chỉ dùng ID (có ý nghĩa)", f"{ten} NeuMF")
    stat(s, 8.5, 3.2, 4.25, n_better(p), "so sánh trong họ đăng ký trước NeuMF-F tốt hơn có ý nghĩa", f"{ten} họ")
    card(s, 8.5, 4.75, 4.25, 2.3, name=f"Thẻ ghi chú {ten}")
    text(s, 8.75, 4.92, 3.8, 2.0, cmp_note, size=14, after=6)


late = lambda p: M[f"{p}sig-4-rel"]
ket_qua("v2", "v", "H&M", M["vdata-Btest-users"], [
    [("So với GMF-F: ", {"bold": True}), (f"{M['vsig-2-rel']}, không khác biệt có ý nghĩa.", {})],
    [("So với LateFusion-F: ", {"bold": True}), (f"{late('v')}, không khác biệt có ý nghĩa "
                                                 f"(p Holm = {M['vsig-4-pholm']}).", {})],
], "Khoảng 1 phút. Trả lời câu hỏi 1: NeuMF-F hơn NeuMF chỉ dùng ID 43,8% và tốt hơn có ý nghĩa 7 trong 9 so sánh "
   "đăng ký trước. Nói thẳng: LateFusion-F có NDCG@10 cao nhất nhưng chênh với NeuMF-F không có ý nghĩa; NeuMF-F ngang "
   "GMF-F. Các mô hình có đặc trưng chiếm bốn vị trí đầu.")
ket_qua("amazon", "a", "Amazon Beauty", M["adata-test-users"], [
    [("So với GMF-F: ", {"bold": True}), (f"{M['asig-2-rel']}, không khác biệt có ý nghĩa.", {})],
    [("So với LateFusion-F: ", {"bold": True}), (f"{late('a')}, LateFusion-F tốt hơn có ý nghĩa "
                                                 f"(p Holm {M['asig-4-pholm']}).", {})],
], "Khoảng 45 giây. Cùng cấu hình chọn trên H&M, không tinh chỉnh lại: NeuMF-F vẫn hơn NeuMF chỉ dùng ID 65,7%. "
   "Ở đây LateFusion-F tốt hơn NeuMF-F có ý nghĩa, và NeuMF-F xếp thứ ba, ngang GMF-F. Kết luận về đặc trưng lặp lại; "
   "kết luận về cách hợp nhất thì phụ thuộc dữ liệu.")

# =============================================================================================== 10. Phân tích
s = content("Đặc trưng nào đóng góp nhiều nhất?", "5 · Kết quả và phân tích",
            "Khoảng 40 giây. Trả lời câu hỏi 2. Phân tích bóc tách tắt từng nhóm đặc trưng (seed 42). Bỏ đặc trưng thời "
            "gian làm NDCG@10 giảm mạnh nhất trên cả hai bộ; khoảng tin cậy của hiệu không chứa 0.")
stat(s, 0.6, 1.8, 3.7, M["vabl-AblTime-rel"], "NDCG@10 khi bỏ đặc trưng thời gian, H&M", "bóc tách H&M")
stat(s, 0.6, 3.4, 3.7, M["aabl-AblTime-rel"], "NDCG@10 khi bỏ đặc trưng thời gian, Amazon", "bóc tách Amazon")
text(s, 0.6, 5.1, 3.7, 1.9, ["Mức giảm lớn nhất trong các biến thể trên cả hai bộ dữ liệu. Phân tích chạy một seed nên "
                             "mang tính mô tả."], size=14, color=MUTED)
picture_fit(s, "Report DACNTT/media/figures/v2/v2_ablation.png", 4.8, 1.75, 7.95, 5.3, "Biểu đồ bóc tách H&M")

# =============================================================================================== 11. Hợp nhất sớm hay muộn
s = content("Hợp nhất sớm (NeuMF-F) hay muộn (LateFusion-F)?", "5 · Kết quả và phân tích",
            "Khoảng 1 phút. Trả lời câu hỏi 3, nêu cả hai chiều. Độ chính xác: LateFusion-F cao hơn; trên H&M chênh nhỏ "
            "và không có ý nghĩa, trên Amazon có ý nghĩa. Chi phí: NeuMF-F chỉ huấn luyện một mạng, khoảng một nửa thời "
            "gian; độ phủ top-10 cao hơn. Đây là thời gian huấn luyện; chưa đo thời gian gợi ý nên không nói chạy nhanh "
            "hơn. LateFusion-F chỉnh được trọng số trộn mà không huấn luyện lại.")
picture_fit(s, "image/slide_08_hop_nhat.png", 0.6, 1.65, 5.7, 3.1, "Sơ đồ hợp nhất sớm và muộn")
rows = [("", "NeuMF-F", "LateFusion-F"),
        ("NDCG@10 · H&M", M["vres-NeuMFF-NDCG10"], M["vres-LateF-NDCG10"]),
        ("NDCG@10 · Amazon", M["ares-NeuMFF-NDCG10"], M["ares-LateF-NDCG10"]),
        ("Huấn luyện (phút/seed) · H&M", M["vbey-NeuMFF-time"], M["vbey-LateF-time"]),
        ("Huấn luyện (phút/seed) · Amazon", M["abey-NeuMFF-time"], M["abey-LateF-time"]),
        ("Độ phủ top-10 · H&M", M["vbey-NeuMFF-cov"], M["vbey-LateF-cov"]),
        ("Độ phủ top-10 · Amazon", M["abey-NeuMFF-cov"], M["abey-LateF-cov"])]
tbl = s.shapes.add_table(len(rows), 3, Inches(6.75), Inches(1.65), Inches(5.98), Inches(0.5 * len(rows))).table
tbl.columns[0].width, tbl.columns[1].width, tbl.columns[2].width = Inches(3.1), Inches(1.44), Inches(1.44)
for r, row in enumerate(rows):
    for c, v in enumerate(row):
        cell = tbl.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY if r == 0 else (TINT if r % 2 else WHITE)
        cell.text_frame.clear()
        paras(cell.text_frame, [v], size=14, bold=(r == 0), color=WHITE if r == 0 else INK,
              align=PP_ALIGN.LEFT if c == 0 else PP_ALIGN.RIGHT, after=0)
        cell.margin_left = cell.margin_right = Inches(0.12)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
text(s, 0.6, 5.15, 5.7, 1.9, [
    [("LateFusion-F: ", {"bold": True}), ("độ chính xác cao hơn, chỉnh được trọng số trộn không cần huấn luyện lại.",
                                          {})],
    [("NeuMF-F: ", {"bold": True}), ("một mạng, thời gian huấn luyện thấp hơn, độ phủ cao hơn; đã chốt trong kế "
                                     "hoạch đăng ký trước.", {})],
], size=15, bullet=True, after=8)
text(s, 6.75, 5.35, 5.98, 1.6, ["Thời gian là thời gian huấn luyện trên cùng một máy; thời gian của LateFusion-F là "
                                "tổng GMF-F và MLP-F. Thời gian tạo khuyến nghị chưa được đo. Độ phủ đo ở seed 42."],
     size=13, color=MUTED)

# =============================================================================================== 12. Demo
s = content("Demo: gợi ý cho một khách thật", "6 · Demo",
            "Khoảng 1 phút 30, chạy demo trực tiếp (đã mở sẵn ở localhost:8000). Gõ mã ngắn để mở khách mẫu, bấm "
            "'Xem khách đã mua gì' để lật đáp án. Khách mẫu là ví dụ chọn lọc; kết quả trung bình xem các slide trước.")
picture_fit(s, "Report DACNTT/poster/media/poster_so_sanh.png", 0.6, 1.6, 8.0, 3.3, "Ảnh demo so sánh gợi ý")
text(s, 0.6, 5.1, 8.0, 1.9, [
    "Bên trái luôn là NeuMF-F, bên phải chọn một mô hình đối chứng; ô xanh là món khách thật sự mua sau mốc kiểm thử.",
    "Ảnh sản phẩm lưu sẵn trên máy, demo chạy không cần mạng.",
], size=15, bullet=True, after=8)
card(s, 9.0, 1.6, 3.73, 5.4, name="Thẻ khách mẫu")
text(s, 9.25, 1.8, 3.3, 0.4, ["Khách mẫu (gõ mã ngắn)"], size=16, bold=True, font=HEAD)
# Khách mẫu: NeuMF-F khuyến nghị đúng trong top-10, NeuMF chỉ dùng ID thì không (nút "Xem ví dụ" của demo, 09/11/2026);
# hạng = hạng tốt nhất của món khách thật sự mua.
samples = [("H&M · KH0028", "NeuMF-F hạng 6, NeuMF hạng 2.363"), ("H&M · KH0303", "NeuMF-F hạng 4, NeuMF hạng 558"),
           ("Amazon · KH0376", "NeuMF-F hạng 1, NeuMF hạng 205"), ("Amazon · KH0039", "NeuMF-F hạng 2, NeuMF hạng 221")]
for i, (code, note) in enumerate(samples):
    text(s, 9.25, 2.4 + i * 1.1, 3.3, 1.0, [[(code, {"bold": True})], [(note, {"size": 13, "color": MUTED})]],
         size=17, after=2)
text(s, 9.25, 6.55, 3.3, 0.35, ["Ví dụ chọn lọc, không phải kết quả trung bình."], size=11, color=MUTED)

# =============================================================================================== 13. Kết luận
s = dark("Khoảng 50 giây. Tóm lại ba câu trả lời, hạn chế và hướng phát triển. Kết thúc, cảm ơn hội đồng.")
text(s, 0.8, 0.6, 11, 0.8, ["Kết luận"], size=36, bold=True, font=HEAD, color=WHITE)
cols = [("Kết quả", [f"NeuMF-F hơn NeuMF chỉ dùng ID {M['vsig-1-rel']} (H&M) và {M['asig-1-rel']} (Amazon).",
                     "Đặc trưng thời gian đóng góp nhiều nhất trên cả hai bộ.",
                     "Hợp nhất muộn LateFusion-F cao nhất; cách hợp nhất nên chọn theo dữ liệu."]),
        ("Hạn chế", ["Mẫu khoảng 1,6% khách H&M, lọc 10-core: nhóm khách mua nhiều.",
                     "Chưa đánh giá định lượng cho sản phẩm mới, khách mới (cold start).",
                     "Chưa đo thời gian tạo khuyến nghị."]),
        ("Hướng phát triển", ["Mở rộng dữ liệu, ngưỡng lọc thấp hơn.",
                              "Đánh giá riêng trên sản phẩm vừa ra mắt.",
                              "Ảnh và mô tả bằng mô hình tiền huấn luyện."])]
for i, (h, items) in enumerate(cols):
    x = 0.8 + i * 4.0
    card(s, x, 1.75, 3.75, 4.0, fill=RGBColor(0x26, 0x33, 0x4D), name=f"Thẻ {h}")
    text(s, x + 0.3, 1.98, 3.2, 0.45, [h], size=20, bold=True, font=HEAD, color=WHITE)
    text(s, x + 0.3, 2.6, 3.2, 3.0, items, size=16, color=ICE, bullet=True, after=10)
text(s, 0.8, 6.25, 11.7, 0.5, ["Cảm ơn hội đồng đã lắng nghe."], size=22, bold=True, font=HEAD, color=WHITE)

# =============================================================================================== 14. Tài liệu tham khảo
s = content("Tài liệu tham khảo", "Tài liệu tham khảo",
            "Không cần nói; để màn hình khi hội đồng đặt câu hỏi.")
refs = ["He, X. và cộng sự (2017). Neural Collaborative Filtering. WWW '17, 173–182.",
        "Koren, Y., Bell, R., Volinsky, C. (2009). Matrix Factorization Techniques for Recommender Systems. Computer, "
        "42, 30–37.",
        "Rendle, S. và cộng sự (2009). BPR: Bayesian Personalized Ranking from Implicit Feedback. UAI '09, 452–461.",
        "Atrey, P. K. và cộng sự (2010). Multimodal Fusion for Multimedia Analysis: A Survey. Multimedia Systems, 16, "
        "345–379.",
        "Hồ Thị Linh (2023). Multi-Source Integration for Recommendation Systems. Luận án tiến sĩ, Trường Đại học Tôn "
        "Đức Thắng.",
        "H&M Group (2022). H&M Personalized Fashion Recommendations. Kaggle.",
        "McAuley, J. và cộng sự (2015). Image-Based Recommendations on Styles and Substitutes. SIGIR '15, 43–52.",
        "Wilcoxon, F. (1945). Individual Comparisons by Ranking Methods. Biometrics Bulletin, 1, 80–83.",
        "Holm, S. (1979). A Simple Sequentially Rejective Multiple Test Procedure. Scand. J. Statistics, 6, 65–70."]
text(s, 0.6, 1.65, 12.13, 5.5, refs, size=16, after=9)

# =============================================================================================== Dự phòng
s = dark("Slide ngăn cách: các slide sau chỉ mở khi hội đồng hỏi.")
text(s, 0.8, 2.9, 11.7, 1.0, ["Slide dự phòng"], size=36, bold=True, font=HEAD, color=WHITE)
text(s, 0.8, 3.9, 11.7, 0.6, ["Chỉ mở khi hội đồng hỏi"], size=18, color=ICE)

s = content("Vì sao mô hình đề xuất xếp thứ hai?", "Dự phòng",
            "Trả lời theo thứ tự: đăng ký trước, số liệu từng bộ, chi phí đo được, và LateFusion-F cũng là mô hình có "
            "đặc trưng.")
reasons = [
    ("Đăng ký trước", "NeuMF-F được chốt là mô hình đề xuất ngày 03/10/2026, trước khi mở tập kiểm thử. Đổi mô hình "
                      "sau khi thấy kết quả là dùng tập kiểm thử để chọn mô hình."),
    ("Số liệu từng bộ", f"H&M: {late('v')}, không có ý nghĩa (p Holm = {M['vsig-4-pholm']}). "
                        f"Amazon: {late('a')}, có ý nghĩa (p Holm {M['asig-4-pholm']})."),
    ("Chi phí đo được", f"Huấn luyện mỗi seed: {M['vbey-NeuMFF-time']} so với {M['vbey-LateF-time']} phút (H&M), "
                        f"{M['abey-NeuMFF-time']} so với {M['abey-LateF-time']} phút (Amazon). Độ phủ top-10 cao hơn."),
    ("Cùng kết luận", "LateFusion-F dùng chính hai nhánh có đặc trưng của NeuMF-F, nên kết quả của nó cũng cho thấy "
                      "phần cải thiện đến từ đặc trưng."),
]
for i, (h, d) in enumerate(reasons):
    x, y = 0.6 + (i % 2) * 6.17, 1.75 + (i // 2) * 2.65
    card(s, x, y, 5.96, 2.4, name=f"Thẻ {h}")
    text(s, x + 0.3, y + 0.22, 5.4, 0.4, [h], size=18, bold=True, font=HEAD, color=TAG)
    text(s, x + 0.3, y + 0.75, 5.4, 1.55, [d], size=15)

s = content("Khách hàng mới, sản phẩm mới (cold start)?", "Dự phòng",
            "Nói đây là ngoài phạm vi đánh giá, đã ghi ở hạn chế và hướng phát triển. Demo vẫn xử lý được khách mới bằng "
            "danh sách phổ biến.")
cold = [("Phạm vi", "Ngoài phạm vi đánh giá định lượng: tập kiểm thử chỉ gồm sản phẩm đã có dữ liệu huấn luyện, lọc "
                    "10-core giữ khách mua nhiều. Đã ghi ở phần hạn chế."),
        ("Khách mới", "Demo vẫn phục vụ được: khách chưa có lịch sử nhận danh sách sản phẩm bán chạy, không báo lỗi."),
        ("Sản phẩm mới", "NeuMF-F chấm điểm được sản phẩm chỉ từ đặc trưng khi bỏ vector ID. Bước tiếp theo: huấn luyện "
                         "với cơ chế này, đánh giá riêng trên sản phẩm vừa ra mắt.")]
for i, (h, d) in enumerate(cold):
    x = 0.6 + i * 4.18
    card(s, x, 1.85, 3.95, 3.6, name=f"Thẻ {h}")
    text(s, x + 0.3, 2.1, 3.4, 0.45, [h], size=20, bold=True, font=HEAD, color=TAG)
    text(s, x + 0.3, 2.75, 3.4, 3.5, [d], size=17)

# ----------------------------------------------------------------------------------------------- số trang
for i, s in enumerate(SLIDES[1:], 2):
    text(s, W - 1.1, H - 0.45, 0.6, 0.3, [str(i)], size=11, color=MUTED, align=PP_ALIGN.RIGHT, name="Số trang")

prs.save(OUT)
print("saved", OUT, len(SLIDES), "slide")
