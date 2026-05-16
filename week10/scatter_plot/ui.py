from shiny import ui
from shinywidgets import output_widget

from analysis import years

YEAR_VALUES = years()

app_ui = ui.page_fluid(
    ui.h2("Wealth buys years of life — but with diminishing returns."),
    ui.markdown(
        "Each bubble is a country: **wider** = more people, **higher** = longer lives, "
        "**further right** = richer. The curve climbs steeply at low incomes and flattens at the top. "
        "Slide through the decades to watch countries chase the frontier."
    ),
    ui.input_slider(
        "year",
        "Year",
        min=YEAR_VALUES[0],
        max=YEAR_VALUES[-1],
        value=YEAR_VALUES[-1],
        step=5,
        sep="",
    ),
    output_widget("scatter"),
    ui.output_ui("caption"),
)
