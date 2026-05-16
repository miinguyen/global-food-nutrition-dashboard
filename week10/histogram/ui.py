from shiny import ui
from shinywidgets import output_widget

from analysis import years

YEAR_VALUES = years()

app_ui = ui.page_fluid(
    ui.h2("The world is living longer — but the gap hasn't closed."),
    ui.markdown(
        "Each bar counts the countries living a given length of life. "
        "The dotted line marks the **1952 median**; the solid line marks the year you choose. "
        "Slide through the decades to watch the distribution drift right."
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
    output_widget("hist"),
    ui.output_ui("caption"),
)
