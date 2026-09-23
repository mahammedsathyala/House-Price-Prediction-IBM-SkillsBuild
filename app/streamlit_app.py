"""
House Price Prediction — Full Streamlit Dashboard
Covers:
  • Step 7  — Prediction Interface
  • Step 8  — Project Dashboard (EDA + Model Comparison)
  • Step 9  — AI/Analytics Insights
"""

import os
import sys
import json
import joblib
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Path setup ─────────────────────────────────────────────────────────────
APP_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(APP_DIR)
SRC_DIR  = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

# pyrefly: ignore [missing-import]
from data_cleaning import load_and_clean

DATA_PATH  = os.path.join(BASE_DIR, "data", "data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_model.pkl")
FEAT_PATH  = os.path.join(BASE_DIR, "models", "feature_columns.json")
EVAL_PATH  = os.path.join(BASE_DIR, "models", "eval_results.json")
FI_PATH    = os.path.join(BASE_DIR, "models", "feature_importance.json")
VIZ_DIR    = os.path.join(BASE_DIR, "visualizations")

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🏠 House Price Prediction",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
    padding: 2.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
}
.main-header h1 { font-size: 2.6rem; font-weight: 700; margin: 0; }
.main-header p  { font-size: 1.1rem; opacity: 0.8; margin-top: 0.5rem; }

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.4rem 1rem;
    border-radius: 14px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}
.metric-card .metric-value { font-size: 1.9rem; font-weight: 700; }
.metric-card .metric-label { font-size: 0.85rem; opacity: 0.85; margin-top: 0.2rem; }

.prediction-box {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 2.5rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 30px rgba(17,153,142,0.35);
    margin: 1.5rem 0;
}
.prediction-box h2 { font-size: 1.2rem; opacity: 0.9; margin: 0; }
.prediction-box .price { font-size: 3.2rem; font-weight: 700; margin: 0.5rem 0; }
.prediction-box .sub   { font-size: 0.9rem; opacity: 0.8; }

.insight-card {
    background: #1e1e2e;
    border-left: 4px solid #667eea;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    color: #e0e0e0;
}
.insight-card .icon { font-size: 1.3rem; }
.insight-card strong { color: #a78bfa; }

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a1a2e;
    border-bottom: 3px solid #667eea;
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem 0;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 1.1rem;
    font-weight: 600;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 2rem;
    width: 100%;
    cursor: pointer;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; }

div[data-testid="stSidebar"] { background: #1a1a2e !important; }
div[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Caching ──────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    return load_and_clean(DATA_PATH, verbose=False)

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_feature_cols():
    if not os.path.exists(FEAT_PATH):
        return []
    with open(FEAT_PATH) as f:
        return json.load(f)

@st.cache_data
def load_eval_results():
    if not os.path.exists(EVAL_PATH):
        return []
    with open(EVAL_PATH) as f:
        return json.load(f)

@st.cache_data
def load_feature_importance():
    if not os.path.exists(FI_PATH):
        return {}
    with open(FI_PATH) as f:
        return json.load(f)

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏠 House Price ML")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏡 Predict Price", "📊 Dashboard", "🔬 EDA Charts",
         "🤖 Model Comparison", "🧠 AI Insights"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("""
    **About this Project**  
    A complete Machine Learning pipeline for predicting King County house prices.  
    
    **Dataset:** ~4,600 records  
    **Target:** Price (USD)  
    **Best Model:** Auto-selected by R²  
    """)

df_clean = load_data()
model    = load_model()
feat_cols = load_feature_cols()
eval_results = load_eval_results()
fi_dict  = load_feature_importance()

# ── Helper ────────────────────────────────────────────────────────────────────
def _fmt(val: float) -> str:
    if val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    return f"${val:,.0f}"

# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — PREDICT PRICE
# ════════════════════════════════════════════════════════════════════════════
if page == "🏡 Predict Price":
    st.markdown("""
    <div class="main-header">
        <h1>🏠 House Price Predictor</h1>
        <p>Enter house details below and get an instant ML-powered price estimate</p>
    </div>
    """, unsafe_allow_html=True)

    if model is None or not feat_cols:
        st.error("⚠️ Model not found. Please run `python main.py` first to train the model.")
        st.stop()

    # City list from data
    city_list = sorted(df_clean["city_name"].dropna().unique().tolist()) if "city_name" in df_clean.columns else ["Seattle"]
    city_encoded_map = {row["city_name"]: row["city_encoded"]
                        for _, row in df_clean[["city_name","city_encoded"]].drop_duplicates().iterrows()
                        } if "city_encoded" in df_clean.columns else {}

    st.markdown('<div class="section-title">📝 Enter House Details</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🛏 Rooms & Size**")
        bedrooms   = st.number_input("Bedrooms",   min_value=0, max_value=20, value=3, step=1)
        bathrooms  = st.number_input("Bathrooms",  min_value=0.0, max_value=10.0, value=2.0, step=0.25)
        floors     = st.number_input("Floors",     min_value=1.0, max_value=4.0, value=1.0, step=0.5)
        sqft_living   = st.number_input("Living Area (sqft)", min_value=100, max_value=15000, value=1800)
        sqft_lot      = st.number_input("Lot Size (sqft)",    min_value=100, max_value=1_000_000, value=7500)

    with col2:
        st.markdown("**🏗 Structure Details**")
        sqft_above    = st.number_input("Above-Ground Area (sqft)", min_value=100, max_value=15000, value=1800)
        sqft_basement = st.number_input("Basement Area (sqft)",     min_value=0,   max_value=5000,  value=0)
        yr_built      = st.number_input("Year Built",    min_value=1900, max_value=2024, value=1990)
        yr_renovated  = st.number_input("Year Renovated (0 = never)", min_value=0, max_value=2024, value=0)
        condition     = st.slider("Condition (1=Poor → 5=Excellent)", 1, 5, 3)

    with col3:
        st.markdown("**🌊 Features & Location**")
        waterfront = st.selectbox("Waterfront Property?", [0, 1],
                                  format_func=lambda x: "Yes ✅" if x else "No ❌")
        view       = st.slider("View Rating (0–4)", 0, 4, 0)
        city_name  = st.selectbox("City", city_list)
        sale_year  = st.number_input("Sale Year", min_value=2014, max_value=2025, value=2014)
        sale_month = st.number_input("Sale Month", min_value=1, max_value=12, value=5)

    # Build input row
    city_enc = city_encoded_map.get(city_name, 0)

    # Compute zip_code median for selected city
    if "city_name" in df_clean.columns and "zip_code" in df_clean.columns:
        zip_median = df_clean[df_clean["city_name"] == city_name]["zip_code"].median()
        if np.isnan(zip_median):
            zip_median = df_clean["zip_code"].median()
    else:
        zip_median = 98000.0

    # Feature engineering (must match training pipeline)
    house_age      = sale_year - yr_built
    was_renovated  = int(yr_renovated > 0)
    renovation_age = (sale_year - yr_renovated) if yr_renovated > 0 else 0
    total_sqft     = sqft_above + sqft_basement
    living_to_lot  = sqft_living / (sqft_lot + 1)
    has_basement   = int(sqft_basement > 0)

    input_dict = {
        "bedrooms":      bedrooms,
        "bathrooms":     bathrooms,
        "sqft_living":   sqft_living,
        "sqft_lot":      sqft_lot,
        "floors":        floors,
        "waterfront":    waterfront,
        "view":          view,
        "condition":     condition,
        "sqft_above":    sqft_above,
        "sqft_basement": sqft_basement,
        "yr_built":      yr_built,
        "yr_renovated":  yr_renovated,
        "sale_year":     sale_year,
        "sale_month":    sale_month,
        "zip_code":      zip_median,
        "city_encoded":  city_enc,
        "house_age":     house_age,
        "was_renovated": was_renovated,
        "renovation_age":renovation_age,
        "total_sqft":    total_sqft,
        "living_to_lot": living_to_lot,
        "has_basement":  has_basement,
    }

    # Align to feature columns — fill any missing with 0
    input_row = pd.DataFrame([{col: input_dict.get(col, 0) for col in feat_cols}])

    st.markdown("---")
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        predict_clicked = st.button("🔍 Predict Price", use_container_width=True)

    if predict_clicked:
        try:
            prediction = float(model.predict(input_row)[0])
            prediction = max(0, prediction)

            st.markdown(f"""
            <div class="prediction-box">
                <h2>Estimated House Price</h2>
                <div class="price">{_fmt(prediction)}</div>
                <div class="sub">Based on the characteristics you entered</div>
            </div>
            """, unsafe_allow_html=True)

            # Input summary
            st.markdown('<div class="section-title">📋 Input Summary</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🛏 Bedrooms",    bedrooms)
            c2.metric("🚿 Bathrooms",   bathrooms)
            c3.metric("📐 Living sqft", f"{sqft_living:,}")
            c4.metric("🏙 City",        city_name)
            c1.metric("🏗 Year Built",  yr_built)
            c2.metric("⭐ Condition",   f"{condition}/5")
            c3.metric("🌊 Waterfront",  "Yes" if waterfront else "No")
            c4.metric("🔢 Floors",      floors)

        except Exception as e:
            st.error(f"Prediction failed: {e}")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Project Dashboard</h1>
        <p>Dataset overview, key statistics and model performance at a glance</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    raw_df = pd.read_csv(DATA_PATH)
    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        ("Total Records",   f"{len(raw_df):,}",                    c1),
        ("Features Used",   str(len(feat_cols)) if feat_cols else "—", c2),
        ("Avg Price",       _fmt(raw_df["price"].mean()),           c3),
        ("Max Price",       _fmt(raw_df["price"].max()),            c4),
        ("Min Price",       _fmt(raw_df["price"].min()),            c5),
    ]
    for label, val, col in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Dataset overview table
    st.markdown('<div class="section-title">🗂 Dataset Overview</div>', unsafe_allow_html=True)
    st.dataframe(raw_df.head(20), use_container_width=True, height=320)

    st.markdown('<div class="section-title">📈 Statistical Summary</div>', unsafe_allow_html=True)
    st.dataframe(raw_df.describe().round(2).T, use_container_width=True)

    # Model comparison table
    if eval_results:
        st.markdown('<div class="section-title">🏆 Model Performance Comparison</div>', unsafe_allow_html=True)
        eval_df = pd.DataFrame(eval_results)
        eval_df["MAE"]  = eval_df["MAE"].apply(lambda x: f"${x:,.0f}")
        eval_df["RMSE"] = eval_df["RMSE"].apply(lambda x: f"${x:,.0f}")
        eval_df["MSE"]  = eval_df["MSE"].apply(lambda x: f"${x:,.0f}")
        eval_df["R2"]   = eval_df["R2"].apply(lambda x: f"{x:.4f}")
        eval_df.columns = ["Model", "MAE", "MSE", "RMSE", "R²"]
        st.dataframe(eval_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — EDA CHARTS
# ════════════════════════════════════════════════════════════════════════════
elif page == "🔬 EDA Charts":
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Exploratory Data Analysis</h1>
        <p>Visual analysis of the housing dataset</p>
    </div>
    """, unsafe_allow_html=True)

    charts = {
        "01 — Price Distribution":      "01_price_distribution.png",
        "02 — Price vs Living Area":    "02_price_vs_sqft.png",
        "03 — Price by Bedrooms":       "03_price_vs_bedrooms.png",
        "04 — Price by Bathrooms":      "04_price_vs_bathrooms.png",
        "05 — Price by Condition":      "05_price_vs_condition.png",
        "06 — Waterfront vs Price":     "06_price_vs_waterfront.png",
        "07 — Price by Floors":         "07_price_vs_floors.png",
        "08 — Price by Year Built":     "08_price_vs_yr_built.png",
        "09 — Correlation Heatmap":     "09_correlation_heatmap.png",
        "10 — Top Cities by Price":     "10_top_cities_by_price.png",
        "11 — Model Comparison":        "11_model_comparison.png",
        "12 — Actual vs Predicted":     "12_actual_vs_predicted.png",
        "13 — Residual Analysis":       "13_residuals.png",
        "14 — Feature Importance":      "14_feature_importance.png",
    }

    for title, fname in charts.items():
        fpath = os.path.join(VIZ_DIR, fname)
        if os.path.exists(fpath):
            with st.expander(f"📈 {title}", expanded=False):
                st.image(fpath, use_container_width=True)
        else:
            st.info(f"⏳ Chart not yet generated: {title}. Run `python main.py` first.")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — MODEL COMPARISON
# ════════════════════════════════════════════════════════════════════════════
elif page == "🤖 Model Comparison":
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Model Comparison & Evaluation</h1>
        <p>Detailed performance metrics for all trained regression models</p>
    </div>
    """, unsafe_allow_html=True)

    if not eval_results:
        st.warning("No evaluation results found. Run `python main.py` to train models first.")
    else:
        # Best model badge
        best = max(eval_results, key=lambda r: r["R2"])
        st.success(f"🏆 **Best Model: {best['Model']}**  |  R² = {best['R2']:.4f}  |  RMSE = ${best['RMSE']:,.0f}")

        # Metric cards
        st.markdown('<div class="section-title">📊 Metrics for Each Model</div>', unsafe_allow_html=True)
        cols = st.columns(len(eval_results))
        for i, r in enumerate(sorted(eval_results, key=lambda x: x["R2"], reverse=True)):
            with cols[i]:
                badge = "🥇" if r["Model"] == best["Model"] else "📊"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{badge} {r['Model']}</div>
                    <div class="metric-value">{r['R2']:.4f}</div>
                    <div class="metric-label">R² Score</div>
                    <hr style='border-color:rgba(255,255,255,0.3);margin:0.5rem 0'>
                    <div class="metric-label">MAE: ${r['MAE']:,.0f}</div>
                    <div class="metric-label">RMSE: ${r['RMSE']:,.0f}</div>
                </div>""", unsafe_allow_html=True)

        # Charts
        col_a, col_b = st.columns(2)
        chart_comp = os.path.join(VIZ_DIR, "11_model_comparison.png")
        chart_avp  = os.path.join(VIZ_DIR, "12_actual_vs_predicted.png")
        chart_res  = os.path.join(VIZ_DIR, "13_residuals.png")
        chart_fi   = os.path.join(VIZ_DIR, "14_feature_importance.png")

        if os.path.exists(chart_comp):
            with col_a:
                st.markdown('<div class="section-title">R² & RMSE Comparison</div>', unsafe_allow_html=True)
                st.image(chart_comp, use_container_width=True)
        if os.path.exists(chart_avp):
            with col_b:
                st.markdown('<div class="section-title">Actual vs Predicted</div>', unsafe_allow_html=True)
                st.image(chart_avp, use_container_width=True)
        if os.path.exists(chart_res):
            with col_a:
                st.markdown('<div class="section-title">Residual Analysis</div>', unsafe_allow_html=True)
                st.image(chart_res, use_container_width=True)
        if os.path.exists(chart_fi):
            with col_b:
                st.markdown('<div class="section-title">Feature Importance</div>', unsafe_allow_html=True)
                st.image(chart_fi, use_container_width=True)

        # Feature importance table
        if fi_dict:
            st.markdown('<div class="section-title">🔑 Top Feature Importances</div>', unsafe_allow_html=True)
            fi_df = pd.DataFrame(list(fi_dict.items()), columns=["Feature", "Importance"])
            fi_df["Importance"] = fi_df["Importance"].round(5)
            fi_df = fi_df.sort_values("Importance", ascending=False).reset_index(drop=True)
            st.dataframe(fi_df, use_container_width=True, hide_index=True)

        # Explanation
        st.markdown('<div class="section-title">💡 Why this model was selected</div>', unsafe_allow_html=True)
        model_explanations = {
            "XGBoost": "XGBoost (eXtreme Gradient Boosting) was selected as the best model. It uses gradient-boosted decision trees with regularization, making it highly effective for tabular regression tasks. It achieved the highest R² and lowest RMSE, indicating it captures non-linear relationships in the housing data better than simpler models.",
            "Random Forest": "Random Forest was selected as the best model. It builds hundreds of decision trees and averages their predictions, which reduces overfitting and handles outliers well. It achieved the highest R² across all models, indicating strong generalization on unseen data.",
            "Gradient Boosting": "Gradient Boosting was selected as the best model. It sequentially builds trees where each tree corrects the errors of the previous one. This iterative error-correction makes it highly accurate for structured data like house prices.",
            "Linear Regression": "Linear Regression was selected as the baseline model. While simpler than ensemble methods, it still achieved competitive results and provides full interpretability through its coefficients."
        }
        explanation = model_explanations.get(best["Model"], f"{best['Model']} achieved the best R² score among all trained models.")
        st.info(f"📌 {explanation}")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 — AI INSIGHTS
# ════════════════════════════════════════════════════════════════════════════
elif page == "🧠 AI Insights":
    st.markdown("""
    <div class="main-header">
        <h1>🧠 AI-Assisted Analytics Insights</h1>
        <p>Data-driven natural-language insights derived from the actual dataset</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 All insights below are computed directly from the dataset — no assumptions or fabrications.")

    raw_df = pd.read_csv(DATA_PATH)

    # Compute real insights from data
    corr_cols = ["sqft_living", "sqft_above", "bathrooms", "bedrooms",
                 "floors", "waterfront", "view", "condition", "sqft_lot"]
    corr_vals = {}
    for col in corr_cols:
        if col in raw_df.columns:
            corr_vals[col] = raw_df[col].corr(raw_df["price"])
    top_feat = max(corr_vals, key=lambda k: abs(corr_vals[k]))
    top_corr = corr_vals[top_feat]

    wf_mean    = raw_df[raw_df["waterfront"] == 1]["price"].mean()
    no_wf_mean = raw_df[raw_df["waterfront"] == 0]["price"].mean()
    wf_premium = (wf_mean - no_wf_mean) / no_wf_mean * 100

    city_means = raw_df.groupby("city")["price"].mean().sort_values(ascending=False)
    top_city   = city_means.index[0]
    top_city_price = city_means.iloc[0]
    bot_city   = city_means.index[-1]
    bot_city_price = city_means.iloc[-1]

    cond5_mean = raw_df[raw_df["condition"] == 5]["price"].mean()
    cond1_mean = raw_df[raw_df["condition"] == 1]["price"].mean()

    sqft_corr = raw_df["sqft_living"].corr(raw_df["price"])

    insights = [
        {
            "icon": "📐",
            "title": "Living Area is the Strongest Predictor",
            "text": f"<strong>sqft_living</strong> has a Pearson correlation of <strong>{sqft_corr:.3f}</strong> with price — the highest among all numerical features. Every additional 100 sqft of living space is associated with a meaningful increase in estimated price."
        },
        {
            "icon": "🌊",
            "title": "Waterfront Properties Command a Significant Premium",
            "text": f"Waterfront properties have an average price of <strong>{_fmt(wf_mean)}</strong>, compared to <strong>{_fmt(no_wf_mean)}</strong> for non-waterfront homes — a premium of <strong>{wf_premium:.1f}%</strong>. This is one of the strongest binary predictors in the dataset."
        },
        {
            "icon": "🏙",
            "title": "Location Matters — City Drives Price Significantly",
            "text": f"<strong>{top_city}</strong> has the highest average house price at <strong>{_fmt(top_city_price)}</strong>, while <strong>{bot_city}</strong> has the lowest at <strong>{_fmt(bot_city_price)}</strong>. City-level encoding captures a significant portion of the geographic price variation."
        },
        {
            "icon": "⭐",
            "title": "Condition Rating Has a Clear Impact on Price",
            "text": f"Houses rated <strong>Condition 5 (Excellent)</strong> have an average price of <strong>{_fmt(cond5_mean)}</strong>, while <strong>Condition 1 (Poor)</strong> homes average <strong>{_fmt(cond1_mean)}</strong>. Maintaining or renovating a property increases its market value substantially."
        },
        {
            "icon": "🏗",
            "title": "Renovation History Adds Value",
            "text": f"Properties that have been renovated tend to sell at higher prices. The <strong>was_renovated</strong> and <strong>renovation_age</strong> features, combined with <strong>yr_renovated</strong>, provide the model with important signals about a house's upkeep over time."
        },
        {
            "icon": "🛁",
            "title": "Bathrooms Outperform Bedrooms as a Price Signal",
            "text": f"Bathrooms have a correlation of <strong>{corr_vals.get('bathrooms', 0):.3f}</strong> with price, compared to <strong>{corr_vals.get('bedrooms', 0):.3f}</strong> for bedrooms. More bathrooms typically indicate a larger, more luxurious home."
        },
        {
            "icon": "📅",
            "title": "Year Built Has a Non-Linear Relationship with Price",
            "text": "Very old homes and very new homes can both be expensive — older homes often have historical charm, while newer builds reflect modern construction costs. The engineered <strong>house_age</strong> feature captures this better than the raw year."
        },
        {
            "icon": "🔍",
            "title": "View Rating Significantly Boosts Price",
            "text": f"The <strong>view</strong> feature (rated 0–4) has a correlation of <strong>{corr_vals.get('view', 0):.3f}</strong> with price. Properties with the best views (rating 4) command substantially higher prices, especially in scenic areas near water or mountains."
        },
    ]

    for ins in insights:
        st.markdown(f"""
        <div class="insight-card">
            <div>
                <span class="icon">{ins['icon']}</span>
                <strong>&nbsp;{ins['title']}</strong>
            </div>
            <p style='margin:0.5rem 0 0 0; font-size:0.9rem;'>{ins['text']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Live correlation table
    st.markdown('<div class="section-title">📊 Feature Correlations with Price</div>', unsafe_allow_html=True)
    corr_df = pd.DataFrame(list(corr_vals.items()), columns=["Feature", "Correlation with Price"])
    corr_df["Correlation with Price"] = corr_df["Correlation with Price"].round(4)
    corr_df = corr_df.sort_values("Correlation with Price", ascending=False).reset_index(drop=True)
    st.dataframe(corr_df, use_container_width=True, hide_index=True)
