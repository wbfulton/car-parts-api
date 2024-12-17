from typing import Union
from uuid import UUID

from fastapi import APIRouter, status

from app.models.part import Part

path_tag = "/parts"

router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get(
    "/",
)
async def get_all_parts() -> list[Union[Part, None]]:
    return None


@router.get(
    "/{part_id}",
)
async def get_part_by_id(part_id: UUID) -> Union[Part, None]:
    print(part_id)
    return None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_part(new_part: Part) -> Union[Part, None]:
    return new_part


@router.put("/", status_code=status.HTTP_201_CREATED)
async def update_part(new_part: Part) -> Union[Part, None]:
    return new_part


@router.post("/", status_code=status.HTTP_201_CREATED)
async def delete_part() -> Union[Part, None]:
    # also must delete from any relevant models
    return None
