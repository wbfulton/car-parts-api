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
    number: str
    # amount: int | None = None
    note: str | None = None
    name: str
    date_range: str | None = None


class Part(PartBase):
    diagrams: List["Diagram"]
    id: int

    class Config:
        orm_mode = True


class CreatePart(PartBase):
    parent_diagram_id: int


class DiagramBase(BaseModel):
    id: int
    name: str
    img_url: Optional[str] = None


class CreateDiagram(DiagramBase):
    parent_group_id: int


class Diagram(DiagramBase):
    parts: list["Part"]
    groups: list["Group"]

    class Config:
        orm_mode = True


class GroupBase(BaseModel):
    id: int
    name: str
    diagrams_url: Optional[str] = None


class CreateGroup(GroupBase):
    parent_group_id: Optional[int] = None


class PartialGroup(GroupBase):
    children: List["PartialGroup"]


class Group(GroupBase):
    parents: List["Group"]
    children: List["Group"]
    diagrams: List["Diagram"]

    class Config:
        orm_mode = True


class PartsSouqPageDataBase(BaseModel):
    id: int
    url: str
    html_string: str


class CreatePartsSouqPageData(PartsSouqPageDataBase):
    pass


class PartsSouqPageData(PartsSouqPageDataBase):
    class Config:
        orm_mode = True
