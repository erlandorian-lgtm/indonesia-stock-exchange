import json
import uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from google.cloud import bigquery

PROJECT_ID = "ihsg-pipeline-515707"
DATASET_ID = "ihsg_warehouse"
LOCATION = "asia-southeast2"

DATA_DIR = Path("data/processed")

def load_json(filename):
    path = DATA_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def transform_ihsg(records):
    return [
        {
            "trade_date": r["Date"],
            "open": r["Open"],
            "high": r["High"],
            "low": r["Low"],
            "close": r["Close"],
            "volume": r["Volume"],
            "ingested_at_utc": r["ingested_at_utc"],
        }
        for r in records
    ]

def transform_bi(records):
        return [
        {
            "rate_date": r["rate_date"],
            "currency": r["Mata Uang"],
            "buy_rate": r["Nilai Beli"],
            "sell_rate": r["Nilai Jual"],
            "ingested_at_utc": r["ingested_at_utc"],
        }
        for r in records
    ]

def transform_cnn(records):
    ingested_at = datetime.now(timezone.utc).isoformat()
    articles = []

    for r in records:
        published = parsedate_to_datetime(r["pubDate"])

        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)

        articles.append({
            "guid" : r["guid"],
            "title" : r["title"],
            "link" : r["link"],
            "pub_date_raw" : r["pubDate"],
            "published_utc" : published.astimezone(timezone.utc).isoformat(),
            "ingested_at_utc" : ingested_at
        })
    return articles

def load_and_merge(client, table_name, records, schema, keys):
    if not records:
        raise ValueError(f"No records found for {table_name}")

    dataset = f"{PROJECT_ID}.{DATASET_ID}"
    destination = f"{dataset}.{table_name}"

    staging_name = f"__stg__{table_name}_{uuid.uuid4().hex[:8]}"
    staging = f"{dataset}.{staging_name}"

    # Create destination table if it does not exist
    table = bigquery.Table(destination, schema=schema)
    client.create_table(table, exists_ok=True)

    # Load records into a temporary staging table
    job_config = bigquery.LoadJobConfig(
          schema=schema,
          write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = client.load_table_from_json(
        records, staging, job_config=job_config,
    )
    job.result()

    columns = [field.name for field in schema]
    update_columns = [c for c in columns if c not in keys]

    on_condition = " AND ".join(
        f"T.{key} = S.{key}" for key in keys
    )

    update_clause = ", ".join(
        f"T.{column} = S.{column}"
        for column in update_columns
    )

    insert_columns = ", ".join(columns)
    insert_values = ", ".join(f"S.{c}" for c in columns)

    merge_sql = f"""
        MERGE `{destination}` T
        USING `{staging}` S 
        ON {on_condition}          
    
        WHEN MATCHED THEN 
            UPDATE SET {update_clause}

        WHEN NOT MATCHED THEN 
            INSERT ({insert_columns})
            VALUES ({insert_values})
    """

    client.query(merge_sql).result()

    # Remove staging table after successful merge
    client.delete_table(staging, not_found_ok=True)

    print(f"{table_name}: {len(records)} records merge successfully")

def main():
    client = bigquery.Client(
        project=PROJECT_ID,
        location=LOCATION,
    )

    ihsg_schema = [
        bigquery.SchemaField("trade_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("open", "FLOAT64"),
        bigquery.SchemaField("high", "FLOAT64"),
        bigquery.SchemaField("low", "FLOAT64"),
        bigquery.SchemaField("close", "FLOAT64"),
        bigquery.SchemaField("volume", "INT64"),
        bigquery.SchemaField("ingested_at_utc", "TIMESTAMP")
    ]

    bi_schema = [
        bigquery.SchemaField("rate_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("currency", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("buy_rate", "NUMERIC"),
        bigquery.SchemaField("sell_rate", "NUMERIC"),
        bigquery.SchemaField("ingested_at_utc", "TIMESTAMP")
    ]

    cnn_schema = [
        bigquery.SchemaField("guid", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("link", "STRING"),
        bigquery.SchemaField("pub_date_raw", "STRING"),
        bigquery.SchemaField("published_utc", "TIMESTAMP"),
        bigquery.SchemaField("ingested_at_utc", "TIMESTAMP")
    ]

    ihsg = transform_ihsg(load_json("ihsg_processed.json"))
    bi = transform_bi(load_json("bi_processed.json"))
    cnn = transform_cnn(load_json("cnn_articles.json"))

    load_and_merge(
        client, "raw_ihsg_daily", ihsg, ihsg_schema, ["trade_date"]
    )

    load_and_merge(
        client, "raw_bi_jisdor", bi, bi_schema, ["rate_date", "currency"]
    )

    load_and_merge(
        client, "raw_cnn_articles", cnn, cnn_schema, ["guid"]
    )

if __name__ == "__main__":
    main()