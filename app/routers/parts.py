from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db

path_tag = "/parts"


router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get("/", response_model=List[schemas.Part])
async def get_all_parts(
    db: Session = Depends(get_db), page_length: int = 10, token: int = 0
):
    parts = crud.get_parts(db, page_length, token)

    print(parts, parts[0])

    return parts
