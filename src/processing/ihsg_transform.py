import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from scripts.saveandload import save_json

raw_data = Path("data/raw/ihsg/ihsg_daily.csv")
output_path = Path("data/processed/ihsg_processed.json")
rejected_output_path = Path("data/processed/ihsg_rejected.json")


def clean_ihsg_records(df):
    cleaned, rejected = [], []

    ingested_at = datetime.now(timezone.utc).isoformat()

    for record in df.to_dict(orient="records"):
        try:
            if any(pd.isna(value) for value in record.values()):
                raise ValueError("missing field")

            if any(record[col] <= 0 for col in ["Close", "High", "Low", "Open"]):
                raise ValueError("non-positive price")

            if record["Volume"] < 0:
                raise ValueError("negative volume")

            if record["High"] < max(record["Open"], record["Close"]):
                raise ValueError("high price below open or close")

            if record["Low"] > min(record["Open"], record["Close"]):
                raise ValueError("low price above open or close")

            record["Date"] = record["Date"].strftime("%Y-%m-%d")
            record["ingested_at_utc"] = ingested_at
            cleaned.append(record)

        except (ValueError, AttributeError) as e:
            record["reason"] = str(e)
            rejected.append(record)

    return cleaned, rejected


def main():
    df = pd.read_csv(raw_data)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Reject invalid dates
    invalid_dates = df[df["Date"].isna()].copy()
    df = df.dropna(subset=["Date"])

    cleaned, rejected = clean_ihsg_records(df)

    for record in invalid_dates.to_dict(orient="records"):
        record["reason"] = "invalid date"
        rejected.append(record)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove duplicate dates, keeping the first record
    cleaned_df = pd.DataFrame(cleaned)
    if not cleaned_df.empty:
        cleaned_df = cleaned_df.drop_duplicates(subset=["Date"], keep="first")
        cleaned = cleaned_df.to_dict(orient="records")

    save_json(cleaned, output_path)
    save_json(rejected, rejected_output_path)


if __name__ == "__main__":
    main()
