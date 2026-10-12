# Document Processing API

A Python REST API for analyzing CSV files, built with FastAPI and Pandas.

## Features

- Upload UTF-8 CSV files.
- Return row count and column names.
- Count missing values in each column.
- Reject unsupported file extensions and empty files.
- Automated service and API tests.
- Store analyses in PostgreSQL and retrieve them by ID.

## Technologies

Python, FastAPI, Pandas, PostgreSQL, SQLAlchemy, Pydantic, pytest, Docker, GitHub Actions.

## Run API and PostgreSQL with Docker Compose

Create a local `.env` file with `POSTGRES_PASSWORD` set to your database password.
For an existing database volume, use the password configured when it was created.
Keep this file out of Git.

```powershell
docker compose up --build -d
```

Open http://127.0.0.1:8081/docs to explore the containerized API.
Host port `8081` maps to port `8080` inside the API container.
Compose waits for PostgreSQL to become healthy, creates missing tables, then starts the API.
Table creation is sufficient for this stage; future schema changes will need migrations.

The API container connects to `db:5432` on the Compose network.
Applications running directly on Windows connect to `localhost:5433`.
Database data is kept in the `postgres_data` volume across container restarts.

```powershell
docker compose ps
docker compose logs api
docker compose down
```

`docker compose down` keeps database data. Adding `-v` deletes the database volume.

## Local setup — Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d db
.\.venv\Scripts\python.exe -m app.db.init_db
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to explore the API.
This also requires `POSTGRES_PASSWORD` in `.env`; local database defaults are
`localhost:5433`, user `app_user`, database `document_processing`.

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

## Endpoints

- GET /health — application health check.
- POST /files/analyze — CSV analysis.
- GET /files/analyses/{analysis_id} — saved analysis, or 404 if absent.

## Project structure

- app/api/routes — HTTP endpoints.
- app/services — CSV processing logic.
- app/schemas — response models.
- app/repositories — database queries and writes.
- app/models — database table definitions.
- app/db — database engine, sessions, and table initialization.
- tests — service and API tests.
