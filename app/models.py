from __future__ import annotations

from typing import Annotated, List

from pydantic import StringConstraints
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, relationship

from app.db import Base

group_group_association_table = Table(
    "group_group_association_table",
    Base.metadata,
    Column("parent_group_id", ForeignKey("groups.id"), primary_key=True),
    Column("child_group_id", ForeignKey("groups.id"), primary_key=True),
)

group_diagram_association_table = Table(
    "group_diagram_association_table",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),
    Column("diagram_id", ForeignKey("diagrams.id"), primary_key=True),
)

# put in amount
diagram_part_association_table = Table(
    "diagram_part_association_table",
    Base.metadata,
    Column("diagram_id", ForeignKey("diagrams.id"), primary_key=True),
    Column("part_id", ForeignKey("parts.id"), primary_key=True),
)


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    diagrams_url = Column(String, nullable=True)

    # relationships

    # Group: Many => Many
    # Child Field
    parents: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="children",
        primaryjoin=(group_group_association_table.c.child_group_id == id),
        secondaryjoin=(group_group_association_table.c.parent_group_id == id),
        secondary=group_group_association_table,
        remote_side=[id],
    )
    # Parent Fields
    children: Mapped[List["Group"]] = relationship(
        "Group",
        secondary=group_group_association_table,
        primaryjoin=(group_group_association_table.c.parent_group_id == id),
        secondaryjoin=(group_group_association_table.c.child_group_id == id),
        back_populates="parents",
    )
    # Diagram: Many => Many
    diagrams: Mapped[List["Diagram"]] = relationship(
        "Diagram",
        secondary=group_diagram_association_table,
        primaryjoin=(group_diagram_association_table.c.group_id == id),
        back_populates="groups",
        passive_deletes=True,
    )


class Diagram(Base):
    __tablename__ = "diagrams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    img_url = Column(String, nullable=True)

    # Group: Many => Many
    groups: Mapped[List["Group"]] = relationship(
        "Group",
        secondary=group_diagram_association_table,
        primaryjoin=(group_diagram_association_table.c.diagram_id == id),
        back_populates="diagrams",
        passive_deletes=True,
    )
    # Parts: Many => Many
    parts: Mapped[List["Part"]] = relationship(
        "Part",
        secondary=diagram_part_association_table,
        primaryjoin=(diagram_part_association_table.c.diagram_id == id),
        back_populates="diagrams",
        passive_deletes=True,
    )


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    number = Column(String, nullable=False)
    # amount = Column(String, nullable=True)
    note = Column(String, nullable=True)
    name = Column(String, nullable=False)
    date_range = Column(String, nullable=True)

    # Relationships
    # Group: Many => Many
    diagrams: Mapped[List["Diagram"]] = relationship(
        "Diagram",
        secondary=diagram_part_association_table,
        primaryjoin=(diagram_part_association_table.c.part_id == id),
        back_populates="parts",
        passive_deletes=True,
    )


# Cache html from urls, specifically group diagrams
class PartsSouqPageData(Base):
    __tablename__ = "parts_souq_data"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    html_string = Column(String, nullable=False)


# TEST THIS
PartNumber = Annotated[
    str,
    StringConstraints(
        min_length=11,
        max_length=11,
        pattern="^\d{5}-[A-Za-z0-9]{4,7}$",
    ),
]
