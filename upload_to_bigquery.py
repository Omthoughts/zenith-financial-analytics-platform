import os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\hp\zenith-capital-pipeline\credentials.json"

client = bigquery.Client(project="zenith-capital-498002")

PROJECT = "zenith-capital-498002"

tables = {
    "zenith_raw.raw_equity_prices": r"C:\Users\hp\zenith-capital-pipeline\raw_equity_prices.csv",
    "zenith_raw.raw_macro_indicators": r"C:\Users\hp\zenith-capital-pipeline\raw_macro_indicators.csv"
}

for table_id, csv_path in tables.items():
    full_table_id = f"{PROJECT}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    with open(csv_path, "rb") as f:
        job = client.load_table_from_file(f, full_table_id, job_config=job_config)
    job.result()
    table = client.get_table(full_table_id)
    print(f"✓ {table_id} — {table.num_rows} rows loaded")

print("\n=== BIGQUERY UPLOAD COMPLETE ===")