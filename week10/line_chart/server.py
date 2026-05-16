from shiny import reactive, render, ui
from shinywidgets import render_widget

from analysis import compute_stories, filter_continent
from chart import build_caption, build_figure


def server(input, output, session):
    @reactive.calc
    def continent_df():
        return filter_continent(input.continent())

    @reactive.calc
    def stories():
        return compute_stories(continent_df())

    @render_widget
    def line():
        return build_figure(continent_df(), stories(), input.continent())

    @render.ui
    def caption():
        return ui.markdown(build_caption(input.continent(), stories()))
