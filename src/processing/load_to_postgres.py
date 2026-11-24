import json
import os
import psycopg
from email.utils import parsedate_to_datetime
from datetime import timezone, datetime
from pathlib import Path

def load_json(path):
    with open(path,"r", encoding="utf-8") as file:
        return json.load(file)

def main():
    conn = psycopg.connect(
        host="db",
        port=5432,
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
    )

    try:
        with conn.cursor() as cur:

            # Load IHSG 
            ihsg_records = load_json("data/processed/ihsg_processed.json")

            cur.executemany(
                """
                INSERT INTO ihsg_daily (
                    trade_date, open, high, low, close, volume, 
                    ingested_at_utc
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trade_date) DO NOTHING
                """,
                [
                    (
                        r["Date"], r["Open"], r["High"],
                        r["Low"], r["Close"], r["Volume"],
                        r["ingested_at_utc"]
                    )
                    for r in ihsg_records
                ]
            )
            print(f"IHSG records processed: {len(ihsg_records)}")

            # Load BI Jisdor
            bi_records = load_json("data/processed/bi_processed.json")

            cur.executemany(
                """
                INSERT INTO bi_jisdor (
                    rate_date, currency, buy_rate, sell_rate,
                    ingested_at_utc
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (rate_date, currency) DO NOTHING
                """, 
                [
                    (
                        r["rate_date"], r["Mata Uang"], r["Nilai Beli"],
                        r["Nilai Jual"], r["ingested_at_utc"]
                    )
                    for r in bi_records
                ]
            )
            print(f"BI records processed: {len(bi_records)}")

            # Load CNN articles
            cnn_records = load_json("data/processed/cnn_articles.json")

            cur.executemany(
                """
                INSERT INTO cnn_articles (
                guid, title, link, pub_date_raw, published_utc,
                ingested_at_utc
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (guid) DO NOTHING
                """,
                [
                    (r["guid"], r["title"], r["link"],
                     r["pubDate"], parsedate_to_datetime(r["pubDate"]).astimezone(timezone.utc),
                     datetime.now(timezone.utc)
                    )
                    for r in cnn_records
                ]
            )
            print(f"CNN records processed: {len(cnn_records)}")

        conn.commit()
        print("All data loaded successfully.")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()

