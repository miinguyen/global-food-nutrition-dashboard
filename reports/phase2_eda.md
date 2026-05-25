# Phase 2 — Exploratory Data Analysis (EDA) Report

**Project:** Global Food & Nutrition Dashboard  
**Course:** COMP5120 — Data Visualization (Spring 2026)  
**Date:** May 25, 2026  
**Script:** [`notebooks/eda.py`](../notebooks/eda.py)

---

## 1. Executive Summary

This report documents our key findings from the Exploratory Data Analysis (EDA) of the country-level and product-level datasets. The objective is to understand global eating habits, relate diet composition to clinical health outcomes, and zoom into individual consumer products to assess nutritional quality. These findings directly shape our visual layouts, chart selections, and features used for machine learning.

### Key Insights

1. **Global Calorie Expansion:** Daily per-capita calorie supply has expanded significantly over the last six decades, rising from an average of ~2,320 kcal in the 1960s to ~2,948 kcal in the 2020s (+27%).
2. **The Global Diet Breakdown (2020):** Cereals remain the bedrock of the human diet, supplying **35.3%** of all daily calories. Oils and fats have climbed to a substantial **16.0%**, followed by sugars and sweeteners at **9.6%**. High-protein categories like meat (8.0%) and dairy/eggs (7.6%) make up smaller portions.
3. **Strong Diet-Health Connections:** Calorie supply is strongly correlated with life expectancy ($r = 0.642$) and adult obesity ($r = 0.317$), while showing a strong inverse relationship with child underweight rates ($r = -0.620$).
4. **Meat and Sugar Drive Obesity:** Per-capita meat intake ($r = 0.556$) and sugar/sweetener intake ($r = 0.462$) exhibit the strongest positive correlations with adult obesity rates, reflecting the impacts of Westernization on global diet profiles.
5. **Ultra-Processing is Ubiquitous:** Over **58.5%** of individual products in our Open Food Facts dataset belong to **NOVA Group 4 (Ultra-processed)**. 
6. **NOVA and Nutri-Score Alignment:** Unprocessed foods (NOVA Group 1) are highly likely to receive an **A grade (70.1%)**, while ultra-processed foods (NOVA Group 4) predominantly score **D or E (60.1% combined)**. Nutri-Score E products have 2.6x higher calorie counts, 6.1x higher sugars, and 10.5x higher salt compared to Nutri-Score A products.

---

## 2. Dietary Trends (Q1: What does the world eat?)

We analyzed historical trends from 1961 to 2023 across 192 countries using the `country_yearly` dataset.

### 2.1 Calorie Supply Over Time
Global average daily per-capita calorie supply has increased steadily by decade:
- **1960s:** 2,319.8 kcal/day
- **1980s:** 2,545.7 kcal/day
- **2000s:** 2,713.7 kcal/day
- **2020s:** 2,947.6 kcal/day

This reflects a global agricultural surplus and increased access to food, but also represents a primary driver of the global obesity epidemic.

### 2.2 Caloric Composition (2020 Global Average)
Breaking down the daily calorie supply by macro groups in 2020 reveals the structure of global eating habits:

| Macro Group | Kcal/day | Caloric Share (%) | Description |
|-------------|----------|-------------------|-------------|
| **Cereals** | 1,032.8 | 35.3% | Wheat, rice, maize, barley, etc. (primary energy source) |
| **Oils & Fats** | 468.7 | 16.0% | Vegetable oils, animal fats, and oil crops |
| **Sugar & Sweeteners**| 282.6 | 9.6% | Refined sugars and sugar crops |
| **Starchy Roots/Pulses**| 254.3 | 8.7% | Potatoes, cassava, beans, lentils, nuts |
| **Meat** | 234.9 | 8.0% | Beef, pork, poultry, sheep, etc. |
| **Dairy & Eggs** | 222.2 | 7.6% | Milk, butter, cheese, eggs |
| **Fruits & Vegetables**| 195.0 | 6.7% | Fresh and processed fruits and vegetables |
| **Other** | 133.0 | 4.5% | Seafood, alcohol, and miscellaneous items |
| **Total** | **2,923.5** | **100%** | Average total across tracked macro groups |

---

## 3. Diet vs. Health Outcomes (Q2: How healthy is it?)

Merging the latest dietary data with country-level health metrics from the WHO (`country_health`) provides 187 paired country records. 

### 3.1 Correlation Matrix

Below is the Pearson correlation coefficient ($r$) between dietary inputs and clinical outcomes:

| Diet / Supply Variable | Life Expectancy | Adult Obesity Rate | Child Underweight Rate |
|------------------------|-----------------|--------------------|------------------------|
| **Total Calorie Supply**| **0.642** | **0.317** | **-0.620** |
| **Cereals** | 0.125 | -0.070 | -0.077 |
| **Meat** | **0.493** | **0.556** | **-0.600** |
| **Dairy & Eggs** | **0.592** | 0.176 | **-0.517** |
| **Oils & Fats** | 0.371 | 0.339 | -0.373 |
| **Sugar & Sweeteners** | **0.523** | **0.462** | **-0.492** |
| **Fruits & Vegetables**| 0.304 | 0.185 | -0.349 |

### 3.2 Visual & Analytical Implications
- **Calorie & Nutrient Abundance vs. Malnutrition:** Higher overall calorie supply is strongly protective against childhood underweight prevalence ($r = -0.620$), but increases obesity risk. Protein and fat sources (Meat, Dairy, Sugar) exhibit strong negative correlations with underweight.
- **Obesity Drivers:** Per-capita meat consumption ($r = 0.556$) and refined sugars ($r = 0.462$) are the primary correlates of obesity. This suggests that the transition toward meat- and sugar-dense diets (the "nutrition transition") is a powerful driver of clinical health outcomes.
- **Life Expectancy:** Life expectancy is most strongly linked to dairy and egg intake ($r = 0.592$), calorie supply ($r = 0.642$), and sugar/sweetener intake ($r = 0.523$, likely acting as a proxy for country-level wealth and overall food security).

---

## 4. Product-Level Nutritional Quality (Q3: What's really in our food?)

We explored the product-level sample of **8,057 products** from Open Food Facts containing valid Nutri-Score grades (A–E) and NOVA groups (1–4).

### 4.1 Distributions
- **Nutri-Score Grades:** A (1,807, 22.4%), B (887, 11.0%), C (1,571, 19.5%), D (1,883, 23.4%), E (1,909, 23.7%). The grades are relatively balanced, which provides an excellent foundation for training our classification model.
- **NOVA Processing Groups:** 1 - Unprocessed (1,567, 19.5%), 2 - Processed Ingredients (245, 3.0%), 3 - Processed (1,527, 19.0%), 4 - Ultra-processed (4,718, **58.5%**). A massive share of products is ultra-processed, reflecting the profile of modern supermarket items.

### 4.2 Nutrient Profiles by Nutri-Score Grade (per 100g)

| Grade | Energy (kcal) | Sugars (g) | Fat (g) | Proteins (g) | Fiber (g) | Salt (g) |
|-------|--------------|------------|---------|--------------|-----------|----------|
| **A** | 154.6 | 4.74 | 3.86 | 6.27 | 3.86 | 0.24 |
| **B** | 147.2 | 5.68 | 4.09 | 4.54 | 1.44 | 0.31 |
| **C** | 224.8 | 6.71 | 7.64 | 6.26 | 2.46 | 0.71 |
| **D** | 317.1 | 14.61 | 14.39 | 5.41 | 3.00 | 1.02 |
| **E** | 406.8 | 29.13 | 21.05 | 5.56 | 2.59 | 2.54 |

This confirms that the Nutri-Score algorithm heavily penalizes high energy, sugars, fat, and salt, while rewarding fiber and protein. Nutri-Score E products contain **6.1 times more sugar** and **10.5 times more salt** than A-grade products.

### 4.3 Nutri-Score vs. NOVA Processing Cross-Tabulation (%)
How does mechanical/chemical processing relate to overall nutritional quality? The table below displays the percentage breakdown of Nutri-Score grades *within each NOVA group*:

| Nutri-Score | NOVA 1 (Unprocessed) | NOVA 2 (Processed Ingred.) | NOVA 3 (Processed) | NOVA 4 (Ultra-processed) |
|-------------|----------------------|----------------------------|--------------------|--------------------------|
| **A** | **70.1%** | 3.7% | 23.4% | 7.2% |
| **B** | 13.2% | 17.1% | 13.2% | 9.3% |
| **C** | 7.9% | 23.3% | 18.7% | 23.4% |
| **D** | 5.4% | 15.9% | **25.5%** | **29.0%** |
| **E** | 3.3% | **40.0%** | 19.2% | **31.1%** |
| **Total** | **100%** | **100%** | **100%** | **100%** |

### 4.4 Major Discoveries
- **NOVA 1 is highly nutritious:** 83.3% of unprocessed products receive an A or B grade.
- **NOVA 2 (Oils, Sugars, Salts) has low nutritional scores:** 40% receive an E, and 15.9% receive a D. This is logical because these are concentrated culinary ingredients.
- **NOVA 4 (Ultra-processed) represents a nutritional hazard:** Over **60.1%** of ultra-processed products are graded D or E, with only 7.2% achieving an A grade. This strong correlation validates the inclusion of both frameworks in our dashboard to help users evaluate food quality.

---

## 5. Conclusions & Next Steps

The EDA findings establish a robust analytical foundation:
1. **Interactive Layouts:** The strong correlations between diet groups (Meat, Dairy, Sugar) and obesity/life expectancy justify our layout for Tab 2, linking nutritional composition directly to WHO outcomes.
2. **NOVA and Nutri-Score Linked Views:** The alignment between ultra-processing (NOVA 4) and poor nutritional grades (D/E) will be highlighted in Tab 3 through a linked stacked bar chart (Chart 9) and donut chart (Chart 11).
3. **ML Features Selection:**
   - **Obesity Regressor:** We will select `calories`, `grp_meat`, `grp_sugar_sweeteners`, `grp_oils_fats`, and `grp_dairy_eggs` as our key inputs to predict adult obesity rates.
   - **Nutri-Score Classifier:** We will leverage energy, sugars, fat, saturated fat, sodium (salt), proteins, and fiber to train a highly accurate classifier.
   - **Dietary Profiling:** Using the 8 macro dietary group percentages per country as inputs to PCA and K-Means will cleanly isolate distinct global diet clusters.
