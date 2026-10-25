"""Bộ dựng sơ đồ draw.io cho báo cáo và slide.

Bảng màu (mỗi màu một nghĩa, dùng chung cho mọi hình):
- xám: dữ liệu, đầu vào;               - xanh dương: bước xử lý, nhánh GMF;
- tím nhạt: nhánh MLP;                 - cam: bước chính, phép hợp nhất;
- xanh lá: kết quả, đầu ra.
Ngoài hộp chữ còn có các hình minh hoạ theo quy ước của bài báo NCF: vector là một dãy ô, vector one-hot có một ô
tô đậm, phép toán (⊙, σ) là vòng tròn nhỏ, kho dữ liệu là hình trụ, màn hình giao diện là khung cửa sổ.
Chữ trong hình không in đậm.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from xml.sax.saxutils import quoteattr

DRAWIO = Path.home() / "AppData/Local/Programs/draw.io/draw.io.exe"

MAU = {  # tên: (nền, viền)
    "xam": ("#F2F2F2", "#7F7F7F"),
    "xanh": ("#DEEBF7", "#2E75B6"),
    "tim": ("#EAE4F2", "#7451A8"),
    "cam": ("#FCE4D6", "#C55A11"),
    "la": ("#E2EFDA", "#548235"),
    "trang": ("#FFFFFF", "#404040"),
}
O_DAM = {"xam": "#7F7F7F", "xanh": "#5B9BD5", "tim": "#9A7FC7", "cam": "#E28743", "la": "#8DB86B"}

_BASE = "fontFamily=Helvetica;html=1;whiteSpace=wrap;fontColor=#1A1A1A;"


def _hop(mau: str, them: str = "") -> str:
    nen, vien = MAU[mau]
    return _BASE + f"rounded=1;arcSize=8;fillColor={nen};strokeColor={vien};align=center;verticalAlign=middle;spacing=4;" + them


STYLE = {
    "nguon": _hop("xam"),
    "xuly": _hop("xanh"),
    "mohinh": _hop("xanh", "strokeWidth=1.5;"),
    "mlp": _hop("tim"),
    "chinh": _hop("cam", "strokeWidth=2;"),
    "ketqua": _BASE + f"shape=ellipse;perimeter=ellipsePerimeter;fillColor={MAU['la'][0]};strokeColor={MAU['la'][1]};align=center;verticalAlign=middle;",
    "ketqua_hop": _hop("la"),
    "phanhe": _BASE + "rounded=1;arcSize=3;fillColor=#F7F9FC;strokeColor=#BFCADB;fontColor=#1F3864;align=left;verticalAlign=top;spacingLeft=10;spacingTop=4;",
    "chu": _BASE + "text;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;",
    "tru": _BASE + f"shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=8;fillColor={MAU['xam'][0]};strokeColor={MAU['xam'][1]};align=center;verticalAlign=middle;",
    "tru_la": _BASE + f"shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=8;fillColor={MAU['la'][0]};strokeColor={MAU['la'][1]};align=center;verticalAlign=middle;",
    "tailieu": _BASE + f"shape=document;boundedLbl=1;size=0.18;fillColor={MAU['xam'][0]};strokeColor={MAU['xam'][1]};align=center;verticalAlign=middle;",
    "phep": _BASE + "shape=ellipse;perimeter=ellipsePerimeter;fillColor=#FFFFFF;strokeColor=#404040;align=center;verticalAlign=middle;",
    "khung": _BASE + "rounded=0;fillColor=none;strokeColor=none;",
    # thanh thời gian
    "huanluyen": _BASE + f"rounded=0;fillColor=#C5D9F1;strokeColor={MAU['xanh'][1]};align=center;verticalAlign=middle;spacing=2;",
    "xacthuc": _BASE + f"rounded=0;fillColor=#C6E0B4;strokeColor={MAU['la'][1]};align=center;verticalAlign=middle;spacing=2;",
    "kiemthu": _BASE + f"rounded=0;fillColor=#F8CBAD;strokeColor={MAU['cam'][1]};align=center;verticalAlign=middle;spacing=2;",
}
EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;endSize=5;strokeColor=#404040;"
        "strokeWidth=1.3;fontFamily=Helvetica;")
LINE = "endArrow=none;html=1;strokeColor=#404040;strokeWidth=1.3;"


class Trang:
    """Một trang draw.io; thêm ô bằng o(...), mũi tên bằng mt(...), vector dãy ô bằng vec(...)."""

    def __init__(self, ten: str, co_chu: int = 13):
        self.ten, self.co = ten, co_chu
        self.cells: list[str] = []
        self.n = 1

    def _id(self) -> str:
        self.n += 1
        return f"c{self.n}"

    def o(self, loai: str, x, y, w, h, text: str = "", co: int | None = None, them: str = "", parent: str = "1") -> str:
        cid = self._id()
        style = STYLE[loai] + f"fontSize={co or self.co};" + them
        self.cells.append(
            f'<mxCell id="{cid}" value={quoteattr(text)} style={quoteattr(style)} vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def vec(self, x, y, n: int, mau: str, o: int = 14, nhan: str = "", vi: str = "duoi", onehot: int | None = None,
            mau_sau: str | None = None, n_sau: int = 0, rong_nhan: int = 120) -> str:
        """Vector vẽ thành n ô vuông cạnh o (thêm n_sau ô màu mau_sau nếu là vector nối). Trả về id khung bao để nối
        mũi tên. onehot = vị trí ô tô đậm (vector one-hot, các ô khác trắng). vi = chỗ đặt nhãn: duoi, tren, trai, phai."""
        w = (n + n_sau) * o
        k = self.o("khung", x, y, w, o)
        for j in range(n + n_sau):
            m = mau if j < n else mau_sau
            nen = MAU[m][0]
            if onehot is not None:
                nen = O_DAM[m] if j == onehot else "#FFFFFF"
            self.o("khung", j * o, 0, o, o, them=f"fillColor={nen};strokeColor={MAU[m][1]};strokeWidth=1;", parent=k)
        if nhan:
            if vi in ("duoi", "tren"):
                self.o("chu", x - 40, y - 22 if vi == "tren" else y + o + 2, w + 80, 20, nhan, co=self.co - 1)
            elif vi == "trai":
                self.o("chu", x - rong_nhan - 4, y - 3, rong_nhan, o + 6, nhan, co=self.co - 1, them="align=right;")
            else:
                self.o("chu", x + w + 4, y - 3, rong_nhan, o + 6, nhan, co=self.co - 1, them="align=left;")
        return k

    def mt(self, a: str, b: str, ra="", vao="", diem=(), nhan: str = "", them: str = "") -> str:
        """Mũi tên a -> b. ra/vao: 'tren', 'duoi', 'trai', 'phai' hoặc (x, y) tương đối 0..1; diem: các điểm gãy."""
        P = {"tren": (0.5, 0), "duoi": (0.5, 1), "trai": (0, 0.5), "phai": (1, 0.5)}
        style = EDGE + them
        for k, v in (("exit", ra), ("entry", vao)):
            if v:
                x, y = P[v] if isinstance(v, str) else v
                style += f"{k}X={x};{k}Y={y};{k}Dx=0;{k}Dy=0;"
        style += f"fontSize={self.co - 1};labelBackgroundColor=#FFFFFF;"
        pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in diem)
        arr = f'<Array as="points">{pts}</Array>' if diem else ""
        cid = self._id()
        self.cells.append(
            f'<mxCell id="{cid}" value={quoteattr(nhan)} style={quoteattr(style)} edge="1" parent="1" source="{a}" target="{b}">'
            f'<mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')
        return cid

    def duong(self, x1, y1, x2, y2, mui_ten: bool = False, net_dut: bool = False) -> str:
        """Đoạn thẳng tự do (trục thời gian, vạch chia)."""
        style = (EDGE if mui_ten else LINE) + ("dashed=1;" if net_dut else "")
        cid = self._id()
        self.cells.append(
            f'<mxCell id="{cid}" style={quoteattr(style)} edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{x1}" y="{y1}" as="sourcePoint"/><mxPoint x="{x2}" y="{y2}" as="targetPoint"/></mxGeometry></mxCell>')
        return cid

    def cua_so(self, x, y, w, h, ten: str) -> str:
        """Màn hình giao diện: khung cửa sổ có thanh tiêu đề."""
        k = self.o("khung", x, y, w, h, them="fillColor=#FFFFFF;strokeColor=#7F7F7F;")
        self.o("khung", 0, 0, w, 12, them="fillColor=#D9D9D9;strokeColor=#7F7F7F;", parent=k)
        for j in range(3):
            self.o("khung", 6 + j * 8, 3, 6, 6, them="shape=ellipse;fillColor=#FFFFFF;strokeColor=#7F7F7F;", parent=k)
        self.o("chu", 0, 12, w, h - 12, ten, parent=k)
        return k

    def xml(self, i: int) -> str:
        body = '<mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(self.cells)
        return (f'<diagram id="p{i}" name={quoteattr(self.ten)}><mxGraphModel grid="0" page="0" math="0" shadow="0">'
                f'<root>{body}</root></mxGraphModel></diagram>')


def b(s: str) -> str:
    """Tên khối: giữ nguyên chữ thường, không in đậm (người dùng không muốn chữ đậm trong hình)."""
    return s


def ghi(trangs: list[Trang], path: Path) -> None:
    pages = "".join(t.xml(i) for i, t in enumerate(trangs, 1))
    path.write_text(f'<mxfile host="drawio">{pages}</mxfile>', encoding="utf-8")


def xuat(path: Path, i: int, out: Path, fmt: str) -> None:
    """Xuất trang i (đếm từ 1) ra PNG hoặc PDF bằng draw.io desktop."""
    args = [str(DRAWIO), "--export", "--format", fmt, "--page-index", str(i), "--border", "6", "--output", str(out)]
    args += ["--crop"] if fmt == "pdf" else ["--scale", "2"]
    subprocess.run(args + [str(path)], check=True, capture_output=True)
