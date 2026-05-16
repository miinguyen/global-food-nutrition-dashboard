from shiny import reactive, render, ui
from shinywidgets import render_widget

from analysis import compute_stats, filter_year
from chart import build_caption, build_figure


def server(input, output, session):
    @reactive.calc
    def year_df():
        return filter_year(input.year())

    @reactive.calc
    def stats():
        return compute_stats(year_df())

    @render_widget
    def hist():
        return build_figure(year_df(), stats(), input.year())

    @render.ui
    def caption():
        return ui.markdown(build_caption(input.year(), stats()))
