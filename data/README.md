# Data

## `raw/`: the files exactly as downloaded

| File | Content | Source | Licence |
|---|---|---|---|
| `avocado_production_owid.csv` | Avocado production in tonnes, by country and region, 1961–2024 | FAO, via [Our World in Data](https://ourworldindata.org/grapher/avocado-production) | CC BY 4.0 |
| `sp500_shiller_monthly.csv` | S&P 500 monthly averages since 1871, with dividends, earnings and CPI | Robert Shiller, via [datasets/s-and-p-500](https://github.com/datasets/s-and-p-500) | Public Domain Dedication and License |

Both files were downloaded on 4 October 2026. `src/data.py` downloads them again if they are missing.

## `processed/`: the table every script uses

`avocados_sp500_yearly.csv` has one row per year, from 1961 to 2024.

| Column | Meaning |
|---|---|
| `year` | Calendar year |
| `avocado_production_tonnes` | World avocado production (the `World` row of the FAO data) |
| `sp500_yearly_mean` | Mean of the twelve monthly S&P 500 values of that year |
| `avocado_change_pct` | Percentage change in production on the previous year |
| `sp500_change_pct` | Percentage change in the S&P 500 yearly mean on the previous year |

The first year has no previous year, so its two change columns are empty.

Rebuild the table with:

```bash
python src/data.py
```
