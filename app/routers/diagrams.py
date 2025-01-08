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


@router.post("/scrape", response_model=List[schemas.Diagram])
async def scrape_all_diagrams(
    db: Session = Depends(get_db), page_length: int = 435, token: int = 0
):
    groups = crud.get_groups(db)

    diagrams: list[schemas.Diagram] = []

    valid_groups: list[schemas.Group] = []
    for group in groups:
        if group.diagrams_url is not None:
            valid_groups.append(group)

    valid_groups: list[schemas.Group] = valid_groups[token : token + page_length]

    diagrams: list[schemas.CreateDiagram] = []
    for valid_group in valid_groups:
        new_diagrams = await scrape_group_diagrams(valid_group)
        diagrams.extend(new_diagrams)

    crud.wipe_diagrams(db)
    crud.post_bulk_diagrams(db, diagrams)

    return diagrams
