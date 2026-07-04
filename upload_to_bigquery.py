import logging
import os
from pathlib import Path

from google.cloud import bigquery

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CREDENTIALS_PATH = BASE_DIR / "credentials.json"


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def configure_google_credentials() -> None:
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path:
        return

    if DEFAULT_CREDENTIALS_PATH.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(DEFAULT_CREDENTIALS_PATH)
        logging.getLogger(__name__).warning(
            "GOOGLE_APPLICATION_CREDENTIALS is not set; using local credentials.json fallback."
        )
        return

    raise RuntimeError(
        "Missing GOOGLE_APPLICATION_CREDENTIALS and no local credentials.json fallback was found."
    )


def main() -> None:
    configure_logging()
    configure_google_credentials()

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "zenith-capital-498002")
    dataset = os.getenv("BIGQUERY_DATASET", "zenith_raw")
    client = bigquery.Client(project=project_id)

    tables = {
        f"{dataset}.raw_equity_prices": BASE_DIR / "raw_equity_prices.csv",
        f"{dataset}.raw_macro_indicators": BASE_DIR / "raw_macro_indicators.csv",
    }

    for table_id, csv_path in tables.items():
        if not csv_path.exists():
            raise FileNotFoundError(f"Expected input file was not found: {csv_path}")

        full_table_id = f"{project_id}.{table_id}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )

        with csv_path.open("rb") as csv_file:
            job = client.load_table_from_file(csv_file, full_table_id, job_config=job_config)

        job.result()
        table = client.get_table(full_table_id)
        logging.info("%s loaded with %s rows", table_id, table.num_rows)

    logging.info("=== BIGQUERY UPLOAD COMPLETE ===")


if __name__ == "__main__":
    main()
