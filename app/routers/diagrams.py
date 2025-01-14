from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db
from app.routers.souq_scraper_v2 import scrape_group_diagrams

path_tag = "/diagrams"


router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get("/", response_model=List[schemas.Diagram])
async def get_all_diagrams(db: Session = Depends(get_db)):
    diagrams = crud.get_diagrams(db)

    return diagrams


@router.post("/scrape", response_model=List[schemas.CreateDiagram])
async def scrape_all_diagrams(
    db: Session = Depends(get_db), page_length: int = 435, token: int = 0
):
    groups = crud.get_groups_flat(db, page_length=400)

    valid_groups: list[schemas.Group] = []
    for group in groups:
        if group.diagrams_url is not None:
            valid_groups.append(group)

    diagrams: list[schemas.CreateDiagram] = []
    parts: list[schemas.CreatePart] = []
    for valid_group in valid_groups:
        [new_diagrams, new_parts] = await scrape_group_diagrams(valid_group)
        diagrams.extend(new_diagrams)
        parts.extend(new_parts)

    crud.post_bulk_diagrams(db, diagrams)
    crud.post_bulk_parts(db, parts)

    return diagrams


# ensure each group has a diagram
@router.post("/clean", response_model=List[schemas.CreateDiagram])
async def clean_all_diagrams(db: Session = Depends(get_db)):
    groups: list[schemas.Group] = crud.get_groups_flat(db, page_length=400)

    group_w_diagrams: list[schemas.Group] = []
    no_diagrams = 0
    diagrams_no_parts = 0
    for group in groups:
        if group.diagrams_url is not None:
            group_w_diagrams.append(group)
            no_diagrams += 1
        # elif group.diagrams_url is not None and len(group.diagrams) > 0:
        #     missing_parts = False
        #     for diagram in group.diagrams:
        #         if len(diagram.parts) == 0:
        #             diagrams_no_parts += 1
        #             missing_parts = True
        #     if missing_parts:
        #         group_w_diagrams.append(group)

    diagrams: list[schemas.CreateDiagram] = []
    parts: list[schemas.CreatePart] = []

    for group_w_diagram in group_w_diagrams:
        [new_diagrams, new_parts] = await scrape_group_diagrams(group_w_diagram)
        diagrams.extend(new_diagrams)
        parts.extend(new_parts)

    crud.post_bulk_diagrams(db, diagrams)
    crud.post_bulk_parts(db, parts)

    return diagrams
