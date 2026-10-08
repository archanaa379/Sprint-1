"""
data_visualization.py
Creates the four project visualizations and saves them to /Visualizations.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from exploratory_analysis import KEY_INDICATORS, country_profile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIZ_DIR = os.path.join(BASE_DIR, "Visualizations")
os.makedirs(VIZ_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="deep")


def _save(fig, name):
    path = os.path.join(VIZ_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_distributions(panel):
    cols = [("GDP_Growth_Pct", "GDP Growth (annual %)"),
            ("Inflation_Pct", "Inflation, GDP deflator (annual %)"),
            ("GNI_Per_Capita", "GNI per capita (current US$)"),
            ("Life_Expectancy", "Life expectancy (years)")]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    for ax, (c, title) in zip(axes.ravel(), cols):
        sns.histplot(panel[c].dropna(), kde=True, bins=25, ax=ax, color="#2a6f97")
        med = panel[c].median()
        ax.axvline(med, color="crimson", ls="--", label=f"Median = {med:,.1f}")
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("")
        ax.legend()
    fig.suptitle("Distribution of Key Economic and Social Indicators (20 countries, 2016-2025)",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "distribution_analysis.png")


def plot_trends(panel):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # Panel 1: GDP growth for every country (faint) + average (bold)
    for country, g in panel.groupby("Country"):
        axes[0].plot(g["Year"], g["GDP_Growth_Pct"], color="grey", alpha=0.35, lw=1)
    avg = panel.groupby("Year")["GDP_Growth_Pct"].mean()
    axes[0].plot(avg.index, avg.values, color="crimson", lw=3, marker="o",
                 label="Average of 20 countries")
    axes[0].axhline(0, color="black", lw=0.8)
    axes[0].axvline(2020, color="orange", ls="--", label="2020")
    axes[0].set_title("GDP Growth (annual %) over time", fontweight="bold")
    axes[0].set_xlabel("Year"); axes[0].set_ylabel("GDP growth (%)")
    axes[0].legend()

    # Panel 2: GDP (trillions US$) for the 6 largest economies
    top = (panel.groupby("Country")["GDP_USD"].mean().nlargest(6).index)
    for c in top:
        g = panel[panel["Country"] == c]
        axes[1].plot(g["Year"], g["GDP_USD"] / 1e12, marker="o", label=c)
    axes[1].set_title("GDP of the 6 largest economies (US$ trillions)", fontweight="bold")
    axes[1].set_xlabel("Year"); axes[1].set_ylabel("GDP (US$ trillions)")
    axes[1].legend()
    fig.tight_layout()
    return _save(fig, "trend_analysis.png")


def plot_categories(panel):
    prof = country_profile(panel)
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    p1 = prof["GNI_Per_Capita"].sort_values()
    axes[0].barh(p1.index, p1.values, color=sns.color_palette("viridis", len(p1)))
    axes[0].set_title("Average GNI per capita by country (US$)", fontweight="bold")
    axes[0].set_xlabel("GNI per capita (current US$)")

    p2 = prof["GDP_Growth_Pct"].sort_values()
    colors = ["#c0392b" if v < 2 else "#27ae60" for v in p2.values]
    axes[1].barh(p2.index, p2.values, color=colors)
    axes[1].set_title("Average GDP growth by country (%)", fontweight="bold")
    axes[1].set_xlabel("Average annual GDP growth (%)  [red = below 2%]")
    fig.tight_layout()
    return _save(fig, "category_analysis.png")


def plot_correlation(panel):
    corr = panel[KEY_INDICATORS].corr()
    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax,
                annot_kws={"size": 8})
    ax.set_title("Correlation Matrix of Key Indicators", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "correlation_analysis.png")


def generate_all(panel):
    return [plot_distributions(panel), plot_trends(panel),
            plot_categories(panel), plot_correlation(panel)]


if __name__ == "__main__":
    from data_loading import load_raw_data
    from data_cleaning import clean_raw_data, to_wide_panel
    panel = to_wide_panel(clean_raw_data(load_raw_data()))
    for p in generate_all(panel):
        print("Saved:", p)