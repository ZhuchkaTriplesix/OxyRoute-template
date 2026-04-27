from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ReprMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__
        return "".join([f"_{c.lower()}" if c.isupper() else c for c in name]).lstrip("_")

    def __repr__(self) -> str:
        values: dict[str, Any] = {}
        for column in self.__table__.columns:
            values[column.name] = getattr(self, column.name)
        return f"{self.__class__.__name__}({values})"
