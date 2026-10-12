import os
import httpx

def test_upload_and_retrieve_analysis():
    base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8082")

    with httpx.Client(base_url = base_url, timeout=10.0) as client:
        upload_response = client.post(
            "/files/analyze",
            files={
                "file": (
                    "integration.csv",
                    b"name,amount\nAlice,10\nBob,\n",
                    "text/csv",
                )
            }
        )

        assert upload_response.status_code == 200, upload_response.text
        saved = upload_response.json()

        assert saved["id"] > 0
        assert saved["created_at"]
        assert saved["filename"] == "integration.csv"
        assert saved["row_count"] == 2
        assert saved["columns"] == ["name", "amount"]
        assert saved["missing_values"] == {"name": 0, "amount": 1}

        get_response = client.get(f"/files/analyses/{saved['id']}")

        assert get_response.status_code == 200, get_response.text
        assert get_response.json() == saved