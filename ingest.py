import logging
import os
import time
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_DIR = Path(__file__).resolve().parent
EQUITY_OUTPUT_PATH = BASE_DIR / "raw_equity_prices.csv"
MACRO_OUTPUT_PATH = BASE_DIR / "raw_macro_indicators.csv"
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "JPM", "SPY"]


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_tickers() -> list[str]:
    configured = os.getenv("ZENITH_TICKERS")
    if not configured:
        return DEFAULT_TICKERS

    tickers = [ticker.strip().upper() for ticker in configured.split(",") if ticker.strip()]
    if not tickers:
        raise RuntimeError("ZENITH_TICKERS was provided but did not contain any valid symbols.")
    return tickers


def build_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_json(session: requests.Session, url: str) -> dict:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def main() -> None:
    configure_logging()
    logger = logging.getLogger(__name__)

    alpha_vantage_key = get_required_env("ALPHA_VANTAGE_API_KEY")
    fred_key = get_required_env("FRED_API_KEY")
    tickers = get_tickers()
    request_delay_seconds = float(os.getenv("ALPHA_VANTAGE_REQUEST_DELAY_SECONDS", "15"))
    session = build_session()

    logger.info("=== ZENITH CAPITAL PIPELINE ===")
    logger.info("Fetching equity data from Alpha Vantage...")

    all_data = []

    for symbol in tickers:
        url = (
            "https://www.alphavantage.co/query"
            f"?function=TIME_SERIES_DAILY&symbol={symbol}"
            f"&outputsize=compact&apikey={alpha_vantage_key}"
        )
        time.sleep(request_delay_seconds)
        data = fetch_json(session, url)

        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            for date, values in list(time_series.items())[:30]:
                all_data.append(
                    {
                        "symbol": symbol,
                        "date": date,
                        "open": float(values["1. open"]),
                        "high": float(values["2. high"]),
                        "low": float(values["3. low"]),
                        "close": float(values["4. close"]),
                        "volume": int(values["5. volume"]),
                    }
                )
            logger.info("%s: 30 days fetched", symbol)
        else:
            logger.warning("%s: unexpected response payload: %s", symbol, data)

    df_equity = pd.DataFrame(all_data)
    df_equity.to_csv(EQUITY_OUTPUT_PATH, index=False)
    logger.info("Equity data saved: %s rows", len(df_equity))

    logger.info("Fetching macro data from FRED...")

    fred_series = {
        "CPIAUCSL": "inflation_cpi",
        "FEDFUNDS": "fed_funds_rate",
        "UNRATE": "unemployment_rate",
        "GDP": "gdp",
    }

    macro_data = []

    for series_id, name in fred_series.items():
        url = (
            "https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}&api_key={fred_key}"
            "&file_type=json&limit=30&sort_order=desc"
        )
        data = fetch_json(session, url)

        if "observations" in data:
            for observation in data["observations"]:
                if observation["value"] != ".":
                    macro_data.append(
                        {
                            "series_id": series_id,
                            "indicator_name": name,
                            "date": observation["date"],
                            "value": float(observation["value"]),
                        }
                    )
            logger.info("%s fetched", name)
        else:
            logger.warning("%s failed with payload: %s", series_id, data)

    df_macro = pd.DataFrame(macro_data)
    df_macro.to_csv(MACRO_OUTPUT_PATH, index=False)
    logger.info("Macro data saved: %s rows", len(df_macro))

    logger.info("=== PIPELINE RUN COMPLETE ===")
    logger.info("Files created: %s, %s", EQUITY_OUTPUT_PATH.name, MACRO_OUTPUT_PATH.name)


if __name__ == "__main__":
    main()
