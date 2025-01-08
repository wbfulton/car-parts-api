from __future__ import annotations

from typing import Annotated, List

from pydantic import StringConstraints
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # duplicate diagrams exist
    diagrams: Mapped[List["Diagram"]] = relationship()
    # duplicate groups exist
    sub_groups: Mapped[List["Group"]] = relationship()
    parent_group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))
    name = Column(String, nullable=False)
    diagrams_url = Column(String, nullable=True)


class Diagram(Base):
    __tablename__ = "diagrams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parent_group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    name = Column(String, nullable=False)
    img_url = Column(String, nullable=True)
    # parts: list[Part] | None = None


# TEST THIS
PartNumber = Annotated[
    str,
    StringConstraints(
        min_length=11,
        max_length=11,
        pattern="^\d{5}-[A-Za-z0-9]{4,7}$",
    ),
]
