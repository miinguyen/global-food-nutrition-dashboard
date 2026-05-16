import plotly.express as px
import plotly.graph_objects as go
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget

df = px.data.gapminder()

HIGHLIGHT = "#1f77b4"
MUTED = "#cfd8dc"

app_ui = ui.page_fluid(
    ui.h2("The continents are converging — but the gap is still decades wide."),
    ui.markdown(
        "Average life expectancy by continent, weighted equally across countries. "
        "Drag the slider to watch the gap close (or not) over half a century."
    ),
    ui.input_slider("year", "Year", min=1952, max=2007, value=2007, step=5, sep=""),
    output_widget("bar"),
    ui.output_ui("caption"),
)


def server(input, output, session):
    @reactive.calc
    def yearly():
        return (
            df[df["year"] == input.year()]
            .groupby("continent", as_index=False)["lifeExp"]
            .mean()
            .sort_values("lifeExp", ascending=False)
            .reset_index(drop=True)
        )

    @reactive.calc
    def global_avg():
        return df[df["year"] == input.year()]["lifeExp"].mean()

    @render_widget
    def bar():
        data = yearly()
        leader = data.iloc[0]["continent"]
        colors = [HIGHLIGHT if c == leader else MUTED for c in data["continent"]]

        fig = go.Figure(
            go.Bar(
                x=data["continent"],
                y=data["lifeExp"],
                marker_color=colors,
                text=[f"{v:.1f}" for v in data["lifeExp"]],
                textposition="outside",
                hovertemplate="%{x}: %{y:.1f} yrs<extra></extra>",
            )
        )
        fig.add_hline(
            y=global_avg(),
            line_dash="dot",
            line_color="#888",
            annotation_text=f"Global avg {global_avg():.1f}",
            annotation_position="top right",
        )
        fig.update_layout(
            title=dict(
                text=f"<b>{leader} led the world in {input.year()}</b>",
                x=0.0,
                font=dict(size=18),
            ),
            yaxis_title="Life expectancy (years)",
            xaxis_title="",
            yaxis_range=[0, max(data["lifeExp"]) * 1.15],
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=False,
        )
        fig.update_yaxes(gridcolor="#eee")
        return fig

    @render.ui
    def caption():
        data = yearly()
        top = data.iloc[0]
        bottom = data.iloc[-1]
        gap = top["lifeExp"] - bottom["lifeExp"]
        return ui.markdown(
            f"In **{input.year()}**, a person in **{top['continent']}** could expect to live "
            f"**{top['lifeExp']:.1f} years** — about **{gap:.0f} years longer** than someone "
            f"in **{bottom['continent']}** ({bottom['lifeExp']:.1f} years)."
        )


app = App(app_ui, server)
