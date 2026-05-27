"""
Global Food & Nutrition Dashboard
COMP5120 — Data Visualization (Spring 2026)

Main Shiny application entry point. Implements 4 interactive tabs, 14 charts,
linked visual components, and real-time machine learning predictions.
"""

from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import pickle
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ============================================================
# Paths & Data Loading
# ============================================================

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR.parent / "data" / "processed"

# Check directories & files
cy_path = DATA_DIR / "country_yearly.parquet"
ch_path = DATA_DIR / "country_health.parquet"
p_path = DATA_DIR / "products.parquet"

if not cy_path.exists():
    raise FileNotFoundError(f"Missing required data file: {cy_path}. Please run data/processing.py first.")

# Load and preprocess datasets
cy = pd.read_parquet(cy_path)
ch = pd.read_parquet(ch_path)
products = pd.read_parquet(p_path)

# Filter out old years and invalid entries
cy = cy[cy['year'] >= 1961].copy()
ch = ch[ch['year'] >= 1975].copy()

# Sort lookups for selectors
countries_list = sorted(cy["entity"].unique().tolist())
continents_list = ["All"] + sorted([c for c in cy["continent"].dropna().unique() if c != "Other"])
categories_list = ["All"] + sorted([cat for cat in products["top_category"].dropna().unique() if cat != "Unknown"])[:30] # Top 30 categories

# Load ML models
try:
    with open(APP_DIR / "models" / "nutriscore_classifier.pkl", "rb") as f:
        nutri_model = pickle.load(f)
    with open(APP_DIR / "models" / "obesity_regressor.pkl", "rb") as f:
        obesity_model = pickle.load(f)
except Exception as e:
    print(f"Warning: Models failed to load. Real-time predictions may fail. Error: {e}")
    nutri_model, obesity_model = None, None

# ============================================================
# Category to Macro Mapping (Tab 4 Simulator)
# ============================================================

def map_category_to_macro(category_name):
    cat = str(category_name).lower()
    if any(k in cat for k in ["cereal", "grain", "bread", "biscuit", "flour", "pasta", "cake", "rice", "wheat", "maize", "barley", "oat", "cookies", "shortbread", "waffles"]):
        return "grp_cereals"
    elif any(k in cat for k in ["meat", "beef", "poultry", "pork", "fish", "seafood", "chicken", "turkey", "lamb", "ham", "sausage", "charcuterie"]):
        return "grp_meat"
    elif any(k in cat for k in ["dairy", "milk", "cheese", "yogurt", "egg", "cream", "butters"]):
        return "grp_dairy_eggs"
    elif any(k in cat for k in ["oil", "fat", "margarine", "lard", "shortening", "butter", "spreads"]):
        return "grp_oils_fats"
    elif any(k in cat for k in ["sugar", "sweet", "chocolate", "candy", "beverage", "soda", "syrup", "honey", "dessert", "snacks", "confectionery", "cola"]):
        return "grp_sugar_sweeteners"
    elif any(k in cat for k in ["fruit", "vegetable", "salad", "juice", "tomato", "apple", "banana", "orange", "berry", "greens"]):
        return "grp_fruits_vegetables"
    elif any(k in cat for k in ["potato", "root", "pulse", "bean", "lentil", "starch", "tuber", "yam"]):
        return "grp_starchy_roots_pulses"
    else:
        return "grp_other"

# ============================================================
# UI Layout
# ============================================================

app_ui = ui.page_navbar(
    # --- Section 1: Country-Level ---
    ui.nav_panel(
        "🌍 What Does the World Eat?",
        ui.layout_sidebar(
            ui.sidebar(
                ui.div(
                    ui.h5("🎛️ Filters", class_="mb-1"),
                    ui.p("Adjust year and region to explore global dietary patterns.", class_="text-muted small mb-3"),
                ),
                ui.input_slider(
                    "year_select",
                    "Select Year",
                    min=1961,
                    max=2023,
                    value=2020,
                    step=1,
                    sep="",
                    animate=ui.AnimationOptions(interval=400, loop=False),
                ),
                ui.input_select(
                    "continent_select",
                    "Continent",
                    choices=continents_list,
                    selected="All",
                ),
                ui.hr(),
                ui.div(
                    ui.h5("🔍 Country Deep Dive", class_="mb-1"),
                    ui.p("Select a country to see its historical trend and dietary breakdown below.", class_="text-muted small mb-2"),
                ),
                ui.input_select(
                    "country_select",
                    "Select Country for Detail",
                    choices=countries_list,
                    selected="United States",
                ),
                width=300,
            ),
            # Tab intro banner
            ui.div(
                ui.h4("🌍 Global Calorie Supply Overview", class_="mb-1 fw-bold"),
                ui.p("Explore how daily per-capita calorie supply varies across 180+ countries from 1961 to 2023. "
                     "Use the year slider to animate trends over time, or drill into a specific country for its dietary composition breakdown.",
                     class_="text-muted mb-0 small"),
                class_="tab-intro-banner mb-3 p-3"
            ),
            # KPIs Row
            ui.layout_columns(
                ui.card(
                    ui.div(
                        ui.div("🔥 Average Daily Calories", class_="kpi-title"),
                        ui.output_ui("kpi_calories", class_="kpi-value"),
                        ui.output_ui("kpi_calories_subtitle", class_="kpi-subtitle"),
                    ),
                    class_="kpi-card kpi-card-calories"
                ),
                ui.card(
                    ui.div(
                        ui.div("🌾 Primary Caloric Source", class_="kpi-title"),
                        ui.output_ui("kpi_source", class_="kpi-value"),
                    ),
                    class_="kpi-card kpi-card-source"
                ),
                ui.card(
                    ui.div(
                        ui.div("📍 Selected Country Intake", class_="kpi-title"),
                        ui.output_ui("kpi_country_intake", class_="kpi-value"),
                        ui.output_ui("kpi_country_vs_global", class_="kpi-subtitle"),
                    ),
                    class_="kpi-card kpi-card-country"
                ),
                ui.card(
                    ui.div(
                        ui.div("🌐 Countries Tracked", class_="kpi-title"),
                        ui.output_ui("kpi_countries_count", class_="kpi-value"),
                    ),
                    class_="kpi-card kpi-card-count"
                ),
                col_widths=[3, 3, 3, 3],
            ),
            # Main maps & rank rows
            ui.layout_columns(
                ui.card(
                    ui.card_header("🗺️ Global Calorie Supply Choropleth"),
                    output_widget("chart_choropleth"),
                ),
                ui.card(
                    ui.card_header("🏆 Top 10 Caloric Supply Countries"),
                    output_widget("chart_ranking_bar"),
                ),
                col_widths=[7, 5],
            ),
            # Detail trends row
            ui.layout_columns(
                ui.card(
                    ui.card_header("📈 Daily Calorie Intake Trend (VS. Global Avg & WHO Guideline)"),
                    output_widget("chart_calorie_trend"),
                ),
                ui.card(
                    ui.card_header("📊 Dietary Composition Over Time (Stacked Area)"),
                    output_widget("chart_stacked_area"),
                ),
                col_widths=[6, 6],
            ),
        ),
    ),
    
    # --- Section 2: Diet vs. Health Outcomes ---
    ui.nav_panel(
        "🥗 How Healthy Is It?",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "health_metric",
                    "Select Health Indicator",
                    choices={
                        "who_obesity_pct": "Obesity Rate (Adults %)",
                        "underweight_pct": "Underweight Prevalence (Children under 5 %)",
                        "life_exp": "Life Expectancy (Years)"
                    },
                    selected="who_obesity_pct"
                ),
                ui.input_select(
                    "h_continent_select",
                    "Continent",
                    choices=continents_list,
                    selected="All",
                ),
                ui.input_slider(
                    "h_year_select",
                    "Select Year",
                    min=1975,
                    max=2022,
                    value=2016,
                    step=1,
                    sep="",
                ),
                width=280,
            ),
            # Scatter Plot and Obesity Map
            ui.layout_columns(
                ui.card(
                    ui.card_header("Diet Calorie Supply vs. Health Outcome"),
                    output_widget("chart_health_scatter"),
                ),
                ui.card(
                    ui.card_header("Obesity Prevalence Trend Map"),
                    output_widget("chart_obesity_map"),
                ),
                col_widths=[6, 6],
            ),
            # Cluster Projection & Obesity Regressor Dashboard
            ui.layout_columns(
                ui.card(
                    ui.card_header("Dietary Profiling Clusters (PCA + K-Means)"),
                    output_widget("chart_diet_clusters"),
                ),
                ui.card(
                    ui.card_header("Obesity Predictor Dashboard (ML actual/predicted + importances)"),
                    output_widget("chart_regression_dashboard"),
                ),
                col_widths=[6, 6],
            ),
        ),
    ),
    
    # --- Section 3: Product-Level Analysis ---
    ui.nav_panel(
        "🔬 What's In Our Food?",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "product_category",
                    "Product Category",
                    choices=categories_list,
                    selected="All",
                ),
                ui.input_checkbox_group(
                    "nova_levels",
                    "NOVA Processing Level",
                    choices={"1": "1 — Unprocessed / Minimally Processed",
                             "2": "2 — Processed Ingredients",
                             "3": "3 — Processed",
                             "4": "4 — Ultra-processed"},
                    selected=["1", "2", "3", "4"],
                ),
                width=280,
            ),
            # Stacked bar and Donut
            ui.layout_columns(
                ui.card(
                    ui.card_header("Nutri-Score Distribution by Category"),
                    output_widget("chart_nutriscore_bar"),
                ),
                ui.card(
                    ui.card_header("NOVA Processing Levels"),
                    output_widget("chart_nova_donut"),
                ),
                col_widths=[6, 6],
            ),
            # Sugar vs Fat Scatter
            ui.card(
                ui.card_header("Sugar vs. Fat by Product (Colored by Nutri-Score, sized by Kcal)"),
                output_widget("chart_sugar_fat_scatter")
            ),
            # ML Real-time form
            ui.card(
                ui.card_header("🤖 Interactive Nutri-Score Predictor (Machine Learning Classifier)"),
                ui.layout_columns(
                    ui.div(
                        ui.p("Enter the macronutrient content per 100g below to predict the Nutri-Score Grade (A–E) in real time:"),
                        ui.layout_columns(
                            ui.input_numeric("in_energy", "Energy (kcal)", value=250, min=0, max=900),
                            ui.input_numeric("in_fat", "Total Fat (g)", value=12.0, min=0.0, max=100.0),
                            ui.input_numeric("in_sat_fat", "Saturated Fat (g)", value=3.5, min=0.0, max=100.0),
                        ),
                        ui.layout_columns(
                            ui.input_numeric("in_sugar", "Sugars (g)", value=8.5, min=0.0, max=100.0),
                            ui.input_numeric("in_salt", "Salt (g)", value=0.6, min=0.0, max=10.0),
                            ui.input_numeric("in_protein", "Protein (g)", value=6.0, min=0.0, max=100.0),
                        ),
                        ui.input_numeric("in_fiber", "Fiber (g)", value=2.5, min=0.0, max=100.0),
                        ui.input_action_button("btn_predict", "Predict Nutri-Score Grade", class_="btn-primary w-100 mt-3"),
                        class_="ml-form-container"
                    ),
                    ui.div(
                        ui.h4("Predicted Nutri-Score Grade:"),
                        ui.output_ui("pred_badge"),
                        ui.hr(),
                        output_widget("chart_pred_prob"),
                        class_="p-3 text-center"
                    ),
                    col_widths=[7, 5]
                ),
            ),
        ),
    ),

    # --- Section 4: My Personal Diet Simulator (Synthesis) ---
    ui.nav_panel(
        "🥗 My Diet Simulator",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "sim_country",
                    "Reference Country",
                    choices=countries_list,
                    selected="United States"
                ),
                ui.input_select(
                    "sim_activity",
                    "Physical Activity Level",
                    choices={
                        "Sedentary": "Sedentary (1.2x)",
                        "Light": "Lightly Active (1.375x)",
                        "Moderate": "Moderately Active (1.55x)",
                        "Active": "Very Active (1.725x)"
                    },
                    selected="Moderate"
                ),
                ui.hr(),
                ui.h5("Add Food to Your Day"),
                ui.input_select(
                    "sim_product_category",
                    "Product Category",
                    choices=categories_list[1:],
                    selected=categories_list[1]
                ),
                ui.input_numeric("sim_grams", "Amount (grams)", value=150, min=10, max=1000),
                ui.input_action_button("btn_add_item", "Add to Daily Diet", class_="btn-primary w-100 mt-2"),
                ui.input_action_button("btn_clear_diet", "Clear Daily Diet", class_="btn-danger w-100 mt-2"),
                ui.hr(),
                ui.h5("Current Daily Diet:"),
                ui.output_ui("sim_diet_list"),
                width=300,
            ),
            # KPIs Row
            ui.layout_columns(
                ui.card(
                    ui.div(
                        ui.div("Simulated Calories", class_="kpi-title"),
                        ui.output_ui("sim_kpi_calories", class_="kpi-value"),
                    ),
                    class_="kpi-card"
                ),
                ui.card(
                    ui.div(
                        ui.div("Average Nutri-Score", class_="kpi-title"),
                        ui.output_ui("sim_kpi_nutriscore", class_="kpi-value"),
                    ),
                    class_="kpi-card"
                ),
                ui.card(
                    ui.div(
                        ui.div("Ultra-Processed Share", class_="kpi-title"),
                        ui.output_ui("sim_kpi_nova", class_="kpi-value"),
                    ),
                    class_="kpi-card"
                ),
                col_widths=[4, 4, 4],
            ),
            # Charts row
            ui.layout_columns(
                ui.card(
                    ui.card_header("Simulated Intake vs. Country Baseline"),
                    output_widget("chart_sim_comparison"),
                ),
                ui.card(
                    ui.card_header("Daily Basket Nutri-Score Balance"),
                    output_widget("chart_sim_donut"),
                ),
                col_widths=[7, 5],
            ),
            # AI Forecast Card
            ui.card(
                ui.card_header("🤖 AI Health Risk Forecast & Recommendations"),
                ui.output_ui("sim_ai_forecast"),
            ),
        ),
    ),
    
    title="🍔 Global Food & Nutrition Dashboard",
    id="main_navbar",
    header=ui.head_content(
        ui.tags.link(rel="stylesheet", href="custom.css")
    ),
)

# ============================================================
# Server Logic
# ============================================================

def server(input, output, session):
    """Server function handling reactive computations and chart rendering."""

    # --- Reactive filtered datasets ---
    
    @reactive.calc
    def get_cy_year():
        """Get country yearly data for the selected year."""
        year = input.year_select()
        df = cy[cy["year"] == year].copy()
        
        continent = input.continent_select()
        if continent != "All":
            df = df[df["continent"] == continent]
        return df

    @reactive.calc
    def get_cy_country():
        """Get historical data for the selected country."""
        country = input.country_select()
        return cy[cy["entity"] == country].copy()

    @reactive.calc
    def get_products_filtered():
        """Get product dataset filtered by sidebar selectors."""
        df = products.copy()
        
        cat = input.product_category()
        if cat != "All":
            df = df[df["top_category"] == cat]
            
        novas = [float(n) for n in input.nova_levels()]
        df = df[df["nova_group"].isin(novas)]
        return df

    # --- KPI Renders ---

    @output
    @render.ui
    def kpi_calories():
        df = get_cy_year()
        if df.empty:
            return "N/A"
        avg_cal = df["calories"].mean()
        return f"{avg_cal:,.0f} kcal/day"

    @output
    @render.ui
    def kpi_calories_subtitle():
        """Shows how average compares to WHO recommended 2,000-2,500 kcal range."""
        df = get_cy_year()
        if df.empty:
            return ""
        avg_cal = df["calories"].mean()
        who_mid = 2250  # midpoint of WHO 2000-2500 range
        diff_pct = ((avg_cal - who_mid) / who_mid) * 100
        if diff_pct > 5:
            return ui.span(f"▲ {diff_pct:+.1f}% above WHO guideline", class_="text-danger")
        elif diff_pct < -5:
            return ui.span(f"▼ {diff_pct:+.1f}% below WHO guideline", class_="text-warning")
        else:
            return ui.span(f"≈ Within WHO guideline range", class_="text-success")

    @output
    @render.ui
    def kpi_source():
        df = get_cy_year()
        if df.empty:
            return "N/A"
        groups = ["grp_cereals", "grp_meat", "grp_dairy_eggs", "grp_oils_fats", 
                  "grp_sugar_sweeteners", "grp_fruits_vegetables", "grp_starchy_roots_pulses", "grp_other"]
        group_labels = {
            "grp_cereals": "Cereals 🌾",
            "grp_meat": "Meat 🥩",
            "grp_dairy_eggs": "Dairy & Eggs 🥛",
            "grp_oils_fats": "Oils & Fats 🧈",
            "grp_sugar_sweeteners": "Sugars & Sweeteners 🍬",
            "grp_fruits_vegetables": "Fruits & Vegetables 🍎",
            "grp_starchy_roots_pulses": "Starchy Roots & Pulses 🥔",
            "grp_other": "Other 🍽️"
        }
        avg_shares = df[groups].mean()
        top_group = avg_shares.idxmax()
        return group_labels.get(top_group, "Unknown")

    @output
    @render.ui
    def kpi_country_intake():
        country = input.country_select()
        year = input.year_select()
        df = cy[(cy["entity"] == country) & (cy["year"] == year)]
        if df.empty:
            return "N/A"
        val = df["calories"].values[0]
        return f"{val:,.0f} kcal/day"

    @output
    @render.ui
    def kpi_country_vs_global():
        """Shows selected country vs global average comparison."""
        country = input.country_select()
        year = input.year_select()
        df_c = cy[(cy["entity"] == country) & (cy["year"] == year)]
        df_all = get_cy_year()
        if df_c.empty or df_all.empty:
            return ""
        country_val = df_c["calories"].values[0]
        global_avg = df_all["calories"].mean()
        diff_pct = ((country_val - global_avg) / global_avg) * 100
        if diff_pct > 0:
            return ui.span(f"▲ {diff_pct:+.1f}% vs. regional avg", class_="text-info")
        else:
            return ui.span(f"▼ {diff_pct:+.1f}% vs. regional avg", class_="text-warning")

    @output
    @render.ui
    def kpi_countries_count():
        df = get_cy_year()
        if df.empty:
            return "0"
        count = df["entity"].nunique()
        return f"{count} countries"

    # ============================================================
    # TAB 1: Chart Outputs
    # ============================================================

    @output
    @render_widget
    def chart_choropleth():
        df = get_cy_year()
        if df.empty:
            return go.Figure()
        
        fig = px.choropleth(
            df,
            locations="iso3",
            color="calories",
            hover_name="entity",
            hover_data={"iso3": False, "calories": ":.0f", "continent": True},
            color_continuous_scale=[
                [0, "#fff7ec"], [0.2, "#fee8c8"], [0.4, "#fdbb84"],
                [0.6, "#fc8d59"], [0.8, "#e34a33"], [1.0, "#b30000"]
            ],
            range_color=[1500, 3800],
            labels={"calories": "Kcal/day", "continent": "Continent"},
            title=f"Global Daily Calorie Supply per Capita ({input.year_select()})"
        )
        fig.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(
                showframe=False, 
                showcoastlines=True, 
                coastlinecolor='#cbd5e1',
                projection_type='natural earth',
                bgcolor='rgba(0,0,0,0)',
                landcolor='#f1f5f9',
                showocean=True,
                oceancolor='#e8f4f8',
            ),
            coloraxis_colorbar=dict(
                title="Kcal/day",
                thickness=15,
                len=0.6,
            ),
        )
        return fig

    @output
    @render_widget
    def chart_ranking_bar():
        df = get_cy_year()
        if df.empty:
            return go.Figure()
        
        top10 = df.nlargest(10, "calories").sort_values("calories", ascending=True)
        
        # Gradient colors from warm to hot
        n = len(top10)
        colors = [f"rgba({180 + int(75 * i/max(n-1,1))}, {100 - int(60 * i/max(n-1,1))}, {50}, 0.85)" for i in range(n)]
        
        fig = go.Figure(go.Bar(
            x=top10["calories"],
            y=top10["entity"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(0,0,0,0.1)", width=1),
            ),
            text=[f"{v:,.0f}" for v in top10["calories"]],
            textposition="outside",
            textfont=dict(size=11, color="#475569", family="Poppins"),
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} kcal/day<extra></extra>",
        ))
        
        fig.update_layout(
            title=f"Top 10 Countries by Calorie Supply ({input.year_select()})",
            xaxis_title="Kcal/day",
            margin={"r":60,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
            yaxis=dict(showgrid=False),
        )
        return fig

    @output
    @render_widget
    def chart_calorie_trend():
        df_country = get_cy_country()
        if df_country.empty:
            return go.Figure()
        
        # Calculate global average per year
        global_avg = cy.groupby("year")["calories"].mean().reset_index()
        years_range = global_avg["year"].tolist()
        
        fig = go.Figure()
        
        # WHO recommended band (2000-2500 kcal/day)
        fig.add_trace(go.Scatter(
            x=years_range + years_range[::-1],
            y=[2500]*len(years_range) + [2000]*len(years_range),
            fill="toself",
            fillcolor="rgba(16, 185, 129, 0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            name="WHO Guideline (2,000–2,500)",
            hoverinfo="skip",
            showlegend=True,
        ))
        
        # Global Avg (behind country line)
        fig.add_trace(go.Scatter(
            x=global_avg["year"],
            y=global_avg["calories"],
            mode="lines",
            name="Global Average",
            line=dict(color="#94a3b8", width=2, dash="dash")
        ))
        
        # Selected Country (on top)
        fig.add_trace(go.Scatter(
            x=df_country["year"],
            y=df_country["calories"],
            mode="lines+markers",
            name=input.country_select(),
            line=dict(color="#FF6B35", width=3),
            marker=dict(size=4),
        ))
        
        fig.update_layout(
            title=f"Caloric Intake Trend: {input.country_select()} VS Global Avg",
            xaxis_title="Year",
            yaxis_title="Calories (kcal/day)",
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
        )
        return fig

    @output
    @render_widget
    def chart_stacked_area():
        df_country = get_cy_country()
        if df_country.empty:
            return go.Figure()
        
        groups = ["grp_cereals", "grp_meat", "grp_dairy_eggs", "grp_oils_fats", 
                  "grp_sugar_sweeteners", "grp_fruits_vegetables", "grp_starchy_roots_pulses", "grp_other"]
        
        labels_map = {
            "grp_cereals": "Cereals",
            "grp_meat": "Meat",
            "grp_dairy_eggs": "Dairy & Eggs",
            "grp_oils_fats": "Oils & Fats",
            "grp_sugar_sweeteners": "Sugar & Sweeteners",
            "grp_fruits_vegetables": "Fruits & Vegetables",
            "grp_starchy_roots_pulses": "Starchy Roots/Pulses",
            "grp_other": "Other"
        }
        
        # Curated food-themed color palette
        food_colors = {
            "grp_cereals": "#f59e0b",             # Amber / wheat
            "grp_meat": "#ef4444",                # Red / meat
            "grp_dairy_eggs": "#60a5fa",           # Light blue / milk
            "grp_oils_fats": "#fbbf24",            # Gold / oil
            "grp_sugar_sweeteners": "#f472b6",     # Pink / candy
            "grp_fruits_vegetables": "#34d399",    # Green / vegetables
            "grp_starchy_roots_pulses": "#a78bfa", # Purple / potato
            "grp_other": "#94a3b8",               # Slate / other
        }
        
        fig = go.Figure()
        for g in groups:
            fig.add_trace(go.Scatter(
                x=df_country["year"],
                y=df_country[g],
                name=labels_map[g],
                stackgroup="one",
                mode="lines",
                line=dict(width=0.5, color=food_colors[g]),
                fillcolor=food_colors[g],
                hovertemplate=f"{labels_map[g]}: " + "%{y:,.0f} kcal<extra></extra>",
            ))
            
        fig.update_layout(
            title=f"Dietary Calorie Composition in {input.country_select()}",
            xaxis_title="Year",
            yaxis_title="Kcal/day",
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5,
                font=dict(size=10),
            ),
            hovermode="x unified",
        )
        return fig

    # ============================================================
    # TAB 2: Diet vs. Health Outcomes
    # ============================================================

    @reactive.calc
    def get_health_data():
        """Get merged dietary and health dataset for Tab 2 year & continent."""
        year = input.h_year_select()
        cy_y = cy[cy["year"] == year].copy()
        ch_y = ch[ch["year"] == year].copy()
        
        merged = pd.merge(cy_y, ch_y, on=["iso3", "year"], suffixes=("_diet", "_health"))
        
        continent = input.h_continent_select()
        if continent != "All":
            merged = merged[merged["continent_diet"] == continent]
        return merged

    @output
    @render_widget
    def chart_health_scatter():
        df = get_health_data()
        if df.empty:
            return go.Figure()
        
        metric = input.health_metric()
        metric_labels = {
            "who_obesity_pct": "Obesity Rate (%)",
            "underweight_pct": "Child Underweight (%)",
            "life_exp": "Life Expectancy (Years)"
        }
        
        fig = px.scatter(
            df,
            x="calories",
            y=metric,
            color="continent_diet",
            hover_name="entity",
            trendline="ols",
            labels={"calories": "Daily Calorie Intake (kcal)", metric: metric_labels.get(metric, metric), "continent_diet": "Continent"},
            title=f"Daily Calories VS. {metric_labels.get(metric, metric)} ({input.h_year_select()})"
        )
        fig.update_layout(
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @output
    @render_widget
    def chart_obesity_map():
        # Get latest WHO health data for the selected year
        df = ch[ch["year"] == input.h_year_select()].copy()
        if df.empty:
            return go.Figure()
        
        fig = px.choropleth(
            df,
            locations="iso3",
            color="who_obesity_pct",
            hover_name="iso3",
            color_continuous_scale="Reds",
            labels={"who_obesity_pct": "Obesity %"},
            title=f"Adult Obesity Prevalence Map ({input.h_year_select()})"
        )
        fig.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular')
        )
        return fig

    @output
    @render_widget
    def chart_diet_clusters():
        """Run PCA + K-Means clustering dynamically on country diets."""
        year = input.h_year_select()
        cy_y = cy[cy["year"] == year].copy()
        
        groups = ["grp_cereals", "grp_meat", "grp_dairy_eggs", "grp_oils_fats", 
                  "grp_sugar_sweeteners", "grp_fruits_vegetables", "grp_starchy_roots_pulses", "grp_other"]
        
        cy_y = cy_y.dropna(subset=["calories"] + groups)
        cy_y = cy_y[cy_y["calories"] > 0]
        
        if len(cy_y) < 10:
            return go.Figure()
        
        # Calculate percentage shares of diet macro categories
        shares = cy_y[groups].div(cy_y["calories"], axis=0) * 100
        
        # PCA + K-Means
        scaled = StandardScaler().fit_transform(shares)
        
        pca = PCA(n_components=2)
        pcs = pca.fit_transform(scaled)
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
        clusters = kmeans.fit_predict(scaled)
        
        plot_df = pd.DataFrame(pcs, columns=["PC1", "PC2"])
        plot_df["Cluster"] = [f"Cluster {c+1}" for c in clusters]
        plot_df["Country"] = cy_y["entity"].values
        plot_df["iso3"] = cy_y["iso3"].values
        plot_df["Calories"] = cy_y["calories"].values
        
        fig = px.scatter(
            plot_df,
            x="PC1",
            y="PC2",
            color="Cluster",
            hover_name="Country",
            text="iso3",
            title=f"Country Dietary Profile Clusters ({year})",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig.update_traces(textposition='top center')
        fig.update_layout(
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @output
    @render_widget
    def chart_regression_dashboard():
        """Shows Obesity Regressor model performance or feature importances."""
        if obesity_model is None:
            return go.Figure()
        
        # Perform prediction on get_health_data() to compare Actual vs. Predicted
        df = get_health_data().copy()
        features = [
            "calories", "grp_cereals", "grp_meat", "grp_dairy_eggs", "grp_oils_fats", 
            "grp_sugar_sweeteners", "grp_fruits_vegetables", "grp_starchy_roots_pulses", "grp_other"
        ]
        df = df.dropna(subset=["who_obesity_pct"] + features)
        
        if df.empty:
            # Fallback feature importance plot if active data is missing
            importances = obesity_model.named_steps['regressor'].feature_importances_
            feature_names = [f.replace("grp_", "").replace("_", " ").title() for f in features]
            imp_df = pd.DataFrame({"Feature": feature_names, "Importance": importances}).sort_values("Importance")
            
            fig = px.bar(imp_df, x="Importance", y="Feature", orientation="h", title="Obesity Predictor Feature Importances")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            return fig
            
        preds = obesity_model.predict(df[features])
        df["Predicted_Obesity"] = preds
        
        # Build comparative scatter plot
        fig = px.scatter(
            df,
            x="who_obesity_pct",
            y="Predicted_Obesity",
            hover_name="entity",
            color="continent_diet",
            labels={"who_obesity_pct": "Actual Obesity %", "Predicted_Obesity": "Predicted Obesity %"},
            title="Adult Obesity Rate: Actual VS. Predicted"
        )
        # Add diagonal line (perfect predictions)
        min_val = min(df["who_obesity_pct"].min(), df["Predicted_Obesity"].min())
        max_val = max(df["who_obesity_pct"].max(), df["Predicted_Obesity"].max())
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            name="Perfect Agreement",
            line=dict(color="#94a3b8", dash="dash")
        ))
        
        fig.update_layout(
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    # ============================================================
    # TAB 3: Product-Level Outputs
    # ============================================================

    @output
    @render_widget
    def chart_nutriscore_bar():
        df = get_products_filtered()
        if df.empty:
            return go.Figure()
        
        # Group by top category and nutriscore grade
        counts = df.groupby(["top_category", "nutriscore_grade"]).size().reset_index(name="count")
        
        # Capitalize grade
        counts["nutriscore_grade"] = counts["nutriscore_grade"].str.upper()
        
        fig = px.bar(
            counts,
            x="top_category",
            y="count",
            color="nutriscore_grade",
            color_discrete_map={"A": "#038141", "B": "#85bb2f", "C": "#fecb02", "D": "#ee8100", "E": "#e63e11"},
            category_orders={"nutriscore_grade": ["A", "B", "C", "D", "E"]},
            labels={"top_category": "Food Category", "count": "Products Count", "nutriscore_grade": "Nutri-Score"},
            title="Nutri-Score Grade Distribution by Category"
        )
        fig.update_layout(
            xaxis={'categoryorder':'total descending'},
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @output
    @render_widget
    def chart_nova_donut():
        df = get_products_filtered()
        if df.empty:
            return go.Figure()
        
        counts = df["nova_group"].value_counts().reset_index()
        counts.columns = ["NOVA Group", "Count"]
        
        nova_labels = {
            1.0: "1 — Unprocessed",
            2.0: "2 — Ingredients",
            3.0: "3 — Processed",
            4.0: "4 — Ultra-processed"
        }
        counts["NOVA Level"] = counts["NOVA Group"].map(nova_labels)
        
        fig = px.pie(
            counts,
            values="Count",
            names="NOVA Level",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu_r,
            title="NOVA Processing Groups Composition"
        )
        fig.update_layout(
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @output
    @render_widget
    def chart_sugar_fat_scatter():
        df = get_products_filtered().copy()
        if df.empty:
            return go.Figure()
        
        # Sample for rendering performance if too large
        if len(df) > 1500:
            df = df.sample(1500, random_state=42)
            
        df["nutriscore_grade"] = df["nutriscore_grade"].str.upper()
        # Create a kcal sizing proxy, ensuring no zeros or negatives
        df["kcal_size"] = df["energy-kcal_100g"].fillna(100).clip(lower=10)
        
        fig = px.scatter(
            df,
            x="fat_100g",
            y="sugars_100g",
            color="nutriscore_grade",
            size="kcal_size",
            hover_name="product_name",
            hover_data=["brands", "top_category", "energy-kcal_100g"],
            color_discrete_map={"A": "#038141", "B": "#85bb2f", "C": "#fecb02", "D": "#ee8100", "E": "#e63e11"},
            category_orders={"nutriscore_grade": ["A", "B", "C", "D", "E"]},
            labels={"fat_100g": "Total Fat (g/100g)", "sugars_100g": "Sugars (g/100g)", "nutriscore_grade": "Nutri-Score"},
            title="Sugar vs. Fat Product Landscape"
        )
        fig.update_layout(
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    # --- Interactive ML Form ---

    # Reactive variables to store predictions
    pred_grade_res = reactive.Value("—")
    pred_probs_res = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.btn_predict)
    def handle_prediction():
        if nutri_model is None:
            pred_grade_res.set("N/A (Model Error)")
            return
            
        # Parse inputs
        energy = input.in_energy()
        fat = input.in_fat()
        sat_fat = input.in_sat_fat()
        sugar = input.in_sugar()
        salt = input.in_salt()
        protein = input.in_protein()
        fiber = input.in_fiber()
        
        # Build features DataFrame
        features_df = pd.DataFrame([{
            'energy-kcal_100g': energy,
            'fat_100g': fat,
            'saturated-fat_100g': sat_fat,
            'sugars_100g': sugar,
            'salt_100g': salt,
            'proteins_100g': protein,
            'fiber_100g': fiber
        }])
        
        try:
            # Generate predictions
            pred = nutri_model.predict(features_df)[0]
            probs = nutri_model.predict_proba(features_df)[0]
            
            pred_grade_res.set(pred.upper())
            pred_probs_res.set(probs)
        except Exception as e:
            pred_grade_res.set("Error")
            print(f"Prediction failed: {e}")

    @output
    @render.ui
    def pred_badge():
        grade = pred_grade_res()
        if grade == "—":
            return ui.div("Click Predict Button", class_="fs-5 text-muted")
            
        color_class = f"badge-{grade.lower()}"
        return ui.span(f"Nutri-Score {grade}", class_=f"badge-score {color_class} fs-3 px-4 py-2 mt-2 d-inline-block")

    @output
    @render_widget
    def chart_pred_prob():
        probs = pred_probs_res()
        if probs is None:
            # Empty chart template
            fig = go.Figure()
            fig.update_layout(title="Class Probabilities will render here", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            return fig
            
        classes = ["A", "B", "C", "D", "E"]
        colors = ["#038141", "#85bb2f", "#fecb02", "#ee8100", "#e63e11"]
        
        fig = px.bar(
            x=classes,
            y=probs * 100,
            color=classes,
            color_discrete_map=dict(zip(classes, colors)),
            labels={"x": "Grade", "y": "Confidence (%)"},
            title="Model Predictor Class Probabilities (%)"
        )
        fig.update_layout(
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        return fig

    # ============================================================
    # TAB 4: Personal Diet Simulator (Synthesis)
    # ============================================================

    # Reactive daily diet list
    # Stores list of dicts: {'category': str, 'grams': float, 'calories': float, 'nutriscore': str, 'nova': float, 'macro': str}
    sim_diet = reactive.Value([])

    @reactive.Effect
    @reactive.event(input.btn_add_item)
    def add_diet_item():
        category = input.sim_product_category()
        grams = input.sim_grams()
        
        # Query representative stats for the product category
        df_cat = products[products["top_category"] == category]
        if df_cat.empty:
            avg_kcal_100g = 150.0
            grade = 'c'
            nova = 3.0
        else:
            avg_kcal_100g = df_cat["energy-kcal_100g"].mean()
            if pd.isna(avg_kcal_100g):
                avg_kcal_100g = 150.0
            grade = df_cat["nutriscore_grade"].mode().values[0] if not df_cat["nutriscore_grade"].dropna().empty else 'c'
            nova = df_cat["nova_group"].mean()
            if pd.isna(nova):
                nova = 3.0
                
        # Calculate nutritional yields
        calories = (grams / 100.0) * avg_kcal_100g
        macro = map_category_to_macro(category)
        
        # Append to reactive value
        current_diet = list(sim_diet())
        current_diet.append({
            'category': category,
            'grams': grams,
            'calories': calories,
            'nutriscore': grade.lower(),
            'nova': round(nova, 1),
            'macro': macro
        })
        sim_diet.set(current_diet)

    @reactive.Effect
    @reactive.event(input.btn_clear_diet)
    def clear_diet_list():
        sim_diet.set([])

    @output
    @render.ui
    def sim_diet_list():
        diet = sim_diet()
        if not diet:
            return ui.p("Your basket is empty. Select a food category and weight, then click 'Add' to build your simulated day!", class_="text-muted mt-2")
            
        # Build html list items
        list_items = []
        for i, item in enumerate(diet):
            badge_color = f"badge-{item['nutriscore'].lower()}"
            list_items.append(
                ui.div(
                    ui.div(
                        ui.span(f"{item['category']}", class_="fw-bold"),
                        ui.div(f"{item['grams']}g | {item['calories']:.0f} kcal | NOVA {item['nova']}", class_="text-muted small"),
                    ),
                    ui.span(item['nutriscore'].upper(), class_=f"badge {badge_color} float-end px-2 py-1 fs-6"),
                    class_="d-flex justify-content-between align-items-center py-2 border-bottom"
                )
            )
        return ui.div(*list_items, class_="mt-2", style="max-height: 250px; overflow-y: auto;")

    # --- Simulator KPIs ---

    @output
    @render.ui
    def sim_kpi_calories():
        diet = sim_diet()
        if not diet:
            return "0 kcal/day"
        tot_kcal = sum(item['calories'] for item in diet)
        return f"{tot_kcal:,.0f} kcal"

    @output
    @render.ui
    def sim_kpi_nutriscore():
        diet = sim_diet()
        if not diet:
            return "N/A"
        
        # Convert Nutri-Score A-E to numeric index 1-5
        score_mapping = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
        tot_scores = [score_mapping.get(item['nutriscore'], 3) for item in diet]
        avg_score = np.mean(tot_scores)
        
        # Convert back to closest score
        closest_grade = 'c'
        min_dist = 999.0
        for grade, val in score_mapping.items():
            dist = abs(avg_score - val)
            if dist < min_dist:
                min_dist = dist
                closest_grade = grade
                
        color_class = f"badge-{closest_grade}"
        return ui.span(f"Grade {closest_grade.upper()}", class_=f"badge {color_class} px-3 py-1 fs-5")

    @output
    @render.ui
    def sim_kpi_nova():
        diet = sim_diet()
        if not diet:
            return "0.0%"
        nova_4_count = sum(1 for item in diet if item['nova'] >= 3.5)
        pct = (nova_4_count / len(diet)) * 100
        return f"{pct:.1f}% Ultra-Processed"

    # --- Simulator Chart Outputs ---

    @output
    @render_widget
    def chart_sim_comparison():
        """Compare simulated intake macro categories against selected country baseline."""
        diet = sim_diet()
        country = input.sim_country()
        
        # Fetch country 2020 baseline
        country_base = cy[(cy["entity"] == country) & (cy["year"] == 2020)]
        
        groups = ["grp_cereals", "grp_meat", "grp_dairy_eggs", "grp_oils_fats", 
                  "grp_sugar_sweeteners", "grp_fruits_vegetables", "grp_starchy_roots_pulses", "grp_other"]
        
        groups_label = {
            "grp_cereals": "Cereals",
            "grp_meat": "Meat",
            "grp_dairy_eggs": "Dairy & Eggs",
            "grp_oils_fats": "Oils & Fats",
            "grp_sugar_sweeteners": "Sugars & Sweet",
            "grp_fruits_vegetables": "Fruits & Veg",
            "grp_starchy_roots_pulses": "Roots & Pulses",
            "grp_other": "Other"
        }
        
        # Initialize calorie counts
        baseline_vals = []
        personal_vals = {g: 0.0 for g in groups}
        
        if country_base.empty:
            baseline_vals = [0.0] * len(groups)
        else:
            baseline_vals = [country_base[g].values[0] for g in groups]
            
        for item in diet:
            macro = item['macro']
            if macro in personal_vals:
                personal_vals[macro] += item['calories']
            else:
                personal_vals["grp_other"] += item['calories']
                
        # Build comparative dataframe
        plot_data = []
        for i, g in enumerate(groups):
            # Country Baseline
            plot_data.append({
                "Dietary Group": groups_label[g],
                "Calories (kcal)": baseline_vals[i],
                "Source": f"{country} Baseline (2020)"
            })
            # Simulated Personal
            plot_data.append({
                "Dietary Group": groups_label[g],
                "Calories (kcal)": personal_vals[g],
                "Source": "Simulated Personal Diet"
            })
            
        df_plot = pd.DataFrame(plot_data)
        
        fig = px.bar(
            df_plot,
            x="Dietary Group",
            y="Calories (kcal)",
            color="Source",
            barmode="group",
            color_discrete_map={f"{country} Baseline (2020)": "#94a3b8", "Simulated Personal Diet": "#FF6B35"},
            title=f"Dietary Intake Comparison: Simulated VS. {country} Baseline"
        )
        fig.update_layout(
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @output
    @render_widget
    def chart_sim_donut():
        """Shows distribution of Nutri-Scores in the simulated daily diet."""
        diet = sim_diet()
        if not diet:
            fig = go.Figure()
            fig.update_layout(title="Add food to see Nutri-Score balance", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            return fig
            
        # Count scores
        counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        for item in diet:
            grade = item['nutriscore'].upper()
            if grade in counts:
                counts[grade] += 1
            else:
                counts['C'] += 1
                
        df_counts = pd.DataFrame([{"Grade": k, "Count": v} for k, v in counts.items() if v > 0])
        
        if df_counts.empty:
            return go.Figure()
            
        fig = px.pie(
            df_counts,
            values="Count",
            names="Grade",
            hole=0.4,
            color="Grade",
            color_discrete_map={"A": "#038141", "B": "#85bb2f", "C": "#fecb02", "D": "#ee8100", "E": "#e63e11"},
            title="Basket Nutri-Score Distribution"
        )
        fig.update_layout(
            margin={"r":10,"t":40,"l":10,"b":10},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    # --- AI Health Risk Forecast & Recommendations ---

    @output
    @render.ui
    def sim_ai_forecast():
        diet = sim_diet()
        country = input.sim_country()
        activity = input.sim_activity()
        
        # Calculate daily intake target based on selected activity level
        activity_factors = {"Sedentary": 1.2, "Light": 1.375, "Moderate": 1.55, "Active": 1.725}
        factor = activity_factors.get(activity, 1.55)
        bmr = 1500.0  # Estimated standard basal metabolic rate
        target_calories = bmr * factor
        
        if not diet:
            return ui.div(
                ui.p("🛡️ Load representative foods in the simulator to run your AI health outcome forecast.", class_="text-center py-4 fs-5 text-muted")
            )
            
        # Fetch country 2020 baseline composition
        base_df = cy[(cy["entity"] == country) & (cy["year"] == 2020)]
        if base_df.empty:
            return ui.p("Error: Baseline data for selected country not found.")
            
        groups = ["grp_cereals", "grp_meat", "grp_dairy_eggs", "grp_oils_fats", 
                  "grp_sugar_sweeteners", "grp_fruits_vegetables", "grp_starchy_roots_pulses", "grp_other"]
        
        # Total personal intake calories
        sim_total_kcal = sum(item['calories'] for item in diet)
        
        # Scale up if the calories are too low for obesity regressor predictions
        scaled_diet = {}
        is_scaled = False
        scale_ratio = 1.0
        
        if sim_total_kcal < 1200:
            is_scaled = True
            scale_ratio = 2000.0 / sim_total_kcal
            sim_total_kcal_scaled = 2000.0
        else:
            sim_total_kcal_scaled = sim_total_kcal
            
        # Aggregate macro calories
        personal_macros = {g: 0.0 for g in groups}
        for item in diet:
            macro = item['macro']
            val = item['calories'] * scale_ratio
            if macro in personal_macros:
                personal_macros[macro] += val
            else:
                personal_macros["grp_other"] += val
                
        # Obesity Model Prediction
        # Features: ['calories', 'grp_cereals', 'grp_meat', 'grp_dairy_eggs', 'grp_oils_fats', 'grp_sugar_sweeteners', 'grp_fruits_vegetables', 'grp_starchy_roots_pulses', 'grp_other']
        pred_df = pd.DataFrame([{
            'calories': sim_total_kcal_scaled,
            'grp_cereals': personal_macros['grp_cereals'],
            'grp_meat': personal_macros['grp_meat'],
            'grp_dairy_eggs': personal_macros['grp_dairy_eggs'],
            'grp_oils_fats': personal_macros['grp_oils_fats'],
            'grp_sugar_sweeteners': personal_macros['grp_sugar_sweeteners'],
            'grp_fruits_vegetables': personal_macros['grp_fruits_vegetables'],
            'grp_starchy_roots_pulses': personal_macros['grp_starchy_roots_pulses'],
            'grp_other': personal_macros['grp_other']
        }])
        
        # Baseline obesity prediction
        base_pred_df = pd.DataFrame([{
            'calories': base_df['calories'].values[0],
            'grp_cereals': base_df['grp_cereals'].values[0],
            'grp_meat': base_df['grp_meat'].values[0],
            'grp_dairy_eggs': base_df['grp_dairy_eggs'].values[0],
            'grp_oils_fats': base_df['grp_oils_fats'].values[0],
            'grp_sugar_sweeteners': base_df['grp_sugar_sweeteners'].values[0],
            'grp_fruits_vegetables': base_df['grp_fruits_vegetables'].values[0],
            'grp_starchy_roots_pulses': base_df['grp_starchy_roots_pulses'].values[0],
            'grp_other': base_df['grp_other'].values[0]
        }])
        
        # Predictions
        if obesity_model is not None:
            try:
                pred_obesity = obesity_model.predict(pred_df)[0]
                base_obesity = obesity_model.predict(base_pred_df)[0]
                diff = pred_obesity - base_obesity
            except Exception:
                pred_obesity, base_obesity, diff = 25.0, 25.0, 0.0
        else:
            pred_obesity, base_obesity, diff = 25.0, 25.0, 0.0
            
        # Assess Simulated Nutri-Score & NOVA
        score_mapping = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
        tot_scores = [score_mapping.get(item['nutriscore'], 3) for item in diet]
        avg_ns = np.mean(tot_scores)
        nova_4_count = sum(1 for item in diet if item['nova'] >= 3.5)
        nova_pct = (nova_4_count / len(diet)) * 100
        
        # Build conditionally generated recommendations
        recs = []
        alert_class = "alert-info"
        
        # 1. Calorie Assessment
        cal_diff = sim_total_kcal - target_calories
        if cal_diff > 300:
            recs.append(f"⚠️ **Caloric Excess:** Your intake of **{sim_total_kcal:,.0f} kcal** exceeds your active daily target of **{target_calories:,.0f} kcal** by **{cal_diff:,.0f} kcal**. This intake profile is strongly associated with an increased long-term obesity prevalence.")
            alert_class = "alert-danger"
        elif cal_diff < -300:
            recs.append(f"🍏 **Caloric Deficit:** Your simulated intake (**{sim_total_kcal:,.0f} kcal**) is significantly below your active physical requirement (**{target_calories:,.0f} kcal**). Ensure you are eating highly nutrient-dense foods to prevent nutritional deficiency.")
            alert_class = "alert-warning"
        else:
            recs.append(f"🌟 **Optimal Calorie Balance:** Your simulated daily intake (**{sim_total_kcal:,.0f} kcal**) aligns perfectly with your physical activity level guideline (**{target_calories:,.0f} kcal**).")
            
        # 2. Composition / Processing Assessment
        if nova_pct >= 40:
            recs.append(f"🏭 **High Ultra-Processing (NOVA 4):** **{nova_pct:.1f}%** of your daily diet contains ultra-processed products. The World Health Organization links diets exceeding 30% ultra-processed shares to chronic inflammation and metabolic syndrome.")
            alert_class = "alert-danger"
        elif avg_ns <= 2.2 and nova_pct < 20:
            recs.append(f"🥗 **Clean, Nutrient-Dense Diet:** Excellent product quality! Your average Nutri-Score is outstanding (**A/B**), and your ultra-processed intake share is very low (**{nova_pct:.1f}%**).")
            
        # 3. Model shift assessment
        if diff > 1.5:
            recs.append(f"📈 **ML Health Risk Shift:** Compared to the average **{country}** baseline lifestyle, this diet shifts your predicted long-term metabolic health risk by **+{diff:.1f}%** on the country obesity scale. Minimizing refined sugars, trans fats, and increasing complex carbohydrates (cereals, legumes) is recommended.")
            alert_class = "alert-danger"
        elif diff < -1.5:
            recs.append(f"📉 **ML Health Risk Shift:** Fantastic! This dietary structure shifts your predicted metabolic health risk by **{diff:.1f}%** compared to the average **{country}** baseline. This composition offers substantial protective health benefits.")
            
        # Renders the final forecast panel
        return ui.div(
            ui.div(
                ui.h4("Long-term Health Outcome Simulation:", class_="mb-3 fw-bold"),
                ui.layout_columns(
                    ui.div(
                        ui.div("Baseline Country Obesity Rate Prediction", class_="text-muted small"),
                        ui.div(f"{base_obesity:.1f}%", class_="fs-4 fw-bold text-dark")
                    ),
                    ui.div(
                        ui.div("Simulated Personal Obesity Rate Forecast", class_="text-muted small"),
                        ui.div(f"{pred_obesity:.1f}%", class_="fs-4 fw-bold text-primary")
                    ),
                    ui.div(
                        ui.div("Forecasted Obesity Index Shift", class_="text-muted small"),
                        ui.div(f"{diff:+.1f}%" if diff != 0 else "0.0%", class_=f"fs-4 fw-bold {'text-danger' if diff > 0 else 'text-success' if diff < 0 else 'text-dark'}")
                    ),
                    col_widths=[4, 4, 4]
                ),
                class_="p-3 bg-light border rounded mb-3"
            ),
            ui.div(
                ui.h5("📋 AI Recommendations & Dietary Analysis:", class_="fw-bold"),
                ui.markdown("\n\n".join(recs)),
                class_=f"alert {alert_class} mt-2"
            )
        )

# ============================================================
# App Construction
# ============================================================

app = App(app_ui, server, static_assets={"/": str(APP_DIR / "www")})
