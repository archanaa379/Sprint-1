"""
exploratory_analysis.py
Statistical exploration of the cleaned World Bank panel data.
"""
import numpy as np
import pandas as pd

KEY_INDICATORS = [
    "GDP_Growth_Pct", "GNI_Per_Capita", "Inflation_Pct", "Exports_Pct_GDP",
    "Imports_Pct_GDP", "Life_Expectancy", "Fertility_Rate", "Under5_Mortality",
    "Population_Growth_Pct", "Industry_Pct_GDP", "Agriculture_Pct_GDP",
    "Capital_Formation_Pct_GDP", "Mobile_Subs_Per100", "Military_Exp_Pct_GDP",
]


def summary_statistics(panel: pd.DataFrame, cols=None) -> pd.DataFrame:
    cols = cols or KEY_INDICATORS
    return panel[cols].describe().T.round(2)


def missing_by_column(panel: pd.DataFrame) -> pd.DataFrame:
    m = panel.isna().sum().rename("Missing").to_frame()
    m["Missing_Pct"] = (m["Missing"] / len(panel) * 100).round(1)
    return m[m["Missing"] > 0].sort_values("Missing", ascending=False)


def country_profile(panel: pd.DataFrame) -> pd.DataFrame:
    """Average of key indicators per country across 2016-2025."""
    prof = (panel.groupby("Country")[
        ["GDP_USD", "GDP_Growth_Pct", "GNI_Per_Capita", "Inflation_Pct",
         "Life_Expectancy", "Exports_Pct_GDP", "Population"]
    ].mean().round(2))
    return prof.sort_values("GNI_Per_Capita", ascending=False)


def add_income_tier(profile: pd.DataFrame) -> pd.DataFrame:
    """Data-driven tiers: split countries into 3 groups by average GNI per capita."""
    p = profile.copy()
    p["Income_Tier"] = pd.qcut(p["GNI_Per_Capita"], 3,
                               labels=["Lower", "Middle", "Upper"])
    return p


def correlation_matrix(panel: pd.DataFrame, cols=None) -> pd.DataFrame:
    cols = cols or KEY_INDICATORS
    return panel[cols].corr().round(2)


def top_correlations(corr: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    pairs = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack()
    pairs = pairs.rename("Correlation").reset_index()
    pairs.columns = ["Indicator_1", "Indicator_2", "Correlation"]
    pairs["Abs"] = pairs["Correlation"].abs()
    return pairs.sort_values("Abs", ascending=False).head(n).drop(columns="Abs")


def detect_outliers_iqr(panel: pd.DataFrame, col: str) -> pd.DataFrame:
    q1, q3 = panel[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out = panel[(panel[col] < low) | (panel[col] > high)]
    return out[["Country", "Year", col]].sort_values(col, ascending=False)


def yearly_average(panel: pd.DataFrame, col: str) -> pd.Series:
    return panel.groupby("Year")[col].mean().round(2)


def covid_impact(panel: pd.DataFrame) -> pd.DataFrame:
    """GDP growth in 2019 vs 2020 vs 2021 per country."""
    t = panel[panel["Year"].isin([2019, 2020, 2021])].pivot(
        index="Country", columns="Year", values="GDP_Growth_Pct").round(2)
    t["Change_2019_to_2020"] = (t[2020] - t[2019]).round(2)
    return t.sort_values("Change_2019_to_2020")