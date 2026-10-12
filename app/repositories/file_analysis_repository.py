from sqlalchemy.orm import Session

from app.models.file_analysis import FileAnalysis


def get_analysis_by_id(session: Session, analysis_id: int) -> FileAnalysis | None:
    return session.get(FileAnalysis, analysis_id)


def save_analysis(
    session: Session,
    filename: str,
    analysis: dict,
) -> FileAnalysis:
    record = FileAnalysis(
        filename=filename,
        **analysis,
    )

    try:
        session.add(record)
        session.commit()
        session.refresh(record)
    except Exception:
        session.rollback()
        raise

    return record
