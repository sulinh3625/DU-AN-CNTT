"""Chuyển các biểu tượng Tabler (media/tabler/*.svg, giấy phép MIT, https://tabler.io/icons) sang PNG 256 px có nền
trong suốt, mỗi biểu tượng hai màu: xanh của slide và trắng. PNG ghi vào media/icons/<tên>_<màu>.png.
Vẽ SVG bằng Microsoft Edge chạy ngầm (có sẵn trên Windows), rồi cắt từng ô bằng Pillow.
Chạy: python tao_bieu_tuong.py
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC, OUT = HERE / "media" / "tabler", HERE / "media" / "icons"
EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
MAU = {"xanh": "#1E46D1", "trang": "#FFFFFF"}
S, COT = 256, 8


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    viec = [(p, ten, mau) for p in sorted(SRC.glob("*.svg")) for ten, mau in MAU.items()]
    hang = (len(viec) + COT - 1) // COT
    o = []
    for p, _, mau in viec:
        svg = p.read_text("utf-8").replace('stroke="currentColor"', f'stroke="{mau}"')
        svg = svg.replace('width="24"', f'width="{S}"').replace('height="24"', f'height="{S}"')
        o.append(f"<div>{svg}</div>")
    html = ("<!doctype html><html><head><style>html,body{margin:0;background:transparent}"
            f"body{{display:grid;grid-template-columns:repeat({COT},{S}px);grid-auto-rows:{S}px}}"
            "div{width:256px;height:256px}svg{display:block}</style></head><body>" + "".join(o) + "</body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        f, png = Path(tmp) / "icons.html", Path(tmp) / "icons.png"
        f.write_text(html, encoding="utf-8")
        subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--default-background-color=00000000", f"--window-size={COT * S},{hang * S}",
                        f"--screenshot={png}", f.as_uri()], check=True, capture_output=True, timeout=120)
        tam = Image.open(png).convert("RGBA")
        for i, (p, ten, _) in enumerate(viec):
            x, y = (i % COT) * S, (i // COT) * S
            tam.crop((x, y, x + S, y + S)).save(OUT / f"{p.stem}_{ten}.png")
    print(len(viec), "biểu tượng -> media/icons")


if __name__ == "__main__":
    main()
