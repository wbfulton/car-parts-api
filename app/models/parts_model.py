from uuid import UUID

from pydantic import BaseModel


class PartsModel(BaseModel):
    id: UUID
    name: str
    description: str
    category: str | None = None
    parts: list[UUID]