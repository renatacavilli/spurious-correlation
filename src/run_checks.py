"""Five checks of whether the avocado / S&P 500 relationship is real.

1. Spurious-regression diagnostic: R^2 against the Durbin-Watson statistic.
2. Engle-Granger cointegration test: do the two series share a long-run equilibrium?
3. Detrending: correlation after removing each series' own time trend.
4. Yearly changes: permutation test and bootstrap confidence interval.
5. Simulation: how correlated are two independent random walks with the same drift?

Writes results/checks.csv and figures/avocados_sp500_checks.png.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import coint

import style
from data import ROOT, load_yearly

FIGURE = ROOT / "figures" / "avocados_sp500_checks.png"
RESULTS = ROOT / "results" / "checks.csv"
SEED = 7
N_RESAMPLES = 10_000


def main() -> None:
    rng = np.random.default_rng(SEED)
    df = load_yearly()
    levels = df[["avocado_production_tonnes", "sp500_yearly_mean"]].rename(
        columns={"avocado_production_tonnes": "avocados", "sp500_yearly_mean": "sp500"})
    logs = np.log(levels)                   # both series grow exponentially, so work in logs
    growth = logs.diff().dropna()           # yearly log changes, used to calibrate the simulation
    changes = df[["avocado_change_pct", "sp500_change_pct"]].dropna().to_numpy()
    n = len(levels)
    r_levels, _ = stats.pearsonr(levels["avocados"], levels["sp500"])
    rows = [("0. Headline", "Correlation of levels", r_levels)]

    # 1. spurious regression: a high R^2 with strongly autocorrelated residuals
    ols = sm.OLS(logs["sp500"], sm.add_constant(logs["avocados"])).fit()
    dw = durbin_watson(ols.resid)
    rows += [("1. Regression in log levels", "R squared", ols.rsquared),
             ("1. Regression in log levels", "Durbin-Watson statistic", dw)]

    # 2. cointegration: H0 = the two series are not cointegrated
    eg_stat, eg_p, _ = coint(logs["sp500"], logs["avocados"], trend="c")
    rows += [("2. Engle-Granger cointegration", "Test statistic", eg_stat),
             ("2. Engle-Granger cointegration", "p-value", eg_p)]

    # 3. remove a linear time trend from each log series and correlate what is left
    time = sm.add_constant(np.arange(n))
    detrended = pd.DataFrame({c: sm.OLS(logs[c], time).fit().resid for c in logs})
    r_detrended, _ = stats.pearsonr(detrended["avocados"], detrended["sp500"])
    rows += [("3. Detrended log levels", "Correlation", r_detrended)]

    # 4. yearly changes: shuffle the years (permutation) and resample them (bootstrap)
    r_changes = np.corrcoef(changes[:, 0], changes[:, 1])[0, 1]
    shuffled = np.array([np.corrcoef(rng.permutation(changes[:, 0]), changes[:, 1])[0, 1]
                         for _ in range(N_RESAMPLES)])
    p_permutation = (np.abs(shuffled) >= abs(r_changes)).mean()
    picks = rng.integers(0, len(changes), size=(N_RESAMPLES, len(changes)))
    bootstrap = np.array([np.corrcoef(changes[i, 0], changes[i, 1])[0, 1] for i in picks])
    ci_low, ci_high = np.percentile(bootstrap, [2.5, 97.5])
    rows += [("4. Yearly changes", "Correlation", r_changes),
             ("4. Yearly changes", "Permutation p-value", p_permutation),
             ("4. Yearly changes", "Bootstrap 95% CI, lower", ci_low),
             ("4. Yearly changes", "Bootstrap 95% CI, upper", ci_high)]

    # 5. independent random walks with each series' own average growth and volatility
    def random_walks(column: str) -> np.ndarray:
        steps = rng.normal(growth[column].mean(), growth[column].std(), (N_RESAMPLES, n))
        return np.exp(np.cumsum(steps, axis=1))

    a, s = random_walks("avocados"), random_walks("sp500")
    a, s = a - a.mean(1, keepdims=True), s - s.mean(1, keepdims=True)
    simulated = (a * s).sum(1) / np.sqrt((a ** 2).sum(1) * (s ** 2).sum(1))
    rows += [("5. Independent random walks", "Median correlation", np.median(simulated)),
             ("5. Independent random walks", "Share of pairs with r > 0.9", (simulated > 0.9).mean())]

    results = pd.DataFrame(rows, columns=["check", "statistic", "value"]).round({"value": 3})
    RESULTS.parent.mkdir(exist_ok=True)
    results.to_csv(RESULTS, index=False)
    print(f"Sample: {df.index.min()}-{df.index.max()}, {n} years\n")
    print(results.to_string(index=False))

    style.apply()
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))

    ax = axes[0]
    ax.hist(simulated, bins=60, color=style.GREY, zorder=2)
    ax.axvline(r_levels, color=style.RED, lw=2.2, zorder=3)
    ax.text(0.05, 0.92, f"avocados vs S&P 500\nr = {r_levels:.2f}", transform=ax.transAxes,
            color=style.RED, va="top", fontweight="bold")
    ax.set_xlabel("Correlation between two independent random walks")
    ax.set_ylabel("Simulated pairs")
    ax.set_title(f"Unrelated trending series are\nhighly correlated: median r = {np.median(simulated):.2f}",
                 loc="left", fontsize=13, fontweight="bold")

    ax = axes[1]
    ax.plot(df.index, detrended["avocados"], color=style.GREEN, lw=2.2, label="Avocados")
    ax.plot(df.index, detrended["sp500"], color=style.BLUE, lw=2.2, label="S&P 500")
    ax.axhline(0, color=style.GREY, lw=0.8)
    ax.legend(frameon=False, loc="upper left")
    ax.set_ylabel("Deviation from own trend (log points)")
    ax.set_title(f"With each trend removed,\nnothing is left: r = {r_detrended:.2f}",
                 loc="left", fontsize=13, fontweight="bold")

    ax = axes[2]
    ax.hist(shuffled, bins=60, color=style.GREY, zorder=2)
    ax.axvline(r_changes, color=style.RED, lw=2.2, zorder=3)
    ax.text(0.72, 0.92, f"observed\nr = {r_changes:.2f}", transform=ax.transAxes,
            color=style.RED, va="top", fontweight="bold")
    ax.set_xlabel("Correlation of yearly changes when the years are shuffled")
    ax.set_ylabel("Shuffles")
    ax.set_title(f"Yearly changes look like\npure chance: p = {p_permutation:.2f}",
                 loc="left", fontsize=13, fontweight="bold")

    for ax in axes:
        ax.grid(alpha=0.25, zorder=0)
    fig.tight_layout()
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"\nSaved {FIGURE.relative_to(ROOT)} and {RESULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
