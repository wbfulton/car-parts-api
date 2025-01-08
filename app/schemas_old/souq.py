from pydantic import BaseModel


class SouqQuery(BaseModel):
    c: str
    ssd: str
    cid: str
    cname: str | None = None
    vid: int | None = 0
    q: str | None = ""


class SouqSearchPart(BaseModel):
    name: str
    part_number: str
    parts_avaliable: int = 0
    weight_kg: float
    price_usd: float
    img_url: str | None = None


class SouqCategoryPart(BaseModel):
    number: str
    part_code: str
    car: str
    amount: str | None = None
    name: str | None = None
    note: str | None = None
    date_range: str | None = None
    diagram_uid: int | None = None
    cid: int | None = None
    gid: int | None = None
    ssd: str | None = None


class SouqGroup(BaseModel):
    name: str
    group_number: int
    parent_group_number: int | None = None

    # query
    car: str | None = None
    ssd: str | None = None
    souq_gid: int | None = None


class SouqCategoryDiagram(BaseModel):
    title: str
    number: int
    image_urls: list[str] | None = None
    souq_uid: int
    car: str
    ssd: str
    cid: int
    misc_links: list[str] = []


class SouqGroupDiagram(BaseModel):
    title: str
    gid: int
    img_url: str | None = None
    parts: list[SouqCategoryPart]


class Everything(BaseModel):
    part_category: str
    diagrams: list[SouqGroupDiagram]
    parts: list[SouqGroup]
