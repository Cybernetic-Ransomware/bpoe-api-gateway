# Configuration Guide

The gateway relies on environment variables loaded through `python-decouple`. This document complements the auto-generated API reference by describing recommended practices, `.env` placement, and validation rules.

## Environment loading

!!! note
    - The application searches for `.env` files inside `./docker` by default. Copy `docker/.env.template` to `docker/.env` and keep it out of version control.
    - When running locally, you can also export these variables to your shell (or replicate the file in project root) as long as `config.search_path` points to the correct directory.

## Core variables

| Variable | Purpose | Notes |
| --- | --- | --- |
| `APP_SECRET_KEY` | Secret used by Starlette's SessionMiddleware | Must be unique per environment; otherwise attackers can forge cookies. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins allowed when cookies/credentials are used | Schemes (`http://` or `https://`) are required; the code trims trailing `/`. Empty value raises a `RuntimeError`. |
| `APP_CLIENT_ID` / `AUTH0_CLIENT_ID` | Auth0 SPA client / M2M client identifiers | SPA client drives the browser login; M2M client is used during `/exchange-token`. |
| `AUTH0_CLIENT_SECRET` | Confidential secret used for code exchange | Never commit this value; rely on secret stores in prod. |
| `AUTH0_DOMAIN`, `AUTH0_API_AUDIENCE`, `AUTH0_ISSUER`, `AUTH0_ALGORITHMS` | Auth0 tenant metadata | `AUTH0_ALGORITHMS` defaults to `RS256`; issuer must end with `/`. |
| `APP_ALLLOWED_CALLBACK_URL` | Redirect URI used after Auth0 login | Make sure it matches the SPA registration in Auth0. |
| `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`, `SENTRY_PROFILES_SAMPLE_RATE` | Observability configuration | DSN optional for local dev; sample rates default to `0.0` to avoid noise. |

## Validation behaviour

`src.config` enforces basic data quality:

- Empty `CORS_ALLOWED_ORIGINS` raises a `RuntimeError`.
- Every origin must start with `http://` or `https://`. Misconfigured entries are rejected at startup.
- Origins are normalized by stripping whitespace and trailing `/`.

If you want different origin sets per environment, define multiple `.env` files (e.g. `docker/.env.dev`, `.env.stg`) and point `config.search_path` or CI pipeline to the correct file before launching.

## Sample workflow

```bash
cp docker/.env.template docker/.env
sed -i 's/APP_SECRET_KEY=/APP_SECRET_KEY=local-secret-123/' docker/.env
# fill Auth0 & Sentry values
poetry run uvicorn src.main:app --reload
```

For containerized deployments use the same variables but distribute them via orchestrator secrets (Docker/Compose `.env`, Kubernetes secrets, etc.).
