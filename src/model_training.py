"""
Steps 5 & 6: Model Training + Evaluation
Trains multiple regression models, evaluates them, and saves the best one.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[WARN] XGBoost not installed — will skip XGBoost model.")

sns.set_theme(style="darkgrid", palette="muted")

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
VIZ_DIR    = os.path.join(BASE_DIR, "visualizations")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(VIZ_DIR, exist_ok=True)

TARGET = "price"
DROP_FROM_FEATURES = {"price", "city_name"}


def _get_features(df: pd.DataFrame):
    return [c for c in df.columns if c not in DROP_FROM_FEATURES]


def _evaluate(name, model, X_test, y_test):
    preds = model.predict(X_test)
    mae   = mean_absolute_error(y_test, preds)
    mse   = mean_squared_error(y_test, preds)
    rmse  = np.sqrt(mse)
    r2    = r2_score(y_test, preds)
    return {"Model": name, "MAE": mae, "MSE": mse, "RMSE": rmse, "R2": r2, "preds": preds}


def train_models(df: pd.DataFrame):
    """
    Train Linear Regression, Random Forest, Gradient Boosting, XGBoost.
    Returns: results list, best model pipeline, feature names, X_test, y_test.
    """
    feature_cols = _get_features(df)
    X = df[feature_cols]
    y = df[TARGET]

    # 80/20 stratified-like split (no data leakage)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"[TRAIN] Train size: {len(X_train):,}  |  Test size: {len(X_test):,}")

    # ── Model definitions ────────────────────────────────────────────────────
    candidates = {
        "Linear Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model",  LinearRegression())
        ]),
        "Random Forest": Pipeline([
            ("scaler", StandardScaler()),
            ("model",  RandomForestRegressor(
                n_estimators=200, max_depth=20,
                min_samples_leaf=2, random_state=42, n_jobs=-1
            ))
        ]),
        "Gradient Boosting": Pipeline([
            ("scaler", StandardScaler()),
            ("model",  GradientBoostingRegressor(
                n_estimators=300, learning_rate=0.08,
                max_depth=5, subsample=0.8, random_state=42
            ))
        ]),
    }

    if XGBOOST_AVAILABLE:
        candidates["XGBoost"] = Pipeline([
            ("scaler", StandardScaler()),
            ("model",  XGBRegressor(
                n_estimators=400, learning_rate=0.07,
                max_depth=6, subsample=0.8,
                colsample_bytree=0.8, random_state=42,
                verbosity=0, eval_metric="rmse"
            ))
        ])

    # ── Training & evaluation ────────────────────────────────────────────────
    results = []
    for name, pipeline in candidates.items():
        print(f"[TRAIN] Training {name} ...", end=" ", flush=True)
        pipeline.fit(X_train, y_train)
        res = _evaluate(name, pipeline, X_test, y_test)
        results.append(res)
        print(f"R²={res['R2']:.4f}  RMSE=${res['RMSE']:,.0f}")

    # ── Pick best model by R² ────────────────────────────────────────────────
    best   = max(results, key=lambda r: r["R2"])
    best_name = best["Model"]
    best_pipeline = candidates[best_name]
    print(f"\n[TRAIN] Best model → {best_name}  (R²={best['R2']:.4f})")

    # ── Save best model ──────────────────────────────────────────────────────
    model_path = os.path.join(MODELS_DIR, "best_model.pkl")
    joblib.dump(best_pipeline, model_path)
    print(f"[TRAIN] Model saved → {model_path}")

    # Save feature column list
    feat_path = os.path.join(MODELS_DIR, "feature_columns.json")
    with open(feat_path, "w") as f:
        json.dump(feature_cols, f)

    # Save evaluation results (without preds array)
    eval_results = [
        {k: v for k, v in r.items() if k != "preds"} for r in results
    ]
    eval_path = os.path.join(MODELS_DIR, "eval_results.json")
    with open(eval_path, "w") as f:
        json.dump(eval_results, f, indent=2)

    # ── Visualizations ───────────────────────────────────────────────────────
    _plot_model_comparison(results)
    _plot_actual_vs_predicted(best, y_test)
    _plot_residuals(best, y_test)
    _plot_feature_importance(best_pipeline, feature_cols, best_name)

    return results, best_pipeline, feature_cols, X_test, y_test


# ── Plots ────────────────────────────────────────────────────────────────────

def _plot_model_comparison(results):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Model Performance Comparison", fontsize=14, fontweight="bold")

    names = [r["Model"] for r in results]
    r2s   = [r["R2"]   for r in results]
    rmses = [r["RMSE"] for r in results]

    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"][:len(names)]

    axes[0].barh(names, r2s, color=colors, edgecolor="white", height=0.5)
    axes[0].set_title("R² Score (higher = better)")
    axes[0].set_xlim(0, 1)
    for i, v in enumerate(r2s):
        axes[0].text(v + 0.005, i, f"{v:.4f}", va="center", fontsize=10)

    axes[1].barh(names, rmses, color=colors, edgecolor="white", height=0.5)
    axes[1].set_title("RMSE (lower = better)")
    axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    for i, v in enumerate(rmses):
        axes[1].text(v + 1000, i, f"${v:,.0f}", va="center", fontsize=10)

    plt.tight_layout()
    fig.savefig(os.path.join(VIZ_DIR, "11_model_comparison.png"), dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("  ✅ Saved → 11_model_comparison.png")


def _plot_actual_vs_predicted(best, y_test):
    preds = best["preds"]
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.scatter(y_test, preds, alpha=0.25, s=12, color="#4C72B0", label="Predictions")
    lo = min(y_test.min(), preds.min())
    hi = max(y_test.max(), preds.max())
    ax.plot([lo, hi], [lo, hi], "r--", linewidth=2, label="Perfect prediction")
    ax.set_title(f"Actual vs Predicted Price ({best['Model']})", fontsize=13, fontweight="bold")
    ax.set_xlabel("Actual Price (USD)")
    ax.set_ylabel("Predicted Price (USD)")
    fmt = mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M")
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
    ax.legend()
    ax.text(0.05, 0.92, f"R² = {best['R2']:.4f}", transform=ax.transAxes,
            fontsize=12, color="darkred", fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(VIZ_DIR, "12_actual_vs_predicted.png"), dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("  ✅ Saved → 12_actual_vs_predicted.png")


def _plot_residuals(best, y_test):
    preds     = best["preds"]
    residuals = y_test.values - preds

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"Residual Analysis — {best['Model']}", fontsize=13, fontweight="bold")

    axes[0].scatter(preds, residuals, alpha=0.25, s=10, color="#4C72B0")
    axes[0].axhline(0, color="red", linestyle="--", linewidth=1.5)
    axes[0].set_title("Residuals vs Predicted")
    axes[0].set_xlabel("Predicted Price")
    axes[0].set_ylabel("Residual (Actual − Predicted)")
    axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))

    axes[1].hist(residuals, bins=60, color="#DD8452", edgecolor="white", alpha=0.85)
    axes[1].axvline(0, color="red", linestyle="--", linewidth=1.5)
    axes[1].set_title("Residual Distribution")
    axes[1].set_xlabel("Residual")
    axes[1].set_ylabel("Count")

    plt.tight_layout()
    fig.savefig(os.path.join(VIZ_DIR, "13_residuals.png"), dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("  ✅ Saved → 13_residuals.png")


def _plot_feature_importance(pipeline, feature_cols, model_name):
    """Extract and plot feature importance for tree-based models."""
    try:
        model = pipeline.named_steps["model"]
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_)
        else:
            print("[INFO] Feature importance not available for this model.")
            return

        fi = pd.Series(importances, index=feature_cols).sort_values(ascending=True)
        top = fi.tail(20)

        fig, ax = plt.subplots(figsize=(10, 8))
        top.plot(kind="barh", ax=ax, color="#4C72B0", edgecolor="white")
        ax.set_title(f"Top Feature Importances — {model_name}", fontsize=13, fontweight="bold")
        ax.set_xlabel("Importance Score")
        plt.tight_layout()
        fig.savefig(os.path.join(VIZ_DIR, "14_feature_importance.png"), dpi=130, bbox_inches="tight")
        plt.close(fig)
        print("  ✅ Saved → 14_feature_importance.png")

        # Save to JSON for dashboard
        fi_dict = fi.sort_values(ascending=False).head(15).round(6).to_dict()
        with open(os.path.join(MODELS_DIR, "feature_importance.json"), "w") as f:
            json.dump(fi_dict, f, indent=2)
    except Exception as e:
        print(f"[WARN] Could not plot feature importance: {e}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from data_cleaning import load_and_clean
    df = load_and_clean(os.path.join(BASE_DIR, "data", "data.csv"))
    train_models(df)
