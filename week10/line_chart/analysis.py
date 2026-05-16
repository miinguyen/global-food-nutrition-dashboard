import plotly.express as px

from theme import GAINER, LAGGARD, LEADER

gapminder = px.data.gapminder()


def continents():
    return sorted(gapminder["continent"].unique().tolist())


def filter_continent(continent):
    return gapminder[gapminder["continent"] == continent].sort_values(["country", "year"])


def compute_stories(data):
    latest = data[data["year"] == data["year"].max()].set_index("country")["lifeExp"]
    earliest = data[data["year"] == data["year"].min()].set_index("country")["lifeExp"]
    gain = latest - earliest
    return [
        {"role": "Leader", "country": latest.idxmax(), "value": latest.max(), "color": LEADER},
        {"role": "Fastest improver", "country": gain.idxmax(), "value": gain.max(), "color": GAINER},
        {"role": "Laggard", "country": latest.idxmin(), "value": latest.min(), "color": LAGGARD},
    ]
