# Document Processing API

A Python REST API for analyzing CSV files, built with FastAPI and Pandas.

## Features

- Upload UTF-8 CSV files.
- Return row count and column names.
- Count missing values in each column.
- Reject unsupported file extensions and empty files.
- Automated service and API tests.

## Technologies

Python, FastAPI, Pandas, Pydantic, pytest.

## Local setup — Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to explore the API.

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

## Endpoints

- GET /health — application health check.
- POST /files/analyze — CSV analysis.

## Project structure

- app/api/routes — HTTP endpoints.
- app/services — CSV processing logic.
- app/schemas — response models.
- tests — service and API tests.