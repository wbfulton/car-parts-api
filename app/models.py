from __future__ import annotations

from typing import Annotated, List

from pydantic import StringConstraints
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.db import Base


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    diagrams_url = Column(String, nullable=True)

    # relationships
    parent_group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True
    )
    parent_group = relationship("Group", back_populates="sub_groups", remote_side=[id])
    diagrams: Mapped[List["Diagram"]] = relationship(
        "Diagram",
        back_populates="parent_group",
        passive_deletes=True,
    )
    sub_groups: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="parent_group",
    )


class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    img_url = Column(String, nullable=True)

    # relationships
    parent_group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    parent_group = relationship(
        "Group",
        back_populates="diagrams",
        passive_deletes=True,
    )
    parts: Mapped[List["Part"]] = relationship(
        "Part",
        back_populates="diagram",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=False)
    amount = Column(String, nullable=True)
    note = Column(String, nullable=True)
    name = Column(String, nullable=False)
    date_range = Column(String, nullable=True)

    # relationships
    parent_diagram_id = Column(
        Integer, ForeignKey("diagrams.id", ondelete="CASCADE"), nullable=False
    )
    diagram = relationship(
        "Diagram",
        back_populates="parts",
        passive_deletes=True,
    )


# TEST THIS
PartNumber = Annotated[
    str,
    StringConstraints(
        min_length=11,
        max_length=11,
        pattern="^\d{5}-[A-Za-z0-9]{4,7}$",
    ),
]
