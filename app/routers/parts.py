from typing import Union
from uuid import UUID

from fastapi import APIRouter, status

from app.data.dummy_data import dummy_parts_data
from app.models.part import Part, PartNumber

path_tag = "/parts"

router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get(
    "/",
)
async def get_all_parts() -> list[Union[Part, None]]:
    return dummy_parts_data


@router.get(
    "/{part_id}",
)
async def get_part_by_id(part_id: UUID) -> Union[Part, None]:
    for datum in dummy_parts_data:
        if datum["id"] == part_id:
            return datum
    return None


@router.get(
    "/part-number/{part_number}",
)
async def get_part_by_part_number(part_number: PartNumber) -> Part:
    print(dummy_parts_data)
    for datum in dummy_parts_data:
        if datum["part_number"] == part_number:
            return datum


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_part(new_part: Part) -> Part:
    dummy_parts_data.append(new_part)
    return new_part


@router.put("/", status_code=status.HTTP_201_CREATED)
async def update_part(new_part: Part) -> Part:
    idx = -1
    for i in range(len(dummy_parts_data)):
        datum = dummy_parts_data[i]
        if datum["id"] == new_part.id:
            idx = i
    if idx == -1:
        return
    dummy_parts_data[idx] = new_part
    return new_part


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(part_id: UUID) -> None:
    # also must delete from any relevant models
    idx = -1
    for i in range(len(dummy_parts_data)):
        datum = dummy_parts_data[i]
        if datum["id"] == part_id:
            idx = i
    if idx == -1:
        return
    dummy_parts_data.pop(idx)
    return None
