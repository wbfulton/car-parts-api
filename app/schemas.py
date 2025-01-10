from typing import List, Optional

from pydantic import BaseModel


class SouqQuery(BaseModel):
    c: str
    ssd: str
    cid: str
    cname: str | None = None
    vid: int | None = 0
    q: str | None = ""


class PartDetailed(BaseModel):
    name: str
    part_number: str
    parts_avaliable: int = 0
    weight_kg: float
    price_usd: float
    img_url: str | None = None


class PartBase(BaseModel):
    id: int

    number: str
    amount: int | None = None
    name: str
    note: str | None = None
    date_range: str | None = None

    parent_diagram_id: int


class Part(PartBase):
    class Config:
        orm_mode = True


class CreatePart(PartBase):
    pass


class DiagramBase(BaseModel):
    id: int
    name: str
    img_url: Optional[str] = None
    parent_group_id: int


class CreateDiagram(DiagramBase):
    pass


class Diagram(DiagramBase):
    parts: list["Part"]

    class Config:
        orm_mode = True


class GroupBase(BaseModel):
    id: int
    name: str
    diagrams_url: Optional[str] = None
    parent_group_id: Optional[int] = None


class CreateGroup(GroupBase):
    pass


class Group(GroupBase):
    diagrams: List["Diagram"]
    sub_groups: List["Group"]

    class Config:
        orm_mode = True
