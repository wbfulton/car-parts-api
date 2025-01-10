from typing import List

from fastapi import APIRouter, Depends, HTTPException
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


@router.get("/", response_model=List[schemas.PartialGroup])
async def get_nested_groups(db: Session = Depends(get_db)):
    groups = crud.get_groups_nested(db)

    return groups


@router.get("/{id}", response_model=schemas.Group)
async def get_group(id: int, db: Session = Depends(get_db)):
    group: schemas.Group = crud.get_group(db, id)

    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    if len(group.diagrams) == 0:
        raise HTTPException(status_code=400, detail="Group has no diagrams")

    return group


@router.post("/scrape", response_model=List[schemas.CreateGroup])
async def scrape_all_groups(db: Session = Depends(get_db)):
    groups = await scrape_groups()

    crud.wipe_groups(db)
    crud.post_bulk_groups(db, groups)

    return groups


@router.delete("/wipe", response_model=List[schemas.Group])
async def delete_all_groups(db: Session = Depends(get_db)):
    crud.wipe_groups(db)
