# -*- coding: utf-8 -*-
"""
Step 1: Data Understanding
Inspects the raw dataset and prints a comprehensive report.
"""

import pandas as pd
import numpy as np


def understand_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    print("=" * 70)
    print("         HOUSE PRICE PREDICTION - DATA UNDERSTANDING REPORT")
    print("=" * 70)

    # Basic shape
    print("\n[Shape] {:,} rows  x  {} columns".format(df.shape[0], df.shape[1]))

    # Column info
    print("\n[Column Names and Data Types]")
    print(df.dtypes.to_string())

    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({"Missing": missing, "Pct (%)": missing_pct})
    print("\n[Missing Values]")
    has_missing = missing_df[missing_df["Missing"] > 0]
    if len(has_missing) > 0:
        print(has_missing.to_string())
    else:
        print("   No missing values found.")

    # Duplicates
    dups = df.duplicated().sum()
    print("\n[Duplicate Rows] {}".format(dups))

    # Unique values per column
    print("\n[Unique Values per Column]")
    for col in df.columns:
        print("   {:<20}: {:>6,}  unique values".format(col, df[col].nunique()))

    # Statistical summary
    print("\n[Statistical Summary - Numerical]")
    print(df.describe().round(2).to_string())

    # Categorical summary
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    print("\n[Categorical Columns ({})] {}".format(len(cat_cols), cat_cols))
    for col in cat_cols:
        top = df[col].value_counts().head(5)
        print("\n   [{}] Top-5 values:\n{}".format(col, top.to_string()))

    # Numerical columns
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print("\n[Numerical Columns ({})] {}".format(len(num_cols), num_cols))

    # Target variable
    if "price" in df.columns:
        print("\n[Target Variable - price]")
        print("   Min    : ${:,.0f}".format(df["price"].min()))
        print("   Max    : ${:,.0f}".format(df["price"].max()))
        print("   Mean   : ${:,.0f}".format(df["price"].mean()))
        print("   Median : ${:,.0f}".format(df["price"].median()))
        print("   Std    : ${:,.0f}".format(df["price"].std()))

    # Outlier quick check (IQR)
    print("\n[Outlier Detection - IQR Method - Numerical Features]")
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        n_out = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum()
        if n_out > 0:
            print("   {:<22}: {:4d} outliers ({:.1f}%)".format(
                col, n_out, n_out / len(df) * 100))

    # Data quality observations
    print("\n[Data Quality Observations]")
    if "yr_renovated" in df.columns:
        zero_reno = (df["yr_renovated"] == 0).sum()
        print("   yr_renovated = 0 (not renovated): {:,} rows ({:.1f}%)".format(
            zero_reno, zero_reno / len(df) * 100))
    if "sqft_basement" in df.columns:
        zero_base = (df["sqft_basement"] == 0).sum()
        print("   sqft_basement = 0 (no basement)  : {:,} rows ({:.1f}%)".format(
            zero_base, zero_base / len(df) * 100))
    if "waterfront" in df.columns:
        wf = df["waterfront"].value_counts()
        print("   Waterfront distribution:\n{}".format(wf.to_string()))

    print("\n" + "=" * 70)
    return df


if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = understand_data(os.path.join(base, "data", "data.csv"))
