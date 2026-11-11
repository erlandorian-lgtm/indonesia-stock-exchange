import yfinance as yf
import pandas as pd 
from pathlib import Path

df = yf.download(
    "^JKSE", 
    start = "2024-10-20",
    end = "2026-10-23",
    multi_level_index = False
)

df = df.reset_index()

#Exporting Data into CSV File
output_path = Path("data/raw/ihsg/ihsg_daily.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False) 
