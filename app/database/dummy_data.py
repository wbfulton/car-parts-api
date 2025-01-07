from uuid import uuid4

from app.models.part import Part
from app.models.parts_model import PartsModel

id1 = uuid4()
id2 = uuid4()

dummy_parts_data: list[Part] = [
    {
        "id": id1,
        "name": "Air Filter",
        "part_number": "17801-50040",
        "old_part_numbers": [],
        "description": "",
    },
    {
        "id": id2,
        "name": "Spark Plug",
        "part_number": "90080-91180",
        "old_part_numbers": [
            "90080-91181",
            "90919-01178",
            "90919-01210",
            "90919-01237",
            "90919-T1007",
            "90919-01211",
        ],
        "description": "",
    },
]

dummy_part_models_data: list[PartsModel] = [
    {
        "id": uuid4(),
        "name": "Air Filter",
        "description": "paper air filter",
        "category": "",
        "parts": [id1],
    },
]
