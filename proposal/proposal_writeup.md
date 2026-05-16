# Project Proposal: Global Food & Nutrition Dashboard

## Project Description

This project builds an interactive Python Shiny dashboard to explore three interconnected questions: *(1) What does the world eat?* — examining dietary patterns and calorie supply across 180+ countries; *(2) How healthy is it?* — linking food systems to health outcomes such as obesity and malnutrition; and *(3) What's really in our food?* — drilling into 45,000+ food products to assess nutritional quality and processing levels. The application combines country-level food supply data (FAOSTAT, Our World in Data, WHO) with product-level nutritional analysis (Kaggle) to provide a comprehensive, multi-scale view of global food and nutrition.

## Motivation

Food is universal, yet deeply unequal. Over 800 million people face hunger while 1 billion are obese — often in the same countries. Understanding what the world eats, and the nutritional quality of available food, is critical for public health policy, sustainable development, and individual awareness. This dashboard makes complex, multi-source nutrition data accessible through interactive visual storytelling, bridging the gap between raw statistics and actionable insight.

## Dataset Description

We combine four complementary data sources:

- **FAOSTAT Food Balance Sheets** (FAO): Daily per-capita calorie, protein, and fat supply for 180+ countries (2010–2023), broken down by food source (meat, cereals, dairy, etc.).
- **Our World in Data — Food Supply**: Long-term trends (1961–2023) linking calorie supply to health outcomes (obesity, life expectancy) across 200+ countries.
- **WHO Global Health Observatory**: Country-level obesity prevalence, malnutrition, and stunting indicators.
- **Kaggle Global Food & Nutrition Dataset**: Product-level data for 45,000+ food items including Nutri-Score (A–E), NOVA processing classification, macronutrients, and Eco-Score.

Data is available in CSV/XLSX format and requires merging across sources using country codes (ISO-3) and standardized food category mappings.

## Visualization Challenge

This data presents several non-trivial visualization challenges:

1. **Multi-scale structure**: Country-level aggregates (180+ nations × 60+ years) must coexist with product-level detail (45,000+ items × 20+ nutritional features) in a single coherent interface.
2. **Spatio-temporal dimensions**: Mapping calorie supply geographically while simultaneously showing temporal trends requires linked, cross-filtered views.
3. **High dimensionality**: Each food product has 20+ nutritional attributes (energy, sugar, fat, sodium, fiber, Nutri-Score, NOVA class) that must be compared across categories without overwhelming the viewer.
4. **Heterogeneous data types**: Combining continuous variables (calories, macronutrients), ordinal scales (Nutri-Score A–E, NOVA 1–4), and categorical groupings (food types, continents) demands diverse chart types and careful encoding choices.
5. **ML integration**: Embedding predictive models (Nutri-Score classification, country clustering, obesity regression) within the visual analytics workflow adds interaction complexity.

*Word count: ~340*
