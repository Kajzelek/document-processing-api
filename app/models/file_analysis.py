from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FileAnalysis(Base):
    __tablename__ = "file_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str] = mapped_column(String(255))

    row_count: Mapped[int] = mapped_column(Integer)

    columns: Mapped[list[str]] = mapped_column(JSON)

    missing_values: Mapped[dict[str, int]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )