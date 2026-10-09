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
    assert response.json() == {
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