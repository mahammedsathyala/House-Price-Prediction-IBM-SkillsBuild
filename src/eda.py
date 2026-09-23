"""
Step 3: Exploratory Data Analysis
Generates and saves all EDA visualizations to the visualizations/ folder.
"""

import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_theme(style="darkgrid", palette="muted")
SAVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "visualizations"
)
os.makedirs(SAVE_DIR, exist_ok=True)


def _save(fig, name: str):
    path = os.path.join(SAVE_DIR, name)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("  Saved --> {}".format(path))
    return path


def run_eda(df: pd.DataFrame) -> dict:
    """Run all EDA plots. Returns dict of {title: filepath}."""
    saved = {}

    # 1. Price distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Price Distribution", fontsize=15, fontweight="bold")
    axes[0].hist(df["price"], bins=60, color="#4C72B0", edgecolor="white", alpha=0.85)
    axes[0].set_title("Price Histogram")
    axes[0].set_xlabel("Price (USD)")
    axes[0].set_ylabel("Count")
    axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
    axes[1].hist(np.log1p(df["price"]), bins=60, color="#DD8452", edgecolor="white", alpha=0.85)
    axes[1].set_title("Log(Price) Histogram")
    axes[1].set_xlabel("log(Price)")
    axes[1].set_ylabel("Count")
    saved["Price Distribution"] = _save(fig, "01_price_distribution.png")

    # 2. Price vs sqft_living
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df["sqft_living"], df["price"], alpha=0.25, s=10, color="#4C72B0")
    ax.set_title("Price vs Living Area (sqft)", fontsize=13, fontweight="bold")
    ax.set_xlabel("sqft_living")
    ax.set_ylabel("Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
    saved["Price vs sqft_living"] = _save(fig, "02_price_vs_sqft.png")

    # 3. Price vs bedrooms
    fig, ax = plt.subplots(figsize=(10, 6))
    bed_order = sorted(df["bedrooms"].unique())
    tmp = df.copy()
    tmp["bedrooms_str"] = tmp["bedrooms"].astype(str)
    bed_order_str = [str(b) for b in bed_order]
    sns.boxplot(data=tmp, x="bedrooms_str", y="price", order=bed_order_str,
                hue="bedrooms_str", palette="Blues_d", ax=ax, showfliers=False, legend=False)
    ax.set_title("Price by Number of Bedrooms", fontsize=13, fontweight="bold")
    ax.set_xlabel("Bedrooms")
    ax.set_ylabel("Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
    saved["Price vs Bedrooms"] = _save(fig, "03_price_vs_bedrooms.png")

    # 4. Price vs bathrooms
    fig, ax = plt.subplots(figsize=(12, 6))
    bath_order = sorted(df["bathrooms"].unique())
    tmp2 = df.copy()
    tmp2["bath_str"] = tmp2["bathrooms"].astype(str)
    bath_order_str = [str(b) for b in bath_order]
    sns.boxplot(data=tmp2, x="bath_str", y="price", order=bath_order_str,
                hue="bath_str", palette="Oranges_d", ax=ax, showfliers=False, legend=False)
    ax.set_title("Price by Number of Bathrooms", fontsize=13, fontweight="bold")
    ax.set_xlabel("Bathrooms")
    ax.set_ylabel("Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
    plt.xticks(rotation=45)
    saved["Price vs Bathrooms"] = _save(fig, "04_price_vs_bathrooms.png")

    # 5. Price vs condition
    fig, ax = plt.subplots(figsize=(9, 6))
    cond_means = df.groupby("condition")["price"].median().reset_index()
    sns.barplot(data=cond_means, x="condition", y="price", hue="condition",
                palette="viridis", ax=ax, legend=False)
    ax.set_title("Median Price by Condition (1=Poor to 5=Excellent)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Condition Rating")
    ax.set_ylabel("Median Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
    saved["Price vs Condition"] = _save(fig, "05_price_vs_condition.png")

    # 6. Price vs waterfront
    fig, ax = plt.subplots(figsize=(8, 6))
    wf_data = df.copy()
    wf_data["Waterfront"] = wf_data["waterfront"].map({0: "No Waterfront", 1: "Waterfront"})
    sns.boxplot(data=wf_data, x="Waterfront", y="price", hue="Waterfront",
                palette=["#5177a8", "#e07b39"], ax=ax, showfliers=False, legend=False)
    ax.set_title("Price: Waterfront vs Non-Waterfront", fontsize=13, fontweight="bold")
    ax.set_ylabel("Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
    saved["Price vs Waterfront"] = _save(fig, "06_price_vs_waterfront.png")

    # 7. Price vs floors
    fig, ax = plt.subplots(figsize=(9, 6))
    floor_means = df.groupby("floors")["price"].median().reset_index()
    sns.barplot(data=floor_means, x="floors", y="price", hue="floors",
                palette="cool", ax=ax, legend=False)
    ax.set_title("Median Price by Number of Floors", fontsize=13, fontweight="bold")
    ax.set_xlabel("Floors")
    ax.set_ylabel("Median Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
    saved["Price vs Floors"] = _save(fig, "07_price_vs_floors.png")

    # 8. Price vs year built
    fig, ax = plt.subplots(figsize=(14, 6))
    yr_means = df.groupby("yr_built")["price"].median().reset_index()
    ax.plot(yr_means["yr_built"], yr_means["price"], color="#4C72B0", linewidth=1.8)
    ax.fill_between(yr_means["yr_built"], yr_means["price"], alpha=0.15, color="#4C72B0")
    ax.set_title("Median Price by Year Built", fontsize=13, fontweight="bold")
    ax.set_xlabel("Year Built")
    ax.set_ylabel("Median Price (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
    saved["Price vs Year Built"] = _save(fig, "08_price_vs_yr_built.png")

    # 9. Correlation heatmap
    num_df = df.select_dtypes(include=[np.number]).copy()
    num_df.drop(columns=[c for c in ["city_encoded", "zip_code"] if c in num_df.columns], inplace=True)
    corr = num_df.corr()
    fig, ax = plt.subplots(figsize=(14, 11))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.4, ax=ax, annot_kws={"size": 8})
    ax.set_title("Correlation Heatmap", fontsize=14, fontweight="bold")
    plt.tight_layout()
    saved["Correlation Heatmap"] = _save(fig, "09_correlation_heatmap.png")

    # 10. Top cities by median price
    if "city_name" in df.columns:
        fig, ax = plt.subplots(figsize=(13, 7))
        city_price = (df.groupby("city_name")["price"]
                      .median()
                      .sort_values(ascending=False)
                      .head(20)
                      .reset_index())
        sns.barplot(data=city_price, x="price", y="city_name", hue="city_name",
                    palette="rocket", ax=ax, legend=False)
        ax.set_title("Top 20 Cities by Median House Price", fontsize=13, fontweight="bold")
        ax.set_xlabel("Median Price (USD)")
        ax.set_ylabel("City")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: "${:.1f}M".format(x/1e6)))
        saved["Top Cities by Price"] = _save(fig, "10_top_cities_by_price.png")

    print("\n[EDA] All {} charts saved to --> {}\n".format(len(saved), SAVE_DIR))
    return saved


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from data_cleaning import load_and_clean
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = load_and_clean(os.path.join(base, "data", "data.csv"))
    run_eda(df)
