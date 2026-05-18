# Project Proposal: Global Food & Nutrition Dashboard

## 1. Proposal Write-up

### What we're storying

We are creating an interactive dashboard using Python Shiny to answer three core questions about our global food system, each mapped to a dedicated tab:

1. **"What does the world eat?"** — We examine how calorie supplies and food sources vary across 180+ countries over decades.
2. **"How healthy is it?"** — We link dietary patterns to health outcomes (obesity, malnutrition) and use ML models to uncover hidden relationships.
3. **"What's really in our food?"** — We zoom into thousands of food products to assess their nutritional quality using Nutri-Score [1] and NOVA classifications [2].

### Why It Matters

More than 800 million people go hungry while over a billion struggle with obesity [3] — often in the same countries. The data to understand these issues exists, but it is scattered across different organizations and formats, making it nearly impossible for anyone to see the full picture in one place. Our dashboard pulls these fragmented sources together into a single interactive experience so that students, researchers, or anyone curious about food systems can explore and learn from it.

### Our Datasets and Why They Fit

We selected datasets that directly serve each of our three questions:

| Question | Dataset | Coverage | Why It Fits |
|----------|---------|----------|-------------|
| **Q1: "What does the world eat?"** | Our World in Data — Calorie Supply [4][5] | 200+ countries, 1961–2023 | Provides the long-term, country-level dietary trends needed to show how food consumption has shifted over six decades |
| | Our World in Data — Food Composition [4][6] | 200+ countries, 1961–2023 | Breaks down calories by food group (meat, cereals, dairy) to reveal what people actually eat |
| **Q2: "How healthy is it?"** | Our World in Data — Obesity [7][3] | 200+ countries, 1975–2016 | Links dietary patterns directly to obesity prevalence for correlation analysis |
| | Our World in Data — Life Expectancy [8] | 200+ countries, 1543–2023 | Connects diet to broader health outcomes beyond obesity |
| | WHO GHO — Adult Obesity & Child Underweight [9][3] | 190+ countries, 1975–2022 | Adds clinical health indicators with confidence intervals for ML modeling |
| **Q3: "What's really in our food?"** | Open Food Facts [10] | ~10,000 products | The only dataset granular enough to assess individual products by Nutri-Score [1], NOVA level [2][11], and macronutrients |

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
- **Layout per tab:** Left sidebar (~25% width) for filters, main panel (~75%) for charts in a 2×2 responsive grid.
- **Responsive behavior:** Charts sit side-by-side on desktop, stack vertically on smaller screens. Sidebar collapses on mobile.

---

### Tab 1: "What does the world eat?"

| Component | Details |
|-----------|---------|
| **Filters** | Year slider (1961–2023), Continent dropdown, Food Type dropdown |
| **Chart 1 — Global Calorie Map** (Choropleth) | Per-capita calorie supply across 200+ countries, color-coded by intake level. Hover = tooltip with values. Click a country = cross-filters Charts 2 & 3. |
| **Chart 2 — Calorie Trend** (Line Chart) | Historical calorie supply (1961–2023) for the selected country (bold) vs. global average (dashed). Updates on map click. |
| **Chart 3 — Food Source Breakdown** (Stacked Area) | How the composition of calories (meat, cereals, dairy, oils) has shifted over time for the selected country. |
| **Chart 4 — Top/Bottom Countries** (Horizontal Bar) | Ranking of the highest and lowest calorie-supply countries for the selected year. |

### Tab 2: "How healthy is it?"

| Component | Details |
|-----------|---------|
| **Filters** | Year slider (shared with Tab 1), Health Metric dropdown (Obesity / Malnutrition / Life Expectancy) |
| **Chart 5 — Calories vs. Health** (Scatter Plot) | X = calorie supply, Y = selected health metric. Dots colored by continent. Brushing selects countries and shows a summary. |
| **Chart 6 — Country Clusters** (2D Projection) | K-means clustering of countries by dietary profile, projected via PCA. Hover = dietary profile. Click a cluster = highlights those countries on Chart 5. |
| **Chart 7 — Obesity Trend Map** (Animated Choropleth) | How obesity prevalence has spread globally over decades. Animated playback with year controls. |
| **Chart 8 — Regression Dashboard** (Line + Residuals) | Obesity regression model with predicted vs. actual values and a feature importance bar chart. |

### Tab 3: "What's really in our food?"

| Component | Details |
|-----------|---------|
| **Filters** | Food Category multi-select, NOVA level [2] checkboxes, optional Nutri-Score [1] filter |
| **Chart 9 — Nutri-Score Distribution** (Stacked Bar) | Nutri-Score [1] (A–E) breakdown per food category. Click a bar segment = filters Charts 10 & 11. |
| **Chart 10 — Sugar vs. Fat** (Scatter Plot) | Per-product sugar (X) vs. fat (Y), colored by Nutri-Score, sized by calories. Brushing selects products for detail view. |
| **Chart 11 — NOVA Processing Levels** (Donut Chart) | Proportion of products by NOVA processing group [2] (1–4). Click a segment = filters the other charts. |
| **Chart 12 — Nutri-Score Predictor** (Interactive Form) | ML classifier that predicts Nutri-Score [1] from user-input macronutrients (fat, sugar, salt, fiber, protein). |

### Interactivity & Cross-Filtering

- **Within tabs:** Clicking a country on the map (Chart 1) updates the trend line (Chart 2), food breakdown (Chart 3), and ranking highlight (Chart 4). Brushing the scatter plot (Chart 5) highlights countries in the cluster view (Chart 6). Clicking a Nutri-Score bar (Chart 9) filters the scatter (Chart 10) and donut (Chart 11).
- **Across tabs:** Clicking a country on Tab 1 pre-selects it when navigating to Tab 2. The year slider persists across Tabs 1 and 2.
- **Tab 3** operates independently (product-level dataset).
- **All charts** use Plotly with built-in zoom, pan, hover tooltips, and PNG export.

### Wireframe Sketches

![Tab 1 — What does the world eat?](wireframe/tab1_what_world_eats.png)

![Tab 2 — How healthy is it?](wireframe/tab2_how_healthy.png)

![Tab 3 — What's really in our food?](wireframe/tab3_whats_in_food.png)

---

## 3. Presentation Slides Outline (5 Minutes)

- **Slide 1:** Title, team (Nguyen Thi Tra My — V202503042, Tran Thi Hoai Phuong — V202502962), [GitHub link](https://github.com/miinguyen/global-food-nutrition-dashboard).
- **Slide 2:** Three-part question, dashboard structure, and project timeline.
- **Slide 3:** Four datasets, integration challenges (ISO-3 codes, mixed formats).
- **Slide 4:** Wireframe walkthrough, interactive features (cross-filtering, brushing), ML components (Nutri-Score prediction, clustering, regression).
- **Slide 5:** Task allocation and next steps (data pipeline → MVP → final submission).

---

## References

[1] C. Julia and S. Hercberg, "Nutri-Score: Evidence of the effectiveness of the French front-of-pack nutrition label," *Ernährungs Umschau*, vol. 64, no. 12, pp. 181–187, 2017. doi: 10.4455/eu.2017.048.

[2] C. A. Monteiro, G. Cannon, J.-C. Moubarac, R. B. Levy, M. L. C. Louzada, and P. C. Jaime, "The UN Decade of Nutrition, the NOVA food classification and the trouble with ultra-processing," *Public Health Nutr.*, vol. 21, no. 1, pp. 5–17, 2018. doi: 10.1017/S1368980017000234.

[3] NCD Risk Factor Collaboration (NCD-RisC), "Worldwide trends in body-mass index, underweight, overweight, and obesity from 1975 to 2016: a pooled analysis of 2416 population-based measurement studies in 128.9 million children, adolescents, and adults," *The Lancet*, vol. 390, no. 10113, pp. 2627–2642, 2017. doi: 10.1016/S0140-6736(17)32129-3.

[4] FAO, "FAOSTAT: Food Balances (2010–)," Food and Agriculture Organization of the United Nations, 2025. [Online]. Available: https://www.fao.org/faostat/en/#data/FBS. [Accessed: May 2025]. Licence: CC-BY-4.0.

[5] H. Ritchie, P. Rosado, and M. Roser, "Food Supply," *Our World in Data*, 2023. [Online]. Available: https://ourworldindata.org/food-supply. [Accessed: May 2025].

[6] H. Ritchie, P. Rosado, and M. Roser, "Diet Compositions," *Our World in Data*, 2023. [Online]. Available: https://ourworldindata.org/diet-compositions. [Accessed: May 2025].

[7] H. Ritchie and M. Roser, "Obesity," *Our World in Data*, 2017. [Online]. Available: https://ourworldindata.org/obesity. [Accessed: May 2025].

[8] M. Roser, E. Ortiz-Ospina, and H. Ritchie, "Life Expectancy," *Our World in Data*, 2013. [Online]. Available: https://ourworldindata.org/life-expectancy. [Accessed: May 2025].

[9] World Health Organization, "Global Health Observatory (GHO) data repository," WHO, 2025. [Online]. Available: https://www.who.int/data/gho. [Accessed: May 2025].

[10] Open Food Facts, "Open Food Facts: Free and open database of food products," 2025. [Online]. Available: https://world.openfoodfacts.org/. [Accessed: May 2025]. Licence: ODbL.

[11] C. A. Monteiro, G. Cannon, M. Lawrence, M. L. Costa Louzada, and P. Pereira Machado, *Ultra-processed foods, diet quality, and health using the NOVA classification system*. Rome, Italy: FAO, 2019.

[12] S. Hercberg, S. Chat-Yung, and M. Chauliac, "The French National Nutrition and Health Program: 2001–2006–2010," *Int. J. Public Health*, vol. 53, no. 2, pp. 68–77, 2008.
