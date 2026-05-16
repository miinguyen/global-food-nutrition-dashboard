# Project Proposal: Global Food & Nutrition Dashboard

## 1. Proposal Write-up

### What We're Building

We are creating an interactive dashboard using Python Shiny to answer three core questions about our global food system, each mapped to a dedicated tab:

1. **"What does the world eat?"** — We examine how calorie supplies and food sources vary across 180+ countries over decades.
2. **"How healthy is it?"** — We link dietary patterns to health outcomes (obesity, malnutrition) and use ML models to uncover hidden relationships.
3. **"What's really in our food?"** — We zoom into 45,000+ food products to assess nutritional quality using Nutri-Score and NOVA classifications.

### Why It Matters

More than 800 million people go hungry while over a billion struggle with obesity — often in the same countries. The data to understand these issues exists, but it is scattered across different organizations and formats. Our dashboard pulls it together into one interactive experience so anyone can explore and learn from it.

### Our Datasets

We combine three major sources to build a complete picture:

1. **Our World in Data (OWID)** — Daily calorie supply, dietary composition by food group (meat, cereals, dairy), obesity rates, and life expectancy across 200+ countries (1961–2023).
2. **WHO Global Health Observatory** — Country-level health outcomes, including adult obesity and child malnutrition prevalence.
3. **Open Food Facts** — A sample of 10,000+ detailed product profiles including Nutri-Score (A–E), NOVA processing classifications, and macronutrients.

Merging requires aligning country identifiers (ISO-3 codes), time periods, and harmonizing the health metrics across different sources.

### Why This Data is Hard to Visualize

1. **Scale mismatch.** Country-level aggregates (180 nations × 60 years) must coexist with product-level detail (45,000+ items × 20+ attributes).
2. **Space + time.** Geographic calorie patterns and their temporal evolution need linked, cross-filtered views.
3. **High dimensionality.** 20+ nutritional attributes per product require careful encoding to avoid clutter.
4. **Mixed types.** Numbers (calories), ranked scales (Nutri-Score A–E), and categories (food groups) each need different visual treatments, all working together.

*(Word count: ~290)*

---

## 2. Wireframe Annotations & Layout Plan

### Interface Structure

- **Navigation:** Three tabs, one per core question. A global header shows the project title and active tab.
- **Layout per tab:** Left sidebar (~25% width) for filters, main panel (~75%) for charts in a responsive grid.
- **Responsive behavior:** Charts sit side-by-side on desktop, stack vertically on smaller screens. Sidebar collapses on mobile.

---

### Tab 1: "What does the world eat?"

| Component | Details |
|-----------|---------|
| **Filters** | Year slider (1961–2023), Continent dropdown, Food Type dropdown |
| **Chart 1 — Choropleth Map** | Shows per-capita calorie supply by country. Hover = tooltip with values. Click a country = cross-filters Chart 2. |
| **Chart 2 — Line Chart** | Shows calorie trend over time for the selected country (bold) vs. global average (dashed). Updates when a country is clicked on the map. |

### Tab 2: "How healthy is it?"

| Component | Details |
|-----------|---------|
| **Filters** | Year slider (shared with Tab 1), Health Metric dropdown (Obesity / Malnutrition / Life Expectancy) |
| **Chart 3 — Scatter Plot** | X = calorie supply, Y = selected health metric. Dots colored by continent. Brushing selects countries and shows a summary. |
| **Chart 4 — Cluster Visualization** | K-means clustering of countries by diet, displayed as a 2D projection. Hover = dietary profile. Click a cluster = highlights those countries on Chart 3. |

### Tab 3: "What's really in our food?"

| Component | Details |
|-----------|---------|
| **Filters** | Food Category multi-select, NOVA level checkboxes, optional Nutri-Score filter |
| **Chart 5 — Stacked Bar Chart** | Nutri-Score distribution (A–E) per food category. Click a bar segment = filters Chart 6. |
| **Chart 6 — Scatter Plot** | Sugar (X) vs. Fat (Y) per product, colored by Nutri-Score, sized by calories. Brushing selects products for detail view. |

### Cross-Filtering

- Clicking a country on Tab 1 pre-selects it when navigating to Tab 2. The year slider persists across Tabs 1 and 2.
- Tab 3 operates independently (different dataset).
- All charts use Plotly (built-in zoom, pan, and export).

*(The wireframe sketch image is in `proposal/wireframe/dashboard_wireframe.png`.)*

---

## 3. Presentation Slides Outline (5 Minutes)

- **Slide 1:** Title, team (Nguyen Thi Tra My — V202503042, Tran Thi Hoai Phuong — V202502962), [GitHub link](https://github.com/miinguyen/global-food-nutrition-dashboard).
- **Slide 2:** Three-part question, dashboard structure, and project timeline.
- **Slide 3:** Four datasets, integration challenges (ISO-3 codes, mixed formats).
- **Slide 4:** Wireframe walkthrough, interactive features (cross-filtering, brushing), ML components (Nutri-Score prediction, clustering, regression).
- **Slide 5:** Task allocation and next steps (data pipeline → MVP → final submission).
