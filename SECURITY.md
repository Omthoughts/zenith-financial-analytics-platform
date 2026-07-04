# Security Policy

## Supported Setup

This repository is intended for local portfolio and demo use. Before running the pipeline:

1. Use [.env.example](/C:/Users/hp/zenith-capital-pipeline/.env.example) as a template for the environment variables you need to set in your shell or IDE.
2. Set `ALPHA_VANTAGE_API_KEY` and `FRED_API_KEY`.
3. Set `GOOGLE_APPLICATION_CREDENTIALS` to a local Google Cloud service-account JSON file that is not committed to Git.
4. Confirm the service account has only the minimum BigQuery permissions required for dataset loads and dbt execution.

## Sensitive Data Rules

- Do not commit service-account JSON files, `.env` files, tokens, or API keys.
- Rotate any credential immediately if it is ever pushed to a shared remote.
- Prefer environment variables for local secrets and CI secret stores for automation.

## Reporting

If you find a security issue in this project, report it privately to the repository owner and avoid opening a public issue with exploit details.
