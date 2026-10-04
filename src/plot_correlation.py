"""Main figure: avocado production and the S&P 500 in levels and in yearly changes."""
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

import style
from data import ROOT, load_yearly

FIGURE = ROOT / "figures" / "avocados_sp500.png"


def main() -> None:
    df = load_yearly()
    avocados = df["avocado_production_tonnes"] / 1e6          # million tonnes
    sp500 = df["sp500_yearly_mean"]
    changes = df[["avocado_change_pct", "sp500_change_pct"]].dropna()

    r_levels, _ = stats.pearsonr(avocados, sp500)
    r_changes, p_changes = stats.pearsonr(changes["avocado_change_pct"], changes["sp500_change_pct"])
    print(f"{df.index.min()}-{df.index.max()}, {len(df)} years")
    print(f"levels:         r = {r_levels:.2f}")
    print(f"yearly changes: r = {r_changes:.2f} (p = {p_changes:.2f})")

    style.apply()
    fig, (left, right) = plt.subplots(1, 2, figsize=(12.5, 5.6))

    left.plot(df.index, avocados, color=style.GREEN, lw=2.6)
    left.set_ylabel("World avocado production (million tonnes)", color=style.GREEN)
    left.tick_params(axis="y", colors=style.GREEN)
    left.set_ylim(0, 12)
    twin = left.twinx()
    twin.plot(df.index, sp500, color=style.BLUE, lw=2.6)
    twin.set_ylabel("S&P 500 (yearly average)", color=style.BLUE)
    twin.tick_params(axis="y", colors=style.BLUE)
    twin.set_ylim(0, 6000)
    twin.spines["top"].set_visible(False)
    twin.spines["right"].set_visible(True)
    left.text(0.05, 0.93, f"r = {r_levels:.2f}", transform=left.transAxes, va="top", fontsize=18, fontweight="bold")
    left.text(0.05, 0.81, "Avocados", transform=left.transAxes, color=style.GREEN, fontweight="bold")
    left.text(0.05, 0.75, "S&P 500", transform=left.transAxes, color=style.BLUE, fontweight="bold")
    left.set_title("Levels: the two lines move together", loc="left", fontsize=14, fontweight="bold")
    left.grid(alpha=0.25)

    x, y = changes["avocado_change_pct"], changes["sp500_change_pct"]
    slope, intercept, *_ = stats.linregress(x, y)
    xs = np.linspace(x.min(), x.max(), 50)
    right.axhline(0, color=style.GREY, lw=0.8)
    right.axvline(0, color=style.GREY, lw=0.8)
    right.scatter(x, y, s=60, color=style.DARK, alpha=0.7, edgecolor="white", linewidth=0.8, zorder=3)
    right.plot(xs, intercept + slope * xs, color=style.RED, lw=2, zorder=2)
    right.text(0.05, 0.93, f"r = {r_changes:.2f}", transform=right.transAxes, va="top",
               fontsize=18, fontweight="bold", color=style.RED)
    right.set_xlabel("Avocado production, change on previous year (%)")
    right.set_ylabel("S&P 500, change on previous year (%)")
    right.set_title("Yearly changes: no relationship at all", loc="left", fontsize=14, fontweight="bold")
    right.grid(alpha=0.25, zorder=0)

    fig.suptitle(f"Do avocados move the stock market? {df.index.min()} to {df.index.max()}",
                 x=0.01, ha="left", fontsize=18, fontweight="bold")
    fig.text(0.01, 0.005, "Data: FAO via Our World in Data (avocado production); Robert Shiller (S&P 500, monthly averages).",
             fontsize=9.5, color="#6B7280")
    fig.tight_layout(rect=(0, 0.03, 1, 0.99))
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"Saved {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
