from io import BytesIO

import pandas as pd


class InvalidCsvError(ValueError):
    pass


def analyze_csv_content(content: bytes) -> dict:
    try:
        dataframe = pd.read_csv(BytesIO(content), encoding="utf-8")
    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as exc:
        raise InvalidCsvError(
            "The file must contain valid UTF-8 CSV data."
        ) from exc

    return {
        "row_count": len(dataframe),
        "columns": dataframe.columns.tolist(),
        "missing_values": {
            column: int(count)
            for column, count in dataframe.isna().sum().items()
        },
    }