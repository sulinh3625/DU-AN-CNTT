"""Xuất từng trang của một file .drawio ra PNG (và PDF nếu cần) khi máy không cài draw.io desktop.

Cách làm: dựng một trang HTML nạp trình xem chính thức của draw.io (viewer-static.min.js, cần mạng), rồi dùng Microsoft
Edge chạy ngầm (có sẵn trên Windows) để chụp PNG hoặc in PDF. PDF giữ dạng vector, dùng cho báo cáo LaTeX.
Khổ ảnh lấy theo khung bao các hình của từng trang, cộng lề VIEN điểm ảnh mỗi bên.

Chạy: python xuat_anh_drawio.py <file.drawio> <thư_mục_png> [tên_1 tên_2 ...]
Không có tên thì ảnh đặt theo số trang: trang_1.png, trang_2.png, ...
"""
import html
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
VIEWER = "https://viewer.diagrams.net/js/viewer-static.min.js"
SCALE = 2   # hệ số điểm ảnh của PNG
VIEN = 6    # lề quanh hình


def _khung(d) -> tuple[int, int]:
    """Rộng, cao của khung bao mọi hình (vertex) trên trang."""
    xs, ys = [], []
    for c in d.iter("mxCell"):
        g = c.find("mxGeometry")
        if c.get("vertex") == "1" and g is not None and c.get("parent") == "1":
            x, y = float(g.get("x", 0)), float(g.get("y", 0))
            xs += [x, x + float(g.get("width", 0))]
            ys += [y, y + float(g.get("height", 0))]
    return int(max(xs) - min(xs)) + 2 * VIEN + 2, int(max(ys) - min(ys)) + 2 * VIEN + 2


def _html(d, w, h) -> str:
    one = ET.Element("mxfile")
    one.append(d)
    cfg = {"xml": ET.tostring(one, encoding="unicode"), "border": VIEN,
           "fit": False, "zoom": 1, "resize": False}
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>@page{{size:{w}px {h + 6}px;margin:0}}"
            f"html,body{{margin:0;background:#fff;overflow:hidden;height:{h}px}}.mxgraph{{width:{w}px;height:{h}px}}</style>"
            f"</head><body><div class='mxgraph' data-mxgraph=\"{html.escape(json.dumps(cfg))}\"></div>"
            f"<script src='{VIEWER}'></script></body></html>")


def _edge(args: list[str], page: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "x.html"
        f.write_text(page, encoding="utf-8")
        subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--virtual-time-budget=15000", *args, f.as_uri()],
                       check=True, capture_output=True, timeout=180)


def xuat(drawio: Path, png_dir: Path, ten: list[str] | None = None, pdf_dir: Path | None = None,
         scale: int = SCALE) -> list[Path]:
    png_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for i, d in enumerate(ET.parse(drawio).getroot().findall("diagram")):
        w, h = _khung(d)
        page = _html(d, w, h)
        stem = ten[i] if ten and i < len(ten) else f"trang_{i + 1}"
        p = png_dir / f"{stem}.png"
        _edge([f"--force-device-scale-factor={scale}", f"--window-size={w},{h}", f"--screenshot={p}"], page)
        out.append(p)
        if pdf_dir is not None:
            pdf_dir.mkdir(parents=True, exist_ok=True)
            _edge(["--no-pdf-header-footer", "--print-to-pdf-no-header", f"--print-to-pdf={pdf_dir / (stem + '.pdf')}"],
                  page)
        print("->", p.name, f"{w}×{h}")
    return out


if __name__ == "__main__":
    xuat(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:] or None)
