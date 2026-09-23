"""
Step 2 & 4: Data Cleaning + Feature Engineering Pipeline
Returns a clean DataFrame ready for modelling.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


def load_and_clean(filepath: str, verbose: bool = True) -> pd.DataFrame:
    """Full cleaning & feature-engineering pipeline."""
    df = pd.read_csv(filepath)

    if verbose:
        print(f"[DATA CLEANING] Loaded {len(df):,} rows, {df.shape[1]} cols")

    # ------------------------------------------------------------------
    # 1. Parse date column → extract year & month
    # ------------------------------------------------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["sale_year"] = df["date"].dt.year
    df["sale_month"] = df["date"].dt.month
    df.drop(columns=["date"], inplace=True)

    # ------------------------------------------------------------------
    # 2. Remove true duplicate rows
    # ------------------------------------------------------------------
    before = len(df)
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    if verbose:
        print(f"[DATA CLEANING] Removed {before - len(df)} duplicate rows")

    # ------------------------------------------------------------------
    # 3. Handle missing values
    # ------------------------------------------------------------------
    # Fill numeric NaNs with median
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].median(), inplace=True)
            if verbose:
                print(f"[DATA CLEANING] Filled NaN in '{col}' with median")

    # Fill categorical NaNs with mode
    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].mode()[0], inplace=True)
            if verbose:
                print(f"[DATA CLEANING] Filled NaN in '{col}' with mode")

    # ------------------------------------------------------------------
    # 4. Drop 'street' — too high cardinality, low value as raw feature
    # ------------------------------------------------------------------
    if "street" in df.columns:
        df.drop(columns=["street"], inplace=True)

    # Drop 'country' — single value (USA)
    if "country" in df.columns:
        if df["country"].nunique() == 1:
            df.drop(columns=["country"], inplace=True)

    # ------------------------------------------------------------------
    # 5. Encode 'statezip' → keep the zip code as numeric
    # ------------------------------------------------------------------
    if "statezip" in df.columns:
        df["zip_code"] = df["statezip"].str.extract(r"(\d+)").astype(float)
        df.drop(columns=["statezip"], inplace=True)

    # ------------------------------------------------------------------
    # 6. Encode 'city' → label encoding (many cities)
    # ------------------------------------------------------------------
    if "city" in df.columns:
        le_city = LabelEncoder()
        df["city_encoded"] = le_city.fit_transform(df["city"].astype(str))
        # Keep city_name for display but drop original string col later
        df.rename(columns={"city": "city_name"}, inplace=True)

    # ------------------------------------------------------------------
    # 7. Outlier capping — price & sqft (winsorise at 1st/99th pct)
    # ------------------------------------------------------------------
    for col in ["price", "sqft_living", "sqft_lot"]:
        if col in df.columns:
            lo = df[col].quantile(0.01)
            hi = df[col].quantile(0.99)
            clipped = ((df[col] < lo) | (df[col] > hi)).sum()
            df[col] = df[col].clip(lower=lo, upper=hi)
            if verbose and clipped > 0:
                print(f"[DATA CLEANING] Winsorised {clipped} values in '{col}'")

    # ------------------------------------------------------------------
    # 8. Feature Engineering
    # ------------------------------------------------------------------

    # house_age: how old the house is (relative to sale year)
    if "yr_built" in df.columns and "sale_year" in df.columns:
        df["house_age"] = df["sale_year"] - df["yr_built"]
        df["house_age"] = df["house_age"].clip(lower=0)

    # was_renovated: binary flag
    if "yr_renovated" in df.columns:
        df["was_renovated"] = (df["yr_renovated"] > 0).astype(int)

    # renovation_age: years since renovation (0 if never renovated)
    if "yr_renovated" in df.columns and "sale_year" in df.columns:
        df["renovation_age"] = np.where(
            df["yr_renovated"] > 0,
            df["sale_year"] - df["yr_renovated"],
            0
        )

    # total_sqft: above + basement
    if "sqft_above" in df.columns and "sqft_basement" in df.columns:
        df["total_sqft"] = df["sqft_above"] + df["sqft_basement"]

    # living_to_lot ratio
    if "sqft_living" in df.columns and "sqft_lot" in df.columns:
        df["living_to_lot"] = df["sqft_living"] / (df["sqft_lot"] + 1)

    # has_basement flag
    if "sqft_basement" in df.columns:
        df["has_basement"] = (df["sqft_basement"] > 0).astype(int)

    # price_per_sqft (only used for analysis, not as a model feature to avoid leakage)
    # → excluded from model input columns

    if verbose:
        print(f"[DATA CLEANING] Final shape: {df.shape}")

    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    """Return the list of feature columns used for modelling."""
    drop_cols = {"price", "city_name"}
    return [c for c in df.columns if c not in drop_cols]


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = load_and_clean(os.path.join(base, "data", "data.csv"))
    print(df.head())
    print("Feature columns:", get_feature_columns(df))
