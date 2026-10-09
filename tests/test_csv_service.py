import pytest

from app.services.csv_service import InvalidCsvError, analyze_csv_content


def test_analyze_csv_counts_rows_and_missing_values():
    content = (
        b"document_id,category,amount\n"
        b"1,invoice,120.50\n"
        b"2,report,\n"
        b"3,invoice,89.90\n"
    )

    result = analyze_csv_content(content)

    assert result["row_count"] == 3
    assert result["columns"] == ["document_id", "category", "amount"]
    assert result["missing_values"] == {
        "document_id": 0,
        "category": 0,
        "amount": 1,
    }


def test_analyze_csv_rejects_empty_file():
    with pytest.raises(InvalidCsvError):
        analyze_csv_content(b"")


def test_analyze_csv_rejects_invalid_utf8():
    with pytest.raises(InvalidCsvError):
        analyze_csv_content(b"name\n\xff\n")