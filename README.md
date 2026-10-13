# Document Processing API

A Python REST API for analyzing CSV files and storing analysis results in PostgreSQL.

Built as a backend and cloud portfolio project with FastAPI, Pandas, SQLAlchemy,
Docker, GitHub Actions, and Google Cloud.

## Features

- Upload and analyze UTF-8 CSV files.
- Calculate row count, column names, and missing values per column.
- Save analysis results in PostgreSQL.
- Retrieve saved analyses by ID.
- Validate file extensions and reject invalid CSV data.
- Manage database schema changes with Alembic migrations.
- Run automated tests and Docker builds in GitHub Actions.
- Reject CSV files larger than 5 MiB before analysis.

The API stores analysis results, not the original uploaded files.

## Technology stack

- Python 3.12
- FastAPI and Pydantic
- Pandas
- PostgreSQL 16
- SQLAlchemy and psycopg
- Alembic
- pytest and HTTPX
- Docker and Docker Compose
- GitHub Actions
- Google Cloud Run, Cloud SQL, Artifact Registry, and Secret Manager

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Application health check |
| POST | `/files/analyze` | Analyze a CSV file and save the result |
| GET | `/files/analyses/{analysis_id}` | Retrieve a saved analysis |

`GET /health` checks that the application responds; it does not check database connectivity.

### Example

Upload a CSV file as the multipart form field `file`:

```csv
name,amount
Alice,10
Bob,
```

Example response:

```json
{
  "id": 1,
  "filename": "sample.csv",
  "row_count": 2,
  "columns": ["name", "amount"],
  "missing_values": {
    "name": 0,
    "amount": 1
  },
  "created_at": "2026-10-12T12:00:00Z"
}
```

The database generates `id` and `created_at`, so their values vary.

### Response codes

- `200` — successful analysis or retrieval.
- `400` — unsupported file extension, filename longer than 255 characters, or invalid CSV content.
- `404` — analysis not found.
- `422` — request validation error, such as a missing upload or an ID outside the integer range 1–2147483647.
- `503` — database operation failed.
- `413` — uploaded CSV exceeds the 5 MiB size limit.

## Application structure

```text
app/
├── main.py               # Application setup and router registration
├── api/
│   ├── dependencies.py   # Database session dependency
│   └── routes/           # HTTP endpoints
├── core/                 # Environment-based configuration
├── db/                   # Database engine and session setup
├── models/               # SQLAlchemy table definitions
├── repositories/         # Database queries and writes
├── schemas/              # Pydantic response schemas
└── services/             # CSV analysis logic

migrations/               # Alembic configuration and migration history
tests/                    # Service and API tests using SQLite
integration_tests/        # HTTP tests against a running API and PostgreSQL
.github/workflows/        # GitHub Actions CI
```

A CSV upload follows this flow:

```text
HTTP request
    → FastAPI route
    → Pandas analysis service
    → SQLAlchemy repository
    → PostgreSQL
    → Pydantic response
```

The routes handle HTTP concerns, the service processes CSV content,
and the repository handles database access.

## Prerequisites

For Docker-based development:

- Git
- Docker Desktop with Docker Compose

For local Python development and running tests:

- Python 3.12
- A virtual environment with dependencies from `requirements.txt`

Run the following commands from the repository root.

## Local configuration

Create a `.env` file in the repository root:

```dotenv
POSTGRES_PASSWORD=replace_with_your_local_password
POSTGRES_USER=app_user
POSTGRES_DB=document_processing
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

Replace the example password with your own local development password.
Do not commit `.env` or real credentials.

If the PostgreSQL volume already exists, use its existing database password.
Changing `.env` alone does not change the password stored in PostgreSQL.

Inside Docker Compose, the API connects to `db:5432`.
Applications running directly on Windows connect to `localhost:5433`.

## Run with Docker Compose

```powershell
docker compose up --build -d
```

Compose waits for PostgreSQL to become healthy, applies Alembic migrations,
then starts the API.

Open:

- Swagger UI: http://127.0.0.1:8081/docs
- Health check: http://127.0.0.1:8081/health

Host port `8081` maps to port `8080` inside the API container.

Useful commands:

```powershell
docker compose ps
docker compose logs api
docker compose down
```

PostgreSQL data is stored in the `postgres_data` volume.
`docker compose down` preserves this data.
Adding `-v` removes the volume and deletes the local database data.

## Run locally — Windows PowerShell

Create the virtual environment and install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start PostgreSQL and apply migrations:

```powershell
docker compose up -d db --wait
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Start the API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

Keep `app/`, `tests/`, and `integration_tests/` outside `.venv`.

## Database migrations

Alembic manages the database schema through versioned migration files.

Apply pending migrations:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Inspect the current database version and migration history:

```powershell
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic history
```

The initial migration creates the `file_analyses` table.

For a new database, use `upgrade head`.
For a database created before Alembic was introduced, verify that its schema
matches the initial migration before using `stamp`.
Stamping records a version without executing or validating the migration.

Migration downgrades can remove tables and data. Review them before execution.

## Tests

### Service and API tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

These tests use an in-memory SQLite database and override the application's
database dependency. They do not require a running PostgreSQL instance.

### Integration test

Start the isolated integration environment:

```powershell
docker compose -p document-processing-test -f compose.test.yaml up --build -d --wait --wait-timeout 120
```

Run all tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests integration_tests -v
```

The integration test sends real HTTP requests to the test API. It uploads a CSV,
checks the analysis response, and retrieves the saved result by ID.

The test API is available at `http://127.0.0.1:8082`.
Its PostgreSQL instance is separate from the normal development database.

The current suite contains 23 tests: 22 service/API tests and one integration test.

Remove the integration environment and its data after testing:

```powershell
docker compose -p document-processing-test -f compose.test.yaml down -v
```

## Continuous integration

GitHub Actions:

1. Installs Python dependencies.
2. Runs service and API tests.
3. Builds the Docker image.
4. Starts the integration API and PostgreSQL environment.
5. Applies migrations through the container startup command.
6. Runs the HTTP integration test.
7. Prints container logs on failure.
8. Cleans up the integration environment.

## Deployment workflow

Deployment is automated through the `Deploy to GCP` GitHub Actions workflow,
started manually with `Run workflow` on the `main` branch.

The workflow:

1. Runs the existing CI checks.
2. Builds and pushes an image tagged with the commit SHA and workflow run identifiers.
3. Updates and executes the Cloud Run migration job.
4. Updates the API only after migrations succeed.

GitHub authenticates to Google Cloud through Workload Identity Federation,
without a stored service account key. Access is restricted to this repository
and the `main` branch.

Deployments run sequentially to avoid concurrent migration executions
from this workflow.

## Google Cloud deployment

The application has been deployed and tested on Google Cloud.

| Service | Purpose |
|---|---|
| Cloud Run | Runs the API container |
| Cloud SQL | Hosts PostgreSQL 16 |
| Artifact Registry | Stores the Docker image |
| Secret Manager | Stores database passwords |
| Cloud Run Jobs | Runs Alembic migrations separately from the API |

Deployment flow:

```text
Build Docker image
    → Push image to Artifact Registry
    → Execute migration job
    → Deploy API to Cloud Run
    → Verify upload and retrieval
```

The container accepts its listening port through the `PORT` environment variable,
defaulting to `8080`.

### Identity and database access

The API and migration job use separate identities:

| Component | GCP service account | PostgreSQL user |
|---|---|---|
| API | `document-api-runtime` | `app_user` |
| Migration job | `document-api-migrations` | `migration_user` |

- The API user can read and insert analyses and use the ID sequence.
- The migration user creates and manages application tables.
- Each service account has access to its corresponding password secret.
- Passwords are not embedded in source code or the Docker image.

### Access the deployed API

The deployed service requires Google Cloud authentication.
Authorized users can open a local proxy:

```powershell
gcloud run services proxy document-api --region=europe-west1 --project=document-api-pc-2026 --port=8085
```

Then open http://127.0.0.1:8085/docs.

The proxy forwards requests to the API running in Google Cloud.
Stopping the proxy does not stop the cloud service or database.

## Scope and limitations

This is a learning and portfolio project, not a production-ready document platform.

- CSV is currently the only supported input format.
- CSV analysis is limited to files of at most 5 MiB. This does not limit the
  entire HTTP request before upload parsing or guarantee a maximum DataFrame
  memory footprint.
- There is no application-level user ownership or per-user isolation of analyses.
- Cloud access is restricted through Google Cloud IAM.
- Deployment is automated but requires manual initiation in GitHub Actions.
- Post-deployment HTTP checks are currently performed manually.
- The cloud environment is a temporary demo using trial credits.

Cloud SQL continues to consume resources while running, even when the API
receives no traffic. Cloud Run scaling settings do not stop the database
or impose a hard spending cap.
