"""
Exploratory Data Analysis — Global Food & Nutrition Dashboard
COMP5120 Data Visualization (Spring 2026)

Generates key statistical summaries and correlation matrices to inform
the dashboard design and machine learning models.
"""

import os
import pandas as pd
import numpy as np

# Load processed data
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
cy_path = os.path.join(DATA_DIR, "country_yearly.parquet")
ch_path = os.path.join(DATA_DIR, "country_health.parquet")
p_path = os.path.join(DATA_DIR, "products.parquet")

cy = pd.read_parquet(cy_path)
ch = pd.read_parquet(ch_path)
p = pd.read_parquet(p_path)

print("============================================================")
print("🔍 EXPLORATORY DATA ANALYSIS (EDA)")
print("============================================================\n")

# --- Q1: Dietary Patterns & Calorie Supply ---
print("--- Q1: Country-Level Diet & Caloric Patterns ---")
print(f"Total Country-Year records: {len(cy)}")
print(f"Unique countries covered: {cy['iso3'].nunique()}")
print(f"Years range: {cy['year'].min()} - {cy['year'].max()}")
print("\nGlobal average calorie supply by decade:")
cy['decade'] = (cy['year'] // 10) * 10
avg_cal_decade = cy.groupby('decade')['calories'].mean().reset_index()
print(avg_cal_decade.to_string(index=False))

print("\nDiet composition global average in 2020 (kcal/day):")
cy_2020 = cy[cy['year'] == 2020]
macro_cols = [c for c in cy.columns if c.startswith('grp_')]
diet_2020 = cy_2020[macro_cols].mean().sort_values(ascending=False).reset_index()
diet_2020.columns = ['Macro Group', 'Kcal/day']
diet_2020['Percentage'] = (diet_2020['Kcal/day'] / cy_2020['calories'].mean()) * 100
print(diet_2020.to_string(index=False))

# --- Q2: Diets vs. Health Outcomes ---
print("\n--- Q2: Diet vs. Health Outcomes ---")
# Merge cy and ch for Q2 correlations
ch_latest = ch.groupby('iso3').last().reset_index() # latest health data per country
cy_latest = cy.groupby('iso3').last().reset_index() # latest dietary data per country
merged = pd.merge(cy_latest, ch_latest, on='iso3', suffixes=('_diet', '_health'))

print(f"Merged Country Health & Diet records: {len(merged)}")
print("\nCorrelation matrix between calorie supply, diet groups, and health outcomes:")
corr_cols = ['calories', 'grp_cereals', 'grp_meat', 'grp_dairy_eggs', 'grp_oils_fats', 
             'grp_sugar_sweeteners', 'grp_fruits_vegetables', 'life_exp', 'who_obesity_pct', 'underweight_pct']
corr_matrix = merged[corr_cols].corr()
print(corr_matrix[['life_exp', 'who_obesity_pct', 'underweight_pct']].round(3))

# --- Q3: Product-Level Analysis ---
print("\n--- Q3: Product-Level Nutritional Quality ---")
print(f"Total products: {len(p)}")
print("\nNutri-Score Grade distribution:")
print(p['nutriscore_grade'].value_counts().sort_index())

print("\nNOVA Processing Group distribution:")
print(p['nova_group'].value_counts().sort_index())

print("\nMean sugars, fat, and energy by Nutri-Score grade:")
nutri_means = p.groupby('nutriscore_grade')[['energy-kcal_100g', 'sugars_100g', 'fat_100g', 'proteins_100g', 'fiber_100g', 'salt_100g']].mean()
print(nutri_means.round(2))

print("\nMean sugars, fat, and energy by NOVA group:")
nova_means = p.groupby('nova_group')[['energy-kcal_100g', 'sugars_100g', 'fat_100g', 'salt_100g']].mean()
print(nova_means.round(2))

print("\nNutri-Score vs. NOVA group cross-tabulation:")
crosstab = pd.crosstab(p['nutriscore_grade'], p['nova_group'], normalize='columns') * 100
print(crosstab.round(1))
