from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    row_count: int
    columns: list[str]
    missing_values: dict[str, int]
    created_at: datetime