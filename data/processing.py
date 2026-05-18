"""
Data Processing & Cleaning — Global Food & Nutrition Dashboard
COMP5120 Data Visualization (Spring 2026)

Reads raw CSVs from data/, cleans and merges them, and outputs
processed tables to data/processed/.

Usage:
    python data/processing.py
"""

import os
import pandas as pd
import numpy as np

# ============================================================
# Paths
# ============================================================

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ============================================================
# Continent Mapping (ISO-3 → Continent)
# ============================================================

# WHO region → continent mapping
WHO_REGION_TO_CONTINENT = {
    "Africa": "Africa",
    "Americas": "Americas",
    "South-East Asia": "Asia",
    "Europe": "Europe",
    "Eastern Mediterranean": "Asia",
    "Western Pacific": "Asia",
}

# Static lookup for countries not in WHO data
# (covers most OWID countries)
ISO3_TO_CONTINENT = {
    # Africa
    "DZA": "Africa", "AGO": "Africa", "BEN": "Africa", "BWA": "Africa",
    "BFA": "Africa", "BDI": "Africa", "CPV": "Africa", "CMR": "Africa",
    "CAF": "Africa", "TCD": "Africa", "COM": "Africa", "COG": "Africa",
    "COD": "Africa", "CIV": "Africa", "DJI": "Africa", "EGY": "Africa",
    "GNQ": "Africa", "ERI": "Africa", "SWZ": "Africa", "ETH": "Africa",
    "GAB": "Africa", "GMB": "Africa", "GHA": "Africa", "GIN": "Africa",
    "GNB": "Africa", "KEN": "Africa", "LSO": "Africa", "LBR": "Africa",
    "LBY": "Africa", "MDG": "Africa", "MWI": "Africa", "MLI": "Africa",
    "MRT": "Africa", "MUS": "Africa", "MAR": "Africa", "MOZ": "Africa",
    "NAM": "Africa", "NER": "Africa", "NGA": "Africa", "RWA": "Africa",
    "STP": "Africa", "SEN": "Africa", "SYC": "Africa", "SLE": "Africa",
    "SOM": "Africa", "ZAF": "Africa", "SSD": "Africa", "SDN": "Africa",
    "TZA": "Africa", "TGO": "Africa", "TUN": "Africa", "UGA": "Africa",
    "ZMB": "Africa", "ZWE": "Africa",
    # Americas
    "ATG": "Americas", "ARG": "Americas", "BHS": "Americas", "BRB": "Americas",
    "BLZ": "Americas", "BOL": "Americas", "BRA": "Americas", "CAN": "Americas",
    "CHL": "Americas", "COL": "Americas", "CRI": "Americas", "CUB": "Americas",
    "DMA": "Americas", "DOM": "Americas", "ECU": "Americas", "SLV": "Americas",
    "GRD": "Americas", "GTM": "Americas", "GUY": "Americas", "HTI": "Americas",
    "HND": "Americas", "JAM": "Americas", "MEX": "Americas", "NIC": "Americas",
    "PAN": "Americas", "PRY": "Americas", "PER": "Americas", "KNA": "Americas",
    "LCA": "Americas", "VCT": "Americas", "SUR": "Americas", "TTO": "Americas",
    "USA": "Americas", "URY": "Americas", "VEN": "Americas",
    # Asia
    "AFG": "Asia", "ARM": "Asia", "AZE": "Asia", "BHR": "Asia",
    "BGD": "Asia", "BTN": "Asia", "BRN": "Asia", "KHM": "Asia",
    "CHN": "Asia", "CYP": "Asia", "GEO": "Asia", "IND": "Asia",
    "IDN": "Asia", "IRN": "Asia", "IRQ": "Asia", "ISR": "Asia",
    "JPN": "Asia", "JOR": "Asia", "KAZ": "Asia", "KWT": "Asia",
    "KGZ": "Asia", "LAO": "Asia", "LBN": "Asia", "MYS": "Asia",
    "MDV": "Asia", "MNG": "Asia", "MMR": "Asia", "NPL": "Asia",
    "OMN": "Asia", "PAK": "Asia", "PSE": "Asia", "PHL": "Asia",
    "QAT": "Asia", "SAU": "Asia", "SGP": "Asia", "KOR": "Asia",
    "LKA": "Asia", "SYR": "Asia", "TWN": "Asia", "TJK": "Asia",
    "THA": "Asia", "TLS": "Asia", "TUR": "Asia", "TKM": "Asia",
    "ARE": "Asia", "UZB": "Asia", "VNM": "Asia", "YEM": "Asia",
    "PRK": "Asia",
    # Europe
    "ALB": "Europe", "AND": "Europe", "AUT": "Europe", "BLR": "Europe",
    "BEL": "Europe", "BIH": "Europe", "BGR": "Europe", "HRV": "Europe",
    "CZE": "Europe", "DNK": "Europe", "EST": "Europe", "FIN": "Europe",
    "FRA": "Europe", "DEU": "Europe", "GRC": "Europe", "HUN": "Europe",
    "ISL": "Europe", "IRL": "Europe", "ITA": "Europe", "LVA": "Europe",
    "LTU": "Europe", "LUX": "Europe", "MLT": "Europe", "MDA": "Europe",
    "MNE": "Europe", "NLD": "Europe", "MKD": "Europe", "NOR": "Europe",
    "POL": "Europe", "PRT": "Europe", "ROU": "Europe", "RUS": "Europe",
    "SRB": "Europe", "SVK": "Europe", "SVN": "Europe", "ESP": "Europe",
    "SWE": "Europe", "CHE": "Europe", "UKR": "Europe", "GBR": "Europe",
    # Oceania
    "AUS": "Oceania", "FJI": "Oceania", "KIR": "Oceania", "MHL": "Oceania",
    "FSM": "Oceania", "NRU": "Oceania", "NZL": "Oceania", "PLW": "Oceania",
    "PNG": "Oceania", "WSM": "Oceania", "SLB": "Oceania", "TON": "Oceania",
    "TUV": "Oceania", "VUT": "Oceania",
}


def get_continent(iso3, who_lookup):
    """Look up continent: try WHO region first, then static table."""
    if iso3 in who_lookup:
        region = who_lookup[iso3]
        return WHO_REGION_TO_CONTINENT.get(region, "Other")
    return ISO3_TO_CONTINENT.get(iso3, "Other")


# ============================================================
# Food Composition Column Mapping
# ============================================================

# Map verbose OWID column names → short readable names
# Group into 8 macro categories for stacked area chart
FOOD_COL_MAP = {
    # Cereals
    "wheat__00002511": "wheat",
    "rice__00002807": "rice",
    "maize__00002514": "maize",
    "barley__00002513": "barley",
    "cereals__other__00002520": "cereals_other",
    # Meat
    "meat__beef_and_buffalo__00002731": "meat_beef",
    "meat__poultry__00002734": "meat_poultry",
    "meat__pig__00002733": "meat_pig",
    "meat__sheep_and_goat__00002732": "meat_sheep",
    "meat__other__00002735": "meat_other",
    # Dairy & Eggs
    "milk__00002948": "dairy",
    "eggs__00002949": "eggs",
    # Oils & Fats
    "vegetable_oils__00002914": "vegetable_oils",
    "animal_fats_group__00002946": "animal_fats",
    "oilcrops__00002913": "oilcrops",
    # Sugar & Sweeteners
    "sugar__and__sweeteners__00002909": "sugar_sweeteners",
    "sugar_crops__00002908": "sugar_crops",
    # Fruits & Vegetables
    "fruit__00002919": "fruit",
    "vegetables__00002918": "vegetables",
    # Starchy Roots & Pulses
    "starchy_roots__00002907": "starchy_roots",
    "pulses__00002911": "pulses",
    "nuts__00002551": "nuts",
    # Other
    "fish_and_seafood__00002960": "fish_seafood",
    "alcoholic_beverages__00002924": "alcohol",
    "miscellaneous_group__00002928": "miscellaneous",
}

# Macro groups for aggregation
MACRO_GROUPS = {
    "Cereals": ["wheat", "rice", "maize", "barley", "cereals_other"],
    "Meat": ["meat_beef", "meat_poultry", "meat_pig", "meat_sheep", "meat_other"],
    "Dairy & Eggs": ["dairy", "eggs"],
    "Oils & Fats": ["vegetable_oils", "animal_fats", "oilcrops"],
    "Sugar & Sweeteners": ["sugar_sweeteners", "sugar_crops"],
    "Fruits & Vegetables": ["fruit", "vegetables"],
    "Starchy Roots & Pulses": ["starchy_roots", "pulses", "nuts"],
    "Other": ["fish_seafood", "alcohol", "miscellaneous"],
}


# ============================================================
# Step 1: Clean Individual Datasets
# ============================================================

def clean_calorie_supply():
    """Clean OWID calorie supply data."""
    print("  📦 Cleaning owid_calorie_supply...")
    df = pd.read_csv(os.path.join(DATA_DIR, "owid_calorie_supply.csv"))
    df = df.rename(columns={"code": "iso3", "daily_calories": "calories"})
    # Drop aggregates (no ISO code)
    df = df.dropna(subset=["iso3"])
    df = df[~df["iso3"].str.startswith("OWID_")]
    df = df.dropna(subset=["calories"])
    df["year"] = df["year"].astype(int)
    print(f"    → {len(df)} rows, {df['iso3'].nunique()} countries")
    return df[["entity", "iso3", "year", "calories"]]


def clean_food_composition():
    """Clean OWID food composition data."""
    print("  📦 Cleaning owid_food_composition...")
    df = pd.read_csv(os.path.join(DATA_DIR, "owid_food_composition.csv"))
    df = df.rename(columns={"code": "iso3"})
    df = df.dropna(subset=["iso3"])
    df = df[~df["iso3"].str.startswith("OWID_")]
    df["year"] = df["year"].astype(int)

    # Rename verbose columns
    rename_map = {"entity": "entity", "iso3": "iso3", "year": "year"}
    for col in df.columns:
        if col in ("entity", "code", "iso3", "year"):
            continue
        matched = False
        for prefix, short in FOOD_COL_MAP.items():
            if col.startswith(prefix):
                rename_map[col] = short
                matched = True
                break
        if not matched:
            rename_map[col] = col  # keep as-is

    df = df.rename(columns=rename_map)
    # Keep only the columns we mapped
    keep = ["entity", "iso3", "year"] + list(FOOD_COL_MAP.values())
    keep = [c for c in keep if c in df.columns]
    df = df[keep].fillna(0)

    # Create macro group totals
    for group_name, cols in MACRO_GROUPS.items():
        valid_cols = [c for c in cols if c in df.columns]
        col_key = group_name.lower().replace(" & ", "_").replace(" ", "_")
        df[f"grp_{col_key}"] = df[valid_cols].sum(axis=1)

    print(f"    → {len(df)} rows, {df['iso3'].nunique()} countries, {len(df.columns)} columns")
    return df


def clean_obesity():
    """Clean OWID obesity data."""
    print("  📦 Cleaning owid_obesity...")
    df = pd.read_csv(os.path.join(DATA_DIR, "owid_obesity.csv"))

    # Identify the obesity column (long name)
    obesity_col = [c for c in df.columns if "obesity" in c.lower() or "bmi" in c.lower()]
    if obesity_col:
        df = df.rename(columns={obesity_col[0]: "obesity_pct"})
    else:
        df = df.rename(columns={df.columns[-1]: "obesity_pct"})

    df = df.rename(columns={"code": "iso3"})
    df = df.dropna(subset=["iso3", "obesity_pct"])
    df = df[~df["iso3"].str.startswith("OWID_")]
    df["year"] = df["year"].astype(int)
    print(f"    → {len(df)} rows, {df['iso3'].nunique()} countries, years {df['year'].min()}-{df['year'].max()}")
    return df[["entity", "iso3", "year", "obesity_pct"]]


def clean_life_expectancy():
    """Clean OWID life expectancy data."""
    print("  📦 Cleaning owid_life_expectancy...")
    df = pd.read_csv(os.path.join(DATA_DIR, "owid_life_expectancy.csv"))
    df = df.rename(columns={"code": "iso3", "life_expectancy_0": "life_exp"})
    df = df.dropna(subset=["iso3", "life_exp"])
    df = df[~df["iso3"].str.startswith("OWID_")]
    # Keep 1960+ to align with other datasets
    df["year"] = df["year"].astype(int)
    df = df[df["year"] >= 1960]
    print(f"    → {len(df)} rows, {df['iso3'].nunique()} countries")
    return df[["entity", "iso3", "year", "life_exp"]]


def clean_who_obesity():
    """Clean WHO adult obesity data."""
    print("  📦 Cleaning who_obesity_adults...")
    df = pd.read_csv(os.path.join(DATA_DIR, "who_obesity_adults.csv"))
    df = df.rename(columns={"country_code": "iso3", "value": "who_obesity_pct"})
    df = df.dropna(subset=["iso3", "who_obesity_pct"])
    df["year"] = df["year"].astype(int)
    print(f"    → {len(df)} rows, {df['iso3'].nunique()} countries")
    return df


def clean_who_underweight():
    """Clean WHO underweight children data."""
    print("  📦 Cleaning who_underweight_children...")
    df = pd.read_csv(os.path.join(DATA_DIR, "who_underweight_children.csv"))
    df = df.rename(columns={"country_code": "iso3", "value": "underweight_pct"})
    df = df.dropna(subset=["iso3", "underweight_pct"])
    df["year"] = df["year"].astype(int)
    print(f"    → {len(df)} rows, {df['iso3'].nunique()} countries")
    return df


def clean_food_facts():
    """Clean Open Food Facts product data."""
    print("  📦 Cleaning open_food_facts_sample...")
    df = pd.read_csv(os.path.join(DATA_DIR, "open_food_facts_sample.csv"))

    # Drop rows without nutriscore or nova
    df = df.dropna(subset=["nutriscore_grade"])
    df = df[df["nutriscore_grade"].isin(["a", "b", "c", "d", "e"])]

    # Cast numeric columns
    num_cols = ["energy-kcal_100g", "fat_100g", "saturated-fat_100g",
                "sugars_100g", "salt_100g", "proteins_100g",
                "fiber_100g", "carbohydrates_100g"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Parse top-level category from the comma-separated categories string
    if "categories" in df.columns:
        df["top_category"] = (
            df["categories"]
            .fillna("Unknown")
            .str.split(",")
            .str[0]
            .str.strip()
            .str.title()
        )
    else:
        df["top_category"] = "Unknown"

    # Cast nova_group
    if "nova_group" in df.columns:
        df["nova_group"] = pd.to_numeric(df["nova_group"], errors="coerce")

    # Drop extreme outliers
    if "energy-kcal_100g" in df.columns:
        df = df[(df["energy-kcal_100g"].isna()) | (df["energy-kcal_100g"] <= 900)]

    print(f"    → {len(df)} products, {df['nutriscore_grade'].value_counts().to_dict()}")
    return df


# ============================================================
# Step 2: Merge into Master Tables
# ============================================================

def merge_country_yearly(cal, comp, life_exp, continent_lookup):
    """Merge country-level datasets into one master table.

    Note: Obesity data is intentionally excluded from this table to avoid
    redundancy with the WHO-sourced obesity in ``country_health``.
    """
    print("\n  🔗 Merging country_yearly...")

    # Start with calorie supply (most complete)
    master = cal.copy()

    # Merge food composition (drop entity col to avoid duplicates)
    comp_cols = [c for c in comp.columns if c not in ("entity",)]
    master = master.merge(comp_cols and comp[comp_cols], on=["iso3", "year"], how="left")

    # Merge life expectancy
    life_slim = life_exp[["iso3", "year", "life_exp"]]
    master = master.merge(life_slim, on=["iso3", "year"], how="left")

    # Add continent
    master["continent"] = master["iso3"].map(
        lambda x: get_continent(x, continent_lookup)
    )

    print(f"    → {len(master)} rows, {master['iso3'].nunique()} countries, {len(master.columns)} columns")
    print(f"    → Continent distribution: {master['continent'].value_counts().to_dict()}")
    return master


def merge_country_health(who_obesity, who_underweight, continent_lookup):
    """Merge WHO health datasets."""
    print("\n  🔗 Merging country_health...")

    master = who_obesity.merge(
        who_underweight[["iso3", "year", "underweight_pct", "ci_low", "ci_high"]],
        on=["iso3", "year"],
        how="outer",
        suffixes=("_obesity", "_underweight"),
    )

    # Add continent from WHO region or static lookup
    if "region" in master.columns:
        master["continent"] = master.apply(
            lambda r: WHO_REGION_TO_CONTINENT.get(r.get("region", ""), "Other")
            if pd.notna(r.get("region")) else get_continent(r["iso3"], {}),
            axis=1,
        )
    else:
        master["continent"] = master["iso3"].map(
            lambda x: get_continent(x, {})
        )

    print(f"    → {len(master)} rows, {master['iso3'].nunique()} countries")
    return master


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("🔧 Phase 1 — Data Processing & Cleaning")
    print("=" * 60)

    # --- Step 1: Clean individual datasets ---
    print("\n📋 Step 1: Cleaning individual datasets...")
    print("-" * 40)

    cal = clean_calorie_supply()
    comp = clean_food_composition()
    life_exp = clean_life_expectancy()
    who_obesity = clean_who_obesity()
    who_underweight = clean_who_underweight()
    products = clean_food_facts()

    # --- Build continent lookup from WHO data ---
    continent_lookup = {}
    if "region" in who_obesity.columns:
        for _, row in who_obesity[["iso3", "region"]].drop_duplicates().iterrows():
            if pd.notna(row["region"]):
                continent_lookup[row["iso3"]] = row["region"]

    # --- Step 2: Merge ---
    print("\n📋 Step 2: Merging into master tables...")
    print("-" * 40)

    country_yearly = merge_country_yearly(cal, comp, life_exp, continent_lookup)
    country_health = merge_country_health(who_obesity, who_underweight, continent_lookup)

    # --- Step 3: Save ---
    print("\n📋 Step 3: Saving processed tables...")
    print("-" * 40)

    # Save as parquet
    cy_path = os.path.join(PROCESSED_DIR, "country_yearly.parquet")
    country_yearly.to_parquet(cy_path, index=False)
    print(f"  💾 {cy_path} ({len(country_yearly)} rows)")

    ch_path = os.path.join(PROCESSED_DIR, "country_health.parquet")
    country_health.to_parquet(ch_path, index=False)
    print(f"  💾 {ch_path} ({len(country_health)} rows)")

    pr_path = os.path.join(PROCESSED_DIR, "products.parquet")
    products.to_parquet(pr_path, index=False)
    print(f"  💾 {pr_path} ({len(products)} rows)")

    # Also save CSV versions for easy inspection
    country_yearly.to_csv(os.path.join(PROCESSED_DIR, "country_yearly.csv"), index=False)
    country_health.to_csv(os.path.join(PROCESSED_DIR, "country_health.csv"), index=False)
    products.to_csv(os.path.join(PROCESSED_DIR, "products.csv"), index=False)

    # Save country metadata
    meta = country_yearly[["iso3", "entity", "continent"]].drop_duplicates()
    meta.to_csv(os.path.join(PROCESSED_DIR, "country_meta.csv"), index=False)
    print(f"  💾 country_meta.csv ({len(meta)} countries)")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("✅ Phase 1 Complete!")
    print("=" * 60)
    print(f"  country_yearly : {country_yearly.shape}")
    print(f"  country_health : {country_health.shape}")
    print(f"  products       : {products.shape}")
    print(f"\n  Files saved to: {PROCESSED_DIR}/")


if __name__ == "__main__":
    main()
