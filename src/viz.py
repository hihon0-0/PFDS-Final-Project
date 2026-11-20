"""Style matplotlib thống nhất cho mọi biểu đồ của đồ án."""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter, PercentFormatter

# Bảng màu phân loại (thứ tự cố định, không xoay vòng)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
NEUTRAL = "#9a9890"

# Màu cố định theo thực thể – dùng lại ở mọi biểu đồ để người đọc không phải học lại
GROUP_COLORS = {
    "Có luật công khai lương": SERIES[0],
    "Chỉ khi được hỏi": SERIES[3],
    "Không có luật": NEUTRAL,
    "Remote": SERIES[0],
    "Tại chỗ / hybrid": SERIES[1],
}

SEQ_CMAP = LinearSegmentedColormap.from_list("seq_blue", ["#eef4fc", "#9cc3ef", "#2a78d6", "#123f75"])
DIV_CMAP = LinearSegmentedColormap.from_list("div", [SERIES[1], "#f2f1ee", SERIES[0]])


def set_style() -> None:
    mpl.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "figure.figsize": (9, 5),
        "font.size": 10.5,
        "axes.titlesize": 12.5,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelcolor": TEXT_2,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "xtick.color": TEXT_2,
        "ytick.color": TEXT_2,
        "text.color": TEXT,
        "legend.frameon": False,
        "axes.prop_cycle": mpl.cycler(color=SERIES),
        "lines.linewidth": 2,
        "lines.markersize": 7,
    })


usd = FuncFormatter(lambda x, _: f"${x/1000:,.0f}k")
pct = PercentFormatter(1.0, decimals=0)


def note(ax, text: str, y: float = -0.16) -> None:
    """Chú thích nguồn/ghi chú nhỏ dưới biểu đồ."""
    ax.annotate(text, xy=(0, y), xycoords="axes fraction", fontsize=8.5,
                color=TEXT_2, ha="left", va="top")
