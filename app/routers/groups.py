from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db
from app.routers.souq_scraper_v2 import scrape_groups

path_tag = "/groups"


router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get("/", response_model=List[schemas.Group])
async def get_all_groups(db: Session = Depends(get_db)):
    groups = crud.get_groups(db)

    return groups


@router.post("/scrape", response_model=List[schemas.Group])
async def scrape_all_groups(db: Session = Depends(get_db)):
    groups = await scrape_groups()

    crud.wipe_groups(db)
    crud.post_bulk_groups(db, groups)

    return groups
