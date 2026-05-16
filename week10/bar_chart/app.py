import plotly.express as px
from shiny import App, ui
from shinywidgets import output_widget, render_widget

df = px.data.gapminder()

app_ui = ui.page_fluid(
    ui.h2("Hello Gapminder"),
    ui.input_slider("year", "Year", min=1952, max=2007, value=2007, step=5),
    output_widget("bar"),
)

def server(input, output, session):
    @render_widget
    def bar():
        data = df[df["year"] == input.year()].groupby("continent", as_index=False)["lifeExp"].mean()
        return px.bar(data, x="continent", y="lifeExp", title="Avg life expectancy by continent")

app = App(app_ui, server)
