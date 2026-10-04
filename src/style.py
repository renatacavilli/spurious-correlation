"""Shared colours and matplotlib settings so every figure looks the same."""
import matplotlib.pyplot as plt

GREEN = "#5B8C2A"    # avocados
BLUE = "#156082"     # S&P 500
RED = "#C8553D"      # highlighted result
DARK = "#374151"
GREY = "#9CA3AF"


def apply() -> None:
    plt.rcParams.update({
        "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    })
