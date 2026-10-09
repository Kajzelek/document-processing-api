from io import BytesIO

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(
    title="Document Processing API",
    description="An API for processing documents and tabular data.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/files/analyze")
def analyze_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    content = file.file.read()

    try:
        dataframe = pd.read_csv(BytesIO(content), encoding="utf-8")
    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ):
        raise HTTPException(
            status_code=400,
            detail="The file must contain valid UTF-8 CSV data.",
        )

    return {
        "filename": file.filename,
        "row_count": len(dataframe),
        "columns": dataframe.columns.tolist(),
        "missing_values": {
            column: int(count)
            for column, count in dataframe.isna().sum().items()
        },
    }