from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints
from sqlalchemy import Column, String, Uuid

from app.database.db import Base


class PartsTable(Base):
    __tablename__ = "parts"

    id = Column(Uuid, primary_key=True, index=True)
    name = Column(String)
    part_number = Column(String, index=True)
    # old_part_numbers = Column(ARRAY(String))
    description = Column(String)


# TEST THIS
PartNumber = Annotated[
    str,
    StringConstraints(
        min_length=11,
        max_length=11,
        pattern="^\d{5}-[A-Za-z0-9]{4,7}$",
    ),
]


class Part(BaseModel):
    id: UUID
    name: str
    part_number: Annotated[PartNumber, Field(examples=["17801-50040"])]
    # old_part_numbers: list[PartNumber] | None = None
    description: str | None = None

    class Config:
        orm_mode = True
