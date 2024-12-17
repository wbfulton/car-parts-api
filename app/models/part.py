from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

# TEST THIS
PartNumber = Annotated[
    str,
    StringConstraints(
        min_length=11,
        max_length=11,
        pattern="^\d{5}-\d{5}$",
    ),
]


class Part(BaseModel):
    id: UUID
    name: str
    part_number: Annotated[PartNumber, Field(examples=["17801-50040"])]
    old_part_numbers: list[PartNumber] | None = None
    description: str | None = None
