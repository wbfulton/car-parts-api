from typing import Union
from uuid import UUID

from fastapi import APIRouter, status

from app.models.part import Part
from app.models.parts_model import PartsModel

path_tag = "/parts-model"

router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get("/", tags=[path_tag])
async def get_all_models() -> list[Union[PartsModel, None]]:
    return None


@router.get(
    "/{model_id}",
    status_code=status.HTTP_201_CREATED,
)
async def get_model_by_id(model_id: UUID) -> Union[PartsModel, None]:
    print("model_id", model_id)
    # if part.part_number == "hello":
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return None


@router.get(
    "/{model_id}/parts",
    status_code=status.HTTP_201_CREATED,
)
async def get_model_parts(model_id: UUID) -> Union[list[Part], None]:
    print("model_id", model_id)
    # if part.part_number == "hello":
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_parts_model(newModel: PartsModel) -> Union[PartsModel, None]:
    return newModel


@router.put("/", status_code=status.HTTP_201_CREATED)
async def update_parts_model(newModel: PartsModel) -> Union[PartsModel, None]:
    return newModel


@router.post("/", status_code=status.HTTP_201_CREATED)
async def delete_parts_model() -> Union[PartsModel, None]:
    return None
