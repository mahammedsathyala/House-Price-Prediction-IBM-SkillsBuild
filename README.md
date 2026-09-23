# 🏠 House Price Prediction Using Machine Learning

A complete end-to-end Machine Learning project that analyzes housing data and predicts house prices using multiple regression models. Built as a college internship data analytics project.

---

## 📌 Project Overview

| Detail | Value |
|--------|-------|
| **Dataset** | King County, WA housing data (~4,600 records) |
| **Target** | `price` (USD) |
| **Models** | Linear Regression, Random Forest, Gradient Boosting, XGBoost |
| **Interface** | Streamlit web application |
| **Language** | Python 3.9+ |

---

## 📁 Project Structure

```
house-price-prediction/
│
├── data/
│   └── data.csv                  ← Dataset (original, unmodified)
│
├── src/
│   ├── data_understanding.py     ← Step 1: Dataset inspection & report
│   ├── data_cleaning.py          ← Steps 2 & 4: Cleaning + feature engineering
│   ├── eda.py                    ← Step 3: EDA visualizations
│   └── model_training.py         ← Steps 5 & 6: Model training & evaluation
│
├── models/
│   ├── best_model.pkl            ← Saved best model (after training)
│   ├── feature_columns.json      ← Feature list used by the model
│   ├── eval_results.json         ← All model evaluation metrics
│   └── feature_importance.json   ← Top feature importances
│
├── visualizations/               ← All generated charts (14 plots)
│
├── app/
│   └── streamlit_app.py          ← Web application (Steps 7, 8, 9)
│
├── main.py                       ← Master training script
├── requirements.txt              ← Python dependencies
└── README.md                     ← This file
```

---

## 🚀 Quick Start

### Step 1 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Train the Models

```bash
python main.py
```

This will:
- Inspect the dataset and print a full data report
- Clean & engineer features
- Generate 10+ EDA visualizations in `visualizations/`
- Train 4 regression models and evaluate them
- Save the best model to `models/best_model.pkl`
- Print a model comparison table

### Step 3 — Launch the Web Application

```bash
streamlit run app/streamlit_app.py
```

Open your browser at: **http://localhost:8501**

---

## 🔬 What the Pipeline Does

### Step 1 — Data Understanding
- Reports shape, dtypes, missing values, duplicates, outliers, and target distribution

### Step 2 — Data Cleaning
- Parses `date` → extracts `sale_year`, `sale_month`
- Removes duplicates
- Fills missing values (median/mode)
- Drops `street` (too high cardinality) and `country` (single value)
- Extracts zip code from `statezip`
- Label-encodes `city`
- Winsorises outliers in `price`, `sqft_living`, `sqft_lot` (1%–99%)

### Step 3 — EDA
10 publication-quality charts including price distribution, correlations, waterfront analysis, top cities by price, and more.

### Step 4 — Feature Engineering
| Feature | Description |
|---------|-------------|
| `house_age` | `sale_year − yr_built` |
| `was_renovated` | Binary flag |
| `renovation_age` | Years since last renovation |
| `total_sqft` | `sqft_above + sqft_basement` |
| `living_to_lot` | Living area ÷ lot size |
| `has_basement` | Binary flag |
| `sale_year`, `sale_month` | Extracted from `date` |

### Steps 5 & 6 — Model Training & Evaluation
Four models trained with 80/20 split, evaluated on MAE, RMSE, R²:

| Model | Expected R² |
|-------|------------|
| Linear Regression | ~0.65 |
| Random Forest | ~0.85 |
| Gradient Boosting | ~0.84 |
| XGBoost | ~0.86 |

Best model is automatically selected and saved.

### Steps 7–9 — Web Application
5-page Streamlit app:
1. **🏡 Predict Price** — Input house features, get instant price estimate
2. **📊 Dashboard** — Dataset overview, statistics, model comparison
3. **🔬 EDA Charts** — All 14 visualizations in interactive expandable panels
4. **🤖 Model Comparison** — Detailed metrics and charts for each model
5. **🧠 AI Insights** — 8 data-driven natural-language insights from the dataset

---

## 📊 Dataset Columns

| Column | Description |
|--------|-------------|
| `date` | Sale date |
| `price` | **Target** — Sale price in USD |
| `bedrooms` | Number of bedrooms |
| `bathrooms` | Number of bathrooms |
| `sqft_living` | Interior living space (sqft) |
| `sqft_lot` | Lot size (sqft) |
| `floors` | Number of floors |
| `waterfront` | Waterfront property (0/1) |
| `view` | View quality rating (0–4) |
| `condition` | Overall condition (1–5) |
| `sqft_above` | Above-ground square footage |
| `sqft_basement` | Basement square footage |
| `yr_built` | Year built |
| `yr_renovated` | Year renovated (0 = never) |
| `street` | Street address (dropped — too many unique values) |
| `city` | City name |
| `statezip` | State + zip code |
| `country` | Country (all USA — dropped) |

---

## 💡 Key Findings

- **Living area** is the strongest predictor of house price (correlation ~0.70)
- **Waterfront properties** sell for ~60–80% more on average
- **City location** is a significant driver (Seattle area cities command premium prices)
- **Condition rating** (1–5) has a clear monotonic relationship with price
- **XGBoost / Gradient Boosting** outperform simpler models significantly on this dataset

---

## 🎓 Viva Questions & Answers

**Q1. What is the target variable in this project?**  
A: The target variable is `price` — the sale price of a house in USD.

**Q2. Why was Linear Regression less accurate than Random Forest / XGBoost?**  
A: House prices have non-linear relationships with features (e.g., living area, location). Tree-based ensemble methods capture these non-linearities far better than linear models.

**Q3. What is feature engineering and why did you do it?**  
A: Feature engineering creates new informative columns from existing ones. For example, `house_age = sale_year − yr_built` is more meaningful to a model than raw `yr_built`.

**Q4. How did you prevent data leakage?**  
A: The train/test split was done before any fitting. The StandardScaler was part of a Pipeline, so it was fit only on training data and applied to test data — never the reverse.

**Q5. What is R² and what does your score mean?**  
A: R² (coefficient of determination) measures how much variance in price the model explains. An R² of 0.86 means the model explains 86% of the price variation — very good for real-estate data.

**Q6. Why did you drop the `street` column?**  
A: `street` had thousands of unique values (very high cardinality). Raw label encoding would mislead the model, and the useful location signal is already captured by `city` and `zip_code`.

**Q7. How did you handle outliers?**  
A: We used Winsorisation (capping) — values below the 1st percentile and above the 99th percentile in `price`, `sqft_living`, and `sqft_lot` were clipped to those boundaries. This preserves the records rather than deleting them.

**Q8. What evaluation metrics did you use and why?**  
A: MAE (average absolute error), RMSE (penalises large errors more), and R² (explained variance). RMSE is particularly important for house price prediction because very large prediction errors are costly.

**Q9. How does the Streamlit app make predictions?**  
A: The app loads the saved `best_model.pkl`, collects user inputs from the UI, applies the same feature engineering steps as training (house_age, city encoding, etc.), and calls `model.predict()`.

**Q10. Which city has the highest average house price in the dataset?**  
A: This is dynamically computed in the AI Insights page. In this King County dataset, cities like Medina and Mercer Island typically rank highest due to their affluent lakefront neighbourhoods.

---

## 🛠 Tech Stack

- **Python** 3.9+
- **Pandas** — Data manipulation
- **NumPy** — Numerical operations
- **Matplotlib / Seaborn** — Visualizations
- **Scikit-learn** — ML pipeline, preprocessing, models
- **XGBoost** — Gradient boosting model
- **Joblib** — Model serialization
- **Streamlit** — Web interface

---

## 👨‍💻 Author

Built as part of a **Data Analytics with AI** internship project.  
Dataset: King County, WA House Sales (USA)
