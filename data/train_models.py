"""
Machine Learning Pipelines — Global Food & Nutrition Dashboard
COMP5120 Data Visualization (Spring 2026)

Trains and serializes:
1. Random Forest Classifier for Nutri-Score prediction (A-E)
2. Random Forest Regressor for Adult Obesity prediction based on dietary supply

Saves serialized models to app/models/.
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

# ============================================================
# Paths
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
APP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app")
MODELS_DIR = os.path.join(APP_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_nutriscore_classifier():
    print("\n------------------------------------------------------------")
    print("🤖 1. Training Nutri-Score Classifier")
    print("------------------------------------------------------------")
    
    # Load products dataset
    p_path = os.path.join(DATA_DIR, "products.parquet")
    df = pd.read_parquet(p_path)
    
    # Features & Target
    features = [
        "energy-kcal_100g", "fat_100g", "saturated-fat_100g",
        "sugars_100g", "salt_100g", "proteins_100g", "fiber_100g"
    ]
    target = "nutriscore_grade"
    
    # Filter dataset for training (must have valid nutriscore grade and complete features)
    train_df = df.dropna(subset=features + [target]).copy()
    
    X = train_df[features]
    y = train_df[target]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Create Pipeline
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1))
    ])
    
    # Fit
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"  Accuracy on test set: {acc:.4f}")
    
    # Save Pipeline
    model_path = os.path.join(MODELS_DIR, "nutriscore_classifier.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"  💾 Saved classifier pipeline to: {model_path}")
    
    # Feature Importances
    importances = pipeline.named_steps['classifier'].feature_importances_
    for name, imp in zip(features, importances):
        print(f"    - {name}: {imp:.4f}")

def train_obesity_regressor():
    print("\n------------------------------------------------------------")
    print("🤖 2. Training Obesity Regressor")
    print("------------------------------------------------------------")
    
    # Load country dietary and health datasets
    cy = pd.read_parquet(os.path.join(DATA_DIR, "country_yearly.parquet"))
    ch = pd.read_parquet(os.path.join(DATA_DIR, "country_health.parquet"))
    
    # Merge on country (iso3) and year
    # ch has 'who_obesity_pct'
    merged = pd.merge(
        cy,
        ch[["iso3", "year", "who_obesity_pct"]],
        on=["iso3", "year"],
        how="inner"
    )
    
    # Drop rows without obesity rate
    merged = merged.dropna(subset=["who_obesity_pct", "calories"])
    print(f"  Total records for obesity regressor training: {len(merged)}")
    
    # Features & Target
    features = [
        "calories",
        "grp_cereals",
        "grp_meat",
        "grp_dairy_eggs",
        "grp_oils_fats",
        "grp_sugar_sweeteners",
        "grp_fruits_vegetables",
        "grp_starchy_roots_pulses",
        "grp_other"
    ]
    target = "who_obesity_pct"
    
    X = merged[features]
    y = merged[target]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create Pipeline
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1))
    ])
    
    # Fit
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"  R^2 score on test set: {r2:.4f}")
    print(f"  RMSE on test set: {rmse:.2f}% obesity")
    
    # Save Pipeline
    model_path = os.path.join(MODELS_DIR, "obesity_regressor.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"  💾 Saved regressor pipeline to: {model_path}")
    
    # Feature Importances
    importances = pipeline.named_steps['regressor'].feature_importances_
    for name, imp in zip(features, importances):
        print(f"    - {name}: {imp:.4f}")

def main():
    print("=" * 60)
    print("🔨 Phase 3 — Machine Learning Model Training")
    print("=" * 60)
    train_nutriscore_classifier()
    train_obesity_regressor()
    print("\n" + "=" * 60)
    print("✅ Phase 3 Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
