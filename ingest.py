import requests
import pandas as pd
import json
import os
import time

ALPHA_VANTAGE_KEY = "FFZFBIYMIQF7RPUC"
FRED_KEY = "46a84c08437b9833eeec3428a2ff0b2f"

tickers = ["AAPL", "MSFT", "GOOGL", "JPM", "SPY"]

print("=== ZENITH CAPITAL PIPELINE ===")
print("Fetching equity data from Alpha Vantage...")

all_data = []

for symbol in tickers:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={ALPHA_VANTAGE_KEY}"
    time.sleep(15)
    response = requests.get(url)
    data = response.json()
    
    if "Time Series (Daily)" in data:
        time_series = data["Time Series (Daily)"]
        for date, values in list(time_series.items())[:30]:
            all_data.append({
                "symbol": symbol,
                "date": date,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"])
            })
        print(f"  ✓ {symbol} — 30 days fetched")
    else:
        print(f"  ✗ {symbol} — {data}")

df_equity = pd.DataFrame(all_data)
df_equity.to_csv("raw_equity_prices.csv", index=False)
print(f"\nEquity data saved: {len(df_equity)} rows")

print("\nFetching macro data from FRED...")

fred_series = {
    "CPIAUCSL": "inflation_cpi",
    "FEDFUNDS": "fed_funds_rate",
    "UNRATE": "unemployment_rate",
    "GDP": "gdp"
}

macro_data = []

for series_id, name in fred_series.items():
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_KEY}&file_type=json&limit=30&sort_order=desc"
    response = requests.get(url)
    data = response.json()
    
    if "observations" in data:
        for obs in data["observations"]:
            if obs["value"] != ".":
                macro_data.append({
                    "series_id": series_id,
                    "indicator_name": name,
                    "date": obs["date"],
                    "value": float(obs["value"])
                })
        print(f"  ✓ {name} fetched")
    else:
        print(f"  ✗ {series_id} failed")

df_macro = pd.DataFrame(macro_data)
df_macro.to_csv("raw_macro_indicators.csv", index=False)
print(f"Macro data saved: {len(df_macro)} rows")

print("\n=== PIPELINE RUN COMPLETE ===")
print(f"Files created:")
print(f"  - raw_equity_prices.csv ({len(df_equity)} rows)")
print(f"  - raw_macro_indicators.csv ({len(df_macro)} rows)")