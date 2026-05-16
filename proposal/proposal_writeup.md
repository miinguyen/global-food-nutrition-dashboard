# Project Proposal: Global Food & Nutrition Dashboard

## 1. Proposal Write-up

### What we're storying

We are creating an interactive dashboard using Python Shiny to answer three core questions about our global food system, each mapped to a dedicated tab:

1. **"What does the world eat?"** — We examine how calorie supplies and food sources vary across 180+ countries over decades.
2. **"How healthy is it?"** — We link dietary patterns to health outcomes (obesity, malnutrition) and use ML models to uncover hidden relationships.
3. **"What's really in our food?"** — We zoom into thousands of food products to assess their nutritional quality using Nutri-Score and NOVA classifications.

### Why It Matters

More than 800 million people go hungry while over a billion struggle with obesity — often in the same countries. The data to understand these issues exists, but it is scattered across different organizations and formats, making it nearly impossible for anyone to see the full picture in one place. Our dashboard pulls these fragmented sources together into a single interactive experience so that students, researchers, or anyone curious about food systems can explore and learn from it.

### Our Datasets and Why They Fit

We selected datasets that directly serve each of our three questions:

| Question | Dataset | Coverage | Why It Fits |
|----------|---------|----------|-------------|
| **Q1: "What does the world eat?"** | [Our World in Data — Calorie Supply](https://ourworldindata.org/grapher/daily-per-capita-caloric-supply) | 200+ countries, 1961–2023 | Provides the long-term, country-level dietary trends needed to show how food consumption has shifted over six decades |
| | [Our World in Data — Food Composition](https://ourworldindata.org/grapher/dietary-composition-by-country) | 200+ countries, 1961–2023 | Breaks down calories by food group (meat, cereals, dairy) to reveal what people actually eat |
| **Q2: "How healthy is it?"** | [Our World in Data — Obesity](https://ourworldindata.org/grapher/share-of-adults-defined-as-obese) | 200+ countries, 1975–2016 | Links dietary patterns directly to obesity prevalence for correlation analysis |
| | [Our World in Data — Life Expectancy](https://ourworldindata.org/grapher/life-expectancy) | 200+ countries, 1543–2023 | Connects diet to broader health outcomes beyond obesity |
| | [WHO GHO — Adult Obesity & Child Underweight](https://ghoapi.azureedge.net/api/) | 190+ countries, 1975–2022 | Adds clinical health indicators with confidence intervals for ML modeling |
| **Q3: "What's really in our food?"** | [Open Food Facts](https://world.openfoodfacts.org/data) | ~10,000 products | The only dataset granular enough to assess individual products by Nutri-Score, NOVA level, and macronutrients |

All datasets are linked through standardized country identifiers and are downloaded automatically via a collection script in our repository.

### Why This Data is Hard to Visualize

1. **Scale mismatch.** Country-level aggregates (180 nations across 60 years) must coexist with product-level detail (thousands of items with 20+ attributes) in one coherent interface.
2. **Space and time together.** Geographic calorie patterns and their temporal evolution need linked, cross-filtered views — a single map or chart cannot capture both.
3. **High dimensionality.** Over 20 nutritional attributes per product require careful encoding to avoid visual clutter.
4. **Mixed variable types.** Numbers (calories), ranked scales (Nutri-Score A–E), and categories (food groups) each need different visual treatments, all working together seamlessly.

*(Word count: ~460)*

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
