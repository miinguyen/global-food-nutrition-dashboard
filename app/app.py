"""
Global Food & Nutrition Dashboard
COMP5120 — Data Visualization (Spring 2026)

Main Shiny application entry point.
"""

from shiny import App, ui, render, reactive
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ============================================================
# UI Layout
# ============================================================

app_ui = ui.page_navbar(
    # --- Section 1: Country-Level ---
    ui.nav_panel(
        "🌍 What Does the World Eat?",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_slider(
                    "year_range",
                    "Year Range",
                    min=2010,
                    max=2023,
                    value=[2015, 2023],
                    step=1,
                ),
                ui.input_select(
                    "continent",
                    "Continent",
                    choices=["All", "Africa", "Asia", "Europe",
                             "North America", "South America", "Oceania"],
                    selected="All",
                ),
                ui.input_select(
                    "food_type",
                    "Food Type",
                    choices=["All", "Cereals", "Meat", "Dairy",
                             "Fruits & Vegetables", "Oils & Fats"],
                    selected="All",
                ),
                width=280,
            ),
            # Main panel — Country-level charts
            ui.layout_columns(
                ui.card(
                    ui.card_header("Daily Calorie Supply by Country"),
                    ui.output_ui("chart_choropleth"),
                ),
                ui.card(
                    ui.card_header("Food Source Composition Over Time"),
                    ui.output_ui("chart_stacked_area"),
                ),
                col_widths=[7, 5],
            ),
            ui.card(
                ui.card_header("Calorie Intake vs. Obesity Rate"),
                ui.output_ui("chart_scatter"),
            ),
        ),
    ),
    # --- Section 2: Product-Level ---
    ui.nav_panel(
        "🔬 What's In Our Food?",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "product_category",
                    "Product Category",
                    choices=["All"],  # Populated from data
                    selected="All",
                ),
                ui.input_checkbox_group(
                    "nova_levels",
                    "NOVA Processing Level",
                    choices={"1": "1 — Unprocessed",
                             "2": "2 — Processed Ingredients",
                             "3": "3 — Processed",
                             "4": "4 — Ultra-processed"},
                    selected=["1", "2", "3", "4"],
                ),
                width=280,
            ),
            # Main panel — Product-level charts
            ui.layout_columns(
                ui.card(
                    ui.card_header("Nutri-Score Distribution"),
                    ui.output_ui("chart_nutriscore_bar"),
                ),
                ui.card(
                    ui.card_header("Sugar & Sodium by Processing Level"),
                    ui.output_ui("chart_violin"),
                ),
                col_widths=[6, 6],
            ),
            ui.card(
                ui.card_header("Nutritional Profile Comparison"),
                ui.output_ui("chart_radar"),
            ),
        ),
    ),
    # --- ML & Insights ---
    ui.nav_panel(
        "🤖 ML Insights",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "ml_model",
                    "Select Model",
                    choices=["Nutri-Score Classifier",
                             "Country Clustering",
                             "Obesity Regression"],
                    selected="Nutri-Score Classifier",
                ),
                width=280,
            ),
            ui.card(
                ui.card_header("Model Results"),
                ui.output_ui("chart_ml"),
            ),
        ),
    ),
    title="🍔 Global Food & Nutrition Dashboard",
    id="main_navbar",
)

# ============================================================
# Server Logic
# ============================================================


def server(input, output, session):
    """Server function — chart rendering and interactivity."""

    # --- Placeholder renders ---
    # Replace these with actual data-driven charts as data is loaded.

    @output
    @render.ui
    def chart_choropleth():
        return ui.p(
            "📍 Choropleth map will be rendered here.",
            style="text-align:center; color:#888; padding:80px 0;",
        )

    @output
    @render.ui
    def chart_stacked_area():
        return ui.p(
            "📈 Stacked area chart will be rendered here.",
            style="text-align:center; color:#888; padding:80px 0;",
        )

    @output
    @render.ui
    def chart_scatter():
        return ui.p(
            "🔵 Scatter plot will be rendered here.",
            style="text-align:center; color:#888; padding:80px 0;",
        )

    @output
    @render.ui
    def chart_nutriscore_bar():
        return ui.p(
            "📊 Nutri-Score bar chart will be rendered here.",
            style="text-align:center; color:#888; padding:80px 0;",
        )

    @output
    @render.ui
    def chart_violin():
        return ui.p(
            "🎻 Violin plot will be rendered here.",
            style="text-align:center; color:#888; padding:80px 0;",
        )

    @output
    @render.ui
    def chart_radar():
        return ui.p(
            "🕸️ Radar chart will be rendered here.",
            style="text-align:center; color:#888; padding:80px 0;",
        )

    @output
    @render.ui
    def chart_ml():
        return ui.p(
            "🤖 ML model results will be rendered here.",
            style="text-align:center; color:#888; padding:80px 0;",
        )


# ============================================================
# App
# ============================================================

app = App(app_ui, server)
