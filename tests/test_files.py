from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


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
