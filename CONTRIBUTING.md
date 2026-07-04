# Contributing

## Workflow

1. Keep changes scoped to a single concern.
2. Validate Python changes before committing.
3. Run `dbt run` and `dbt test` for transformation changes when BigQuery access is available.
4. Use clear, professional commit messages.

## Guardrails

- Do not commit secrets, `.env` files, or service-account JSON files.
- Do not replace working business logic with broad rewrites.
- Prefer small, reviewable changes with clear rollback paths.
