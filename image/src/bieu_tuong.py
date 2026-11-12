"""Biểu tượng cho sơ đồ draw.io: ô vuông bo góc tô màu chuyển nhẹ, hình vẽ nét trắng ở giữa (kiểu biểu tượng ứng dụng).

Hình vẽ lấy từ bộ Tabler Icons (giấy phép MIT, https://tabler.io/icons), các tệp SVG nằm ở
Report DACNTT/slides/media/tabler/. Mỗi biểu tượng nhúng thẳng vào draw.io dưới dạng data URI nên tệp .drawio mở được ở
máy khác mà không cần thư viện ngoài.
"""
import base64
import re
from pathlib import Path

TABLER = Path(__file__).resolve().parents[2] / "Report DACNTT" / "slides" / "media" / "tabler"

# màu ô: (sáng, đậm), chuyển từ góc trên trái xuống góc dưới phải
MAU_O = {
    "xam": ("#8A99AF", "#56657C"),
    "xanh": ("#3B86E6", "#1858B0"),
    "tim": ("#8E70C4", "#593C8A"),
    "cam": ("#F5A04F", "#D2651A"),
    "la": ("#4CAF63", "#2A7A3B"),
    "navy": ("#5B7BB3", "#1F3A5F"),
}


def _net(ten: str) -> str:
    """Các phần tử vẽ của một biểu tượng Tabler (bỏ khung 24×24 trong suốt)."""
    svg = (TABLER / f"{ten}.svg").read_text(encoding="utf-8")
    body = svg[svg.index(">", svg.index("<svg")) + 1: svg.rindex("</svg>")]
    return re.sub(r'<path stroke="none" d="M0 0h24v24H0z" fill="none"\s*/>', "", body).strip()


def o(ten: str, mau: str = "xanh") -> str:
    """Data URI của biểu tượng `ten` (tên tệp Tabler) trên ô màu `mau`."""
    a, b = MAU_O[mau]
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>"
           f"<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='{a}'/>"
           f"<stop offset='1' stop-color='{b}'/></linearGradient></defs>"
           "<rect x='2' y='2' width='60' height='60' rx='16' fill='url(#g)'/>"
           "<rect x='2' y='2' width='60' height='30' rx='16' fill='#FFFFFF' opacity='0.10'/>"
           "<g transform='translate(14 14) scale(1.5)' fill='none' stroke='#FFFFFF' stroke-width='1.9' "
           f"stroke-linecap='round' stroke-linejoin='round'>{_net(ten).replace(chr(34), chr(39))}</g></svg>")
    return "data:image/svg+xml," + base64.b64encode(svg.encode("utf-8")).decode()
