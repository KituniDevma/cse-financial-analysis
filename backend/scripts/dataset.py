import pandas as pd
from pathlib import Path

# ----------------- CONFIG -----------------
IN_CSV  = Path("data/processed/financial_data.csv")
OUT_CSV = Path("data/processed/clean_dataset.csv")
# ------------------------------------------

def build_clean_dataset(in_csv: Path, out_csv: Path):
    # Load the processed CSV
    df = pd.read_csv(in_csv)

    # Select only the required columns
    keep_cols = [
        "file_name",
        "quarter_end",
        "Revenue",
        "GrossProfit",
        "COGS",
        "OperatingExpenses",
        "OperatingIncome",
        "NetIncome",
    ]

    # Keep only the columns that exist
    df_clean = df[[c for c in keep_cols if c in df.columns]]

    # Save clean dataset
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(out_csv, index=False)

    print(f"✅ Clean dataset written to: {out_csv.resolve()}")
    print(df_clean.head())

if __name__ == "__main__":
    build_clean_dataset(IN_CSV, OUT_CSV)
