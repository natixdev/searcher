from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    """Запрос на поиск."""

    text: str = Field(min_length=1)


class DocumentResponse(BaseModel):
    """Документ, возвращаемый клиенту."""

    id: int
    rubrics: list[str]
    text: str
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    """Ответ на поиск."""

    documents: list[DocumentResponse]
