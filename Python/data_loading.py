"""
data_loading.py
Loads the raw World Bank (WDI) extract.
"""
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "Dataset", "raw_dataset.csv")


def load_raw_data(path: str = RAW_PATH) -> pd.DataFrame:
    """Read the raw CSV exactly as downloaded from World Bank DataBank."""
    return pd.read_csv(path)


def basic_overview(df: pd.DataFrame) -> None:
    """Print a quick structural overview of a dataframe."""
    print("Shape:", df.shape)
    print("\nColumns:", list(df.columns))
    print("\nData types:\n", df.dtypes)
    print("\nFirst 5 rows:\n", df.head())


if __name__ == "__main__":
    raw = load_raw_data()
    basic_overview(raw)