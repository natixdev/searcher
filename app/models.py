from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Document(Base):
    """Модель документа."""

    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    rubrics: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
