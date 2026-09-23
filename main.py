"""
main.py - Master training script
Run this once to:
  1. Understand the data
  2. Clean and engineer features
  3. Generate EDA visualizations
  4. Train all models and evaluate
  5. Save the best model to models/

Usage:
  python main.py
"""
# -*- coding: utf-8 -*-
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from data_understanding import understand_data
from data_cleaning       import load_and_clean
from eda                 import run_eda
from model_training      import train_models

DATA_PATH = os.path.join(BASE_DIR, "data", "data.csv")


def main():
    print("\n" + "=" * 70)
    print("  HOUSE PRICE PREDICTION - Complete ML Pipeline")
    print("=" * 70 + "\n")

    # Step 1: Data Understanding
    print("\n[STEP 1]  DATA UNDERSTANDING\n")
    understand_data(DATA_PATH)

    # Step 2 + 4: Data Cleaning + Feature Engineering
    print("\n[STEP 2 & 4]  DATA CLEANING + FEATURE ENGINEERING\n")
    df_clean = load_and_clean(DATA_PATH, verbose=True)
    print("\n   Clean dataset shape: {}".format(df_clean.shape))
    print("   Columns: {}".format(list(df_clean.columns)))

    # Step 3: EDA
    print("\n[STEP 3]  EXPLORATORY DATA ANALYSIS\n")
    saved_charts = run_eda(df_clean)
    print("   Generated {} visualizations.".format(len(saved_charts)))

    # Steps 5 & 6: Train + Evaluate
    print("\n[STEPS 5 & 6]  MODEL TRAINING & EVALUATION\n")
    results, best_pipeline, features, X_test, y_test = train_models(df_clean)

    # Summary table
    print("\n" + "=" * 70)
    print("  MODEL COMPARISON TABLE")
    print("=" * 70)
    print("{:<22} {:>13} {:>14} {:>8}".format("Model", "MAE", "RMSE", "R2"))
    print("-" * 62)
    for r in sorted(results, key=lambda x: x["R2"], reverse=True):
        print("{:<22} ${:>11,.0f} ${:>13,.0f} {:>8.4f}".format(
            r["Model"], r["MAE"], r["RMSE"], r["R2"]))

    best = max(results, key=lambda x: x["R2"])
    print("\n" + "=" * 70)
    print("  Best Model : {}".format(best["Model"]))
    print("  R2 Score   : {:.4f}".format(best["R2"]))
    print("  MAE        : ${:,.0f}".format(best["MAE"]))
    print("  RMSE       : ${:,.0f}".format(best["RMSE"]))
    print("=" * 70)

    print("\nTraining complete!")
    print("  Model saved      --> models/best_model.pkl")
    print("  Visualizations   --> visualizations/")
    print("\nTo launch the web app, run:")
    print("  streamlit run app/streamlit_app.py\n")


if __name__ == "__main__":
    main()
