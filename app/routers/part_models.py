from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.database.dummy_data import dummy_part_models_data
from app.models.parts_model import PartsModel

path_tag = "/parts-model"

router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get("/", tags=[path_tag])
async def get_all_models() -> list[PartsModel]:
    return dummy_part_models_data


@router.get(
    "/{model_id}",
)
async def get_model_by_id(model_id: UUID) -> PartsModel:
    for datum in dummy_part_models_data:
        if datum["id"] == model_id:
            return datum

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")


@router.get(
    "/{model_id}/parts",
    status_code=status.HTTP_201_CREATED,
)
async def get_model_parts(model_id: UUID) -> list[UUID]:
    for datum in dummy_part_models_data:
        if datum["id"] == model_id:
            return datum["parts"]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_parts_model(new_model: PartsModel) -> PartsModel:
    dummy_part_models_data.append(new_model)
    return new_model


@router.put("/", status_code=status.HTTP_201_CREATED)
async def update_parts_model(new_model: PartsModel) -> PartsModel:
    idx = -1
    for i in range(len(dummy_part_models_data)):
        datum = dummy_part_models_data[i]
        if datum["id"] == new_model.id:
            idx = i
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
        )
    dummy_part_models_data[idx] = new_model

    return new_model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parts_model(model_id: UUID) -> None:
    idx = -1
    for i in range(len(dummy_part_models_data)):
        datum = dummy_part_models_data[i]
        if datum["id"] == model_id:
            idx = i
    if idx == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
        )
    dummy_part_models_data.pop(idx)
