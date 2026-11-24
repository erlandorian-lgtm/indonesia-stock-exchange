import yfinance as yf
from datetime import date, timedelta 
from pathlib import Path

def main():
    df = yf.download(
        "^JKSE", 
        start = "2024-10-20",
        end = (date.today() + timedelta(days=1)).isoformat(),
        multi_level_index = False
    )
    
    if df.empty:
        raise ValueError("No IHSG data returned from Yahoo Finance")
    
    df = df.reset_index()

    # Exporting Data into CSV File
    output_path = Path("data/raw/ihsg/ihsg_daily.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False) 

    print(f"Downloaded {len(df)} IHSG Records")

if __name__ == "__main__":
    main()
