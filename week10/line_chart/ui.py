from shiny import ui
from shinywidgets import output_widget

from analysis import continents

app_ui = ui.page_fluid(
    ui.h2("Most countries are gaining decades — a few are still left behind."),
    ui.markdown(
        "Three countries tell the story: the **leader**, the **fastest improver**, "
        "and the **laggard** — measured against the continent average."
    ),
    ui.input_select(
        "continent",
        "Continent",
        choices=continents(),
        selected="Asia",
    ),
    output_widget("line"),
    ui.output_ui("caption"),
)
