"""Shared colours (from the template) and matplotlib style for the slide figures."""

import matplotlib.pyplot as plt

# Template palette ("Aarhus Agentic Meetup.pptx")
GREY = "#595959"  # text, data points
GREY_DARK = "#404040"
GREY_MID = "#A6A6A6"
GREY_LIGHT = "#BFBFBF"
GREY_BAR = "#EDEDED"  # decorative bars
GREY_CARD = "#F2F2F2"  # cards
WHITE = "#FFFFFF"

BLUE = "#92B0D0"
BLUE_DARK = "#5B7FA6"  # darker shade of BLUE, for thin lines and text
BLUE_LIGHT = "#DCE6F1"

ROSE = "#BC6D86"
ROSE_DARK = "#855669"
ROSE_LIGHT = "#DFAFBA"

SAGE = "#8BB57C"
SAGE_DARK = "#5E8C4F"
SAGE_LIGHT = "#D9EAD3"

FONTS = ["Lao UI", "Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"]


def use_style(base_size: float = 14) -> None:
    """Apply the course matplotlib style. `base_size` is the tick-label size in pt."""
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": FONTS,
            "mathtext.fontset": "stixsans",
            "font.size": base_size,
            "axes.titlesize": base_size + 2,
            "axes.labelsize": base_size + 1,
            "xtick.labelsize": base_size,
            "ytick.labelsize": base_size,
            "legend.fontsize": base_size,
            "text.color": GREY,
            "axes.labelcolor": GREY,
            "axes.edgecolor": GREY_LIGHT,
            "axes.linewidth": 1.0,
            "axes.titlecolor": GREY,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GREY_BAR,
            "grid.linewidth": 1.0,
            "axes.axisbelow": True,
            "xtick.color": GREY,
            "ytick.color": GREY,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "legend.frameon": False,
            "lines.linewidth": 2.5,
            "lines.solid_capstyle": "round",
            "scatter.edgecolors": "none",
            "axes.prop_cycle": plt.cycler(color=[GREY, BLUE, ROSE, SAGE]),
            "figure.facecolor": WHITE,
            "axes.facecolor": WHITE,
            "savefig.facecolor": WHITE,
            "axes.unicode_minus": True,
            "figure.dpi": 100,
        }
    )
