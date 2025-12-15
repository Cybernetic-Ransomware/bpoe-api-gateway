# API Gateway for BPOE app
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-ASGI-009688?logo=fastapi&logoColor=white)
![Auth0](https://img.shields.io/badge/Auth0-OAuth2-orange?logo=auth0&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Sentry](https://img.shields.io/badge/Sentry-Monitoring-362D59?logo=sentry&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-Dependencies-60A5FA?logo=poetry&logoColor=white)
![MkDocs](https://img.shields.io/badge/MkDocs-Material-3D6DAD?logo=mkdocs&logoColor=white)

This repository contains a gateway application used to orchestrate communication in Be Part Of the Event application.

## Tech Stack
- FastAPI gateway with Starlette middleware (sessions, CORS) and Auth0 authentication helpers.
- Python 3.12 managed via Poetry (production + dev dependency groups).
- Sentry SDK for error monitoring, tracing, and profiling.
- Docker Compose setup for local orchestration of dependencies and the API gateway.
- Postman collection (`FAstAPI with Aoth0.postman_collection.json`) and static frontend (`index.html`) for manual auth flows. The HTML file is a developer helper only; production SPA/clients should replicate the PKCE/state flow on their side instead of referencing this file directly.

## Overview
The purpose of this project is to build frame for the microservices.

## Features
- 2 kinds of frontends communication (web, mobile),
- Auth0 authorisation,
- gateway for:
  - OCR,
  - events service,
  - receipt service,
  - statement/reports service.

## Requirements
- Python >=3.12.7 with poetry package manager
- Docker Desktop / Docker + Compose

## Getting Started (Windows)
> Tip: before running any command copy `docker/.env.template` to `docker/.env` (and to the project root if you alter `config.search_path`). Fill in the Auth0 credentials, session secret, CORS allow-list, and optional Sentry values directly in that file—the inline comments explain every variable.

### Deploy
1. Clone the repository:
      ```powershell
      git clone https://github.com/Cybernetic-Ransomware/bpoe-api-gateway.git
      ```
2. Configure environment variables: `cp docker/.env.template docker/.env` and update the values.
3. Run using Docker:
      ```powershell
      docker-compose -f ./docker/docker-compose.yml up --build
      ```
### Dev-instance
1. Clone the repository:
      ```powershell
      git clone https://github.com/Cybernetic-Ransomware/bpoe-api-gateway.git
      ```
2. Configure environment variables: `cp docker/.env.template docker/.env` and update the values (they are required even for local dev).
3. Install poetry:
      ```powershell
      pip install poetry
      ```
4. Install dependencies:
      ```powershell
      poetry install --with dev
      ```
5. Install pre-commit hooks:
      ```powershell
      poetry run pre-commit install
      poetry run pre-commit autoupdate
      poetry run pre-commit run --all-files
      ```
6. Run the application locally:
      ```powershell
      poetry run uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
      ```
#### Versioning & Releases
1. Daily Commits: Stage your changes and create commits through Commitizen to keep messages consistent:
      ```powershell
      git add .
      poetry run cz commit
      ```


## Testing
#### Postman
- The repository include a Postman collection with ready-to-import webhook mockers

#### Pytest
```powershell
poetry install --with dev
poetry run pytest
```
- Tests automatically load configuration from `.env.test` (see `tests/conftest.py`). Adjust this file to point at staging tenants or fake credentials when needed.

#### Ruff
```powershell
poetry install --with dev
poetry run ruff check
```

#### Mypy
```powershell
poetry install --with dev
poetry run mypy .\src\
```

#### Codespell
```powershell
poetry install --with dev
poetry run codespell
```

#### Simple Frontend:
```powershell
python -m http.server 8070
```

## Developer Docs
- The project ships with a MkDocs Material site under `doc/` that renders API reference straight from the Python docstrings via `mkdocstrings`.
- Edit navigation/content in `mkdocs.yml` and the `doc/` directory; auto-generated reference pages live in `doc/api/`.
- The `mkdocs.yml` config embeds Mermaid fences via `!!python/name` tags; because `check-yaml` cannot parse those safely, this file is excluded from the pre-commit hook (see `.pre-commit-config.yaml` comment for details).
- Serve docs locally while coding:
  ```powershell
  poetry run mkdocs serve
  ```
- Produce a static site (generated into `site/`) ready for hosting:
  ```powershell
  poetry run mkdocs build
  ```

## Observability (Sentry)
- The gateway is instrumented with `sentry_sdk` inside `src/main.py`. Set `SENTRY_DSN` (and the sampling rates) in your environment before starting the service so every exception, trace, and profile is captured in the proper project.
- Telemetry is activated only when `SENTRY_DSN` is provided; when left blank no events are sent, which is useful for local development.
- `send_default_pii` is disabled by default to avoid leaking user metadata. Enable it only if your compliance requirements allow attaching identities to errors.
- For local development you can either omit `SENTRY_DSN` or guard the initialization call to avoid noisy events. For CI/staging, consider reducing `traces_sample_rate`/`profiles_sample_rate` to avoid unnecessary volume.
- Consult the official [Sentry FastAPI documentation](https://docs.sentry.io/platforms/python/guides/fastapi/) for advanced configuration such as custom scrubbers or sampling rules.

## Useful links and documentation
- API Gateway microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe-api-gateway.git)
- Databases handler microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe_events_db_handler)
- OCR microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe-ocr)
- Reports microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe_events_reports)
