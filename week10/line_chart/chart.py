import plotly.graph_objects as go

from theme import AVG


def build_figure(data, stories, continent):
    avg = data.groupby("year", as_index=False)["lifeExp"].mean()

    fig = go.Figure()
    for s in stories:
        g = data[data["country"] == s["country"]]
        fig.add_trace(
            go.Scatter(
                x=g["year"],
                y=g["lifeExp"],
                mode="lines",
                line=dict(color=s["color"], width=3),
                hovertemplate=f"<b>{s['country']}</b><br>%{{x}}: %{{y:.1f}} yrs<extra></extra>",
            )
        )
        last = g.iloc[-1]
        fig.add_annotation(
            x=last["year"],
            y=last["lifeExp"],
            text=f"<b>{s['country']}</b><br>{s['role']}",
            showarrow=False,
            xanchor="left",
            xshift=6,
            font=dict(color=s["color"], size=11),
        )

    fig.add_trace(
        go.Scatter(
            x=avg["year"],
            y=avg["lifeExp"],
            mode="lines",
            line=dict(color=AVG, width=2, dash="dot"),
            hovertemplate="Continent avg %{x}: %{y:.1f} yrs<extra></extra>",
        )
    )

    leader = stories[0]["country"]
    fig.update_layout(
        title=dict(
            text=f"<b>{leader} leads {continent}, 1952–2007</b>",
            x=0.0,
            font=dict(size=18),
        ),
        yaxis_title="Life expectancy (years)",
        xaxis_title="",
        plot_bgcolor="white",
        margin=dict(l=20, r=140, t=60, b=20),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, dtick=10)
    fig.update_yaxes(gridcolor="#eee")
    return fig


def build_caption(continent, stories):
    leader, gainer, laggard = stories
    return (
        f"In **{continent}**, **{gainer['country']}** added the most years of life — "
        f"**+{gainer['value']:.0f} years** since 1952. **{leader['country']}** now leads, "
        f"while **{laggard['country']}** still trails."
    )
