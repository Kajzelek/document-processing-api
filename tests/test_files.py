import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize("prefix", ["a", "ą"])
def test_upload_accepts_filename_at_length_limit(prefix):
    filename = prefix * 251 + ".csv"
    response = client.post(
        "/files/analyze",
        files={"file": (filename, b"name\nAlice\n", "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["filename"] == filename


def test_upload_rejects_filename_above_length_limit(monkeypatch):
    def unexpected_save(*args, **kwargs):
        raise AssertionError("Invalid filename must not reach the repository.")

    monkeypatch.setattr("app.api.routes.files.save_analysis", unexpected_save)
    response = client.post(
        "/files/analyze",
        files={"file": ("a" * 252 + ".csv", b"name\nAlice\n", "text/csv")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Filename must not exceed 255 characters."}


@pytest.mark.parametrize("analysis_id", [0, -1, 2_147_483_648, 10**40])
def test_get_analysis_rejects_out_of_range_id(analysis_id, monkeypatch):
    def unexpected_query(*args, **kwargs):
        raise AssertionError("Invalid ID must not reach the repository.")

    monkeypatch.setattr("app.api.routes.files.get_analysis_by_id", unexpected_query)
    response = client.get(f"/files/analyses/{analysis_id}")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "analysis_id"]


@pytest.mark.parametrize("analysis_id", [1, 2_147_483_647])
def test_get_analysis_accepts_id_range_boundaries(analysis_id):
    response = client.get(f"/files/analyses/{analysis_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Analysis not found."}


def test_upload_valid_csv():
    response = client.post(
        "/files/analyze",
        files={
            "file": (
                "sample.csv",
                b"name,amount\nAlice,10\nBob,\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert result["id"] > 0
    assert result["created_at"]
    assert result["filename"] == "sample.csv"
    assert result["row_count"] == 2
    assert result["columns"] == ["name", "amount"]
    assert result["missing_values"] == {
        "name": 0,
        "amount": 1,
    }

    assert response.json() == {
        "id": result["id"],
        "created_at": result["created_at"],
        "filename": "sample.csv",
        "row_count": 2,
        "columns": ["name", "amount"],
        "missing_values": {
            "name": 0,
            "amount": 1,
        },
    }


def test_upload_rejects_wrong_extension():
    response = client.post(
        "/files/analyze",
        files={
            "file": (
                "sample.txt",
                b"name,amount\nAlice,10\n",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Please upload a CSV file."


def test_upload_rejects_empty_csv():
    response = client.post(
        "/files/analyze",
        files={"file": ("empty.csv", b"", "text/csv")},
    )

    assert response.status_code == 400


def test_upload_requires_file():
    response = client.post("/files/analyze")

    assert response.status_code == 422


def test_get_saved_analysis():
    upload_response = client.post(
        "/files/analyze",
        files={"file": ("sample.csv", b"name,amount\nAlice,10\nBob,\n", "text/csv")},
    )
    assert upload_response.status_code == 200
    saved_analysis = upload_response.json()

    response = client.get(f"/files/analyses/{saved_analysis['id']}")

    assert response.status_code == 200
    assert response.json() == saved_analysis


def test_get_missing_analysis():
    response = client.get("/files/analyses/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Analysis not found."}


def test_get_analysis_requires_integer_id():
    response = client.get("/files/analyses/not-a-number")

    assert response.status_code == 422


def test_get_analysis_database_unavailable(monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError

    def unavailable_database(session, analysis_id):
        raise SQLAlchemyError("Database unavailable")

    monkeypatch.setattr(
        "app.api.routes.files.get_analysis_by_id", unavailable_database
    )

    response = client.get("/files/analyses/1")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Could not retrieve the analysis. Please try again later."
    }

def test_upload_accepts_csv_at_size_limit(monkeypatch):
    content = b"name,amount\nAlice,10\n"

    monkeypatch.setattr(
        "app.api.routes.files.MAX_CSV_SIZE_BYTES",
        len(content),
    )

    response = client.post(
        "/files/analyze",
        files={"file": ("sample.csv", content, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["row_count"] == 1


def test_upload_rejects_csv_above_size_limit(monkeypatch):
    content = b"name,amount\nAlice,10\n"

    monkeypatch.setattr(
        "app.api.routes.files.MAX_CSV_SIZE_BYTES",
        len(content) - 1,
    )

    def unexpected_analysis(content):
        raise AssertionError("Oversized CSV must not be analyzed.")

    monkeypatch.setattr(
        "app.api.routes.files.analyze_csv_content",
        unexpected_analysis,
    )

    response = client.post(
        "/files/analyze",
        files={"file": ("sample.csv", content, "text/csv")},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "CSV file exceeds the size limit."
    }
