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


class Part(BaseModel):
    id: int
    number: str
    amount: int | None = None
    note: str | None = None
    name: str
    date_range: str | None = None


class DiagramBase(BaseModel):
    id: int
    name: str
    img_url: Optional[str] = None
    parent_group_id: Optional[int] = None
    # parts: list[Part] | None = None


class CreateDiagram(DiagramBase):
    pass


class Diagram(DiagramBase):
    class Config:
        orm_mode = True


class GroupBase(BaseModel):
    id: int
    name: str
    diagrams_url: Optional[str] = None
    parent_group_id: Optional[int] = None
    diagrams: List["Diagram"]
    sub_groups: List["Group"]


class CreateGroup(GroupBase):
    pass


class Group(GroupBase):
    class Config:
        orm_mode = True
