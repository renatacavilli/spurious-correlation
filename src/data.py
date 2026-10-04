"""Download the two public datasets and build the yearly table used by every script."""
from __future__ import annotations

import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed" / "avocados_sp500_yearly.csv"

SOURCES = {
    "avocado_production_owid.csv": (
        "https://ourworldindata.org/grapher/avocado-production.csv"
        "?v=1&csvType=full&useColumnShortNames=true"
    ),
    "sp500_shiller_monthly.csv": (
        "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv"
    ),
}


def fetch(name: str) -> Path:
    """Return the path of a raw file, downloading it first if it is not there."""
    path = RAW / name
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(SOURCES[name], headers={"User-Agent": "Mozilla/5.0"})
        path.write_bytes(urllib.request.urlopen(request).read())
    return path


def build_yearly() -> pd.DataFrame:
    """Merge world avocado production and the S&P 500 into one row per year."""
    avocados = pd.read_csv(fetch("avocado_production_owid.csv"))
    avocados = avocados[avocados["entity"] == "World"].set_index("year").iloc[:, -1]

    sp500 = pd.read_csv(fetch("sp500_shiller_monthly.csv"), parse_dates=["Date"])
    sp500 = sp500.groupby(sp500["Date"].dt.year)["SP500"].mean()

    yearly = pd.concat(
        [avocados.rename("avocado_production_tonnes"), sp500.rename("sp500_yearly_mean")], axis=1
    ).dropna()
    yearly.index.name = "year"
    yearly["avocado_production_tonnes"] = yearly["avocado_production_tonnes"].astype(int)
    yearly["sp500_yearly_mean"] = yearly["sp500_yearly_mean"].round(2)
    yearly["avocado_change_pct"] = (yearly["avocado_production_tonnes"].pct_change() * 100).round(2)
    yearly["sp500_change_pct"] = (yearly["sp500_yearly_mean"].pct_change() * 100).round(2)
    return yearly


def load_yearly() -> pd.DataFrame:
    """Load the processed yearly table, building and saving it on first use."""
    if not PROCESSED.exists():
        PROCESSED.parent.mkdir(parents=True, exist_ok=True)
        build_yearly().to_csv(PROCESSED)
    return pd.read_csv(PROCESSED, index_col="year")


if __name__ == "__main__":
    PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    table = build_yearly()
    table.to_csv(PROCESSED)
    print(f"Saved {PROCESSED.relative_to(ROOT)}: {table.index.min()}-{table.index.max()}, {len(table)} years")
