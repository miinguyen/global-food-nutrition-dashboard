# Data Dictionary — Processed Datasets

**Project:** Global Food & Nutrition Dashboard  
**Course:** COMP5120 — Data Visualization (Spring 2026)  
**Date:** May 16, 2026  
**Source directory:** `data/processed/`

---

## Overview

After running `data/processing.py`, four output files are generated. Each table serves a specific role in the dashboard and ML pipeline:

| File | Format | Rows | Description | Dashboard Usage |
|------|--------|------|-------------|-----------------|
| `country_yearly` | `.parquet` / `.csv` | 10,418 | Country-level nutrition, diet composition, obesity, and life expectancy by year (1961–2023) | Tab 1 (Choropleth, Trend Lines, Stacked Area, Bar Chart) & Tab 2 (Scatter, Parallel Coordinates) |
| `country_health` | `.parquet` / `.csv` | 7,778 | WHO adult obesity and child underweight prevalence with confidence intervals (1990–2023) | Tab 2 (Obesity vs. Underweight Scatter, Dual-Burden Analysis) |
| `products` | `.parquet` / `.csv` | 8,058 | Product-level nutritional profiles from Open Food Facts with Nutri-Score and NOVA classification | Tab 3 (Nutri-Score Distribution, Radar Chart, NOVA Breakdown, ML Classifier) |
| `country_meta` | `.csv` only | 193 | Unique country → continent lookup table | Internal reference for filtering and labeling |

---

## Table 1: `country_yearly`

### What is a row?

Each row represents **one country in one year**. For example, row `(AFG, 1961)` contains Afghanistan's total calorie supply, the caloric contribution of 26 individual food groups, aggregated macro-group totals, obesity prevalence, and life expectancy — all for the year 1961.

### Column Definitions

#### Identifiers

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `entity` | string | `Afghanistan` | Full country name (from OWID) |
| `iso3` | string | `AFG` | ISO 3166-1 alpha-3 country code (primary key alongside `year`) |
| `year` | int | `1961` | Calendar year (range: 1961–2023) |
| `continent` | string | `Asia` | Continent label: `Africa`, `Americas`, `Asia`, `Europe`, or `Other` |

#### Calorie Supply

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `calories` | float | kcal/capita/day | Total daily food supply in kilocalories per person per day |

#### Individual Food Groups (26 columns)

These columns represent the caloric contribution (kcal/capita/day) of each specific food category:

**Cereals:**

| Column | Description |
|--------|-------------|
| `wheat` | Calories from wheat and wheat products |
| `rice` | Calories from rice and rice products |
| `maize` | Calories from maize (corn) and maize products |
| `barley` | Calories from barley and barley products |
| `cereals_other` | Calories from other cereals (millet, sorghum, oats, rye, etc.) |

**Meat:**

| Column | Description |
|--------|-------------|
| `meat_beef` | Calories from bovine meat (beef, veal, buffalo) |
| `meat_poultry` | Calories from poultry meat (chicken, turkey, duck) |
| `meat_pig` | Calories from pig meat (pork) |
| `meat_sheep` | Calories from mutton and goat meat |
| `meat_other` | Calories from other meats (game, offal, etc.) |

**Animal Products:**

| Column | Description |
|--------|-------------|
| `dairy` | Calories from milk and dairy products (cheese, butter, yogurt) |
| `eggs` | Calories from eggs and egg products |

**Fats & Oils:**

| Column | Description |
|--------|-------------|
| `vegetable_oils` | Calories from vegetable oils (soybean, palm, sunflower, olive, etc.) |
| `animal_fats` | Calories from animal fats (lard, tallow, fish oil) |
| `oilcrops` | Calories from oil-bearing crops (soybeans, groundnuts, sesame, etc.) |

**Sugars:**

| Column | Description |
|--------|-------------|
| `sugar_sweeteners` | Calories from refined sugar, syrups, and artificial sweeteners |
| `sugar_crops` | Calories from raw sugar crops (sugarcane, sugar beet) |

**Plant Foods:**

| Column | Description |
|--------|-------------|
| `fruit` | Calories from fruits |
| `vegetables` | Calories from vegetables |
| `starchy_roots` | Calories from starchy root crops (potatoes, cassava, yams) |
| `pulses` | Calories from pulses (beans, lentils, peas, chickpeas) |
| `nuts` | Calories from tree nuts and groundnuts |

**Other:**

| Column | Description |
|--------|-------------|
| `fish_seafood` | Calories from fish, shellfish, and other aquatic products |
| `alcohol` | Calories from alcoholic beverages (beer, wine, spirits) |
| `miscellaneous` | Calories from other food items not classified above |

#### Aggregated Macro Groups (8 columns)

These columns are computed sums of the individual food groups above, designed for the **Stacked Area Chart** in Tab 1:

| Column | Formula | Description |
|--------|---------|-------------|
| `grp_cereals` | wheat + rice + maize + barley + cereals_other | Total cereal-based calories |
| `grp_meat` | meat_beef + meat_poultry + meat_pig + meat_sheep + meat_other | Total meat-based calories |
| `grp_dairy_eggs` | dairy + eggs | Total dairy and egg calories |
| `grp_oils_fats` | vegetable_oils + animal_fats + oilcrops | Total fat and oil calories |
| `grp_sugar_sweeteners` | sugar_sweeteners + sugar_crops | Total sugar-related calories |
| `grp_fruits_vegetables` | fruit + vegetables | Total fruit and vegetable calories |
| `grp_starchy_roots_pulses` | starchy_roots + pulses + nuts | Total starchy root, pulse, and nut calories |
| `grp_other` | fish_seafood + alcohol + miscellaneous | Total other food calories |

> **Note:** The 8 macro groups should sum approximately to the `calories` column. Minor discrepancies may exist due to rounding in the source data.

#### Health Indicators

| Column | Type | Unit | Description |
|--------|------|------|-------------|
| `obesity_pct` | float | % | Prevalence of obesity among adults (BMI ≥ 30). Source: OWID (derived from NCD-RisC). Available 1990–2022 only; earlier years are `NaN`. |
| `life_exp` | float | years | Life expectancy at birth (both sexes). Source: OWID (derived from UN World Population Prospects). Available 1950–2023. |

---

## Table 2: `country_health`

### What is a row?

Each row represents **one country in one year** with WHO-sourced health indicator data. Some country-year pairs may appear more than once if both obesity and underweight survey data exist for that year.

### Column Definitions

| Column | Type | Unit | Example | Description |
|--------|------|------|---------|-------------|
| `iso3` | string | — | `AFG` | ISO 3166-1 alpha-3 country code |
| `year` | int | — | `2010` | Calendar year (range: 1990–2023) |
| `who_obesity_pct` | float | % | `8.95` | Adult obesity prevalence (BMI ≥ 30), age-standardized. Source: WHO Global Health Observatory. |
| `ci_low_obesity` | float | % | `7.28` | Lower bound of the 95% confidence interval for obesity estimate |
| `ci_high_obesity` | float | % | `10.82` | Upper bound of the 95% confidence interval for obesity estimate |
| `region` | string | — | `Eastern Mediterranean` | WHO administrative region (6 regions: Africa, Americas, South-East Asia, Europe, Eastern Mediterranean, Western Pacific) |
| `underweight_pct` | float | % | `29.1` | Prevalence of underweight children under 5 years of age (weight-for-age < -2 SD). Source: WHO/UNICEF/World Bank Joint Child Malnutrition Estimates. Often `NaN` — data is only available for survey years. |
| `ci_low_underweight` | float | % | `27.4` | Lower bound of 95% CI for underweight estimate |
| `ci_high_underweight` | float | % | `31.0` | Upper bound of 95% CI for underweight estimate |
| `continent` | string | — | `Asia` | Continent label derived from WHO region mapping |

### Key Notes

- **Obesity data** is available annually (modeled estimates) for most countries from 1990–2022.
- **Underweight data** is only available for specific survey years (irregular), so most rows have `NaN` for underweight columns.
- This table is useful for the **dual burden of malnutrition** analysis: countries can simultaneously have high obesity and high child underweight.

---

## Table 3: `products`

### What is a row?

Each row represents **one food product** from the Open Food Facts database. Products were collected via the Open Food Facts API (10,000 entries requested, 8,058 retained after filtering for valid Nutri-Score grades).

### Column Definitions

| Column | Type | Unit | Example | Description |
|--------|------|------|---------|-------------|
| `product_name` | string | — | `Madeleines ChocoLait` | Commercial name of the product. May be empty for some entries. |
| `brands` | string | — | `Apple bandit` | Brand name of the product manufacturer |
| `categories` | string | — | `Snacks, Biscuits et gâteaux` | Comma-separated list of food categories (hierarchical, from broad to specific) |
| `countries_tags` | string | — | `en:france` | Countries where the product is sold (comma-separated, prefixed with language code) |
| `nutriscore_grade` | string | — | `e` | **Nutri-Score grade** (a, b, c, d, e) — a nutritional quality rating system: |
| | | | | **a** = Best nutritional quality (green) |
| | | | | **b** = Good (light green) |
| | | | | **c** = Average (yellow) |
| | | | | **d** = Poor (orange) |
| | | | | **e** = Worst nutritional quality (red) |
| `nova_group` | float | — | `4.0` | **NOVA food classification** (1–4): |
| | | | | **1** = Unprocessed or minimally processed foods |
| | | | | **2** = Processed culinary ingredients |
| | | | | **3** = Processed foods |
| | | | | **4** = Ultra-processed food and drink products |
| `energy-kcal_100g` | float | kcal | `452.0` | Energy content per 100 grams of product |
| `fat_100g` | float | g | `21.3` | Total fat per 100g |
| `saturated-fat_100g` | float | g | `8.7` | Saturated fat per 100g |
| `carbohydrates_100g` | float | g | `55.0` | Total carbohydrates per 100g |
| `sugars_100g` | float | g | `28.5` | Total sugars per 100g |
| `fiber_100g` | float | g | `3.2` | Dietary fiber per 100g |
| `proteins_100g` | float | g | `6.5` | Protein content per 100g |
| `salt_100g` | float | g | `0.8` | Salt content per 100g |
| `top_category` | string | — | `Snacks` | First (broadest) category extracted from the `categories` field. Used for grouping in charts. |

### Key Notes

- **~60% of nutritional columns are NaN.** Many products in Open Food Facts have incomplete nutritional panels. Dashboard visualizations handle missing values gracefully.
- Only products with **valid `nutriscore_grade`** ∈ {a, b, c, d, e} are retained. Products with `unknown` or `not-applicable` grades were filtered out (1,943 removed).
- The **Nutri-Score** is a European front-of-pack labeling system developed by Santé publique France. It considers both negative factors (energy, sugars, saturated fat, sodium) and positive factors (fiber, protein, fruits/vegetables/nuts).

---

## Table 4: `country_meta`

### What is a row?

Each row represents **one unique country** and its continent assignment.

### Column Definitions

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `iso3` | string | `AFG` | ISO 3166-1 alpha-3 country code |
| `entity` | string | `Afghanistan` | Full country name |
| `continent` | string | `Asia` | Continent label |

### Continent Distribution

| Continent | Countries |
|-----------|-----------|
| Africa | 47 |
| Americas | 35 |
| Asia | 47 |
| Europe | 43 |
| Other | 4 |
| **Total** | **193** |

> Countries labeled `Other` include Hong Kong, Macao, Netherlands Antilles, and New Caledonia — territories that don't fit neatly into a single continent classification.

---

## Summary Statistics

### `country_yearly` — Temporal Coverage

| Metric | Value |
|--------|-------|
| Year range | 1961–2023 |
| Countries covered | 193 |
| Average rows per country | ~54 |
| Calorie range | ~1,280 – ~3,900 kcal/capita/day |
| Obesity range | ~0.3% – ~75% (Pacific islands highest) |
| Life expectancy range | ~26 – ~85 years |

### `country_health` — WHO Indicators

| Metric | Value |
|--------|-------|
| Year range | 1986–2024 (underweight surveys span wider) |
| Countries covered | ~200 (WHO member states) |
| Obesity data availability | Annual modeled estimates for most countries |
| Underweight data availability | Sporadic survey years only |

### `products` — Open Food Facts

| Metric | Value |
|--------|-------|
| Total products (after filtering) | 8,058 |
| Nutri-Score distribution | a: ~8%, b: ~12%, c: ~15%, d: ~30%, e: ~35% |
| Most common NOVA group | 4 (ultra-processed) |
| Nutritional completeness | ~40% of products have full nutritional panels |
| Top countries | France, Germany, United States |

---

## Relationships Between Tables

```
┌──────────────────┐      ┌──────────────────┐
│  country_yearly   │      │  country_health   │
│                    │      │                    │
│  iso3 ◄──────────►│ iso3 │  iso3              │
│  year              │ year │  year              │
│  calories          │      │  who_obesity_pct   │
│  grp_cereals...    │      │  underweight_pct   │
│  obesity_pct       │      │  ci_low / ci_high  │
│  life_exp          │      │  region            │
│  continent         │      │  continent         │
└────────┬───────────┘      └──────────────────┘
         │
         │ iso3
         ▼
┌──────────────────┐      ┌──────────────────┐
│  country_meta     │      │     products       │
│                    │      │                    │
│  iso3              │      │  product_name      │
│  entity            │      │  nutriscore_grade  │
│  continent         │      │  nova_group        │
│                    │      │  energy-kcal_100g   │
│                    │      │  fat / sugar / ...  │
└──────────────────┘      │  top_category      │
                           └──────────────────┘
                           (standalone — no join key)
```

- **`country_yearly`** and **`country_health`** can be joined on `(iso3, year)` to combine OWID nutrition data with WHO health indicators.
- **`country_meta`** provides a lookup for country names and continent labels.
- **`products`** is a standalone table — it does not join with the country-level tables. It powers the product-level analysis in Tab 3.

---

## File Format Notes

| Format | Extension | Library Required | Advantages |
|--------|-----------|-----------------|------------|
| **Parquet** | `.parquet` | `pyarrow` or `fastparquet` | Columnar storage, ~5–10× smaller than CSV, faster reads, preserves data types |
| **CSV** | `.csv` | built-in `csv` or `pandas` | Human-readable, easy to inspect in text editors or Excel |

Both formats contain identical data. The Shiny dashboard loads **Parquet** files for performance; **CSV** files are provided for manual inspection and debugging.
