from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.file_analysis_repository import get_analysis_by_id, save_analysis
from app.schemas.file_analysis import FileAnalysisResponse
from app.services.csv_service import InvalidCsvError, analyze_csv_content

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/analyses/{analysis_id}", response_model=FileAnalysisResponse)
def get_analysis(analysis_id: int, session: Session = Depends(get_db)):
    try:
        record = get_analysis_by_id(session, analysis_id)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve the analysis. Please try again later.",
        ) from exc

    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    return record


@router.post("/analyze", response_model=FileAnalysisResponse)
def analyze_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
):
    filename = file.filename

    if not filename or not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file.",
        )

    content = file.file.read()

    try:
        analysis = analyze_csv_content(content)
    except InvalidCsvError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    try:
        record = save_analysis(session, filename, analysis)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not save the analysis. Please try again later.",
        ) from exc

    return record
