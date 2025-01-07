# from typing import Annotated, Any, Generator
# from uuid import UUID

# from fastapi import APIRouter, HTTPException, status
# from sqlalchemy.orm import Session

# from app.database.db import engine, get_db
# from app.database.dummy_data import dummy_part_models_data, dummy_parts_data
# from app.models.part import Part, PartNumber, PartsTable

# path_tag = "/parts"

# PartsTable.metadata.create_all(bind=engine)


# router = APIRouter(
#     prefix=path_tag,
#     tags=[path_tag],
#     dependencies=Annotated[callable[None, Generator[Session, Any, None]], get_db],
# )


# @router.get(
#     "/",
# )
# async def get_all_parts(skip: int = 0, limit: int = 10, search: str = ""):
#     items = (
#         db.query(PartsTable)
#         .filter(
#             PartsTable.part_number.contains(search)
#             or PartsTable.name.contains(search)
#             or PartsTable.description.contains(search)
#         )
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )

#     return items


# @router.get(
#     "/{part_id}",
# )
# async def get_part_by_id(part_id: UUID) -> Part:
#     for datum in dummy_parts_data:
#         if datum["id"] == part_id:
#             return datum

#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")


# @router.get(
#     "/part-number/{part_number}",
# )
# async def get_part_by_part_number(part_number: PartNumber) -> Part:
#     print(dummy_parts_data)
#     for datum in dummy_parts_data:
#         if datum["part_number"] == part_number:
#             return datum
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")


# @router.post("/", status_code=status.HTTP_201_CREATED)
# async def create_part(new_part: Part) -> Part:
#     db_item = PartsTable(**new_part)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item


# # use patch
# @router.put("/", status_code=status.HTTP_201_CREATED)
# async def update_part(new_part: Part) -> Part:
#     idx = -1
#     for i in range(len(dummy_parts_data)):
#         datum = dummy_parts_data[i]
#         if datum["id"] == new_part.id:
#             idx = i
#     if idx == -1:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
#         )
#     dummy_parts_data[idx] = new_part
#     return new_part


# @router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_part(part_id: UUID) -> None:
#     idx = -1
#     for i in range(len(dummy_parts_data)):
#         datum = dummy_parts_data[i]
#         if datum["id"] == part_id:
#             idx = i
#     if idx == -1:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
#         )
#     dummy_parts_data.pop(idx)

#     for parts_model in dummy_part_models_data:
#         if part_id in parts_model["parts"]:
#             parts_model["parts"].remove(part_id)
