import math

import plotly.express as px

gapminder = px.data.gapminder()

YEARS = sorted(gapminder["year"].unique().tolist())
BASELINE_YEAR = YEARS[0]

GDP_LOG_RANGE = [
    math.log10(gapminder["gdpPercap"].min() * 0.9),
    math.log10(gapminder["gdpPercap"].max() * 1.1),
]
LIFE_RANGE = [
    float(gapminder["lifeExp"].min()) - 2,
    float(gapminder["lifeExp"].max()) + 2,
]


def years():
    return YEARS


def filter_year(year):
    return gapminder[gapminder["year"] == year]


def compute_stats(data, baseline_year=BASELINE_YEAR):
    baseline = filter_year(baseline_year)
    longest = data.loc[data["lifeExp"].idxmax()]
    biggest = data.loc[data["pop"].idxmax()]
    return {
        "median_life": float(data["lifeExp"].median()),
        "baseline_median_life": float(baseline["lifeExp"].median()),
        "baseline_year": baseline_year,
        "longest_country": longest["country"],
        "longest_value": float(longest["lifeExp"]),
        "biggest_country": biggest["country"],
        "biggest_pop": float(biggest["pop"]),
    }
