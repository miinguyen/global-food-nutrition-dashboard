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
        "url": "https://ghoapi.azureedge.net/api/NCD_BMI_30A",
        "filename": "who_obesity_adults.csv",
        "description": "WHO: Prevalence of obesity among adults (BMI ≥ 30)",
        "type": "who_api",
        "filter_sex": "SEX_BTSX",
    },
    "who_underweight_children": {
        "url": "https://ghoapi.azureedge.net/api/NUTRITION_WA_2",
        "filename": "who_underweight_children.csv",
        "description": "WHO: Prevalence of underweight among children under 5",
        "type": "who_api",
        "filter_sex": "SEX_BTSX",
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

    if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
        print(f"  ⏭️  {name}: Already exists, skipping. Delete to re-download.")
        return True
    elif os.path.exists(filepath):
        os.remove(filepath)  # Remove empty/corrupt file

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
    """Download data from the WHO GHO OData API with pagination."""
    filepath = os.path.join(DATA_DIR, filename)

    if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
        print(f"  ⏭️  {name}: Already exists, skipping.")
        return True
    elif os.path.exists(filepath):
        os.remove(filepath)  # Remove empty/corrupt file

    print(f"  ⬇️  {name}: {description}")
    filter_sex = kwargs.get("filter_sex", None)

    try:
        # OData API paginates — collect all pages
        all_records = []
        next_url = url

        while next_url:
            response = requests.get(
                next_url, timeout=120,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            if "value" not in data:
                break

            all_records.extend(data["value"])
            next_url = data.get("@odata.nextLink", None)
            print(f"\r      Fetched {len(all_records)} records...", end="")

        print()

        if not all_records:
            print(f"      ❌ No records returned")
            return False

        df = pd.DataFrame(all_records)

        # Filter by sex if specified (e.g., SEX_BTSX = both sexes)
        if filter_sex and "Dim1" in df.columns:
            df = df[df["Dim1"] == filter_sex]

        # Keep only country-level data
        if "SpatialDimType" in df.columns:
            df = df[df["SpatialDimType"] == "COUNTRY"]

        # Select and rename useful columns
        col_map = {
            "SpatialDim": "country_code",
            "TimeDim": "year",
            "NumericValue": "value",
            "Low": "ci_low",
            "High": "ci_high",
            "ParentLocation": "region",
        }
        keep = [c for c in col_map if c in df.columns]
        df = df[keep].rename(columns=col_map)

        df.to_csv(filepath, index=False)
        print(f"      ✅ Saved: {filename} ({len(df)} rows, {len(df.columns)} columns)")
        return True

    except Exception as e:
        print(f"      ❌ Failed: {e}")
        return False


def download_open_food_facts():
    """
    Download product-level nutrition data from Open Food Facts.
    Strategy:
      1. Try the API (fast, but may be down)
      2. Fallback: download static CSV export and sample (slower, reliable)
      3. Last resort: instructions for manual Kaggle download
    """
    import time
    import gzip

    filepath = os.path.join(DATA_DIR, OFF_CONFIG["filename"])

    if os.path.exists(filepath):
        print(f"  ⏭️  open_food_facts: Already exists, skipping.")
        return True

    print(f"  ⬇️  open_food_facts: {OFF_CONFIG['description']}")

    # --- Strategy 1: Try API ---
    print("      Strategy 1: Trying API...")
    headers = {
        "User-Agent": "COMP5120-DataViz-Dashboard/1.0 (academic project)",
    }
    fields = ",".join([
        "product_name", "brands", "categories",
        "countries_tags", "nutriscore_grade", "nova_group",
        "ecoscore_grade",
        "energy-kcal_100g", "fat_100g", "saturated-fat_100g",
        "sugars_100g", "salt_100g", "proteins_100g",
        "fiber_100g", "carbohydrates_100g",
    ])

    all_products = []
    api_works = True

    for page in range(1, 101):
        if len(all_products) >= 10000:
            break
        try:
            url = (
                f"https://world.openfoodfacts.org/api/v2/search"
                f"?fields={fields}&page_size=100&page={page}"
                f"&sort_by=popularity_key"
            )
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            products = resp.json().get("products", [])
            if not products:
                break
            all_products.extend(products)
            print(f"\r      API: {len(all_products)}/10000 products...", end="")
            time.sleep(0.3)
        except Exception as e:
            print(f"\n      API unavailable: {e}")
            api_works = False
            break

    if all_products:
        df = pd.DataFrame(all_products)
        df.to_csv(filepath, index=False)
        print(f"\n      ✅ Saved via API: {len(df)} rows")
        return True

    # --- Strategy 2: Static CSV export (stream + sample) ---
    print("      Strategy 2: Downloading static CSV export (this may take a few minutes)...")
    static_url = "https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz"
    gz_path = os.path.join(DATA_DIR, "_off_temp.csv.gz")

    try:
        # Stream download to avoid loading entire file in memory
        print("      Downloading compressed file...", end=" ")
        with requests.get(static_url, stream=True, timeout=300, headers=headers) as r:
            r.raise_for_status()
            total = 0
            with open(gz_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
                    total += len(chunk)
                    print(f"\r      Downloaded {total / (1024*1024):.0f} MB...", end="")
                    # Stop after ~500 MB — enough for our sample
                    if total > 500 * 1024 * 1024:
                        break
        print()

        # Read with chunked processing, keeping only products with nutriscore + nova
        print("      Filtering products with Nutri-Score and NOVA data...")
        keep_cols = [
            "product_name", "brands", "categories",
            "countries_tags", "nutriscore_grade", "nova_group",
            "ecoscore_grade",
            "energy-kcal_100g", "fat_100g", "saturated-fat_100g",
            "sugars_100g", "salt_100g", "proteins_100g",
            "fiber_100g", "carbohydrates_100g",
        ]

        filtered = []
        for chunk in pd.read_csv(
            gz_path, sep="\t", compression="gzip",
            usecols=lambda c: c in keep_cols,
            chunksize=5000, on_bad_lines="skip",
            low_memory=False,
        ):
            valid = chunk.dropna(subset=["nutriscore_grade", "nova_group"])
            filtered.append(valid)
            total_rows = sum(len(f) for f in filtered)
            print(f"\r      Found {total_rows} valid products...", end="")
            if total_rows >= 10000:
                break

        if filtered:
            df = pd.concat(filtered, ignore_index=True).head(10000)
            df.to_csv(filepath, index=False)
            print(f"\n      ✅ Saved via static export: {len(df)} rows")
            # Clean up temp file
            os.remove(gz_path)
            return True

    except Exception as e:
        print(f"\n      Static download failed: {e}")
        if os.path.exists(gz_path):
            os.remove(gz_path)

    # --- Strategy 3: Manual instructions ---
    print()
    print("      ⚠️  Both automated methods failed.")
    print("      📥 Please download manually from Kaggle:")
    print("         https://www.kaggle.com/datasets/openfoodfacts/world-food-facts")
    print(f"         Save as: {filepath}")
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
