# Zenith dbt Project

This dbt project transforms raw market and macroeconomic data loaded into BigQuery into analytics-ready models for downstream Power BI reporting.

## Model Layers

- `staging`: direct views over raw BigQuery tables.
- `intermediate`: reusable calculations such as equity returns and macro trend signals.
- `marts`: business-facing summary tables for executive reporting.

## Commands

```bash
dbt run
dbt test
```

## Expected Sources

- `zenith_raw.raw_equity_prices`
- `zenith_raw.raw_macro_indicators`
