"""
data_cleaning.py
Cleans the raw World Bank extract and reshapes it for analysis.

Issues found in the raw file:
  1. Footer / blank rows at the bottom ("Data from database...", "Last Updated...")
  2. Missing values are written as '..' instead of blank/NaN
  3. Year columns are named like '2016 [YR2016]'
  4. Data is in wide format (one column per year)
"""
import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "Dataset", "cleaned_dataset.csv")

# Short, readable names for the indicators used in the analysis
SHORT_NAMES = {
    "GDP (current US$)": "GDP_USD",
    "GDP growth (annual %)": "GDP_Growth_Pct",
    "GNI per capita, Atlas method (current US$)": "GNI_Per_Capita",
    "Population, total": "Population",
    "Population growth (annual %)": "Population_Growth_Pct",
    "Life expectancy at birth, total (years)": "Life_Expectancy",
    "Fertility rate, total (births per woman)": "Fertility_Rate",
    "Mortality rate, under-5 (per 1,000 live births)": "Under5_Mortality",
    "Exports of goods and services (% of GDP)": "Exports_Pct_GDP",
    "Imports of goods and services (% of GDP)": "Imports_Pct_GDP",
    "Foreign direct investment, net inflows (BoP, current US$)": "FDI_Inflows_USD",
    "Inflation, GDP deflator (annual %)": "Inflation_Pct",
    "Military expenditure (% of GDP)": "Military_Exp_Pct_GDP",
    "Mobile cellular subscriptions (per 100 people)": "Mobile_Subs_Per100",
    "Electric power consumption (kWh per capita)": "Electric_kWh_Per_Capita",
    "Industry (including construction), value added (% of GDP)": "Industry_Pct_GDP",
    "Agriculture, forestry, and fishing, value added (% of GDP)": "Agriculture_Pct_GDP",
    "Gross capital formation (% of GDP)": "Capital_Formation_Pct_GDP",
    "Urban population growth (annual %)": "Urban_Pop_Growth_Pct",
}


def clean_raw_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a long-format, clean dataframe: Country, Code, Indicator, Year, Value."""
    df = raw.copy()

    # 1. Drop footer / completely blank rows
    df = df.dropna(subset=["Country Code"])
    df = df[df["Country Code"].str.len() == 3]

    # 2. Rename year columns '2016 [YR2016]' -> '2016'
    df.columns = [c.split(" [")[0] for c in df.columns]

    # 3. Replace '..' with NaN
    df = df.replace("..", np.nan)

    # 4. Reshape wide -> long
    year_cols = [c for c in df.columns if c.isdigit()]
    long_df = df.melt(
        id_vars=["Country Name", "Country Code", "Series Name", "Series Code"],
        value_vars=year_cols,
        var_name="Year",
        value_name="Value",
    )

    # 5. Fix data types
    long_df["Year"] = long_df["Year"].astype(int)
    long_df["Value"] = pd.to_numeric(long_df["Value"], errors="coerce")

    # 6. Tidy column names
    long_df = long_df.rename(columns={
        "Country Name": "Country",
        "Country Code": "Country_Code",
        "Series Name": "Indicator",
        "Series Code": "Indicator_Code",
    })

    # 7. Remove duplicates
    long_df = long_df.drop_duplicates()
    return long_df.reset_index(drop=True)


def to_wide_panel(long_df: pd.DataFrame, indicators=None) -> pd.DataFrame:
    """One row per Country-Year, one column per (short-named) indicator."""
    d = long_df.copy()
    d["Short"] = d["Indicator"].map(SHORT_NAMES)
    d = d.dropna(subset=["Short"])
    if indicators:
        d = d[d["Short"].isin(indicators)]
    panel = d.pivot_table(index=["Country", "Country_Code", "Year"],
                          columns="Short", values="Value").reset_index()
    panel.columns.name = None
    return panel


def missing_report(long_df: pd.DataFrame) -> pd.DataFrame:
    """Percent missing per indicator, sorted highest first."""
    return (long_df.groupby("Indicator")["Value"]
            .apply(lambda s: s.isna().mean() * 100)
            .sort_values(ascending=False)
            .rename("Missing_Pct")
            .reset_index())


if __name__ == "__main__":
    from data_loading import load_raw_data
    raw = load_raw_data()
    clean = clean_raw_data(raw)
    clean.to_csv(CLEAN_PATH, index=False)
    print("Saved:", CLEAN_PATH, clean.shape)