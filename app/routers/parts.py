from typing import Union
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.data.dummy_data import dummy_part_models_data, dummy_parts_data
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
async def get_part_by_id(part_id: UUID) -> Part:
    for datum in dummy_parts_data:
        if datum["id"] == part_id:
            return datum

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")


@router.get(
    "/part-number/{part_number}",
)
async def get_part_by_part_number(part_number: PartNumber) -> Part:
    print(dummy_parts_data)
    for datum in dummy_parts_data:
        if datum["part_number"] == part_number:
            return datum
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
        )
    dummy_parts_data[idx] = new_part
    return new_part


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(part_id: UUID) -> None:
    idx = -1
    for i in range(len(dummy_parts_data)):
        datum = dummy_parts_data[i]
        if datum["id"] == part_id:
            idx = i
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
        )
    dummy_parts_data.pop(idx)

    for parts_model in dummy_part_models_data:
        if part_id in parts_model["parts"]:
            parts_model["parts"].remove(part_id)
