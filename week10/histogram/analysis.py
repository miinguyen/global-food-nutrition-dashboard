import numpy as np
import plotly.express as px

gapminder = px.data.gapminder()

YEARS = sorted(gapminder["year"].unique().tolist())
BASELINE_YEAR = YEARS[0]
X_RANGE = (20, 90)
NBINS = 24


def years():
    return YEARS


def filter_year(year):
    return gapminder[gapminder["year"] == year]


def compute_stats(data, baseline_year=BASELINE_YEAR):
    baseline = filter_year(baseline_year)
    longest = data.loc[data["lifeExp"].idxmax()]
    return {
        "median": float(data["lifeExp"].median()),
        "baseline_median": float(baseline["lifeExp"].median()),
        "baseline_year": baseline_year,
        "above_70": int((data["lifeExp"] >= 70).sum()),
        "total": int(len(data)),
        "longest_country": longest["country"],
        "longest_value": float(longest["lifeExp"]),
    }


def _compute_y_max():
    peak = 0
    for y in YEARS:
        counts, _ = np.histogram(
            filter_year(y)["lifeExp"], bins=NBINS, range=X_RANGE
        )
        peak = max(peak, int(counts.max()))
    return int(peak * 1.15) + 1


Y_MAX = _compute_y_max()
