"""
Data Collection Script — Global Food & Nutrition Dashboard
COMP5120 Data Visualization (Spring 2026)

Downloads datasets from:
  1. Our World in Data (OWID) — Calorie supply, food supply composition, obesity
  2. WHO Global Health Observatory (GHO) — Obesity & overweight prevalence
  3. Open Food Facts — Product-level nutrition (Nutri-Score, NOVA)

Usage:
    python data/collect_data.py
"""

import os
import io
import requests
import pandas as pd

# ============================================================
# Configuration
# ============================================================

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

DATASETS = {
    # --- OWID: Country-Level ---
    "owid_calorie_supply": {
        "url": "https://ourworldindata.org/grapher/daily-per-capita-caloric-supply.csv?v=1&csvType=full&useColumnShortNames=true",
        "filename": "owid_calorie_supply.csv",
        "description": "Daily calorie supply per person by country (1961–2023)",
    },
    "owid_obesity": {
        "url": "https://ourworldindata.org/grapher/share-of-adults-defined-as-obese.csv?v=1&csvType=full&useColumnShortNames=true",
        "filename": "owid_obesity.csv",
        "description": "Share of adults who are obese (BMI ≥ 30) by country",
    },
    "owid_food_supply_composition": {
        "url": "https://ourworldindata.org/grapher/dietary-composition-by-country.csv?v=1&csvType=full&useColumnShortNames=true",
        "filename": "owid_food_composition.csv",
        "description": "Dietary composition by food group and country",
    },
    "owid_life_expectancy": {
        "url": "https://ourworldindata.org/grapher/life-expectancy.csv?v=1&csvType=full&useColumnShortNames=true",
        "filename": "owid_life_expectancy.csv",
        "description": "Life expectancy at birth by country",
    },
    # --- WHO GHO: Health Outcomes ---
    "who_obesity_adults": {
        "url": "https://ghoapi.azureedge.net/api/NCD_BMI_30A?$filter=Dim1 eq 'BTSX'",
        "filename": "who_obesity_adults.csv",
        "description": "WHO: Prevalence of obesity among adults (BMI ≥ 30), both sexes",
        "type": "who_api",
    },
    "who_underweight_children": {
        "url": "https://ghoapi.azureedge.net/api/NUTRITION_WA_2?$filter=Dim1 eq 'BTSX'",
        "filename": "who_underweight_children.csv",
        "description": "WHO: Prevalence of underweight among children under 5",
        "type": "who_api",
    },
}

# Open Food Facts — filtered via Advanced Search API (manageable size)
OFF_CONFIG = {
    "url": "https://world.openfoodfacts.org/cgi/search.pl",
    "filename": "open_food_facts_sample.csv",
    "description": "Open Food Facts — 10,000 products with Nutri-Score and NOVA",
}


# ============================================================
# Download Functions
# ============================================================


def download_csv(name: str, url: str, filename: str, description: str, **kwargs):
    """Download a CSV file from a direct URL."""
    filepath = os.path.join(DATA_DIR, filename)

    if os.path.exists(filepath):
        print(f"  ⏭️  {name}: Already exists, skipping. Delete to re-download.")
        return True

    print(f"  ⬇️  {name}: {description}")
    print(f"      URL: {url[:80]}...")

    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        # Save raw content
        with open(filepath, "wb") as f:
            f.write(response.content)

        # Quick validation
        df = pd.read_csv(filepath, nrows=5)
        print(f"      ✅ Saved: {filename} ({len(df.columns)} columns)")
        return True

    except Exception as e:
        print(f"      ❌ Failed: {e}")
        return False


def download_who_api(name: str, url: str, filename: str, description: str, **kwargs):
    """Download data from the WHO GHO OData API."""
    filepath = os.path.join(DATA_DIR, filename)

    if os.path.exists(filepath):
        print(f"  ⏭️  {name}: Already exists, skipping.")
        return True

    print(f"  ⬇️  {name}: {description}")

    try:
        response = requests.get(url, timeout=120, headers={"Accept": "application/json"})
        response.raise_for_status()
        data = response.json()

        if "value" not in data:
            print(f"      ❌ Unexpected API response format")
            return False

        df = pd.DataFrame(data["value"])

        # Keep useful columns
        keep_cols = [
            c for c in df.columns
            if c in [
                "SpatialDim", "TimeDim", "Dim1", "NumericValue",
                "Low", "High", "SpatialDimType", "Value",
            ]
        ]
        if keep_cols:
            df = df[keep_cols]

        df.to_csv(filepath, index=False)
        print(f"      ✅ Saved: {filename} ({len(df)} rows, {len(df.columns)} columns)")
        return True

    except Exception as e:
        print(f"      ❌ Failed: {e}")
        return False


def download_open_food_facts():
    """
    Download a filtered sample from Open Food Facts via Advanced Search API.
    We request 10,000 products that have both nutriscore and nova data.
    """
    filepath = os.path.join(DATA_DIR, OFF_CONFIG["filename"])

    if os.path.exists(filepath):
        print(f"  ⏭️  open_food_facts: Already exists, skipping.")
        return True

    print(f"  ⬇️  open_food_facts: {OFF_CONFIG['description']}")

    all_products = []
    page_size = 1000
    max_pages = 10  # 10 pages × 1000 = 10,000 products

    for page in range(1, max_pages + 1):
        print(f"      Fetching page {page}/{max_pages}...", end=" ")

        params = {
            "action": "process",
            "tagtype_0": "nutrition_grades",
            "tag_contains_0": "contains",
            "tag_0": "",
            "tagtype_1": "nova_groups",
            "tag_contains_1": "contains",
            "tag_1": "",
            "sort_by": "unique_scans_n",
            "page_size": page_size,
            "page": page,
            "json": 1,
            "fields": ",".join([
                "product_name", "brands", "categories",
                "countries_tags", "nutriscore_grade", "nova_group",
                "ecoscore_grade",
                "energy-kcal_100g", "fat_100g", "saturated-fat_100g",
                "sugars_100g", "salt_100g", "proteins_100g",
                "fiber_100g", "carbohydrates_100g",
            ]),
        }

        try:
            resp = requests.get(OFF_CONFIG["url"], params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            products = data.get("products", [])
            if not products:
                print("no more products.")
                break

            all_products.extend(products)
            print(f"{len(products)} products.")

        except Exception as e:
            print(f"error: {e}")
            break

    if all_products:
        df = pd.DataFrame(all_products)
        df.to_csv(filepath, index=False)
        print(f"      ✅ Saved: {OFF_CONFIG['filename']} ({len(df)} rows, {len(df.columns)} columns)")
        return True
    else:
        print(f"      ❌ No products retrieved.")
        return False


# ============================================================
# Main
# ============================================================


def main():
    print("=" * 60)
    print("🍔 Global Food & Nutrition — Data Collection")
    print("=" * 60)
    print()

    results = {}

    # --- OWID & WHO datasets ---
    print("📊 Downloading OWID & WHO datasets...")
    print("-" * 40)
    for name, config in DATASETS.items():
        dataset_type = config.get("type", "csv")
        if dataset_type == "who_api":
            success = download_who_api(name=name, **config)
        else:
            success = download_csv(name=name, **config)
        results[name] = success
    print()

    # --- Open Food Facts ---
    print("🔬 Downloading Open Food Facts product data...")
    print("-" * 40)
    results["open_food_facts"] = download_open_food_facts()
    print()

    # --- Summary ---
    print("=" * 60)
    print("📋 Summary")
    print("=" * 60)
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n  {passed}/{total} datasets collected successfully.")

    # List files in data directory
    print(f"\n📁 Files in {DATA_DIR}/:")
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith((".csv", ".tsv")):
            size_mb = os.path.getsize(os.path.join(DATA_DIR, f)) / (1024 * 1024)
            print(f"  📄 {f} ({size_mb:.1f} MB)")

    print()


if __name__ == "__main__":
    main()
