import plotly.express as px

from analysis import GDP_LOG_RANGE, LIFE_RANGE
from theme import CONTINENT_COLORS, HIGHLIGHT


def build_figure(data, stats, year):
    fig = px.scatter(
        data,
        x="gdpPercap",
        y="lifeExp",
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        size_max=60,
        color_discrete_map=CONTINENT_COLORS,
        category_orders={"continent": list(CONTINENT_COLORS.keys())},
    )
    fig.update_traces(
        marker=dict(line=dict(width=0), opacity=0.85),
        hovertemplate="<b>%{hovertext}</b><br>$%{x:,.0f} · %{y:.1f} yrs<extra></extra>",
    )

    mid_y = (LIFE_RANGE[0] + LIFE_RANGE[1]) / 2
    callouts = [
        ("Longest-lived", stats["longest_country"], f"{stats['longest_value']:.0f} yrs"),
        ("Most people", stats["biggest_country"], f"{stats['biggest_pop']/1e6:.0f}M"),
    ]
    for label, country, suffix in callouts:
        row = data[data["country"] == country].iloc[0]
        ay = 60 if row["lifeExp"] > mid_y else -60
        fig.add_annotation(
            x=row["gdpPercap"],
            y=row["lifeExp"],
            text=f"<b>{country}</b><br>{label} · {suffix}",
            showarrow=True,
            arrowhead=0,
            arrowwidth=1,
            arrowcolor=HIGHLIGHT,
            ax=0,
            ay=ay,
            font=dict(color=HIGHLIGHT, size=11),
            align="center",
        )

    fig.update_layout(
        title=dict(
            text=f"<b>Wealth buys years — {year}</b>",
            x=0.0,
            font=dict(size=18),
        ),
        xaxis_title="GDP per capita (log scale)",
        yaxis_title="Life expectancy (years)",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=80, b=60),
        legend=dict(title="", orientation="h", y=-0.18, x=0),
    )
    fig.update_xaxes(
        range=GDP_LOG_RANGE,
        gridcolor="#eee",
        tickprefix="$",
        tickformat=",",
    )
    fig.update_yaxes(range=LIFE_RANGE, gridcolor="#eee")
    return fig


def build_caption(year, stats):
    shift = stats["median_life"] - stats["baseline_median_life"]
    return (
        f"In **{year}**, the median country lives **{stats['median_life']:.0f} years** — "
        f"a **+{shift:.0f}-year** shift since {stats['baseline_year']}. "
        f"**{stats['longest_country']}** lives longest at {stats['longest_value']:.0f} years, "
        f"while **{stats['biggest_country']}** carries the most people "
        f"({stats['biggest_pop']/1e6:.0f}M)."
    )
