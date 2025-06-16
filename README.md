# API Gateway for BPOE app
This repository contains a gateway application used to orchestrate communication in Be Part Of the Event application.

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
### Deploy
1. Clone the repository:
      ```powershell
      git clone https://github.com/Cybernetic-Ransomware/bpoe-api-gateway.git
      ```
2. Set .env file based on the template.
3. Run using Docker:
      ```powershell
      docker-compose -f ./docker/docker-compose.yml up --build
      ```
### Dev-instance
1. Clone the repository:
      ```powershell
      git clone https://github.com/Cybernetic-Ransomware/bpoe-api-gateway.git
      ```
2. Set .env file based on the template.
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

## Testing
#### Postman
- The repository include a Postman collection with ready-to-import webhook mockers

#### Pytest
```powershell
poetry install --with dev
poetry run pytest
```

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

## Useful links and documentation
- API Gateway microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe-api-gateway.git)
- Databases handler microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe_events_db_handler)
- OCR microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe-ocr)
- Reports microservice: [GitHub](https://github.com/Cybernetic-Ransomware/bpoe_events_reports)
