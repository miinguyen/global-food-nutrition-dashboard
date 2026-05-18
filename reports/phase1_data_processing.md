# Phase 1 — Data Processing & Cleaning Report

**Project:** Global Food & Nutrition Dashboard  
**Course:** COMP5120 — Data Visualization (Spring 2026)  
**Date:** May 18, 2026  
**Script:** [`data/processing.py`](../data/processing.py)

---

## 1. Objective

Phase 1 transforms the seven raw datasets collected in the data-gathering stage into three clean, analysis-ready master tables. The goals are:

1. **Standardize identifiers** — Normalize country codes to ISO-3166-1 alpha-3 (`iso3`) across all datasets.
2. **Clean & filter** — Remove aggregate/continental rows, cast data types, handle missing values, and drop outliers.
3. **Enrich** — Add continent labels via WHO region mapping and a static ISO-3 → Continent lookup.
4. **Merge** — Combine related datasets into unified master tables joined on `iso3` + `year`.
5. **Eliminate redundancy** — Obesity prevalence is sourced exclusively from WHO (in `country_health`), avoiding duplication with the OWID-derived estimate.
6. **Export** — Save outputs as Parquet (for app performance) and CSV (for inspection).

---

## 2. Raw Data Inventory

| # | File | Source | Rows | Columns | Size | Description |
|---|------|--------|------|---------|------|-------------|
| 1 | `owid_calorie_supply.csv` | OWID | 13,265 | 4 | 393 KB | Daily per-capita calorie supply by country & year (1961–2023) |
| 2 | `owid_food_composition.csv` | OWID | 13,032 | 28 | 2.97 MB | Caloric breakdown by 26 food groups per country & year |
| 3 | `owid_obesity.csv` | OWID | 6,798 | 4 | 187 KB | Adult obesity prevalence (BMI ≥ 30), 1990–2022 — **not used in final output** (see §3.3) |
| 4 | `owid_life_expectancy.csv` | OWID | 21,565 | 4 | 605 KB | Life expectancy at birth, 1950–2023 |
| 5 | `who_obesity_adults.csv` | WHO GHO API | 6,568 | 6 | 326 KB | Adult obesity (%) with confidence intervals & WHO region |
| 6 | `who_underweight_children.csv` | WHO GHO API | 2,255 | 6 | 72 KB | Underweight children under 5 (%) with CIs & WHO region |
| 7 | `open_food_facts_sample.csv` | Open Food Facts API | 10,001 | 14 | 1.36 MB | Product-level nutritional data with Nutri-Score & NOVA |

**Total raw data:** ~72,484 rows across 7 files (~5.9 MB)

---

## 3. Processing Pipeline

### 3.1 Step 1 — Clean Individual Datasets

Each raw CSV undergoes the following transformations:

#### OWID Datasets (files 1, 2, 4)

| Operation | Details |
|-----------|---------|
| Rename columns | `code` → `iso3`, `daily_calories` → `calories`, `life_expectancy_0` → `life_exp` |
| Drop aggregates | Remove rows where `iso3` is null or starts with `OWID_` (e.g., `OWID_WRL`, `OWID_EUR`) |
| Cast types | `year` → `int`, numeric columns → `float` |
| Filter range | Life expectancy limited to 1960+ to align with nutrition data |

#### OWID Food Composition (file 2) — Special Handling

The raw file has 26 verbose column names like:
```
wheat__00002511__food_available_for_consumption__0664pc__kilocalories_per_day_per_capita
```

These are:
1. **Renamed** to short identifiers (e.g., `wheat`, `rice`, `meat_beef`, `dairy`)
2. **Aggregated** into 8 macro groups for the stacked area chart:

| Macro Group | Component Columns |
|-------------|-------------------|
| Cereals | wheat, rice, maize, barley, cereals_other |
| Meat | meat_beef, meat_poultry, meat_pig, meat_sheep, meat_other |
| Dairy & Eggs | dairy, eggs |
| Oils & Fats | vegetable_oils, animal_fats, oilcrops |
| Sugar & Sweeteners | sugar_sweeteners, sugar_crops |
| Fruits & Vegetables | fruit, vegetables |
| Starchy Roots & Pulses | starchy_roots, pulses, nuts |
| Other | fish_seafood, alcohol, miscellaneous |

Each macro group is stored as a new column prefixed with `grp_` (e.g., `grp_cereals`, `grp_meat`).

#### WHO Datasets (files 5–6)

| Operation | Details |
|-----------|---------|
| Rename columns | `country_code` → `iso3`, `value` → `who_obesity_pct` / `underweight_pct` |
| Preserve metadata | Keep `ci_low`, `ci_high` (confidence intervals) and `region` (WHO region) |
| Cast types | `year` → `int` |

#### Open Food Facts (file 7)

| Operation | Details |
|-----------|---------|
| Filter | Keep only rows with valid `nutriscore_grade` ∈ {a, b, c, d, e} |
| Cast numerics | `energy-kcal_100g`, `fat_100g`, `sugars_100g`, `salt_100g`, `proteins_100g`, `fiber_100g`, `saturated-fat_100g`, `carbohydrates_100g` |
| Parse categories | Extract top-level category from comma-separated `categories` string |
| Outlier removal | Drop products with energy > 900 kcal/100g |
| NOVA cast | `nova_group` → numeric |

---

### 3.2 Step 2 — Continent Mapping

Countries are assigned a continent label using a two-tier lookup:

1. **WHO Region** (preferred) — The `region` column in WHO datasets maps to continent:

   | WHO Region | Continent |
   |------------|-----------|
   | Africa | Africa |
   | Americas | Americas |
   | South-East Asia | Asia |
   | Europe | Europe |
   | Eastern Mediterranean | Asia |
   | Western Pacific | Asia |

2. **Static ISO-3 Table** (fallback) — A hardcoded dictionary of ~170 ISO-3 codes covers countries absent from WHO data (e.g., OWID-only countries).

Countries not matched by either method are labeled `"Other"`.

---

### 3.3 Step 3 — Merge into Master Tables

#### Table 1: `country_yearly`

The primary nutrition and diet analysis table, built by left-joining on `(iso3, year)`:

```
owid_calorie_supply (base)
  ← LEFT JOIN owid_food_composition
  ← LEFT JOIN owid_life_expectancy
  + continent mapping
```

> **Design decision:** OWID obesity (`owid_obesity.csv`) is intentionally excluded from this table. Both OWID and WHO provide adult obesity prevalence derived from similar underlying NCD-RisC estimates, so including both would create data redundancy. The WHO source in `country_health` is preferred because it provides age-standardized estimates with 95% confidence intervals and WHO region labels, enabling richer analysis. Dashboard views that require obesity data join to `country_health` on `(iso3, year)`.

**Used by:** Tab 1 (Choropleth, Trend Line, Stacked Area, Bar Chart) and Tab 2 (Scatter via join to `country_health`)

#### Table 2: `country_health`

WHO-specific health indicators, built by outer-joining:

```
who_obesity_adults
  ← OUTER JOIN who_underweight_children
  + continent mapping
```

**Used by:** Tab 2 (Obesity vs. Underweight scatter, Dual-Burden chart, Obesity trends)

#### Table 3: `products`

Cleaned Open Food Facts data (no merge needed — standalone product-level table).

**Used by:** Tab 3 (Nutri-Score distribution, Radar chart, NOVA breakdown, ML classifier)

---

### 3.4 Step 4 — Export

All tables are saved in two formats:

| Format | Purpose | Location |
|--------|---------|----------|
| **Parquet** (.parquet) | Fast loading in the Shiny dashboard | `data/processed/` |
| **CSV** (.csv) | Human-readable inspection & debugging | `data/processed/` |

Additionally, a `country_meta.csv` is exported containing unique `(iso3, entity, continent)` triples for reference.

---

## 4. Output Summary

| Output File | Rows | Columns | Key Columns |
|-------------|------|---------|-------------|
| `country_yearly.parquet` | 10,417 | 39 | `iso3`, `year`, `calories`, `grp_cereals`…`grp_other`, `life_exp`, `continent` |
| `country_health.parquet` | 7,777 | 10 | `iso3`, `year`, `who_obesity_pct`, `underweight_pct`, `ci_low`, `ci_high`, `continent` |
| `products.parquet` | 8,057 | 15 | `product_name`, `nutriscore_grade`, `nova_group`, `energy-kcal_100g`, `fat_100g`, `sugars_100g`, … |
| `country_meta.csv` | 192 | 3 | `iso3`, `entity`, `continent` |

---

## 5. Data Quality Notes

### Known Limitations

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **Open Food Facts — missing nutrition values** | ~60% of products lack `fat_100g`, `sugars_100g`, etc. | Dashboard charts handle `NaN` gracefully; ML classifier uses available subset |
| **Obesity data only in `country_health`** | Dashboard views needing obesity must join to `country_health` on `(iso3, year)` | Avoids redundancy; join is lightweight |
| **WHO underweight data** (~2,254 raw rows) | Limited country-year coverage | Outer join preserves all available data; NaN values handled at chart level |
| **Continent "Other" label** | Small island nations may not be in the lookup table | Acceptable — affects < 5 countries |
| **Duplicate WHO rows** | Some country-year pairs appear twice (WHO + underweight surveys) | Acceptable — grouped aggregations in charts handle duplicates |

### Data Integrity Checks

All validations passed after running `processing.py` (verified May 18, 2026):

- [x] All `iso3` codes are exactly 3 uppercase letters
- [x] No `OWID_*` aggregate rows remain in output tables
- [x] `year` column is integer type in all tables
- [x] `country_yearly` has no duplicate `(iso3, year)` pairs
- [x] Macro group columns (`grp_*`) sum approximately to total `calories` column
- [x] `country_yearly` does **not** contain `obesity_pct` — obesity is exclusively in `country_health`
- [x] `nutriscore_grade` contains only lowercase {a, b, c, d, e} — 8,057 valid products
- [x] Continent distribution covers Africa, Americas, Asia, Europe, Other

---

## 6. How to Run

```bash
# From project root
cd data-visualization-project
python data/processing.py
```

**Prerequisites:**
```
pip install pandas numpy pyarrow
```

The script creates `data/processed/` automatically and writes all output files there.

---

## 7. Next Steps

| Phase | Task | Status |
|-------|------|--------|
| **Phase 1** | Data Processing & Cleaning | ✅ Complete |
| **Phase 2** | Exploratory Data Analysis (EDA) | 🔲 Pending |
| **Phase 3** | Machine Learning Models | 🔲 Pending |
| **Phase 4** | Shiny Dashboard Development | 🔲 Pending |
| **Phase 5** | Deployment & Documentation | 🔲 Pending |

Phase 2 will produce statistical summaries, distribution plots, and correlation analyses to inform the dashboard chart designs and ML feature selection.
