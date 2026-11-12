"""Dựng slide bảo vệ DACNTT: 15 slide (khoảng 10 phút), theo thứ tự GVHD dặn ở buổi họp 09/11/2026: bài toán và câu
hỏi nghiên cứu -> cơ sở liên quan và mô hình đề xuất -> dữ liệu, quy trình thực nghiệm -> kết quả và phân tích -> demo ->
kết luận. Không có slide tài liệu tham khảo (người dùng bỏ ngày 11/11/2026);
slide không nhắc kế hoạch đăng ký trước, LateFusion-F chỉ nêu ở slide hợp nhất và câu trả lời câu hỏi 3.

Giao diện và cách dựng theo slide bảo vệ khóa luận của nhóm (Khoa_luan/Report KLTN, 15 slide):
- font Be Vietnam Pro, nền sáng có mảng xanh mờ, logo TDT, nhãn chương ở góc phải, thanh "Nhận xét" cuối slide;
- sơ đồ theo lối sơ đồ kiến trúc tác tử của khóa luận: khung nét đứt đánh số, thẻ có biểu tượng, số thứ tự đặt trên mũi
  tên, các tầng có dải màu dọc bên trái, giai đoạn A/B nối bằng một mũi tên có số;
- một slide chứa nhiều pha nhờ hiệu ứng: nhóm hình hiện ra (mờ dần, phóng nhẹ, lau từ trái), thoát ra (mờ dần) để pha
  sau dùng lại đúng chỗ đó; khung cam phóng vào từng phần của sơ đồ kèm chú thích đánh số ở vị trí thanh nhận xét.
Sơ đồ dựng bằng hình khối PowerPoint, sửa được trực tiếp.

Mọi con số lấy từ macro do neumf_project/scripts/24_report_v2.py sinh (Report DACNTT/content/tables/*/..._macros.tex) và
từ summary.csv của đánh giá cuối, không gõ tay. Biểu đồ: mọi cột cùng một màu, không tô riêng mô hình đề xuất (góp ý
GVHD). Biểu tượng ở media/icons (sinh bằng tao_bieu_tuong.py); ảnh demo cắt từ Report DACNTT/media/figures/demo/.

Chạy: python build_slides.py [đường_dẫn_ra.pptx]
Ngoài file .pptx, script ghi <tên>.buoc.json: các hình bị ẩn ở từng lần bấm, để xuất ảnh xem trước từng pha.
"""
import csv
import json
import math
import os
import random
import re
import sys

from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

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
    """Số mô hình đối chứng truyền thống (so sánh 5–9: BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content) mà
    NeuMF-F tốt hơn có ý nghĩa, dạng 'a/5'."""
    v = [M[f"{p}sig-{i}-verdict"] for i in range(5, 10)]
    return f"{sum(x == 'A tốt hơn' for x in v)}/{len(v)}"


def p_holm(key: str) -> str:
    v = M[key]
    return "p Holm " + (v if v.startswith("<") else "= " + v)


def so(v: str) -> float:
    return float(v.replace(",", "."))


def vn4(x: float) -> str:
    return f"{x:.4f}".replace(".", ",")


SO_CHU = {2: "hai", 3: "ba", 4: "bốn", 5: "năm", 6: "sáu"}

# ----------------------------------------------------------------------------------------------- giao diện
C = RGBColor.from_string
BLUE, NAVY, INK, MUTED = C("1E46D1"), C("1F2F5C"), C("1E293B"), C("475569")
DEEP, PALE, LINE, CARD = C("2A4A9C"), C("DCE7FB"), C("B9CCF0"), C("F3F7FE")
FOOT, BG, WHITE, GOLD = C("C9D7F2"), C("FDFDFD"), C("FFFFFF"), C("FFD166")
DASH, SUB = C("8DB3DA"), C("D6E2FA")
# sơ đồ: xanh = nhánh GMF, xanh ngọc = nhánh MLP, cam = đặc trưng / hợp nhất / khung chú thích, xanh lá = đầu ra
GMF_NEN, MLP, MLP_NEN = C("EEF3FD"), C("0891B2"), C("E6F6FA")
CAM, CAM_NEN, CAM_NHAT, LA, LA_NEN = C("E07B24"), C("FCE3C7"), C("FFF6EC"), C("2E7D32"), C("EAF6EC")
NAVY_NEN = C("E8EEF9")
FONT, FONT_MED = "Be Vietnam Pro", "Be Vietnam Pro Medium"
W, H = 13.333, 7.5
L, R = 0.45, 12.88
CW = R - L
FOOT_TEXT = "Dự án công nghệ thông tin · ĐH Tôn Đức Thắng"

LOGO = os.path.join(REPORT, "media", "logo.png")
BLOB = os.path.join(HERE, "media", "nen_mang_xanh.png")
PANEL = os.path.join(HERE, "media", "nen_chuyen_mau.png")
CAM_ON = os.path.join(HERE, "media", "minh_hoa_cam_on.png")

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
TITLE_ONLY, BLANK = prs.slide_layouts[5], prs.slide_layouts[6]
SLIDES = []      # (slide, ô số trang hoặc None) theo thứ tự
ANIM = {}        # slide_id -> các lần bấm (xem bam())


def paras(tf, items, size=16, color=INK, bold=False, font=FONT, align=PP_ALIGN.LEFT, after=4, bullet=False,
          spacing=None):
    """items: chuỗi, hoặc danh sách (chữ, tuỳ chọn) cho một đoạn nhiều kiểu chữ.
    Tuỳ chọn của một đoạn chữ: size, color, bold, font, italic, sup, sub."""
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(after)
        if spacing:
            p.line_spacing = spacing
        for t, o in ([(it, {})] if isinstance(it, str) else [(x, {}) if isinstance(x, str) else x for x in it]):
            r = p.add_run()
            r.text = t
            f = r.font
            f.name, f.size, f.bold = o.get("font", font), Pt(o.get("size", size)), o.get("bold", bold)
            f.italic = o.get("italic", False)
            f.color.rgb = o.get("color", color)
            if o.get("sup") or o.get("sub"):
                f._rPr.set("baseline", "30000" if o.get("sup") else "-25000")
        if bullet:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(Inches(0.26)))
            pPr.set("indent", str(-Inches(0.26)))
            bu = etree.SubElement(pPr, qn("a:buClr"))
            etree.SubElement(bu, qn("a:srgbClr")).set("val", str(BLUE))
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


def bong(sp):
    """Bóng xanh rất nhẹ dưới thẻ, như mẫu khóa luận."""
    ef = sp._element.spPr.find(qn("a:effectLst"))
    if ef is None:
        ef = etree.SubElement(sp._element.spPr, qn("a:effectLst"))
    sh = etree.SubElement(ef, qn("a:outerShdw"), blurRad="127000", dist="25400", dir="5400000", algn="bl",
                          rotWithShape="0")
    clr = etree.SubElement(sh, qn("a:srgbClr"), val=str(BLUE))
    etree.SubElement(clr, qn("a:alpha"), val="12000")


def hop(s, x, y, w, h, fill=None, line=None, lw=1.25, r=0.08, shape=MSO_SHAPE.ROUNDED_RECTANGLE, dash=False,
        shadow=False, name=None, items=None, **kw):
    """Hình khối (mặc định chữ nhật bo góc); items: chữ đặt giữa hình."""
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sp.adjustments[0] = r
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(lw)
        if dash:
            sp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    sp.shadow.inherit = False
    if shadow:
        bong(sp)
    if name:
        sp.name = name
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = Inches(kw.pop("pad", 0.08))
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = kw.pop("anchor", MSO_ANCHOR.MIDDLE)
    if items:
        kw.setdefault("align", PP_ALIGN.CENTER)
        kw.setdefault("after", 0)
        paras(tf, items, **kw)
    return sp


def anh(s, path, x, y, w=None, h=None, name=None):
    pic = s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    pic.name = name or os.path.basename(path)
    return pic


def anh_vua(s, path, x, y, w, h, name=None):
    """Ảnh giữ tỉ lệ, căn giữa trong khung (x, y, w, h)."""
    iw, ih = Image.open(path).size
    sc = min(w / iw, h / ih)
    return anh(s, path, x + (w - iw * sc) / 2, y + (h - ih * sc) / 2, iw * sc, ih * sc, name)


def bt(s, ten, x, y, d, mau="xanh", name=None):
    return anh(s, os.path.join(HERE, "media", "icons", f"{ten}_{mau}.png"), x, y, d, d, name)


def vong(s, ten, x, y, d, fill=PALE, mau="xanh", line=None, lw=1.5, ti=0.58, name=None):
    """Biểu tượng trong vòng tròn tô màu."""
    c = hop(s, x, y, d, d, fill=fill, line=line, lw=lw, shape=MSO_SHAPE.OVAL, name=name and name + "-vong")
    k = d * ti
    i = bt(s, ten, x + (d - k) / 2, y + (d - k) / 2, k, mau, name=name and name + "-bt")
    return [c, i]


def mui_ten(s, x1, y1, x2, y2, color=NAVY, w=2.25, dau=True, dash=False, name=None):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = color
    ln.line.width = Pt(w)
    if dash:
        ln.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if dau:
        etree.SubElement(ln.line._get_or_add_ln(), qn("a:tailEnd"), type="triangle", w="med", len="med")
    if name:
        ln.name = name
    return ln


def so_tron(s, x, y, n, color=BLUE, d=0.3, size=12, name=None, mau_chu=WHITE):
    return hop(s, x, y, d, d, fill=color, shape=MSO_SHAPE.OVAL, name=name, items=[str(n)], size=size, bold=True,
               color=mau_chu, pad=0)


def nhan_xet(s, ten, noi_dung, y=6.22, h=0.64, size=16, x=L, w=CW, tren_nen=False):
    """Thanh nhận xét cuối slide, bo tròn hai đầu."""
    if tren_nen:
        b = hop(s, x, y, w, h, fill=None, line=WHITE, lw=1.25, r=0.5, name="Thanh nhận xét")
        col = WHITE
    else:
        b = hop(s, x, y, w, h, fill=PALE, r=0.5, name="Thanh nhận xét")
        col = NAVY
    t = text(s, x + 0.32, y, w - 0.55, h, [[(ten + ": ", {"bold": True}), (noi_dung, {})]], size=size, color=col,
             anchor=MSO_ANCHOR.MIDDLE, after=0, name="Chữ nhận xét")
    return [b, t]


def chu_thich(s, n, noi_dung, y=6.22, h=0.64, x=L, w=CW, size=15, color=CAM):
    """Chú thích đánh số ở chỗ thanh nhận xét: đi cùng một khung cam phóng vào một phần của sơ đồ."""
    b = hop(s, x, y, w, h, fill=WHITE, line=color, lw=1.75, r=0.5, name=f"Chú thích {n}")
    c = so_tron(s, x + 0.17, y + (h - 0.38) / 2, n, color, d=0.38, size=14)
    t = text(s, x + 0.7, y, w - 0.95, h, [noi_dung], size=size, color=INK, anchor=MSO_ANCHOR.MIDDLE, after=0)
    return [b, c, t]


def khung_cam(s, x, y, w, h, n=None):
    """Khung cam phóng vào một phần sơ đồ (pha 'đọc theo số'), kèm số ở góc trên bên trái."""
    out = [hop(s, x, y, w, h, line=CAM, lw=3, r=0.05, name="Khung chú thích")]
    if n is not None:
        out.append(so_tron(s, x - 0.17, y - 0.17, n, CAM, d=0.38, size=14))
    return out


def the(s, x, y, w, h, fill=CARD, line=LINE, r=0.075, name=None):
    """Thẻ nền nhạt, viền xanh nhạt, bóng nhẹ."""
    return hop(s, x, y, w, h, fill=fill, line=line, r=r, shadow=True, name=name)


def the_so(s, x, y, w, h, nhan, so_lon, mo_ta, name, co_so=34):
    """Thẻ số liệu: nhãn nhỏ, số lớn, một dòng mô tả."""
    c = the(s, x, y, w, h, name=f"Thẻ {name}")
    a = text(s, x + 0.25, y + 0.12, w - 0.5, 0.32, [nhan], size=14, color=MUTED, name=f"Nhãn {name}")
    b = text(s, x + 0.25, y + 0.4, w - 0.5, 0.62, [so_lon], size=co_so, font=FONT_MED, color=DEEP,
             anchor=MSO_ANCHOR.BOTTOM, name=f"Số {name}")
    d = text(s, x + 0.25, y + 1.06, w - 0.5, h - 1.1, [mo_ta], size=13.5, name=f"Mô tả {name}")
    return [c, a, b, d]


def the_bt(s, x, y, w, h, ten, tieu_de, mo_ta="", fill=WHITE, line=LINE, d=0.55, co=14, co_phu=11.5, mau_chu=INK,
           mau_phu=MUTED, vong_fill=PALE, mau_bt="xanh", lw=1.25, name=None, shadow=False):
    """Thẻ ngang: biểu tượng tròn bên trái, tên và một dòng mô tả bên phải (như thẻ trong sơ đồ khóa luận)."""
    c = hop(s, x, y, w, h, fill=fill, line=line, lw=lw, r=0.12, name=name, shadow=shadow)
    v = vong(s, ten, x + 0.1, y + (h - d) / 2, d, fill=vong_fill, mau=mau_bt)
    items = [[(tieu_de, {"bold": True, "size": co, "color": mau_chu})]]
    if mo_ta:
        items.append([(mo_ta, {"size": co_phu, "color": mau_phu})])
    t = text(s, x + d + 0.22, y, w - d - 0.3, h, items, anchor=MSO_ANCHOR.MIDDLE, after=1)
    return [c, *v, t]


# ----------------------------------------------------------------------------------------------- khung slide
def ra_sau(s, *pics):
    """Đưa ảnh nền xuống dưới mọi hình khác (kể cả placeholder tiêu đề có sẵn từ bố cục)."""
    tree = s.shapes._spTree
    for k, p in enumerate(pics):
        tree.remove(p._element)
        tree.insert(2 + k, p._element)


def nen(s, blob=None, blob2=None):
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    pics = []
    if blob:
        pics.append(anh(s, BLOB, *blob, name="!!blob"))
    if blob2:
        pics.append(anh(s, BLOB, *blob2, name="!!blob2"))
    ra_sau(s, *pics)


def logo(s, tren_nen=False):
    if tren_nen:
        hop(s, 0.3, 0.18, 1.5, 0.86, fill=WHITE, r=0.12, name="!!logocard")
    anh(s, LOGO, 0.4, 0.25, 1.3, 0.72, name="!!logo")


def nhan_chuong(s, chuong, tren_nen=False):
    if tren_nen:
        return hop(s, 9.95, 0.4, 2.93, 0.46, line=WHITE, lw=1, r=0.5, name="!!sec", items=[chuong], size=14,
                   font=FONT_MED, color=WHITE)
    return hop(s, 9.95, 0.4, 2.93, 0.46, fill=WHITE, line=LINE, lw=1, r=0.5, name="!!sec", items=[chuong], size=14,
               font=FONT_MED, color=BLUE)


def chan_trang(s, tren_nen=False):
    col = WHITE if tren_nen else BLUE
    mui_ten(s, L, 7.02, R, 7.02, color=WHITE if tren_nen else FOOT, w=0.75, dau=False, name="!!footline")
    text(s, L, 7.08, 7.0, 0.3, [FOOT_TEXT], size=11, color=col, name="!!foot")
    return text(s, R - 1.6, 7.08, 1.6, 0.3, [""], size=11, color=col, align=PP_ALIGN.RIGHT, name="!!page")


def slide(tieu_de, chuong, notes, blob=(10.3, -3.3, 6.0, 6.1), blob2=None, panel=False):
    """Slide nội dung: logo, nhãn chương, tiêu đề (placeholder thật để PowerPoint đọc được dàn ý), chân trang."""
    s = prs.slides.add_slide(TITLE_ONLY)
    nen(s, None if panel else blob, None if panel else blob2)
    if panel:
        ra_sau(s, anh(s, PANEL, 0, 0, W, H, name="!!panel"), anh(s, BLOB, 9.6, -2.6, 5.6, 5.7, name="!!blob"))
    logo(s, panel)
    nhan_chuong(s, chuong, panel)
    t = s.shapes.title
    t.left, t.top, t.width, t.height = Inches(L), Inches(1.06), Inches(CW), Inches(0.76)
    t.name = "!!title"
    tf = t.text_frame
    tf.clear()
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = True
    paras(tf, [tieu_de], size=34, bold=True, color=WHITE if panel else BLUE)
    page = chan_trang(s, panel)
    s.notes_slide.notes_text_frame.text = notes
    SLIDES.append((s, page))
    return s


# ----------------------------------------------------------------------------------------------- hiệu ứng theo lần bấm
def phang(x):
    """Làm phẳng danh sách lồng nhau thành danh sách hình."""
    if isinstance(x, (list, tuple)):
        return [h for el in x for h in phang(el)]
    return [x]


def bam(s, ra=(), zoom=(), lau=(), vao=(), auto=False, nhip=90):
    """Một lần bấm. ra: các hình thoát (mờ dần) trước; rồi zoom (mờ dần + phóng nhẹ như khóa luận), lau (lau từ trái
    sang), vao (mờ dần) hiện ra. Mỗi phần tử cấp một của zoom/lau/vao hiện sau phần tử trước nhip mili giây; muốn
    nhiều hình hiện cùng lúc thì gói chúng vào một danh sách con. auto=True: lần 'bấm' đầu chạy ngay khi vào slide."""
    items = [(sh, "ra", 0) for sh in phang(ra)]
    t0, k = (300 if items else 0), 0
    for kind, seq in (("zoom", zoom), ("lau", lau), ("vao", vao)):
        for el in seq:
            items += [(sh, kind, t0 + k * nhip) for sh in phang(el)]
            k += 1
    ANIM.setdefault(s.slide_id, []).append({"auto": auto, "items": items})


def pha(s, *nhom, cuoi=None, hieu="zoom"):
    """Các pha nối tiếp ở cùng một chỗ: pha i hiện ở lần bấm i (pha 0 có sẵn khi vào slide) và thoát ở lần bấm sau.
    cuoi: nhóm hình hiện ở lần bấm cuối (thường là thanh nhận xét) sau khi pha cuối thoát."""
    for i in range(1, len(nhom)):
        bam(s, ra=nhom[i - 1], **{hieu: [nhom[i]]})
    if cuoi is not None:
        bam(s, ra=nhom[-1], vao=[cuoi])


NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"


def morph(s):
    """Chuyển Morph (PowerPoint 2019 trở lên), máy cũ hơn thì mờ dần."""
    xml = (f'<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
           f'<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
           f'<p:transition xmlns:p="{NS_P}" xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" '
           f'spd="slow" p14:dur="900"><p159:morph option="byObject"/></p:transition></mc:Choice>'
           f'<mc:Fallback><p:transition xmlns:p="{NS_P}" spd="slow"><p:fade/></p:transition></mc:Fallback>'
           f'</mc:AlternateContent>')
    s._element.append(etree.fromstring(xml))


def _hien(sid):
    return (f'<p:set><p:cBhvr><p:cTn id="{{}}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
            f'</p:cTn><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility'
            f'</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>')


def _hieu_ung(kind, sid):
    """(presetID, presetClass, presetSubtype, phần thân XML có chỗ trống {} cho id) của một hiệu ứng, chép theo deck
    khóa luận: 10 mờ dần, 53 mờ dần + phóng từ 85%, 22 lau từ trái, thoát 10 mờ dần."""
    tg = f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl>'
    if kind == "ra":
        body = (f'<p:animEffect transition="out" filter="fade"><p:cBhvr><p:cTn id="{{}}" dur="350"/>{tg}</p:cBhvr>'
                f'</p:animEffect><p:set><p:cBhvr><p:cTn id="{{}}" dur="1" fill="hold"><p:stCondLst>'
                f'<p:cond delay="349"/></p:stCondLst></p:cTn>{tg}<p:attrNameLst><p:attrName>style.visibility'
                f'</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="hidden"/></p:to></p:set>')
        return "10", "exit", "0", body
    if kind == "zoom":
        sc = "".join(f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{{}}" dur="500" fill="hold"/>{tg}'
                     f'<p:attrNameLst><p:attrName>ppt_{a}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
                     f'<p:tav tm="0"><p:val><p:strVal val="#ppt_{a}*0.85"/></p:val></p:tav><p:tav tm="100000">'
                     f'<p:val><p:strVal val="#ppt_{a}"/></p:val></p:tav></p:tavLst></p:anim>' for a in "wh")
        body = (_hien(sid) + sc + f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{{}}" dur="500"/>'
                f'{tg}</p:cBhvr></p:animEffect>')
        return "53", "entr", "0", body
    if kind == "lau":
        body = (_hien(sid) + f'<p:animEffect transition="in" filter="wipe(left)"><p:cBhvr><p:cTn id="{{}}" '
                f'dur="600"/>{tg}</p:cBhvr></p:animEffect>')
        return "22", "entr", "8", body
    body = (_hien(sid) + f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{{}}" dur="450"/>{tg}'
            f'</p:cBhvr></p:animEffect>')
    return "10", "entr", "0", body


def ghi_hieu_ung(s, clicks):
    nid = iter(range(3, 1000000))
    pars = []
    for ci, cl in enumerate(clicks):
        o1, o2 = next(nid), next(nid)
        inner = []
        for k, (sh, kind, delay) in enumerate(cl["items"]):
            pid, pcls, psub, body = _hieu_ung(kind, sh.shape_id)
            a = next(nid)
            body = body.replace("{}", "\0")
            while "\0" in body:
                body = body.replace("\0", str(next(nid)), 1)
            node = ("afterEffect" if cl["auto"] else "clickEffect") if k == 0 else "withEffect"
            inner.append(f'<p:par><p:cTn id="{a}" presetID="{pid}" presetClass="{pcls}" presetSubtype="{psub}" '
                         f'fill="hold" nodeType="{node}"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst>'
                         f'<p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>')
        start = ('<p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>'
                 if cl["auto"] and ci == 0 else '<p:cond delay="indefinite"/>')
        pars.append(f'<p:par><p:cTn id="{o1}" fill="hold"><p:stCondLst>{start}</p:stCondLst><p:childTnLst><p:par>'
                    f'<p:cTn id="{o2}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                    f'{"".join(inner)}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    xml = (f'<p:timing xmlns:p="{NS_P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" '
           f'nodeType="tmRoot"><p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" '
           f'nodeType="mainSeq"><p:childTnLst>{"".join(pars)}</p:childTnLst></p:cTn><p:prevCondLst>'
           f'<p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst><p:nextCondLst>'
           f'<p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           f'</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
    s._element.append(etree.fromstring(xml))


def trang_thai(clicks):
    """Danh sách id hình bị ẩn ở từng trạng thái: trạng thái 0 là khi vừa vào slide (đã chạy phần tự động), trạng thái
    k là sau k lần bấm. Dùng để xuất ảnh xem trước từng pha."""
    an = set()
    first = {}
    for cl in clicks:
        for sh, kind, _ in cl["items"]:
            first.setdefault(sh.shape_id, kind)
    an = {sid for sid, kind in first.items() if kind != "ra"}
    out = []
    for i, cl in enumerate(clicks):
        if i == 0 and not cl["auto"]:
            out.append(sorted(an))
        for sh, kind, _ in cl["items"]:
            (an.add if kind == "ra" else an.discard)(sh.shape_id)
        out.append(sorted(an))
    return out or [[]]


# ----------------------------------------------------------------------------------------------- biểu đồ
def bieu_do(s, data, x, y, w, h, ten, co=13, max_ty=1.2, dao=False):
    cd = CategoryChartData()
    cd.categories = [n for n, _ in data]
    cd.add_series("NDCG@10", [v for _, v in data])
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    gf.name = ten
    ch = gf.chart
    ch.has_legend = False
    ch.has_title = False
    ch.font.name, ch.font.size = FONT, Pt(co)
    ch.font.color.rgb = INK
    plot = ch.plots[0]
    plot.gap_width = 45
    plot.vary_by_categories = False
    ser = plot.series[0]
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = BLUE
    for i, (_, v) in enumerate(data):  # nhãn ghi tay để có dấu phẩy thập phân như báo cáo
        dl = ser.points[i].data_label
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
        dl.text_frame.text = vn4(v)
        r = dl.text_frame.paragraphs[0].runs[0]
        r.font.size, r.font.name = Pt(co - 1), FONT
        r.font.color.rgb = MUTED
    va = ch.value_axis
    va.visible = False
    va.has_major_gridlines = False
    va.minimum_scale = 0
    va.maximum_scale = max(v for _, v in data) * max_ty
    ca = ch.category_axis
    ca.format.line.color.rgb = LINE
    ca.tick_labels.font.size = Pt(co)
    ca.tick_labels.font.name = FONT
    if dao:
        ca.reverse_order = True
    return gf


def chuoi_buoc(s, x0, y, w, h, gap, buoc, mau=BLUE, so0=1):
    """Một hàng thẻ đọc từ trái sang phải, mỗi thẻ có số thứ tự ở góc (như sơ đồ quy trình của khóa luận).
    Trả về danh sách nhóm hình, mỗi bước một nhóm (thẻ + mũi tên dẫn vào nó)."""
    nhom = []
    for k, (ic, a, b) in enumerate(buoc):
        x = x0 + k * (w + gap)
        g = the_bt(s, x, y, w, h, ic, a, b, d=0.52, co=13.5, co_phu=11, shadow=True)
        g.append(so_tron(s, x - 0.1, y - 0.13, so0 + k, mau, d=0.3, size=11))
        if k:
            g.append(mui_ten(s, x - gap, y + h / 2, x, y + h / 2, color=mau, w=2))
        nhom.append(g)
    return nhom


HINH_DIR = os.path.join(REPO, "image")


def hinh(s, ten, x, y, k, name=None):
    """Chèn hình sơ đồ của báo cáo (image/<ten>.png, xuất ở hệ số 2) với tỉ lệ k inch cho mỗi đơn vị draw.io.
    Dùng cùng k cho hai hình có cùng bố cục (NeuMF, NeuMF-F) để các hàng trùng chỗ khi hình này thay hình kia."""
    p = os.path.join(HINH_DIR, ten + ".png")
    w_px, h_px = Image.open(p).size
    return anh(s, p, x, y, w_px / 2 * k, h_px / 2 * k, name or ten)


def khung_tren_hinh(s, pic, goc, box, n=None, le=0.04):
    """Khung cam phủ lên vùng box = (x, y, rộng, cao) theo toạ độ draw.io của hình pic; goc = toạ độ nhỏ nhất của các
    hình trên trang draw.io (trình xem vẽ hình bắt đầu từ đó, cách lề 6 + 1 đơn vị)."""
    w_px = Image.open(os.path.join(HINH_DIR, pic.name + ".png")).size[0]
    k = pic.width / Inches(1) / (w_px / 2)
    x0, y0 = pic.left / Inches(1), pic.top / Inches(1)
    bx, by, bw, bh = box
    return khung_cam(s, x0 + (bx - goc[0] + 7) * k - le, y0 + (by - goc[1] + 7) * k - le, bw * k + 2 * le,
                     bh * k + 2 * le, n)


def cat_anh(ten, src, box=None):
    """Cắt ảnh chụp demo của báo cáo cho vừa khung slide; lưu ở media/demo/."""
    os.makedirs(os.path.join(HERE, "media", "demo"), exist_ok=True)
    out = os.path.join(HERE, "media", "demo", ten)
    im = Image.open(os.path.join(REPORT, "media", "figures", "demo", src))
    (im.crop(box) if box else im).save(out)
    return out


# =============================================================================================== 1. Mở đầu
s = prs.slides.add_slide(BLANK)
nen(s, (7.6, -1.6, 6.0, 6.1), (-2.2, 4.6, 4.6, 4.65))
logo(s)
s.notes_slide.notes_text_frame.text = ("Khoảng 20 giây. Chào hội đồng, giới thiệu tên đề tài, hai thành viên và giảng "
                                       "viên hướng dẫn.")
SLIDES.append((s, None))
hop(s, 0.6, 1.4, 3.9, 0.5, fill=BLUE, r=0.5, items=["DỰ ÁN CÔNG NGHỆ THÔNG TIN"], size=15, bold=True, color=WHITE,
    name="!!sec")
text(s, 0.6, 2.02, 8.4, 2.0, [[("Xây dựng mô hình khuyến nghị lai", {"color": INK})],
                              [("kết hợp nhân tử hoá ma trận", {})], [("và mạng lưới thần kinh sâu", {})]],
     size=31, bold=True, color=BLUE, after=2, spacing=1.05, name="!!title")
vien = [hop(s, x, 4.25, w, 0.48, fill=PALE, r=0.5, items=[t], size=14, font=FONT_MED, color=INK)
        for x, w, t in [(0.6, 3.05, "Mô hình đề xuất NeuMF-F"), (3.78, 2.55, "H&M · Amazon Beauty"),
                        (6.46, 2.25, "Khuyến nghị Top-K")]]
for x, ic, a, b in [(0.6, "school", "Giảng viên hướng dẫn", ["TS. Hồ Thị Linh"]),
                    (4.6, "users", "Sinh viên thực hiện", ["Lê Minh Lý", "Sử Thị Yến Linh"])]:
    vong(s, ic, x, 5.12, 0.66, ti=0.6)
    text(s, x + 0.8, 5.06, 3.4, 1.2, [[(a, {"size": 13, "color": MUTED})]] +
         [[(n, {"size": 17, "bold": True, "color": INK})] for n in b], after=1)
text(s, 0.6, 6.85, 6.0, 0.35, ["Khoa Công nghệ thông tin · TP. Hồ Chí Minh, 2026"], size=13, color=BLUE)
# mạng khách hàng – sản phẩm: một tâm, sáu vệ tinh; hiện dần ngay khi vào slide
cx, cy, rr = 11.0, 3.7, 1.85
ve_tinh = ["users", "shirt", "users", "perfume", "users", "shopping-bag"]
day, nut = [], []
for k, ic in enumerate(ve_tinh):
    goc_ = math.radians(-90 + 60 * k)
    day.append(mui_ten(s, cx, cy, cx + rr * math.cos(goc_), cy + rr * math.sin(goc_), color=LINE, w=2, dau=False))
for k, ic in enumerate(ve_tinh):
    goc_ = math.radians(-90 + 60 * k)
    nut.append(vong(s, ic, cx + rr * math.cos(goc_) - 0.5, cy + rr * math.sin(goc_) - 0.5, 1.0, fill=WHITE, line=LINE,
                    ti=0.56))
tam = vong(s, "affiliate", cx - 0.85, cy - 0.85, 1.7, fill=BLUE, mau="trang", line=WHITE, lw=3, ti=0.56)
bam(s, zoom=[tam, day, *nut, vien], auto=True, nhip=110)

# =============================================================================================== 2. Bài toán
s = slide("Bối cảnh và bài toán", "Chương 1 · Tổng quan",
          "Khoảng 40 giây. Dữ liệu thời trang chỉ có lịch sử mua, ma trận khách–sản phẩm rất thưa. NeuMF (He và cộng "
          "sự, 2017) ghép GMF với MLP nhưng chỉ dùng mã khách và mã sản phẩm, nên chưa khai thác thông tin có sẵn: thuộc tính, "
          "mô tả, doanh số theo thời gian, thông tin khách. Bấm để hiện bốn nguồn thông tin, bấm tiếp để hiện câu đề "
          "tài.")
g1 = [the(s, L, 1.98, 4.9, 3.85, name="Thẻ ma trận")]
g1.append(text(s, L + 0.3, 2.12, 4.3, 0.4, ["Ma trận khách – sản phẩm"], size=17, bold=True, color=NAVY))
rnd = random.Random(7)
o_mua = []
for r_ in range(8):  # ô tô màu = khách đã mua sản phẩm; phần lớn ô trống
    for c_ in range(14):
        on = rnd.random() < 0.09
        o = hop(s, L + 0.32 + c_ * 0.305, 2.68 + r_ * 0.3, 0.25, 0.25, fill=BLUE if on else WHITE,
                line=None if on else FOOT, lw=0.75, r=0.2)
        if on:
            o_mua.append(o)
g1.append(text(s, L + 0.3, 5.18, 4.3, 0.55, ["Mỗi khách chỉ mua vài món: hầu hết ô trống."], size=14, color=MUTED))
g2 = [text(s, 5.75, 1.98, 7.1, 0.85, [[("NeuMF", {"bold": True}), (" kết hợp nhân tử hoá ma trận với mạng nơ-ron, nhưng "
                                                                  "chỉ học từ mã khách và mã sản phẩm.",
                                                                  {})]],
           size=19, color=INK, after=0)]
g2.append(text(s, 5.75, 2.95, 7.1, 0.4, ["Thông tin có sẵn nhưng NeuMF chưa khai thác"], size=17, bold=True, color=NAVY))
nguon = []
for k, (ic, t) in enumerate([("shirt", "Thuộc tính sản phẩm"), ("file-text", "Mô tả văn bản"),
                             ("clock", "Doanh số theo thời gian"), ("users", "Thông tin khách hàng")]):
    x, y = 5.75 + (k % 2) * 3.6, 3.5 + (k // 2) * 1.12
    nguon.append(vong(s, ic, x, y, 0.88, ti=0.55) + [text(s, x + 1.05, y, 2.45, 0.88, [t], size=17,
                                                          anchor=MSO_ANCHOR.MIDDLE)])
g3 = [hop(s, L, 6.05, CW, 0.82, fill=BLUE, r=0.22, items=[[("Giải pháp: ", {"bold": True}),
                                                            ("NeuMF-F đưa bốn nhóm thông tin này vào cả hai nhánh của NeuMF",
                                                             {})]], size=21, color=WHITE)]
bam(s, zoom=o_mua, auto=True, nhip=25)
bam(s, zoom=[g2[1], *nguon])
bam(s, lau=[g3])

# =============================================================================================== 3. Câu hỏi nghiên cứu
s = slide("Mục tiêu và câu hỏi nghiên cứu", "Chương 1 · Tổng quan",
          "Khoảng 20 giây. Ba câu hỏi; phần kết quả và slide kết luận trả lời lần lượt từng câu. Câu hỏi 1 là câu hỏi "
          "chính.", panel=True)
text(s, L, 1.88, 11.0, 0.5, [[("Mục tiêu: ", {"bold": True}),
                             ("bổ sung đặc trưng vào NeuMF và đánh giá trên hai bộ dữ liệu thực tế.", {})]],
     size=19, color=WHITE)
qs = [("chart-bar", "Câu hỏi 1", "NeuMF-F có khuyến nghị tốt hơn các mô hình đối chứng được tinh chỉnh đầy đủ không?"),
      ("stack-2", "Câu hỏi 2", "Đặc trưng có giúp không, và nhóm đặc trưng nào đóng góp nhiều nhất?"),
      ("git-merge", "Câu hỏi 3", "Ghép hai nhánh có tốt hơn dùng từng nhánh riêng, và nên hợp nhất sớm hay muộn?")]
nhom = []
for k, (ic, h_, q) in enumerate(qs):
    d, x = 3.05, 0.95 + k * 3.95
    g = [hop(s, x, 2.55, d, d, fill=CARD, line=GOLD if k == 0 else None, lw=4.5, shape=MSO_SHAPE.OVAL,
             name=f"!!cau-hoi-{k + 1}")]
    g.append(bt(s, ic, x + d / 2 - 0.32, 2.82, 0.64, name=f"!!cau-hoi-{k + 1}-bt"))
    g.append(text(s, x, 3.5, d, 0.4, [h_], size=17, bold=True, color=BLUE, align=PP_ALIGN.CENTER,
                  name=f"!!cau-hoi-{k + 1}-ten"))
    g.append(text(s, x + 0.35, 3.95, d - 0.7, 1.3, [q], size=14, color=INK, align=PP_ALIGN.CENTER, after=0))
    nhom.append(g)
nx = nhan_xet(s, "Nhận xét", "Câu hỏi 1 là câu hỏi chính; phần kết quả trả lời lần lượt từng câu.",
              y=5.95, tren_nen=True)
bam(s, zoom=[nhom[0]], auto=True)
bam(s, zoom=[nhom[1]])
bam(s, zoom=[nhom[2]])
bam(s, vao=[nx])

# =============================================================================================== 4. NeuMF -> NeuMF-F
s = slide("Từ NeuMF đến mô hình đề xuất NeuMF-F", "Chương 2, 3 · Mô hình",
          "Khoảng 1 phút 30. Đầu tiên là NeuMF gốc (cơ sở lý thuyết): khách và sản phẩm vào bằng mã ID; nhánh GMF nhân "
          "từng phần tử, tổng quát hoá MF; nhánh MLP nối hai vector rồi qua lớp ẩn; nối hai đầu ra là hợp nhất sớm. "
          "Bấm 1: hạn chế chỉ dùng ID. Bấm 2: hình đổi thành NeuMF-F (cùng kiểu hình 3.4 của báo cáo), ba nhóm đặc "
          "trưng hiện ở dưới. Bấm 3–5: đọc hình theo số, khung cam chỉ phần đang nói. Bấm 6: nhận xét.")
K4 = CW / 1674  # bản nằm ngang của hình 2.1 và 3.4 (image/hinh_*_ngang.png), cùng tỉ lệ nên các cột trùng chỗ
h_neumf = hinh(s, "hinh_neumf_ngang", L, 1.95, K4)
h_neumf_f = hinh(s, "hinh_neumf_f_ngang", L, 1.95, K4)
co_so = []
for k, (a, b) in enumerate([("GMF", "nhân từng phần tử vector khách với vector sản phẩm, dạng tổng quát của nhân tử "
                                    "hoá ma trận"),
                            ("MLP", "nối hai vector rồi qua các lớp ẩn ReLU để học tương tác phi tuyến"),
                            ("Hợp nhất sớm", "nối đầu ra hai nhánh trước một lớp dự đoán chung, cả mạng học chung")]):
    x = L + k * 4.215
    co_so.append([the(s, x, 5.0, 4.0, 1.08, fill=WHITE, name=f"Thẻ {a}"),
                  text(s, x + 0.22, 5.0, 3.6, 1.08, [[(a + ": ", {"bold": True, "color": BLUE}), (b, {})]], size=13,
                       anchor=MSO_ANCHOR.MIDDLE, after=0)])
dac_trung = []
for k, (ic, a, b) in enumerate([("shirt", "Sản phẩm", "thuộc tính danh mục, vector mô tả văn bản"),
                                ("clock", "Thời gian", "doanh số 7, 28, 91 ngày trước, tuổi sản phẩm, tính tại đúng "
                                                       "thời điểm mua"),
                                ("users", "Khách hàng", "nhóm tuổi, hội viên (H&M); số ngày từ lần mua gần nhất")]):
    x = L + k * 4.215
    dac_trung.append([the(s, x, 5.0, 4.0, 1.08, fill=WHITE, name=f"Thẻ đặc trưng {a}"),
                      *vong(s, ic, x + 0.15, 5.24, 0.6, fill=CAM_NEN, ti=0.56),
                      text(s, x + 0.9, 5.0, 3.0, 1.08, [[(a, {"bold": True, "color": CAM})], [(b, {"size": 12.5})]],
                           size=14, anchor=MSO_ANCHOR.MIDDLE, after=1)])
han_che = nhan_xet(s, "Hạn chế", "NeuMF chỉ dùng mã ID, không tận dụng thông tin của khách và sản phẩm.")
G4 = (0, 30)  # toạ độ nhỏ nhất của các hình trên hai trang nằm ngang
doc = [(khung_tren_hinh(s, h_neumf_f, G4, (0, 30, 610, 320), 1),
        chu_thich(s, 1, "Biểu diễn lai: mỗi vector là vector nhúng mã ID cộng với phép chiếu của đặc trưng (ô màu cam).",
                  size=14.5)),
       (khung_tren_hinh(s, h_neumf_f, G4, (680, 35, 300, 310), 2),
        chu_thich(s, 2, "Hai nhánh: GMF nhân từng phần tử; MLP nối hai vector rồi qua các lớp 64 → 32 → 16 → 8.")),
       (khung_tren_hinh(s, h_neumf_f, G4, (1050, 55, 610, 290), 3),
        chu_thich(s, 3, "Nối hai nhánh, qua sigmoid ra điểm dự đoán. Huấn luyện bằng BCE với 8 mẫu âm cho mỗi lượt "
                        "mua; khuyến nghị K sản phẩm điểm cao nhất.", size=14.5))]
cuoi = nhan_xet(s, "Nhận xét", "Phần mới của NeuMF-F là lớp biểu diễn lai: đặc trưng đi vào cả nhánh GMF lẫn nhánh MLP.")
bam(s, vao=[han_che])
bam(s, ra=[h_neumf, co_so, han_che], zoom=[h_neumf_f, *dac_trung], nhip=120)
bam(s, zoom=[doc[0]])
bam(s, ra=doc[0], zoom=[doc[1]])
bam(s, ra=doc[1], zoom=[doc[2]])
bam(s, ra=doc[2], vao=[cuoi])

# =============================================================================================== 5. Dữ liệu
s = slide("Dữ liệu: H&M và Amazon Beauty", "Chương 3 · Dữ liệu",
          "Khoảng 50 giây. H&M: lấy hai mẫu khách tách rời, gộp màu theo mẫu thiết kế, lọc 10-core, chia theo thời "
          "gian. Mẫu phát triển để tinh chỉnh, mẫu kiểm định để kết luận. Bấm: chuyển sang Amazon Beauty, bộ kiểm chứng "
          "ở lĩnh vực khác: lọc 5-core, không có thông tin khách hàng, giữ nguyên cấu hình chọn trên H&M, chỉ chọn lại "
          "số epoch.", blob=(-2.6, 4.4, 6.0, 6.1))


def du_lieu(hinh_ten, so_lieu, ghi_chu):
    """Một pha của slide dữ liệu: hình quy trình nằm ngang ở trên, bốn thẻ số liệu một hàng, một dòng ghi chú."""
    g = [hinh(s, hinh_ten, L, 1.95, CW / 1530)]
    w4 = (CW - 3 * 0.15) / 4
    for k, (a, b, c_, ic) in enumerate(so_lieu):
        x = L + k * (w4 + 0.15)
        g.append(the_so(s, x, 4.05, w4, 1.45, a, b, c_, f"dữ liệu {k}") + [bt(s, ic, x + w4 - 0.62, 4.17, 0.42)])
    g.append([the(s, L, 5.62, CW, 0.5, fill=WHITE),
              text(s, L + 0.25, 5.62, CW - 0.5, 0.5, [ghi_chu], size=14, anchor=MSO_ANCHOR.MIDDLE, after=0)])
    return g


hm = du_lieu("hinh_du_lieu_hm_ngang",
             [("Mẫu phát triển · khách", M["vdata-A-nusers"], f"{M['vdata-A-nitems']} sản phẩm · tinh chỉnh", "users"),
              ("Mẫu kiểm định · khách", M["vdata-B-nusers"], f"{M['vdata-B-nitems']} sản phẩm · kết luận", "users"),
              ("Tập kiểm thử · khách", M["vdata-Btest-users"], "khách mua sản phẩm mới", "target-arrow"),
              ("Sản phẩm ứng viên", M["vdata-Btest-cand"], "xếp hạng cho mỗi khách", "list-numbers")],
             "Hai mẫu khách tách rời: chọn cấu hình trên mẫu phát triển, kết luận trên mẫu kiểm định.")
am = du_lieu("hinh_du_lieu_amazon_ngang",
             [("Sau lọc · khách", M["adata-all-nusers"], f"{M['adata-all-nitems']} sản phẩm", "users"),
              ("Tương tác sau lọc", M["adata-all-nkeptpairs"], "dùng để huấn luyện", "database"),
              ("Tập kiểm thử · khách", M["adata-test-users"], "khách mua sản phẩm mới", "target-arrow"),
              ("Sản phẩm ứng viên", M["adata-test-cand"], "xếp hạng cho mỗi khách", "list-numbers")],
             "Không có thông tin khách hàng: nhánh khách chỉ còn hai đặc trưng thời gian.")
nx = nhan_xet(s, "Nhận xét", "Amazon Beauty kiểm chứng ở lĩnh vực khác, giữ nguyên cấu hình đã chọn trên H&M.", size=14.5)
bam(s, zoom=hm[1:], auto=True, nhip=80)
bam(s, ra=hm, zoom=am, nhip=80)
bam(s, vao=[nx])

# =============================================================================================== 6. Quy trình
s = slide("Quy trình thực nghiệm", "Chương 3 · Đánh giá",
          "Khoảng 1 phút, phần cô dặn phải nói rõ. Trục thời gian: học trên quá khứ, đoán tương lai. Bấm 1: giai đoạn A "
          "trên mẫu phát triển: mọi mô hình học thử 6 cấu hình, chọn theo NDCG@10 trên tập xác thực, rồi giữ cố định. "
          "Bấm 2: giai đoạn B trên mẫu kiểm định với cấu hình đã chọn: huấn luyện lại 5 seed, xếp hạng mọi ứng viên, "
          "kiểm định Wilcoxon, khoảng tin cậy bootstrap, hiệu chỉnh Holm. Tập kiểm thử chỉ dùng cho đánh giá cuối.")
tl = [hinh(s, "hinh_chia_thoi_gian", L, 2.0, CW / 958)]  # hình 3.3 của báo cáo
tl += [the(s, L, 5.0, CW, 1.0, fill=WHITE),
       text(s, L + 0.3, 5.0, CW - 0.6, 1.0,
            [[("Học trên quá khứ, đánh giá trên tương lai. ", {"bold": True, "color": NAVY}),
              ("Đặc trưng và mẫu âm đều tính tại đúng thời điểm, nên mô hình không nhìn thấy thông tin của giai đoạn "
               "được đánh giá.", {})]], size=15, anchor=MSO_ANCHOR.MIDDLE, after=0)]
# sơ đồ hai giai đoạn A, B như sơ đồ quy trình huấn luyện của khóa luận
A = [hop(s, L, 1.95, CW, 1.68, fill=C("F5F8FE"), line=BLUE, lw=1.5, r=0.04, dash=True),
     text(s, L + 0.2, 2.0, CW - 0.4, 0.4, [[("A · CHỌN CẤU HÌNH", {"bold": True, "color": BLUE}),
                                            ("   mẫu phát triển · tập xác thực 4 tuần · seed 42",
                                             {"size": 12.5, "color": MUTED})]], size=15, anchor=MSO_ANCHOR.MIDDLE)]
bw, gap = 2.7, 0.5
x0 = L + (CW - 4 * bw - 3 * gap) / 2
buoc_a = chuoi_buoc(s, x0, 2.5, bw, 0.92, gap,
                    [("database", "Dữ liệu, đặc trưng", "tính tại mốc, trước 01/07/2020"),
                     ("settings", "Tinh chỉnh", "mỗi mô hình thử 6 cấu hình"),
                     ("target-arrow", "Chọn cấu hình", "theo NDCG@10 trên tập xác thực"),
                     ("lock", "Cố định cấu hình", "dùng nguyên cho giai đoạn B")])
B = [hop(s, L, 4.33, CW, 1.68, fill=C("FFF8F1"), line=CAM, lw=1.5, r=0.04, dash=True),
     text(s, L + 2.4, 4.38, CW - 2.6, 0.4, [[("B · ĐÁNH GIÁ CUỐI", {"bold": True, "color": CAM}),
                                            ("   mẫu kiểm định · tập kiểm thử 8 tuần cuối",
                                             {"size": 12.5, "color": MUTED})]], size=15, anchor=MSO_ANCHOR.MIDDLE,
          align=PP_ALIGN.RIGHT)]  # căn phải để mũi tên nối từ A xuống không cắt qua chữ
buoc_b = chuoi_buoc(s, x0, 4.88, bw, 0.92, gap,
                    [("player-play", "Huấn luyện lại", f"{M['vdata-run-seeds']} lần chạy, dữ liệu trước 29/07/2020"),
                     ("list-numbers", "Xếp hạng", "mọi ứng viên của từng khách"),
                     ("scale", "Kiểm định", "Wilcoxon, bootstrap, Holm"),
                     ("checks", "Kết luận", "NeuMF-F với từng đối chứng")], mau=CAM, so0=5)
# mũi tên từ "Khoá kế hoạch" (cuối hàng A) vòng xuống đầu hàng B, đi trong khe giữa hai khung nên không cắt hình nào
xa, xb, ym = x0 + 3 * (bw + gap) + bw / 2, x0 + bw / 2, 3.98
noi = [mui_ten(s, xa, 3.42, xa, ym, color=NAVY, w=2, dau=False), mui_ten(s, xa, ym, xb, ym, color=NAVY, w=2, dau=False),
       mui_ten(s, xb, ym, xb, 4.85, color=NAVY, w=2),
       hop(s, (xa + xb) / 2 - 2.0, ym - 0.17, 4.0, 0.34, fill=WHITE, line=NAVY, lw=1, r=0.5,
           items=["cấu hình đã chọn chuyển sang mẫu kiểm định"], size=12, color=NAVY)]
nx = nhan_xet(s, "Nhận xét", "Chọn cấu hình và đánh giá cuối trên hai mẫu khách tách rời; mọi mô hình cùng dữ liệu, "
                             "cùng 5 seed.", size=15)
bam(s, ra=[tl], zoom=[A, *buoc_a], nhip=120)
bam(s, lau=[noi], zoom=[B, *buoc_b], nhip=120)
bam(s, vao=[nx])

# =============================================================================================== 7. Đối chứng
s = slide("Mô hình đối chứng", "Chương 3 · Đối chứng",
          "Khoảng 25 giây. Ba nhóm đối chứng theo góp ý của cô: mô hình đơn lẻ, học máy truyền thống, chuyên biệt cho "
          "khuyến nghị. GMF-F, MLP-F là từng nhánh có đặc trưng đứng riêng; LateFusion-F là hợp nhất muộn của chính "
          "hai nhánh đó.", blob=(-2.6, 4.4, 6.0, 6.1))
cx_ = L + CW / 2
g = the_bt(s, cx_ - 1.85, 1.95, 3.7, 0.8, "brain", "NeuMF-F", "mô hình đề xuất", fill=NAVY, line=None,
           mau_chu=WHITE, mau_phu=SUB, vong_fill=BLUE, mau_bt="trang", d=0.56, co=17, co_phu=12.5)
# mỗi nhóm là các hàng hai viên bằng nhau; hàng chỉ có một viên thì viên đó rộng hết hàng
nhom_dc = [("stack-2", "Mô hình đơn lẻ", "từng nhánh, có và không có đặc trưng",
            [["GMF", "MLP"], ["GMF-F", "MLP-F"]]),
           ("books", "Học máy truyền thống", "láng giềng, nhân tử hoá, nội dung, lai",
            [["Content", "ItemKNN"], ["UserKNN", "BPR-MF"], ["Hybrid-CBCF"]]),
           ("target-arrow", "Chuyên biệt cho khuyến nghị", "mô hình phổ biến, NCF, hợp nhất muộn",
            [["Most Popular", "NeuMF"], ["MostPopular-Recent"], ["LateFusion-F", "Random"]])]
gw, gap = 3.98, (CW - 3 * 3.98) / 2
centers = [L + k * (gw + gap) + gw / 2 for k in range(3)]
day_ = [mui_ten(s, cx_, 2.75, cx_, 3.0, color=NAVY, w=2, dau=False),
        mui_ten(s, centers[0], 3.0, centers[2], 3.0, color=NAVY, w=2, dau=False)]
day_ += [mui_ten(s, c_, 3.0, c_, 3.32, color=NAVY, w=2) for c_ in centers]
g2 = []
for k, (ic, a, phu, ms) in enumerate(nhom_dc):
    x = L + k * (gw + gap)
    gg = [the(s, x, 3.32, gw, 2.62, name=f"Nhóm {a}")]
    gg += vong(s, ic, x + 0.2, 3.48, 0.62, fill=WHITE, ti=0.56)
    gg.append(text(s, x + 0.95, 3.46, gw - 1.05, 0.66, [[(a, {"bold": True, "color": NAVY})],
                                                        [(phu, {"size": 11, "color": MUTED})]], size=14.5,
                   anchor=MSO_ANCHOR.MIDDLE, after=0))
    x_in, w_in, khe = x + 0.24, gw - 0.48, 0.14
    for r_, hang_ in enumerate(ms):
        w_ = (w_in - khe * (len(hang_) - 1)) / len(hang_)
        for c_, m in enumerate(hang_):
            gg.append(hop(s, x_in + c_ * (w_ + khe), 4.36 + r_ * 0.5, w_, 0.4, fill=WHITE, line=LINE, lw=1, r=0.5,
                          items=[m], size=13, color=INK, pad=0.02))
    g2.append(gg)
nx = nhan_xet(s, "Nhận xét", "Hậu tố -F chỉ mô hình có đặc trưng. So từng cặp có và không có -F sẽ thấy phần cải thiện "
                             "do đặc trưng.", size=14.5)
bam(s, lau=[day_], zoom=g2, auto=True, nhip=160)
bam(s, vao=[nx])


# =============================================================================================== 8–9. Kết quả
def ket_qua(ds, p, ten, n_users, the3, xet, notes):
    s = slide(f"Kết quả trên {ten}", "Chương 4 · Thực nghiệm", notes)
    text(s, L, 1.88, 7.6, 0.35, [f"NDCG@10 trên tập kiểm thử, trung bình 5 seed, {n_users} khách"], size=15,
         color=MUTED)
    bd = bieu_do(s, summary(ds), L - 0.05, 2.2, 7.8, 3.95, f"Biểu đồ NDCG@10 {ten}", co=12.5)
    g = [the_so(s, 8.35, 1.98, 4.53, 1.42, "So với NeuMF chỉ dùng ID", M[f"{p}sig-1-rel"],
                f"NDCG@10 · {M[f'{p}sig-1-phrase']}", f"{ten} NeuMF")]
    g.append(the_so(s, 8.35, 3.54, 4.53, 1.42, "Mô hình đối chứng truyền thống", n_better(p),
                    "bị NeuMF-F vượt có ý nghĩa thống kê", f"{ten} họ"))
    g.append([the(s, 8.35, 5.1, 4.53, 0.98, fill=WHITE, name=f"Thẻ ghi chú {ten}"),
              text(s, 8.58, 5.1, 4.1, 0.98, the3, size=12.5, anchor=MSO_ANCHOR.MIDDLE, after=3)])
    bam(s, lau=[bd], auto=True)
    bam(s, zoom=g, nhip=150)
    bam(s, vao=[nhan_xet(s, "Nhận xét", xet, size=14.5)])


def top_dac_trung(ds):
    """Số mô hình có đặc trưng (tên kết thúc bằng -F) đứng liền nhau ở đầu bảng xếp hạng."""
    k = 0
    for n, _ in reversed(summary(ds)):
        if not n.endswith("-F"):
            break
        k += 1
    return SO_CHU.get(k, str(k))


def so_voi_truyen_thong(p):
    """Thẻ thứ ba: NeuMF-F so với hai mô hình truyền thống mạnh nhất (UserKNN và mô hình lai Hybrid-CBCF)."""
    return [[("So với UserKNN: ", {"bold": True}), (f"{M[p + 'sig-7-rel']}, {M[p + 'sig-7-phrase']}.", {})],
            [("So với Hybrid-CBCF: ", {"bold": True}), (f"{M[p + 'sig-B1-rel']}, {M[p + 'sig-B1-phrase']}.", {})]]


ket_qua("v2", "v", "H&M", M["vdata-Btest-users"], so_voi_truyen_thong("v"),
        f"{top_dac_trung('v2').capitalize()} vị trí đầu đều là mô hình có đặc trưng; NeuMF-F tốt hơn có ý nghĩa mọi mô "
        f"hình học máy truyền thống.",
        f"Khoảng 1 phút. Trả lời câu hỏi 1. Biểu đồ hiện trước: các mô hình có đặc trưng đứng đầu. Bấm: NeuMF-F hơn "
        f"NeuMF chỉ dùng ID {M['vsig-1-rel']}, vượt có ý nghĩa {n_better('v')} mô hình đối chứng truyền thống, kể cả "
        f"UserKNN mạnh nhất và mô hình lai truyền thống Hybrid-CBCF. So sánh với các mô hình cùng dùng đặc trưng nói ở "
        f"slide hợp nhất.")
ket_qua("amazon", "a", "Amazon Beauty", M["adata-test-users"], so_voi_truyen_thong("a"),
        "Giữ nguyên cấu hình chọn trên H&M, NeuMF-F vẫn tốt hơn có ý nghĩa mọi mô hình học máy truyền thống.",
        f"Khoảng 45 giây. Bộ dữ liệu khác lĩnh vực, không có thông tin khách, không tinh chỉnh lại. Lợi ích của đặc "
        f"trưng lặp lại: NeuMF-F hơn NeuMF chỉ dùng ID {M['asig-1-rel']} và tốt hơn có ý nghĩa mọi mô hình học máy "
        f"truyền thống, kể cả Hybrid-CBCF.")

# =============================================================================================== 10. Bóc tách
s = slide("Đặc trưng nào đóng góp nhiều nhất?", "Chương 4 · Thực nghiệm",
          "Khoảng 40 giây. Trả lời câu hỏi 2. Phân tích bóc tách tắt từng nhóm đặc trưng (seed 42). H&M trước, bấm để "
          "hiện Amazon Beauty. Bỏ đặc trưng thời gian làm NDCG@10 giảm mạnh nhất trên cả hai bộ. Nếu hội đồng hỏi: "
          "phân tích chạy với seed 42 nên mang tính mô tả.")
the_hm = the_so(s, L, 1.98, 3.55, 1.75, "H&M", M["vabl-AblTime-rel"], "NDCG@10 khi bỏ đặc trưng thời gian",
                "bóc tách H&M")
the_am = the_so(s, L, 3.95, 3.55, 1.75, "Amazon Beauty", M["aabl-AblTime-rel"], "NDCG@10 khi bỏ đặc trưng thời gian",
                "bóc tách Amazon")
BIEN_THE = [("Full", "Đầy đủ"), ("AblText", "Bỏ vector văn bản"), ("AblTime", "Bỏ đặc trưng thời gian"),
            ("AblUser", "Bỏ thông tin khách"), ("AblAttr", "Bỏ thuộc tính sản phẩm")]
bd_ = []
for k, (p, ten, x, w, xt) in enumerate([("v", "H&M", 4.25, 4.75, 6.55), ("a", "Amazon Beauty", 9.15, 3.75, 9.35)]):
    t_ = text(s, xt, 1.95, 3.3, 0.35, [ten], size=16, bold=True, color=NAVY)
    data = [(lab, so(M[f"{p}abl-{key}-NDCG10"])) for key, lab in BIEN_THE]
    ch_ = bieu_do(s, data, x, 2.3, w, 3.65, f"Biểu đồ bóc tách {ten}", co=12, max_ty=1.32, dao=True)
    if k:  # tên biến thể đã ghi ở biểu đồ bên trái, cùng thứ tự
        ch_.chart.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.NONE
    bd_.append([t_, ch_])
bam(s, zoom=[the_hm], lau=[bd_[0]], auto=True)
bam(s, zoom=[the_am], lau=[bd_[1]])
bam(s, vao=[nhan_xet(s, "Nhận xét", "Đặc trưng thời gian đóng góp nhiều nhất: bỏ đi làm NDCG@10 giảm mạnh nhất "
                                    "trên cả hai bộ dữ liệu.", size=15)])

# =============================================================================================== 11. Hợp nhất
s = slide("Hợp nhất sớm và hợp nhất muộn", "Chương 4 · Thực nghiệm",
          "Khoảng 1 phút. Trả lời câu hỏi 3. Hình: hợp nhất sớm ghép hai nhánh trong một mạng, học chung; hợp nhất muộn "
          "huấn luyện hai mạng riêng rồi trộn điểm. Bảng: NeuMF-F chỉ một mạng nên thời gian huấn luyện thấp hơn và độ "
          "phủ danh mục cao hơn; hợp nhất muộn cho NDCG@10 cao hơn (trên H&M chênh lệch không có ý nghĩa thống kê). Đây "
          "là thời gian huấn luyện. Nhóm chọn hợp nhất sớm cho mô hình đề xuất vì đúng tên đề tài: một mô hình lai duy "
          "nhất, MF và DNN học chung; LateFusion-F dùng lại chính hai nhánh có đặc trưng. Bấm 2: ý nghĩa của kết quả. "
          "Bấm 3: nhận xét.")
so_do = [hinh(s, "hinh_hop_nhat", L, 1.95, 4.15 / 434)]  # hình 2.2 của báo cáo, cao 4,15 inch
rows = [("", "NeuMF-F", "LateFusion-F"),
        ("Phút huấn luyện · H&M", M["vbey-NeuMFF-time"], M["vbey-LateF-time"]),
        ("Phút huấn luyện · Amazon", M["abey-NeuMFF-time"], M["abey-LateF-time"]),
        ("Độ phủ top-10 · H&M", M["vbey-NeuMFF-cov"], M["vbey-LateF-cov"]),
        ("Độ phủ top-10 · Amazon", M["abey-NeuMFF-cov"], M["abey-LateF-cov"]),
        ("NDCG@10 · H&M", M["vres-NeuMFF-NDCG10"], M["vres-LateF-NDCG10"]),
        ("NDCG@10 · Amazon", M["ares-NeuMFF-NDCG10"], M["ares-LateF-NDCG10"])]
XB = 7.95  # bảng nằm bên phải hình
gf = s.shapes.add_table(len(rows), 3, Inches(XB), Inches(1.98), Inches(R - XB), Inches(0.46 * len(rows)))
gf.name = "Bảng so sánh"
tbl = gf.table
tbl.columns[0].width, tbl.columns[1].width, tbl.columns[2].width = Inches(2.33), Inches(1.15), Inches(R - XB - 3.48)
for r_, row in enumerate(rows):
    tbl.rows[r_].height = Inches(0.46)
    for c_, v in enumerate(row):
        cell = tbl.cell(r_, c_)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BLUE if r_ == 0 else (CARD if r_ % 2 else WHITE)
        cell.text_frame.clear()
        paras(cell.text_frame, [v], size=12 if r_ == 0 else 12.5, bold=(r_ == 0), color=WHITE if r_ == 0 else INK,
              align=PP_ALIGN.LEFT if c_ == 0 else PP_ALIGN.RIGHT, after=0)
        cell.margin_left = cell.margin_right = Inches(0.1)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
ghi = text(s, XB, 5.4, R - XB, 0.75, ["Thời gian huấn luyện mỗi lần chạy; LateFusion-F tính tổng GMF-F và MLP-F. Độ phủ: "
                                     "tỉ lệ sản phẩm có mặt trong danh sách khuyến nghị."], size=12, color=MUTED)
nx1 = nhan_xet(s, "Nhận xét", "NeuMF-F một mạng: huấn luyện nhanh hơn, gợi ý đa dạng hơn. Hợp nhất muộn cao hơn về "
                              "NDCG@10.", size=14.5)
y_nghia = [text(s, L, 1.98, CW, 0.4, ["Ý nghĩa của kết quả"], size=17, bold=True, color=NAVY)]
for k, (ic, a, b) in enumerate([
        ("stack-2", "Đặc trưng là nguồn cải thiện chính",
         (f"{top_dac_trung('v2').capitalize()} vị trí đầu trên cả hai bộ dữ liệu đều là mô hình dùng đặc trưng."
          if top_dac_trung('v2') == top_dac_trung('amazon') else
          f"{top_dac_trung('v2').capitalize()} vị trí đầu trên H&M, {top_dac_trung('amazon')} vị trí đầu trên Amazon đều "
          "là mô hình dùng đặc trưng.")),
        ("package", "NeuMF-F gọn khi triển khai",
         "Một mạng, một lần huấn luyện; danh sách khuyến nghị phủ được nhiều sản phẩm hơn."),
        ("git-merge", "Hai cách hợp nhất cùng hưởng lợi",
         "LateFusion-F dùng lại hai nhánh có đặc trưng của NeuMF-F; kết quả cao cũng nhờ đặc trưng.")]):
    x = L + k * 4.215
    y_nghia.append([the(s, x, 2.55, 4.0, 2.9, fill=WHITE if k else CARD, name=f"Thẻ ý nghĩa {k + 1}"),
                    *vong(s, ic, x + 0.25, 2.78, 0.8, ti=0.56),
                    text(s, x + 0.3, 3.75, 3.45, 0.85, [a], size=17, bold=True, color=NAVY, after=0),
                    text(s, x + 0.3, 4.6, 3.45, 0.8, [b], size=14, after=0)])
bam(s, vao=[nx1])
nx3 = nhan_xet(s, "Nhận xét", "Giá trị của đặc trưng rõ trên cả hai bộ, với cả hợp nhất sớm lẫn hợp nhất muộn.",
               size=15)
bam(s, ra=[so_do, gf, ghi, nx1], zoom=y_nghia, nhip=150)
bam(s, vao=[nx3])

# =============================================================================================== 12. Demo: kiến trúc
s = slide("Demo: kiến trúc hệ thống", "Chương 3 · Demo",
          "Khoảng 45 giây. Kiến trúc ba tầng (cùng hình 3.6 của báo cáo), bấm để đọc từng tầng: (1) giao diện web ba "
          "màn hình, chỉ gọi API; (2) API suy luận FastAPI: xếp hạng mọi ứng viên của khách bằng NeuMF-F và mô hình "
          "đối chứng được chọn, khách mới nhận danh sách bán chạy; (3) tầng mô hình và dữ liệu nạp một lần khi khởi "
          "động. Bấm 4: nhận xét.", blob=(-2.6, 4.4, 6.0, 6.1))
K12 = CW / 1254  # bản nằm ngang của hình kiến trúc demo
h_demo = hinh(s, "hinh_demo_ngang", L, 1.95, K12)
the_tang = []
for k, (a, box) in enumerate([
        ("Giao diện web: ba màn hình, chỉ gọi API, không đọc trực tiếp trọng số hay dữ liệu.", (0, 0, 340, 330)),
        ("API suy luận (FastAPI): xếp hạng mọi ứng viên của khách, trả về Top-K; khách mới nhận danh sách bán chạy.",
         (450, 0, 340, 330)),
        ("Mô hình và dữ liệu: nạp trọng số đã huấn luyện, dữ liệu và kết quả đánh giá một lần khi khởi động.",
         (900, 0, 340, 330))]):
    the_tang.append((khung_tren_hinh(s, h_demo, (0, 0), box), chu_thich(s, k + 1, a, size=14.5)))
nx = nhan_xet(s, "Nhận xét", "Demo chạy hoàn toàn trên máy, không cần mạng; số liệu trên demo là kết quả đánh giá cuối "
                             "đã lưu.", size=14.5)
bam(s, zoom=[the_tang[0]])
bam(s, ra=the_tang[0], zoom=[the_tang[1]])
bam(s, ra=the_tang[1], zoom=[the_tang[2]])
bam(s, ra=the_tang[2], vao=[nx])

# =============================================================================================== 13. Demo: giao diện
s = slide("Demo: giao diện ứng dụng", "Chương 3 · Demo",
          "Khoảng 1 phút. Mỗi lần bấm một màn hình. (1) Khuyến nghị sản phẩm: chọn khách, NeuMF-F bên trái, mô hình đối "
          "chứng bên phải, dòng xanh là món khách thật sự mua sau mốc kiểm thử. (2) Khách mới chưa có lịch sử: nhận "
          "danh sách bán chạy, không báo lỗi. (3), (4) Trang kết quả: đọc lại kết quả đánh giá cuối. Có thể chạy demo "
          "trực tiếp ở localhost:8000. Khách mẫu: H&M KH0028, KH0303; Amazon KH0376, KH0039 (NeuMF-F trúng trong "
          "top-10, NeuMF chỉ dùng ID thì không); đây là ví dụ chọn lọc, kết quả trung bình xem các slide kết quả.",
          blob=(10.3, -3.3, 6.0, 6.1))
man = [(cat_anh("cua_hang.png", "demo_v2.png", (0, 1232, 2428, 2360)), "Khuyến nghị sản phẩm",
        "NeuMF-F bên trái, đối chứng bên phải; dòng xanh là món khách mua"),
       (cat_anh("khach_moi.png", "demo_v2_new.png", (0, 0, 2428, 1460)), "Khách mới",
        "chưa có lịch sử: nhận danh sách bán chạy"),
       (cat_anh("ket_qua.png", "demo_v2_results.png", (0, 255, 1280, 790)), "Kết quả kiểm định",
        "NeuMF-F với từng đối chứng: NDCG@10 và chênh lệch"),
       (cat_anh("xep_hang.png", "demo_v2_results.png", (0, 805, 1280, 1332)), "Xếp hạng và bóc tách",
        "NDCG@10 của 15 mô hình; mức giảm khi bỏ từng nhóm đặc trưng")]
XA, WA, HA = L, 8.75, 4.85  # khung ảnh cao gần hết vùng nội dung (slide này không có thanh nhận xét)
khung_anh = the(s, XA, 1.95, WA, HA, fill=WHITE, name="Khung ảnh demo")
anh_ = [anh_vua(s, p, XA + 0.12, 2.07, WA - 0.24, HA - 0.24, f"Ảnh demo {a}") for p, a, _ in man]
XD = XA + WA + 0.2
nen_chon = [hop(s, XD, 1.95 + k * 1.22, R - XD, 1.12, fill=PALE, line=BLUE, lw=1.5, r=0.12) for k in range(4)]
ds_man = []
for k, (_, a, b) in enumerate(man):
    y = 1.95 + k * 1.22
    ds_man.append([so_tron(s, XD + 0.12, y + 0.38, k + 1, BLUE, d=0.36, size=13),
                   text(s, XD + 0.58, y, R - XD - 0.66, 1.12, [[(a, {"bold": True, "color": NAVY, "size": 14.5})],
                                                             [(b, {"size": 11.5, "color": MUTED})]],
                        anchor=MSO_ANCHOR.MIDDLE, after=1)])
bam(s, zoom=[khung_anh, [anh_[0], nen_chon[0]], *ds_man], auto=True, nhip=110)
for k in (1, 2, 3):
    bam(s, ra=[anh_[k - 1], nen_chon[k - 1]], zoom=[[anh_[k], nen_chon[k]]])

# =============================================================================================== 14. Kết luận
s = slide("Kết luận", "Chương 5 · Kết luận",
          "Khoảng 1 phút. Pha 1: trả lời lần lượt ba câu hỏi nghiên cứu (mỗi lần bấm một câu). Bấm 4: đóng góp, phạm vi "
          "nhóm đã chọn và hướng phát triển, theo chương 5 của báo cáo.")
tra_loi = [("chart-bar", "Câu hỏi 1 · Có tốt hơn đối chứng?",
            f"Có. Vượt có ý nghĩa mọi mô hình học máy truyền thống trên cả hai bộ; cao hơn NeuMF chỉ dùng ID "
            f"{M['vsig-1-rel']} (H&M), {M['asig-1-rel']} (Amazon)."),
           ("stack-2", "Câu hỏi 2 · Đặc trưng có giúp không?",
            f"Có. Đặc trưng thời gian đóng góp nhiều nhất: bỏ đi làm NDCG@10 giảm "
            f"{M['vabl-AblTime-rel'].lstrip('−-')} (H&M), {M['aabl-AblTime-rel'].lstrip('−-')} (Amazon)."),
           ("git-merge", "Câu hỏi 3 · Hợp nhất sớm hay muộn?",
            "Cả hai đều hưởng lợi từ đặc trưng. Hợp nhất sớm gọn, huấn luyện nhanh hơn; hợp nhất muộn NDCG@10 "
            "cao hơn.")]
hang = []
for k, (ic, q, a) in enumerate(tra_loi):
    y = 1.98 + k * 1.42
    hang.append([the(s, L, y, CW, 1.28, fill=CARD if k == 0 else WHITE, line=GOLD if k == 0 else LINE),
                 *vong(s, ic, L + 0.25, y + 0.29, 0.7, fill=WHITE if k == 0 else PALE, ti=0.56),
                 text(s, L + 1.2, y + 0.1, 3.4, 1.08, [q], size=16, bold=True, color=BLUE, anchor=MSO_ANCHOR.MIDDLE),
                 text(s, L + 4.75, y + 0.1, CW - 5.0, 1.08, [a], size=15, anchor=MSO_ANCHOR.MIDDLE, after=0)])
cols = [("trending-up", "Đóng góp", ["Mô hình lai có đặc trưng tốt hơn NeuMF gốc và các mô hình truyền thống được so "
                                     "sánh, trên hai bộ dữ liệu.",
                                     "Chỉ ra đặc trưng thời gian đóng góp nhiều nhất.",
                                     "Quy trình đánh giá dùng lại được cho bài toán khác."]),
        ("target-arrow", "Phạm vi", ["Mẫu khoảng 1,6% khách H&M, lọc 10-core: đủ để tinh chỉnh đều, chạy 5 seed.",
                                     "Tập trung khách, sản phẩm đã có lịch sử; khách mới nhận danh sách bán chạy.",
                                     "Mô tả sản phẩm dùng TF-IDF: gọn, dễ giải thích."]),
        ("bulb", "Hướng phát triển", ["Mở rộng dữ liệu, ngưỡng lọc thấp hơn.",
                                      "Đánh giá riêng trên sản phẩm vừa ra mắt.",
                                      "Ảnh và mô tả bằng mô hình tiền huấn luyện."])]
cot = []
for k, (ic, h_, items) in enumerate(cols):
    x = L + k * 4.215
    cot.append([the(s, x, 1.98, 4.0, 4.85, fill=WHITE if k else CARD, name=f"Thẻ {h_}"),
                *vong(s, ic, x + 0.25, 2.18, 0.8, ti=0.56),
                text(s, x + 1.2, 2.18, 2.7, 0.8, [h_], size=21, bold=True, color=NAVY, anchor=MSO_ANCHOR.MIDDLE),
                text(s, x + 0.3, 3.25, 3.45, 3.4, items, size=15, bullet=True, after=12)])
bam(s, zoom=[hang[0]], auto=True)
bam(s, zoom=[hang[1]])
bam(s, zoom=[hang[2]])
bam(s, ra=hang, zoom=cot, nhip=160)

# =============================================================================================== 15. Cảm ơn
s = slide("", "Chương 5 · Kết luận", "Cảm ơn hội đồng, mời đặt câu hỏi.", blob=(-2.2, -1.6, 6.0, 6.1))
s.shapes.title.text_frame.text = ""
hinh = anh_vua(s, CAM_ON, 0.25, 1.55, 4.9, 4.7, "Minh hoạ cảm ơn")
loi = [text(s, 5.6, 2.15, 7.3, 2.0, [[("Cảm ơn hội đồng", {"color": INK})], [("đã lắng nghe", {"color": BLUE})]],
            size=50, bold=True, after=0, spacing=1.0, name="Lời cảm ơn"),
       text(s, 5.6, 4.35, 7.3, 0.5, ["Nhóm rất mong nhận được câu hỏi và góp ý của hội đồng."], size=20, color=MUTED),
       text(s, 5.6, 5.1, 7.3, 0.5, ["Lê Minh Lý · Sử Thị Yến Linh   |   GVHD: TS. Hồ Thị Linh"], size=18, color=INK)]
bam(s, zoom=[hinh, *loi], auto=True, nhip=150)

# ----------------------------------------------------------------------------------------------- số trang, hiệu ứng
assert len(SLIDES) == 15, len(SLIDES)
for i, (s, page) in enumerate(SLIDES, 1):
    if page is not None:
        page.text_frame.paragraphs[0].runs[0].text = f"{i} / {len(SLIDES)}"
buoc = {}
for i, (s, _) in enumerate(SLIDES, 1):
    morph(s)
    if s.slide_id in ANIM:
        ghi_hieu_ung(s, ANIM[s.slide_id])
        buoc[i] = trang_thai(ANIM[s.slide_id])
    else:
        buoc[i] = [[]]
prs.save(OUT)
with open(os.path.splitext(OUT)[0] + ".buoc.json", "w", encoding="utf-8") as f:
    json.dump(buoc, f)
print("saved", OUT, len(SLIDES), "slide,", sum(len(v) for v in buoc.values()), "trạng thái")
