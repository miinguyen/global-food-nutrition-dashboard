import plotly.express as px

from analysis import NBINS, X_RANGE, Y_MAX
from theme import BASELINE, CONTINENT_COLORS, MEDIAN


def build_figure(data, stats, year):
    fig = px.histogram(
        data,
        x="lifeExp",
        color="continent",
        nbins=NBINS,
        range_x=X_RANGE,
        color_discrete_map=CONTINENT_COLORS,
        category_orders={"continent": list(CONTINENT_COLORS.keys())},
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="%{y} countries · %{x} yrs<extra>%{fullData.name}</extra>",
    )

    fig.add_vline(
        x=stats["baseline_median"],
        line=dict(color=BASELINE, width=2, dash="dot"),
        annotation_text=f"{stats['baseline_year']} median {stats['baseline_median']:.0f}",
        annotation_position="top left",
        annotation_font=dict(color=BASELINE, size=11),
    )
    fig.add_vline(
        x=stats["median"],
        line=dict(color=MEDIAN, width=2),
        annotation_text=f"<b>{year} median {stats['median']:.0f}</b>",
        annotation_position="top right",
        annotation_font=dict(color=MEDIAN, size=12),
    )

    pct = 100 * stats["above_70"] / stats["total"]
    fig.update_layout(
        title=dict(
            text=(
                f"<b>{stats['above_70']} of {stats['total']} countries "
                f"live past 70 in {year}</b>  ·  {pct:.0f}%"
            ),
            x=0.0,
            font=dict(size=18),
        ),
        xaxis_title="Life expectancy (years)",
        yaxis_title="Countries",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=80, b=60),
        legend=dict(title="", orientation="h", y=-0.18, x=0),
        bargap=0.05,
    )
    fig.update_xaxes(showgrid=False, dtick=10)
    fig.update_yaxes(gridcolor="#eee", range=[0, Y_MAX])
    return fig


def build_caption(year, stats):
    shift = stats["median"] - stats["baseline_median"]
    pct = 100 * stats["above_70"] / stats["total"]
    return (
        f"In **{year}**, the median country reaches **{stats['median']:.0f} years** — "
        f"a **+{shift:.0f}-year** shift since {stats['baseline_year']}. "
        f"**{stats['above_70']} of {stats['total']} countries** ({pct:.0f}%) now live past 70, "
        f"led by **{stats['longest_country']}** at {stats['longest_value']:.0f} years."
    )
