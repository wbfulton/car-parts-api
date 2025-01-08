from typing import Annotated

from pydantic import StringConstraints
from sqlalchemy import Boolean, Column, Integer, String

from app.db import Base


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    diagrams_url = Column(String, nullable=True)
    is_root = Column(Boolean, server_default="FALSE")
    # sub_groups: Column(List(int))


class Diagram(Base):
    __tablename__ = "diagrams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    img_url = Column(String, nullable=True)
    # group_id = Column(Integer, index=True, nullable=False)
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
